"""Deterministic, explainable book recommendation engine.

No ML model is used (and none is claimed) — recommendations are derived
from simple, auditable signals: the member's own borrowing history
(category/author preference) plus catalog-wide popularity. Each
recommendation includes plain-language reasons.
"""
from __future__ import annotations

from collections import Counter

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.book import Book
from app.models.loan import Loan

ScoredRecommendation = tuple[float, "Recommendation"]


class Recommendation:
    def __init__(self, book: Book, reasons: list[str]):
        self.book = book
        self.reasons = reasons

    def to_dict(self) -> dict:
        return {
            "book_id": self.book.id,
            "title": self.book.title,
            "author": self.book.author,
            "category": self.book.category,
            "reasons": self.reasons,
        }


class RecommendationService:
    def __init__(self, db: Session):
        self.db = db

    def recommend_for_member(self, member_id: str, limit: int = 5) -> list[Recommendation]:
        history = list(
            self.db.execute(select(Loan).where(Loan.member_id == member_id)).scalars().all()
        )
        borrowed_book_ids = {loan.book_id for loan in history}
        borrowed_books: list[Book] = [b for bid in borrowed_book_ids if (b := self.db.get(Book, bid)) is not None]

        category_counts = Counter(b.category for b in borrowed_books if b.category)
        author_counts = Counter(b.author for b in borrowed_books if b.author)

        popularity = Counter(loan.book_id for loan in self.db.execute(select(Loan)).scalars().all())

        candidates = list(self.db.execute(select(Book)).scalars().all())
        scored: list[ScoredRecommendation] = []

        for book in candidates:
            if book.id in borrowed_book_ids:
                continue
            reasons: list[str] = []
            score = 0.0

            if book.category and category_counts.get(book.category):
                score += 2 * category_counts[book.category]
                reasons.append(f"You frequently borrow {book.category} books")

            if author_counts.get(book.author):
                score += 3 * author_counts[book.author]
                reasons.append(f"You previously borrowed books by {book.author}")

            pop = popularity.get(book.id, 0)
            if pop:
                score += 0.5 * pop
                reasons.append("This title is popular among readers in your library")

            if score > 0:
                scored.append((score, Recommendation(book, reasons)))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        results = [rec for _, rec in scored[:limit]]

        if len(results) < limit:
            # Fall back to overall popularity for members with no history yet.
            popular_ids = [bid for bid, _ in popularity.most_common(limit * 2)]
            for bid in popular_ids:
                if len(results) >= limit:
                    break
                if bid in borrowed_book_ids or any(r.book.id == bid for r in results):
                    continue
                fallback_book = self.db.get(Book, bid)
                if fallback_book:
                    results.append(Recommendation(fallback_book, ["Popular among readers in your library"]))

        return results[:limit]
