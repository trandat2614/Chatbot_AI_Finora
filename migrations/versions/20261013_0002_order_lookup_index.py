"""Add the tenant-scoped exact order lookup index.

Revision ID: 20261013_0002
Revises: 20260930_0001
"""
from __future__ import annotations

from alembic import op
from sqlalchemy import inspect

revision = "20261013_0002"
down_revision = "20260930_0001"
branch_labels = None
depends_on = None

INDEX_NAME = "ix_order_owner_external"


def upgrade() -> None:
    # The initial migration creates current metadata dynamically, so a fresh
    # database may already contain this index by the time this revision runs.
    existing = {item["name"] for item in inspect(op.get_bind()).get_indexes("orders")}
    if INDEX_NAME not in existing:
        op.create_index(
            INDEX_NAME,
            "orders",
            ["tenant_id", "shop_id", "external_order_id"],
            unique=False,
        )


def downgrade() -> None:
    existing = {item["name"] for item in inspect(op.get_bind()).get_indexes("orders")}
    if INDEX_NAME in existing:
        op.drop_index(INDEX_NAME, table_name="orders")
