from __future__ import annotations

from sqlalchemy import select

from app.models.loan import Loan, LoanStatus
from app.repositories.implementations.sqlalchemy_repo import SQLAlchemyRepository


class LoanRepository(SQLAlchemyRepository[Loan]):
    model = Loan

    def active_loans(self, member_id: str | None = None) -> list[Loan]:
        stmt = select(Loan).where(Loan.status.in_([LoanStatus.ACTIVE, LoanStatus.OVERDUE]))
        if member_id:
            stmt = stmt.where(Loan.member_id == member_id)
        return list(self.db.execute(stmt).scalars().all())

    def active_loan_for_copy(self, copy_id: str) -> Loan | None:
        stmt = select(Loan).where(
            Loan.copy_id == copy_id, Loan.status.in_([LoanStatus.ACTIVE, LoanStatus.OVERDUE])
        )
        return self.db.execute(stmt).scalars().first()

    def history_for_member(self, member_id: str) -> list[Loan]:
        stmt = select(Loan).where(Loan.member_id == member_id).order_by(Loan.issued_at.desc())
        return list(self.db.execute(stmt).scalars().all())
