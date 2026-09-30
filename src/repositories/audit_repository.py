"""Database-backed structured audit repository."""
from __future__ import annotations

import uuid

from src.db.models import AuditEvent
from src.db.session import Database, get_database
from src.security.auth import AuthContext


class SQLAlchemyAuditRepository:
    def __init__(self, database: Database | None = None) -> None:
        self.database = database or get_database()

    def append(
        self,
        context: AuthContext | None,
        action: str,
        outcome: str,
        resource: str | None,
        details: dict,
    ) -> str:
        event_id = str(uuid.uuid4())
        with self.database.session() as session:
            session.add(
                AuditEvent(
                    id=event_id,
                    tenant_id=context.tenant_id if context else None,
                    shop_id=context.shop_id if context else None,
                    user_id=context.user_id if context else None,
                    action=action,
                    outcome=outcome,
                    resource=resource,
                    details=details,
                )
            )
        return event_id
