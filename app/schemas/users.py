from __future__ import annotations

from pydantic import BaseModel, EmailStr

from app.models.user import UserRole, UserStatus


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.MEMBER


class UserUpdate(BaseModel):
    name: str | None = None
    role: UserRole | None = None
    status: UserStatus | None = None


class UserDetail(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: UserRole
    status: UserStatus

    model_config = {"from_attributes": True}
