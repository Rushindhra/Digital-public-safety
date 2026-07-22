"""
Pydantic request/response schemas for authentication.
"""
import uuid
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.enums import UserRole


class UserRegister(BaseModel):
    full_name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    phone_number: Optional[str] = Field(default=None, max_length=20)
    password: str = Field(min_length=8, max_length=128)
    role: UserRole = UserRole.CITIZEN
    badge_number: Optional[str] = None
    district: Optional[str] = None
    preferred_language: str = "en"

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain at least one letter")
        return v

    @field_validator("role")
    @classmethod
    def restrict_self_registration(cls, v: UserRole) -> UserRole:
        if v in (UserRole.OFFICER, UserRole.ADMIN, UserRole.ANALYST):
            raise ValueError(
                "This role cannot self-register. Contact a platform administrator."
            )
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: uuid.UUID
    full_name: str
    email: EmailStr
    role: UserRole
    district: Optional[str] = None
    preferred_language: str
    is_verified: bool

    model_config = {"from_attributes": True}
