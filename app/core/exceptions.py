"""Centralized application exceptions.

All domain/service-layer errors should raise one of these instead of
generic exceptions, so the API layer can translate them into consistent
JSON error responses via the exception handlers registered in
`app.core.middleware`.
"""
from __future__ import annotations


class AppError(Exception):
    """Base class for all application-level errors."""

    status_code: int = 400
    error_code: str = "APP_ERROR"

    def __init__(self, message: str | None = None):
        self.message = message or self.__class__.__doc__ or "Application error"
        super().__init__(self.message)


class NotFoundError(AppError):
    status_code = 404
    error_code = "NOT_FOUND"


class BookNotFound(NotFoundError):
    error_code = "BOOK_NOT_FOUND"


class BookCopyNotFound(NotFoundError):
    error_code = "BOOK_COPY_NOT_FOUND"


class UserNotFound(NotFoundError):
    error_code = "USER_NOT_FOUND"


class LoanNotFound(NotFoundError):
    error_code = "LOAN_NOT_FOUND"


class ReservationNotFound(NotFoundError):
    error_code = "RESERVATION_NOT_FOUND"


class ValidationError(AppError):
    status_code = 422
    error_code = "VALIDATION_ERROR"


class DuplicateISBN(AppError):
    status_code = 409
    error_code = "DUPLICATE_ISBN"


class DuplicateEmail(AppError):
    status_code = 409
    error_code = "DUPLICATE_EMAIL"


class BookUnavailable(AppError):
    status_code = 409
    error_code = "BOOK_UNAVAILABLE"


class AlreadyIssued(AppError):
    status_code = 409
    error_code = "ALREADY_ISSUED"


class AlreadyReturned(AppError):
    status_code = 409
    error_code = "ALREADY_RETURNED"


class RenewalNotAllowed(AppError):
    status_code = 409
    error_code = "RENEWAL_NOT_ALLOWED"


class Unauthorized(AppError):
    status_code = 401
    error_code = "UNAUTHORIZED"


class Forbidden(AppError):
    status_code = 403
    error_code = "FORBIDDEN"


class AccountDisabled(AppError):
    status_code = 403
    error_code = "ACCOUNT_DISABLED"


class InvalidCredentials(Unauthorized):
    error_code = "INVALID_CREDENTIALS"


class InvalidToken(Unauthorized):
    error_code = "INVALID_TOKEN"
