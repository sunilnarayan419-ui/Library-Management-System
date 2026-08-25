from __future__ import annotations

from app.models.fine import Fine
from app.repositories.implementations.sqlalchemy_repo import SQLAlchemyRepository


class FineRepository(SQLAlchemyRepository[Fine]):
    model = Fine
