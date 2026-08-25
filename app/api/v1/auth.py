from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponseData,
    RefreshRequest,
    RegisterRequest,
    TokenPair,
    UserOut,
)
from app.schemas.common import ApiResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=ApiResponse[UserOut], status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    user = service.register(payload.name, payload.email, payload.password, payload.role)
    db.commit()
    return ApiResponse(data=UserOut.model_validate(user), message="Account created successfully")


@router.post("/login", response_model=ApiResponse[LoginResponseData])
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    user = service.authenticate(payload.email, payload.password)
    tokens = service.issue_tokens(user)
    db.commit()
    return ApiResponse(
        data=LoginResponseData(user=UserOut.model_validate(user), tokens=TokenPair(**tokens)),
        message="Login successful",
    )


@router.post("/refresh", response_model=ApiResponse[TokenPair])
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    tokens = service.refresh(payload.refresh_token)
    db.commit()
    return ApiResponse(data=TokenPair(**tokens), message="Token refreshed")


@router.post("/logout", response_model=ApiResponse[None])
def logout(user: User = Depends(get_current_user)):
    # Stateless JWTs: the client discards its tokens. A production system
    # would additionally track a revocation/blocklist (e.g. in Redis) keyed
    # by the token's `jti` claim; documented as a roadmap item in docs/security.md.
    return ApiResponse(data=None, message="Logged out")


@router.get("/me", response_model=ApiResponse[UserOut])
def me(user: User = Depends(get_current_user)):
    return ApiResponse(data=UserOut.model_validate(user), message="")
