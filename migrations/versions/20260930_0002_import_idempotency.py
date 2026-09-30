"""Add import fingerprint idempotency and persisted write counts.

Revision ID: 20260930_0002
Revises: 20260930_0001
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260930_0002"
down_revision = "20260930_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {item["name"] for item in inspector.get_columns("data_imports")}
    constraints = {
        item.get("name")
        for item in inspector.get_unique_constraints("data_imports")
    }
    with op.batch_alter_table("data_imports") as batch:
        if "fingerprint" not in columns:
            batch.add_column(sa.Column("fingerprint", sa.String(length=64), nullable=True))
        if "orders_created" not in columns:
            batch.add_column(
                sa.Column("orders_created", sa.Integer(), nullable=False, server_default="0")
            )
        if "order_items_created" not in columns:
            batch.add_column(
                sa.Column(
                    "order_items_created", sa.Integer(), nullable=False, server_default="0"
                )
            )
        if "uq_import_owner_fingerprint" not in constraints:
            batch.create_unique_constraint(
                "uq_import_owner_fingerprint",
                ["tenant_id", "shop_id", "fingerprint"],
            )


def downgrade() -> None:
    with op.batch_alter_table("data_imports") as batch:
        batch.drop_constraint("uq_import_owner_fingerprint", type_="unique")
        batch.drop_column("order_items_created")
        batch.drop_column("orders_created")
        batch.drop_column("fingerprint")
