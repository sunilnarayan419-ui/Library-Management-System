from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import require_permission
from app.database.session import get_db
from app.models.user import User
from app.schemas.circulation import (
    FineOut,
    IssueRequest,
    LoanOut,
    RenewRequest,
    ReservationOut,
    ReserveRequest,
    ReturnRequest,
)
from app.schemas.common import ApiResponse
from app.services.circulation_service import CirculationService

router = APIRouter(tags=["circulation"])


@router.post("/circulation/issue", response_model=ApiResponse[LoanOut])
def issue(payload: IssueRequest, db: Session = Depends(get_db), user: User = Depends(require_permission("circulation:issue"))):
    service = CirculationService(db)
    loan = service.issue_book(payload.book_id, payload.member_id, payload.days, actor=user)
    db.commit()
    return ApiResponse(data=LoanOut.model_validate(loan), message="Book issued successfully")


@router.post("/circulation/return", response_model=ApiResponse[LoanOut])
def return_loan(payload: ReturnRequest, db: Session = Depends(get_db), user: User = Depends(require_permission("circulation:return"))):
    service = CirculationService(db)
    loan, fine = service.return_book(payload.loan_id, actor=user)
    db.commit()
    message = "Book returned successfully"
    if fine:
        message += f" (fine of {fine.amount:.2f} applied for late return)"
    return ApiResponse(data=LoanOut.model_validate(loan), message=message)


@router.post("/circulation/renew", response_model=ApiResponse[LoanOut])
def renew(payload: RenewRequest, db: Session = Depends(get_db), user: User = Depends(require_permission("circulation:renew"))):
    service = CirculationService(db)
    loan = service.renew_loan(payload.loan_id, actor=user)
    db.commit()
    return ApiResponse(data=LoanOut.model_validate(loan), message="Loan renewed")


@router.post("/reservations", response_model=ApiResponse[ReservationOut], status_code=201)
def reserve(payload: ReserveRequest, db: Session = Depends(get_db), user: User = Depends(require_permission("circulation:issue"))):
    service = CirculationService(db)
    reservation = service.reserve_book(payload.book_id, payload.member_id, actor=user)
    db.commit()
    return ApiResponse(data=ReservationOut.model_validate(reservation), message="Reservation created")


@router.delete("/reservations/{reservation_id}", response_model=ApiResponse[ReservationOut])
def cancel_reservation(reservation_id: str, db: Session = Depends(get_db), user: User = Depends(require_permission("circulation:issue"))):
    service = CirculationService(db)
    reservation = service.cancel_reservation(reservation_id, actor=user)
    db.commit()
    return ApiResponse(data=ReservationOut.model_validate(reservation), message="Reservation cancelled")


@router.post("/fines/{fine_id}/pay", response_model=ApiResponse[FineOut])
def pay_fine(fine_id: str, db: Session = Depends(get_db), user: User = Depends(require_permission("circulation:return"))):
    service = CirculationService(db)
    fine = service.pay_fine(fine_id, actor=user)
    db.commit()
    return ApiResponse(data=FineOut.model_validate(fine), message="Fine paid")
