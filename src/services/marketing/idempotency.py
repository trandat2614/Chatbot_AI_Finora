"""Database uniqueness arbitrates duplicate requests across API workers."""
import hashlib
import json
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError

from config.settings import settings
from src.db.models import MarketingIdempotency


class IdempotencyStore:
    def __init__(self, database):
        self.database = database

    def claim(self, context, endpoint, key, body):
        scope = [context.auth_method, settings.WEB_TOKEN_ISSUER, context.user_id,
                 context.tenant_id, context.shop_id, endpoint, key]
        scope_key = hashlib.sha256(json.dumps(scope).encode()).hexdigest()
        payload_hash = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
        now = datetime.now(timezone.utc)
        operation_id = str(uuid.uuid4())
        try:
            with self.database.session() as session:
                # Indexed TTL cleanup also removes expired private response text.
                session.execute(delete(MarketingIdempotency).where(MarketingIdempotency.expires_at <= now))
                session.add(MarketingIdempotency(scope_key=scope_key, payload_hash=payload_hash,
                    operation_id=operation_id,
                    expires_at=now + timedelta(seconds=max(settings.MARKETING_IDEMPOTENCY_TTL_SECONDS,
                                                         int(settings.MARKETING_TIMEOUT_SECONDS) + 60))))
                session.flush()
            return scope_key, operation_id, None, None
        except IntegrityError:
            with self.database.session() as session:
                record = session.get(MarketingIdempotency, scope_key)
                if record is None:
                    raise HTTPException(409, detail={"code": "IDEMPOTENCY_RETRY", "message": "Thử lại cùng key."})
                if record.payload_hash != payload_hash:
                    raise HTTPException(409, detail={"code": "IDEMPOTENCY_CONFLICT", "message": "Cùng key nhưng payload khác."})
                if record.response is None:
                    raise HTTPException(409, detail={"code": "IDEMPOTENCY_IN_PROGRESS", "message": "Request đang xử lý hoặc cần đối soát sau gián đoạn."}, headers={"Retry-After": "2"})
                return scope_key, record.operation_id, record.response, record.http_status

    def complete(self, scope_key, operation_id, response, http_status):
        with self.database.session() as session:
            record = session.get(MarketingIdempotency, scope_key)
            if record is None or record.operation_id != operation_id:
                raise RuntimeError("Idempotency ownership lost.")
            record.response = response
            record.http_status = http_status
