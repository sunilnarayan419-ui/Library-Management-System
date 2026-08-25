from __future__ import annotations

from sqlalchemy import select

from app.models.reservation import Reservation, ReservationStatus
from app.repositories.implementations.sqlalchemy_repo import SQLAlchemyRepository


class ReservationRepository(SQLAlchemyRepository[Reservation]):
    model = Reservation

    def next_pending_for_book(self, book_id: str) -> Reservation | None:
        stmt = (
            select(Reservation)
            .where(Reservation.book_id == book_id, Reservation.status == ReservationStatus.PENDING)
            .order_by(Reservation.reserved_at.asc())
            .limit(1)
        )
        return self.db.execute(stmt).scalars().first()
