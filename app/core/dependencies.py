"""Shared FastAPI dependencies: DB session, current user, RBAC guards."""
from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.exceptions import Forbidden, InvalidToken
from app.database.session import get_db
from app.models.user import User, UserRole
from app.services.auth_service import AuthService

# Explicit, centralized permission map: role -> permissions.
# Services/routes check permissions via `require_permission(...)` instead of
# scattering `if role == "admin"` checks throughout the codebase.
ROLE_PERMISSIONS: dict[UserRole, set[str]] = {
    UserRole.ADMIN: {
        "books:create", "books:update", "books:delete", "books:view",
        "circulation:issue", "circulation:return", "circulation:renew",
        "users:create", "users:update", "users:disable",
        "analytics:view", "audit:view",
    },
    UserRole.LIBRARIAN: {
        "books:create", "books:update", "books:view",
        "circulation:issue", "circulation:return", "circulation:renew",
        "analytics:view", "audit:view",
    },
    UserRole.MEMBER: {
        "books:view",
    },
}


def get_token_from_header(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise InvalidToken("Missing or malformed Authorization header")
    return authorization.split(" ", 1)[1]


def get_current_user(token: str = Depends(get_token_from_header), db: Session = Depends(get_db)) -> User:
    return AuthService(db).get_current_user(token)


def require_permission(permission: str) -> Callable[[User], User]:
    def _dependency(user: User = Depends(get_current_user)) -> User:
        if permission not in ROLE_PERMISSIONS.get(user.role, set()):
            raise Forbidden(f"Role '{user.role.value}' lacks permission '{permission}'")
        return user

    return _dependency
