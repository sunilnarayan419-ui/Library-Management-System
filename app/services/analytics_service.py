"""Analytics/reporting service. Kept independent from API routes so the
same calculations can be reused by scripts, tests, or a future async
job runner."""
from __future__ import annotations

import datetime as dt
from collections import Counter

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.book import Book
from app.models.book_copy import BookCopy, CopyStatus
from app.models.fine import Fine, FineStatus
from app.models.loan import Loan, LoanStatus
from app.models.reservation import Reservation, ReservationStatus
from app.models.user import User, UserStatus
from app.schemas.analytics import CategoryShare, DashboardSummary, MonthlyCirculation, TopBook


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def dashboard_summary(self) -> DashboardSummary:
        total_books = self.db.execute(select(func.count()).select_from(Book)).scalar_one()
        total_copies = self.db.execute(select(func.count()).select_from(BookCopy)).scalar_one()
        available_copies = self.db.execute(
            select(func.count()).select_from(BookCopy).where(BookCopy.status == CopyStatus.AVAILABLE)
        ).scalar_one()
        issued_copies = self.db.execute(
            select(func.count()).select_from(BookCopy).where(BookCopy.status == CopyStatus.ISSUED)
        ).scalar_one()
        overdue_loans = self.db.execute(
            select(func.count()).select_from(Loan).where(Loan.status == LoanStatus.OVERDUE)
        ).scalar_one()
        active_members = self.db.execute(
            select(func.count()).select_from(User).where(User.status == UserStatus.ACTIVE)
        ).scalar_one()
        pending_reservations = self.db.execute(
            select(func.count()).select_from(Reservation).where(Reservation.status == ReservationStatus.PENDING)
        ).scalar_one()
        outstanding = self.db.execute(
            select(func.coalesce(func.sum(Fine.amount), 0.0)).where(Fine.status == FineStatus.OUTSTANDING)
        ).scalar_one()

        return DashboardSummary(
            total_books=total_books,
            total_copies=total_copies,
            available_copies=available_copies,
            issued_copies=issued_copies,
            overdue_loans=overdue_loans,
            active_members=active_members,
            pending_reservations=pending_reservations,
            outstanding_fines_amount=float(outstanding),
        )

    def most_borrowed_books(self, limit: int = 10) -> list[TopBook]:
        rows = self.db.execute(select(Loan.book_id, func.count(Loan.id)).group_by(Loan.book_id)).all()
        counts = Counter({book_id: count for book_id, count in rows})
        top = counts.most_common(limit)
        results = []
        for book_id, count in top:
            book = self.db.get(Book, book_id)
            if book:
                results.append(TopBook(book_id=book_id, title=book.title, borrow_count=count))
        return results

    def category_distribution(self) -> list[CategoryShare]:
        rows = self.db.execute(
            select(Book.category, func.count(Book.id)).group_by(Book.category)
        ).all()
        return [CategoryShare(category=cat or "Uncategorized", count=count) for cat, count in rows]

    def monthly_circulation(self, months: int = 6) -> list[MonthlyCirculation]:
        loans = list(self.db.execute(select(Loan)).scalars().all())
        buckets: dict[str, dict[str, int]] = {}
        now = dt.datetime.now(dt.UTC)

        # Build an ordered list of the last `months` "YYYY-MM" keys.
        keys = []
        y, m = now.year, now.month
        for _ in range(months):
            keys.append(f"{y:04d}-{m:02d}")
            m -= 1
            if m == 0:
                m = 12
                y -= 1
        keys.reverse()
        for k in keys:
            buckets[k] = {"issued": 0, "returned": 0}

        for loan in loans:
            issued_key = loan.issued_at.strftime("%Y-%m")
            if issued_key in buckets:
                buckets[issued_key]["issued"] += 1
            if loan.returned_at:
                returned_key = loan.returned_at.strftime("%Y-%m")
                if returned_key in buckets:
                    buckets[returned_key]["returned"] += 1

        return [MonthlyCirculation(month=k, issued=v["issued"], returned=v["returned"]) for k, v in buckets.items()]

    def utilization_rate(self) -> float:
        total = self.db.execute(select(func.count()).select_from(BookCopy)).scalar_one()
        if total == 0:
            return 0.0
        issued = self.db.execute(
            select(func.count()).select_from(BookCopy).where(BookCopy.status == CopyStatus.ISSUED)
        ).scalar_one()
        return round(issued / total * 100, 2)
