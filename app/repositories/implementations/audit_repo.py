from __future__ import annotations

from sqlalchemy import select

from app.models.audit_log import AuditLog
from app.repositories.implementations.sqlalchemy_repo import SQLAlchemyRepository


class AuditRepository(SQLAlchemyRepository[AuditLog]):
    model = AuditLog

    def recent(self, limit: int = 50) -> list[AuditLog]:
        stmt = select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit)
        return list(self.db.execute(stmt).scalars().all())
