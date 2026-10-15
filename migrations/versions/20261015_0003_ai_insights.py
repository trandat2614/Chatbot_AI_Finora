"""Add tenant-scoped AI business insights.

Revision ID: 20261015_0003
Revises: 20261013_0002
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20261015_0003"
down_revision = "20261013_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = inspect(op.get_bind())
    if "ai_insights" in inspector.get_table_names():
        return
    op.create_table(
        "ai_insights",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=200), nullable=False),
        sa.Column("shop_id", sa.String(length=200), nullable=False),
        sa.Column("type", sa.String(length=100), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("title", sa.String(length=60), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("recommendation", sa.Text(), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("data_hash", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id", "shop_id", "type", "period_start", "period_end",
            name="uq_ai_insight_period_type",
        ),
    )
    op.create_index(
        "ix_ai_insights_tenant_created",
        "ai_insights",
        ["tenant_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_ai_insights_scope_created",
        "ai_insights",
        ["tenant_id", "shop_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    if "ai_insights" in inspect(op.get_bind()).get_table_names():
        op.drop_table("ai_insights")
