"""Authentication service: registration, login, and token refresh."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import (
    AccountDisabled,
    DuplicateEmail,
    InvalidCredentials,
    InvalidToken,
    UserNotFound,
)
from app.core.security import create_token, decode_token, hash_password, verify_password
from app.models.user import User, UserRole, UserStatus
from app.repositories.implementations.user_repo import UserRepository
from app.services.audit_service import AuditService


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.audit = AuditService(db)

    def register(self, name: str, email: str, password: str, role: UserRole = UserRole.MEMBER) -> User:
        if self.users.get_by_email(email):
            raise DuplicateEmail(f"A user with email '{email}' already exists")
        user = User(name=name, email=email.lower(), password_hash=hash_password(password), role=role)
        self.users.add(user)
        self.audit.record("USER_REGISTERED", "user", user.id, actor=user)
        return user

    def authenticate(self, email: str, password: str) -> User:
        user = self.users.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise InvalidCredentials("Invalid email or password")
        if user.status != UserStatus.ACTIVE:
            raise AccountDisabled("This account has been disabled")

        import datetime as dt

        user.last_login_at = dt.datetime.now(dt.UTC)
        self.db.flush()
        self.audit.record("USER_LOGIN", "user", user.id, actor=user)
        return user

    def issue_tokens(self, user: User) -> dict[str, str]:
        access = create_token(user.id, user.role.value, "access")
        refresh = create_token(user.id, user.role.value, "refresh")
        return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}

    def refresh(self, refresh_token: str) -> dict[str, str]:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise InvalidToken("Provided token is not a refresh token")
        user = self.users.get(payload["sub"])
        if not user:
            raise UserNotFound("User no longer exists")
        if user.status != UserStatus.ACTIVE:
            raise AccountDisabled("This account has been disabled")
        return self.issue_tokens(user)

    def get_current_user(self, access_token: str) -> User:
        payload = decode_token(access_token)
        if payload.get("type") != "access":
            raise InvalidToken("Provided token is not an access token")
        user = self.users.get(payload["sub"])
        if not user:
            raise UserNotFound("User no longer exists")
        if user.status != UserStatus.ACTIVE:
            raise AccountDisabled("This account has been disabled")
        return user
