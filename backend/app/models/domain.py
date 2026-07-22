"""Core public-safety domain documents stored in MongoDB."""
import uuid
from datetime import datetime
from typing import Any, Optional

from beanie import Document
from pydantic import Field
from pymongo import IndexModel

from app.models.enums import ReportStatus


class FraudReport(Document):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    reporter_id: Optional[uuid.UUID] = None
    category: str
    title: str
    description: str
    channel: str = "web"
    risk_score: float = 0.0
    status: ReportStatus = ReportStatus.SUBMITTED
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    district: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "fraud_reports"
        indexes = [
            IndexModel([("reporter_id", 1)]),
            IndexModel([("category", 1)]),
            IndexModel([("status", 1)]),
            IndexModel([("district", 1)]),
            IndexModel([("created_at", -1)]),
        ]


class Evidence(Document):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    report_id: uuid.UUID
    kind: str
    filename: str
    storage_path: str
    sha256: str
    content_type: str
    size_bytes: int
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "evidence"
        indexes = [
            IndexModel([("report_id", 1)]),
            IndexModel([("sha256", 1)], unique=True),
        ]


class Notification(Document):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    user_id: uuid.UUID
    channel: str
    title: str
    message: str
    severity: str = "info"
    read_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "notifications"
        indexes = [
            IndexModel([("user_id", 1)]),
            IndexModel([("created_at", -1)]),
        ]
