#!/usr/bin/env python
"""Create (or promote) an administrator account.

Usage:
    python scripts/create_admin.py --email admin@example.com --password 'ChangeMe123!' --name 'Site Admin'

Never rely on a hardcoded default admin password in production — this
script exists specifically so no such default needs to ship in code.
"""
from __future__ import annotations

import argparse
import sys

sys.path.insert(0, ".")

from app.core.exceptions import DuplicateEmail
from app.database.base import Base
from app.database.session import SessionLocal, engine
from app.models.user import UserRole, UserStatus
from app.services.auth_service import AuthService


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--name", default="Administrator")
    args = parser.parse_args()

    if len(args.password) < 8:
        print("Password must be at least 8 characters.", file=sys.stderr)
        sys.exit(1)

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        service = AuthService(db)
        try:
            user = service.register(args.name, args.email, args.password, role=UserRole.ADMIN)
        except DuplicateEmail:
            user = service.users.get_by_email(args.email)
            user.role = UserRole.ADMIN
            user.status = UserStatus.ACTIVE
        db.commit()
        print(f"Admin account ready: {user.email} (id={user.id})")
    finally:
        db.close()


if __name__ == "__main__":
    main()
