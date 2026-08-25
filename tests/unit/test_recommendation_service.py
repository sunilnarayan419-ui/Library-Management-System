"""Unit tests for the deterministic, explainable recommendation engine."""
from __future__ import annotations

from app.services.book_service import BookService
from app.services.circulation_service import CirculationService
from app.services.recommendation_service import RecommendationService


def test_recommends_same_category_with_reason(db_session, member_user):
    db_session.commit()
    books = BookService(db_session)
    scifi_1 = books.create_book(title="Dune", author="Frank Herbert", category="Sci-Fi", initial_copies=1)
    scifi_2 = books.create_book(title="Foundation", author="Isaac Asimov", category="Sci-Fi", initial_copies=1)
    db_session.commit()

    circ = CirculationService(db_session)
    loan = circ.issue_book(scifi_1.id, member_user.id)
    db_session.commit()
    circ.return_book(loan.id)
    db_session.commit()

    recs = RecommendationService(db_session).recommend_for_member(member_user.id)
    titles = [r.book.title for r in recs]

    assert scifi_2.title in titles
    matched = next(r for r in recs if r.book.id == scifi_2.id)
    assert any("Sci-Fi" in reason for reason in matched.reasons)


def test_does_not_recommend_already_borrowed_book(db_session, member_user):
    db_session.commit()
    books = BookService(db_session)
    book = books.create_book(title="1984", author="George Orwell", category="Dystopian", initial_copies=1)
    db_session.commit()

    circ = CirculationService(db_session)
    circ.issue_book(book.id, member_user.id)
    db_session.commit()

    recs = RecommendationService(db_session).recommend_for_member(member_user.id)
    assert all(r.book.id != book.id for r in recs)
