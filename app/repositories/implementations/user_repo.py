from __future__ import annotations

from sqlalchemy import select

from app.models.user import User
from app.repositories.implementations.sqlalchemy_repo import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository[User]):
    model = User

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(func_lower_eq(User.email, email))
        return self.db.execute(stmt).scalars().first()


def func_lower_eq(column, value: str):
    from sqlalchemy import func

    return func.lower(column) == value.lower()
