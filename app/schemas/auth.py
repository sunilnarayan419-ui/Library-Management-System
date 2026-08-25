from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole, UserStatus


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: UserRole = UserRole.MEMBER


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: UserRole
    status: UserStatus

    model_config = {"from_attributes": True}


class LoginResponseData(BaseModel):
    user: UserOut
    tokens: TokenPair
