from __future__ import annotations

from app.services.analytics_service import AnalyticsService
from app.services.book_service import BookService
from app.services.circulation_service import CirculationService


def test_dashboard_summary_reflects_catalog_and_loans(db_session, member_user):
    db_session.commit()
    book = BookService(db_session).create_book(title="Refactoring", author="Martin Fowler", initial_copies=2)
    db_session.commit()

    circ = CirculationService(db_session)
    circ.issue_book(book.id, member_user.id)
    db_session.commit()

    summary = AnalyticsService(db_session).dashboard_summary()
    assert summary.total_books == 1
    assert summary.total_copies == 2
    assert summary.available_copies == 1
    assert summary.issued_copies == 1


def test_utilization_rate_is_percentage(db_session, member_user):
    db_session.commit()
    book = BookService(db_session).create_book(title="Refactoring", author="Martin Fowler", initial_copies=4)
    db_session.commit()
    circ = CirculationService(db_session)
    circ.issue_book(book.id, member_user.id)
    db_session.commit()

    rate = AnalyticsService(db_session).utilization_rate()
    assert rate == 25.0
