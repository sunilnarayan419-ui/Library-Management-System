from __future__ import annotations

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_books: int
    total_copies: int
    available_copies: int
    issued_copies: int
    overdue_loans: int
    active_members: int
    pending_reservations: int
    outstanding_fines_amount: float


class TopBook(BaseModel):
    book_id: str
    title: str
    borrow_count: int


class CategoryShare(BaseModel):
    category: str
    count: int


class MonthlyCirculation(BaseModel):
    month: str
    issued: int
    returned: int
