"""Validated contracts shared by the platform modules."""
import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.models.enums import ReportStatus


class ScamRequest(BaseModel):
    content: str = Field(min_length=3, max_length=20000)
    channel: Literal["sms", "email", "chat", "call_transcript", "whatsapp"] = "chat"
    language: str = Field(default="en", min_length=2, max_length=10)


class Signal(BaseModel):
    name: str
    weight: float
    evidence: list[str]


class ScamResult(BaseModel):
    risk_score: float
    confidence: float
    risk_level: str
    scam_types: list[str]
    signals: list[Signal]
    explanation: str
    suggested_actions: list[str]


class ReportCreate(BaseModel):
    category: str = Field(min_length=2, max_length=50)
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=10, max_length=20000)
    channel: str = Field(default="web", max_length=30)
    risk_score: float = Field(default=0, ge=0, le=100)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    district: str | None = Field(default=None, max_length=100)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ReportUpdate(BaseModel):
    status: ReportStatus


class ReportOut(ReportCreate):
    id: uuid.UUID
    reporter_id: uuid.UUID | None
    status: ReportStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class GraphRequest(BaseModel):
    nodes: list[dict[str, Any]] = Field(min_length=1, max_length=2000)
    edges: list[dict[str, Any]] = Field(max_length=10000)


class AssistantRequest(BaseModel):
    message: str = Field(min_length=2, max_length=5000)
    language: str = Field(default="en", max_length=10)
