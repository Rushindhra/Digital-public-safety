"""
User document model for MongoDB via Beanie ODM.
"""
import uuid
from datetime import datetime
from typing import Optional

from beanie import Document
from pydantic import EmailStr, Field
from pymongo import IndexModel

from app.models.enums import UserRole


class User(Document):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    full_name: str
    email: EmailStr
    phone_number: Optional[str] = None
    hashed_password: str
    role: UserRole = UserRole.CITIZEN
    badge_number: Optional[str] = None
    district: Optional[str] = None
    preferred_language: str = "en"
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"
        indexes = [
            IndexModel([("email", 1)], unique=True),
            IndexModel([("phone_number", 1)], unique=True, sparse=True),
        ]

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role})>"
