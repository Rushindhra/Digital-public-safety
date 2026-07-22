"""create users table

Revision ID: 20260704_0001
Revises:
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260704_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    role = postgresql.ENUM("CITIZEN", "OFFICER", "ANALYST", "ADMIN", name="userrole")
    role.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "users", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False), sa.Column("phone_number", sa.String(20)),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", role, nullable=False, server_default="CITIZEN"),
        sa.Column("badge_number", sa.String(50)), sa.Column("district", sa.String(100)),
        sa.Column("preferred_language", sa.String(10), server_default="en"),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true()),
        sa.Column("is_verified", sa.Boolean(), server_default=sa.false()),
        sa.Column("created_at", sa.DateTime()), sa.Column("updated_at", sa.DateTime()),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_phone_number", "users", ["phone_number"], unique=True)


def downgrade() -> None:
    op.drop_table("users")
    postgresql.ENUM(name="userrole").drop(op.get_bind(), checkfirst=True)
