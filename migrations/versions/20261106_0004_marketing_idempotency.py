"""Durable, multi-worker marketing idempotency (no BE business schema changes)."""
import sqlalchemy as sa
from alembic import op

revision = "20261106_0004"
down_revision = "20261015_0003"
branch_labels = None
depends_on = None


def upgrade():
    if "marketing_idempotency" in sa.inspect(op.get_bind()).get_table_names():
        return
    op.create_table("marketing_idempotency",
        sa.Column("scope_key", sa.String(64), primary_key=True),
        sa.Column("payload_hash", sa.String(64), nullable=False),
        sa.Column("operation_id", sa.String(36), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("response", sa.JSON(), nullable=True),
        sa.Column("http_status", sa.Integer(), nullable=True))
    op.create_index("ix_marketing_idempotency_expires_at", "marketing_idempotency", ["expires_at"])


def downgrade():
    op.drop_table("marketing_idempotency")
