"""platform domain tables

Revision ID: 20260704_0002
Revises: 20260704_0001
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260704_0002"
down_revision: Union[str, None] = "20260704_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    status = postgresql.ENUM("SUBMITTED", "TRIAGED", "INVESTIGATING", "RESOLVED", name="reportstatus")
    status.create(op.get_bind(), checkfirst=True)
    op.create_table("fraud_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("reporter_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("category", sa.String(50), nullable=False), sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False), sa.Column("channel", sa.String(30), nullable=False),
        sa.Column("risk_score", sa.Float(), nullable=False), sa.Column("status", status, nullable=False),
        sa.Column("latitude", sa.Float()), sa.Column("longitude", sa.Float()), sa.Column("district", sa.String(100)),
        sa.Column("metadata_json", sa.JSON(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False))
    for col in ("reporter_id", "category", "status", "district", "created_at"):
        op.create_index(f"ix_fraud_reports_{col}", "fraud_reports", [col])
    op.create_table("evidence",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("report_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fraud_reports.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", sa.String(30), nullable=False), sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("storage_path", sa.String(500), nullable=False), sa.Column("sha256", sa.String(64), nullable=False, unique=True),
        sa.Column("content_type", sa.String(100), nullable=False), sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(), nullable=False))
    op.create_index("ix_evidence_report_id", "evidence", ["report_id"])
    op.create_table("notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("channel", sa.String(20), nullable=False), sa.Column("title", sa.String(160), nullable=False),
        sa.Column("message", sa.Text(), nullable=False), sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("read_at", sa.DateTime()), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_index("ix_notifications_created_at", "notifications", ["created_at"])


def downgrade() -> None:
    op.drop_table("notifications"); op.drop_table("evidence"); op.drop_table("fraud_reports")
    postgresql.ENUM(name="reportstatus").drop(op.get_bind(), checkfirst=True)
