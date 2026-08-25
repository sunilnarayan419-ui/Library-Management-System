"""Append-only audit logging service."""
from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.user import User
from app.repositories.implementations.audit_repo import AuditRepository


class AuditService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AuditRepository(db)

    def record(
        self,
        action: str,
        resource: str,
        resource_id: str | None = None,
        actor: User | None = None,
        ip_address: str | None = None,
        metadata: dict | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            actor_id=actor.id if actor else None,
            actor_name=actor.name if actor else "system",
            action=action,
            resource=resource,
            resource_id=resource_id,
            ip_address=ip_address,
            metadata_json=json.dumps(metadata) if metadata else None,
        )
        return self.repo.add(entry)

    def recent(self, limit: int = 50) -> list[AuditLog]:
        return self.repo.recent(limit=limit)
