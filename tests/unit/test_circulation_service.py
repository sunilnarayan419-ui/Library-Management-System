"""Unit tests for circulation business rules (issue/return/renew/reserve)."""
from __future__ import annotations

import pytest

from app.core.exceptions import BookUnavailable, RenewalNotAllowed, ValidationError
from app.models.book_copy import CopyStatus
from app.services.book_service import BookService
from app.services.circulation_service import CirculationService


def _make_book(db_session, copies: int = 1):
    return BookService(db_session).create_book(
        title="Clean Code", author="Robert C. Martin", category="Software", initial_copies=copies
    )


def test_issue_book_marks_copy_issued(db_session, member_user):
    db_session.commit()
    book = _make_book(db_session)
    db_session.commit()

    circ = CirculationService(db_session)
    loan = circ.issue_book(book.id, member_user.id)
    db_session.commit()

    assert loan.status.value == "ACTIVE"
    copy = circ.copies.get(loan.copy_id)
    assert copy.status == CopyStatus.ISSUED


def test_issue_book_fails_when_no_copies_available(db_session, member_user):
    db_session.commit()
    book = _make_book(db_session, copies=1)
    db_session.commit()
    circ = CirculationService(db_session)
    circ.issue_book(book.id, member_user.id)
    db_session.commit()

    with pytest.raises(BookUnavailable):
        circ.issue_book(book.id, member_user.id)


def test_return_book_makes_copy_available_again(db_session, member_user):
    db_session.commit()
    book = _make_book(db_session)
    db_session.commit()
    circ = CirculationService(db_session)
    loan = circ.issue_book(book.id, member_user.id)
    db_session.commit()

    returned_loan, fine = circ.return_book(loan.id)
    db_session.commit()

    assert returned_loan.status.value == "RETURNED"
    assert fine is None
    copy = circ.copies.get(loan.copy_id)
    assert copy.status == CopyStatus.AVAILABLE


def test_renew_increments_count_and_extends_due_date(db_session, member_user):
    db_session.commit()
    book = _make_book(db_session)
    db_session.commit()
    circ = CirculationService(db_session)
    loan = circ.issue_book(book.id, member_user.id)
    db_session.commit()
    original_due = loan.due_at

    renewed = circ.renew_loan(loan.id)
    db_session.commit()

    assert renewed.renewal_count == 1
    assert renewed.due_at > original_due


def test_renew_blocked_after_max_renewals(db_session, member_user):
    db_session.commit()
    book = _make_book(db_session)
    db_session.commit()
    circ = CirculationService(db_session)
    loan = circ.issue_book(book.id, member_user.id)
    db_session.commit()

    circ.renew_loan(loan.id)
    circ.renew_loan(loan.id)
    db_session.commit()

    with pytest.raises(RenewalNotAllowed):
        circ.renew_loan(loan.id)


def test_reserve_blocked_when_copies_available(db_session, member_user):
    db_session.commit()
    book = _make_book(db_session)
    db_session.commit()
    circ = CirculationService(db_session)

    with pytest.raises(ValidationError):
        circ.reserve_book(book.id, member_user.id)


def test_reserve_allowed_when_no_copies_available_and_fulfilled_on_return(db_session, member_user, admin_user):
    db_session.commit()
    book = _make_book(db_session, copies=1)
    db_session.commit()
    circ = CirculationService(db_session)

    loan = circ.issue_book(book.id, admin_user.id)
    db_session.commit()

    reservation = circ.reserve_book(book.id, member_user.id)
    db_session.commit()
    assert reservation.status.value == "PENDING"

    circ.return_book(loan.id)
    db_session.commit()

    copy = circ.copies.get(loan.copy_id)
    assert copy.status == CopyStatus.RESERVED
    db_session.refresh(reservation)
    assert reservation.status.value == "FULFILLED"
