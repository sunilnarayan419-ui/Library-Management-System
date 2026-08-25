"""User/member management service (admin-facing CRUD)."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import DuplicateEmail, UserNotFound
from app.core.security import hash_password
from app.models.user import User, UserRole, UserStatus
from app.repositories.implementations.user_repo import UserRepository
from app.services.audit_service import AuditService


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.audit = AuditService(db)

    def create_user(self, name: str, email: str, password: str, role: UserRole, actor: User | None = None) -> User:
        if self.users.get_by_email(email):
            raise DuplicateEmail(f"A user with email '{email}' already exists")
        user = User(name=name, email=email.lower(), password_hash=hash_password(password), role=role)
        self.users.add(user)
        self.audit.record("USER_CREATED", "user", user.id, actor=actor)
        return user

    def get_user(self, user_id: str) -> User:
        user = self.users.get(user_id)
        if not user:
            raise UserNotFound(f"User '{user_id}' not found")
        return user

    def list_users(self, offset: int = 0, limit: int = 20, role: UserRole | None = None) -> list[User]:
        return self.users.list(offset=offset, limit=limit, role=role)

    def update_role(self, user_id: str, role: UserRole, actor: User | None = None) -> User:
        user = self.get_user(user_id)
        old_role = user.role
        user.role = role
        self.db.flush()
        self.audit.record("USER_ROLE_CHANGED", "user", user.id, actor=actor, metadata={"from": old_role.value, "to": role.value})
        return user

    def set_status(self, user_id: str, status: UserStatus, actor: User | None = None) -> User:
        user = self.get_user(user_id)
        user.status = status
        self.db.flush()
        action = "USER_DISABLED" if status == UserStatus.DISABLED else "USER_ENABLED"
        self.audit.record(action, "user", user.id, actor=actor)
        return user
