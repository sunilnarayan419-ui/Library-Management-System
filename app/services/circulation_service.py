"""Circulation domain service: issue, return, renew, reserve, cancel.

All state transitions for BookCopy/Loan/Reservation/Fine happen here and
nowhere else, so business rules stay in one place. Each public method
runs inside the caller's existing SQLAlchemy Session/transaction; on any
exception the API layer's session dependency rolls back the transaction,
so partially-applied circulation changes are never committed.
"""
from __future__ import annotations

import datetime as dt

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import (
    AlreadyReturned,
    BookNotFound,
    BookUnavailable,
    LoanNotFound,
    RenewalNotAllowed,
    ReservationNotFound,
    ValidationError,
)
from app.models.book_copy import ALLOWED_COPY_TRANSITIONS, BookCopy, CopyStatus
from app.models.fine import Fine, FineStatus
from app.models.loan import Loan, LoanStatus
from app.models.reservation import Reservation, ReservationStatus
from app.models.user import User
from app.repositories.implementations.book_copy_repo import BookCopyRepository
from app.repositories.implementations.book_repo import BookRepository
from app.repositories.implementations.fine_repo import FineRepository
from app.repositories.implementations.loan_repo import LoanRepository
from app.repositories.implementations.reservation_repo import ReservationRepository
from app.services.audit_service import AuditService


def _now() -> dt.datetime:
    return dt.datetime.now(dt.UTC)


class CirculationService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.books = BookRepository(db)
        self.copies = BookCopyRepository(db)
        self.loans = LoanRepository(db)
        self.reservations = ReservationRepository(db)
        self.fines = FineRepository(db)
        self.audit = AuditService(db)

    # -- internal: state machine enforcement -----------------------------
    def _transition_copy(self, copy: BookCopy, new_status: CopyStatus) -> None:
        allowed = ALLOWED_COPY_TRANSITIONS.get(copy.status, set())
        if new_status not in allowed and new_status != copy.status:
            raise ValidationError(f"Cannot move copy from {copy.status} to {new_status}")
        copy.status = new_status
        self.db.flush()

    # -- issue -------------------------------------------------------------
    def issue_book(self, book_id: str, member_id: str, days: int | None = None, actor: User | None = None) -> Loan:
        book = self.books.get(book_id)
        if not book:
            raise BookNotFound(f"Book '{book_id}' not found")

        copy = self.copies.first_available_for_book(book_id)
        if not copy:
            raise BookUnavailable(f"No available copies of '{book.title}' right now")

        # Re-validate the copy is still AVAILABLE at the moment of transition
        # (guards against a lost race in a concurrent request).
        if copy.status != CopyStatus.AVAILABLE:
            raise BookUnavailable(f"No available copies of '{book.title}' right now")

        loan_days = days or self.settings.default_loan_period_days
        due_at = _now() + dt.timedelta(days=loan_days)

        loan = Loan(
            copy_id=copy.id,
            book_id=book.id,
            member_id=member_id,
            issued_by_id=actor.id if actor else None,
            due_at=due_at,
            status=LoanStatus.ACTIVE,
        )
        self.loans.add(loan)
        self._transition_copy(copy, CopyStatus.ISSUED)

        self.audit.record(
            "BOOK_ISSUED", "loan", loan.id, actor=actor,
            metadata={"book_id": book.id, "member_id": member_id, "due_at": due_at.isoformat()},
        )
        return loan

    # -- return ------------------------------------------------------------
    def return_book(self, loan_id: str, actor: User | None = None) -> tuple[Loan, Fine | None]:
        loan = self.loans.get(loan_id)
        if not loan:
            raise LoanNotFound(f"Loan '{loan_id}' not found")
        if loan.status == LoanStatus.RETURNED:
            raise AlreadyReturned("This loan has already been returned")

        copy = self.copies.get(loan.copy_id)
        now = _now()
        loan.returned_at = now
        loan.status = LoanStatus.RETURNED

        fine: Fine | None = None
        if loan.is_overdue(now):
            days_late = (now - (loan.due_at if loan.due_at.tzinfo else loan.due_at.replace(tzinfo=dt.UTC))).days
            amount = max(days_late, 0) * self.settings.fine_per_day
            if amount > 0:
                fine = Fine(loan_id=loan.id, member_id=loan.member_id, amount=amount, reason="Overdue return")
                self.fines.add(fine)

        self.db.flush()

        # Fulfil the next pending reservation for this book, if any; otherwise
        # release the copy back into general circulation.
        next_reservation = self.reservations.next_pending_for_book(loan.book_id)
        if copy:
            # A copy always returns to AVAILABLE first (the only state ISSUED
            # may transition into), then moves on to RESERVED if someone is
            # waiting — two explicit, individually-valid transitions rather
            # than a single ISSUED -> RESERVED jump that isn't in the
            # allowed-transition table.
            self._transition_copy(copy, CopyStatus.AVAILABLE)
            if next_reservation:
                self._transition_copy(copy, CopyStatus.RESERVED)
                next_reservation.status = ReservationStatus.FULFILLED
                self.db.flush()

        self.audit.record(
            "BOOK_RETURNED", "loan", loan.id, actor=actor,
            metadata={"fine_amount": fine.amount if fine else 0},
        )
        return loan, fine

    # -- renew ---------------------------------------------------------------
    def renew_loan(self, loan_id: str, actor: User | None = None) -> Loan:
        loan = self.loans.get(loan_id)
        if not loan:
            raise LoanNotFound(f"Loan '{loan_id}' not found")
        if loan.status == LoanStatus.RETURNED:
            raise AlreadyReturned("Cannot renew a loan that has already been returned")
        if loan.renewal_count >= self.settings.max_renewals:
            raise RenewalNotAllowed(f"Maximum of {self.settings.max_renewals} renewals reached")

        pending_reservation = self.reservations.next_pending_for_book(loan.book_id)
        if pending_reservation:
            raise RenewalNotAllowed("Cannot renew: another member is waiting on a reservation")

        loan.due_at = loan.due_at + dt.timedelta(days=self.settings.default_loan_period_days)
        loan.renewal_count += 1
        loan.status = LoanStatus.ACTIVE
        self.db.flush()

        self.audit.record("BOOK_RENEWED", "loan", loan.id, actor=actor, metadata={"new_due_at": loan.due_at.isoformat()})
        return loan

    # -- reservations ----------------------------------------------------
    def reserve_book(self, book_id: str, member_id: str, actor: User | None = None) -> Reservation:
        book = self.books.get(book_id)
        if not book:
            raise BookNotFound(f"Book '{book_id}' not found")

        available = self.copies.first_available_for_book(book_id)
        if available:
            raise ValidationError("Book has available copies; issue it directly instead of reserving")

        reservation = Reservation(book_id=book_id, member_id=member_id)
        self.reservations.add(reservation)
        self.audit.record("RESERVATION_CREATED", "reservation", reservation.id, actor=actor)
        return reservation

    def cancel_reservation(self, reservation_id: str, actor: User | None = None) -> Reservation:
        reservation = self.reservations.get(reservation_id)
        if not reservation:
            raise ReservationNotFound(f"Reservation '{reservation_id}' not found")
        if reservation.status != ReservationStatus.PENDING:
            raise ValidationError("Only pending reservations can be cancelled")
        reservation.status = ReservationStatus.CANCELLED
        self.db.flush()
        self.audit.record("RESERVATION_CANCELLED", "reservation", reservation.id, actor=actor)
        return reservation

    # -- overdue sweep -----------------------------------------------------
    def mark_overdue_loans(self) -> int:
        """Flip ACTIVE loans past their due date to OVERDUE. Idempotent."""
        now = _now()
        count = 0
        for loan in self.loans.active_loans():
            if loan.status == LoanStatus.ACTIVE and loan.is_overdue(now):
                loan.status = LoanStatus.OVERDUE
                count += 1
        if count:
            self.db.flush()
        return count

    def pay_fine(self, fine_id: str, actor: User | None = None) -> Fine:
        fine = self.fines.get(fine_id)
        if not fine:
            raise ValidationError("Fine not found")
        fine.status = FineStatus.PAID
        fine.settled_at = _now()
        self.db.flush()
        self.audit.record("FINE_PAID", "fine", fine.id, actor=actor)
        return fine
