from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import require_permission
from app.database.session import get_db
from app.models.user import User, UserRole, UserStatus
from app.schemas.common import ApiResponse
from app.schemas.users import UserCreate, UserDetail, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=ApiResponse[list[UserDetail]])
def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    role: UserRole | None = Query(default=None),
    db: Session = Depends(get_db),
    _user: User = Depends(require_permission("users:create")),
):
    service = UserService(db)
    offset = (page - 1) * page_size
    users = service.list_users(offset=offset, limit=page_size, role=role)
    return ApiResponse(data=[UserDetail.model_validate(u) for u in users])


@router.get("/{user_id}", response_model=ApiResponse[UserDetail])
def get_user(user_id: str, db: Session = Depends(get_db), _user: User = Depends(require_permission("users:create"))):
    service = UserService(db)
    return ApiResponse(data=UserDetail.model_validate(service.get_user(user_id)))


@router.post("", response_model=ApiResponse[UserDetail], status_code=201)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("users:create")),
):
    service = UserService(db)
    created = service.create_user(payload.name, payload.email, payload.password, payload.role, actor=user)
    db.commit()
    return ApiResponse(data=UserDetail.model_validate(created), message="User created")


@router.patch("/{user_id}", response_model=ApiResponse[UserDetail])
def update_user(
    user_id: str,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("users:update")),
):
    service = UserService(db)
    if payload.role is not None:
        service.update_role(user_id, payload.role, actor=user)
    if payload.status is not None:
        service.set_status(user_id, payload.status, actor=user)
    db.commit()
    return ApiResponse(data=UserDetail.model_validate(service.get_user(user_id)), message="User updated")


@router.post("/{user_id}/disable", response_model=ApiResponse[UserDetail])
def disable_user(
    user_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("users:disable")),
):
    service = UserService(db)
    updated = service.set_status(user_id, UserStatus.DISABLED, actor=user)
    db.commit()
    return ApiResponse(data=UserDetail.model_validate(updated), message="User disabled")
