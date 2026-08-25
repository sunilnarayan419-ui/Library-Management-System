from __future__ import annotations

import datetime as dt

from pydantic import BaseModel

from app.models.fine import FineStatus
from app.models.loan import LoanStatus
from app.models.reservation import ReservationStatus


class IssueRequest(BaseModel):
    book_id: str
    member_id: str
    days: int | None = None


class ReturnRequest(BaseModel):
    loan_id: str


class RenewRequest(BaseModel):
    loan_id: str


class ReserveRequest(BaseModel):
    book_id: str
    member_id: str


class LoanOut(BaseModel):
    id: str
    book_id: str
    copy_id: str
    member_id: str
    issued_at: dt.datetime
    due_at: dt.datetime
    returned_at: dt.datetime | None
    renewal_count: int
    status: LoanStatus

    model_config = {"from_attributes": True}


class ReservationOut(BaseModel):
    id: str
    book_id: str
    member_id: str
    status: ReservationStatus
    reserved_at: dt.datetime
    expires_at: dt.datetime | None

    model_config = {"from_attributes": True}


class FineOut(BaseModel):
    id: str
    loan_id: str
    member_id: str
    amount: float
    reason: str
    status: FineStatus

    model_config = {"from_attributes": True}
