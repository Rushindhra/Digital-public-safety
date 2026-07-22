"""Shared enumeration types for domain models."""
import enum


class UserRole(str, enum.Enum):
    CITIZEN = "citizen"
    OFFICER = "officer"
    ANALYST = "analyst"
    ADMIN = "admin"


class ReportStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    TRIAGED = "triaged"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
