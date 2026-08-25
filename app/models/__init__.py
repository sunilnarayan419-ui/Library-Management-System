"""SQLAlchemy ORM models. Import all models here so Alembic autogenerate
and Base.metadata.create_all() can discover them.
"""
from app.models.audit_log import AuditLog  # noqa: F401
from app.models.book import Book  # noqa: F401
from app.models.book_copy import BookCopy, CopyStatus  # noqa: F401
from app.models.fine import Fine, FineStatus  # noqa: F401
from app.models.loan import Loan, LoanStatus  # noqa: F401
from app.models.reservation import Reservation, ReservationStatus  # noqa: F401
from app.models.user import User, UserRole, UserStatus  # noqa: F401
