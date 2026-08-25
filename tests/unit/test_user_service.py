from __future__ import annotations

import pytest

from app.core.exceptions import DuplicateEmail
from app.models.user import UserRole, UserStatus
from app.services.user_service import UserService


def test_create_user_and_role_change(db_session):
    svc = UserService(db_session)
    user = svc.create_user("Nina", "nina@example.com", "Password123", UserRole.MEMBER)
    db_session.commit()

    updated = svc.update_role(user.id, UserRole.LIBRARIAN)
    db_session.commit()
    assert updated.role == UserRole.LIBRARIAN


def test_duplicate_email_rejected(db_session):
    svc = UserService(db_session)
    svc.create_user("Nina", "dupe@example.com", "Password123", UserRole.MEMBER)
    db_session.commit()
    with pytest.raises(DuplicateEmail):
        svc.create_user("Nina2", "dupe@example.com", "Password123", UserRole.MEMBER)


def test_disable_user_sets_status(db_session):
    svc = UserService(db_session)
    user = svc.create_user("Omar", "omar@example.com", "Password123", UserRole.MEMBER)
    db_session.commit()
    disabled = svc.set_status(user.id, UserStatus.DISABLED)
    db_session.commit()
    assert disabled.status == UserStatus.DISABLED
