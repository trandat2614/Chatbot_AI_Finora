"""Persistence, caching, deduplication and orchestration for insights."""
from __future__ import annotations

import hashlib
import json
import threading
import uuid
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict
from sqlalchemy import delete, select

from services.insights.data_provider import InsightDataProvider
from services.insights.generator import GeneratedInsight, InsightGenerator, InsightLLM
from services.insights.metrics import InsightMetrics, PeriodName, PeriodRange, collect_metrics
from services.insights.rules import evaluate_rules
from src.db.models import AIInsight
from src.db.session import Database

InsightStatus = Literal["new", "read", "dismissed"]


class StoredInsight(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: str
    type: str
    severity: Literal["info", "warning", "critical", "positive"]
    title: str
    summary: str
    recommendation: str
    evidence: dict
    created_at: datetime


def _stored(row: AIInsight) -> StoredInsight:
    created_at = row.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    return StoredInsight(
        id=row.id,
        type=row.type,
        severity=row.severity,  # type: ignore[arg-type]
        title=row.title,
        summary=row.summary,
        recommendation=row.recommendation,
        evidence=row.evidence,
        created_at=created_at,
    )


def metrics_hash(metrics: InsightMetrics) -> str:
    payload = json.dumps(
        metrics.model_dump(mode="json"),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class InsightRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def list(
        self,
        tenant_id: str,
        shop_id: str,
        *,
        limit: int,
        status: InsightStatus | None,
    ) -> list[StoredInsight]:
        with self.database.session() as session:
            statement = (
                select(AIInsight)
                .where(AIInsight.tenant_id == tenant_id, AIInsight.shop_id == shop_id)
                .order_by(AIInsight.created_at.desc(), AIInsight.id.desc())
                .limit(limit)
            )
            if status is not None:
                statement = statement.where(AIInsight.status == status)
            return [_stored(row) for row in session.scalars(statement).all()]

    def cached(
        self,
        tenant_id: str,
        shop_id: str,
        period: PeriodRange,
        data_hash: str,
    ) -> list[StoredInsight]:
        with self.database.session() as session:
            rows = session.scalars(
                select(AIInsight)
                .where(
                    AIInsight.tenant_id == tenant_id,
                    AIInsight.shop_id == shop_id,
                    AIInsight.period_start == period.start,
                    AIInsight.period_end == period.end,
                    AIInsight.data_hash == data_hash,
                )
                .order_by(AIInsight.created_at.desc(), AIInsight.id.desc())
            ).all()
            return [_stored(row) for row in rows]

    def upsert_period(
        self,
        tenant_id: str,
        shop_id: str,
        period: PeriodRange,
        data_hash: str,
        insights: list[GeneratedInsight],
    ) -> list[StoredInsight]:
        now = datetime.now(timezone.utc)
        active_types = {item.type for item in insights}
        with self.database.session() as session:
            stale = delete(AIInsight).where(
                AIInsight.tenant_id == tenant_id,
                AIInsight.shop_id == shop_id,
                AIInsight.period_start == period.start,
                AIInsight.period_end == period.end,
            )
            if active_types:
                stale = stale.where(AIInsight.type.not_in(active_types))
            session.execute(stale)
            rows: list[AIInsight] = []
            for item in insights:
                row = session.scalar(
                    select(AIInsight).where(
                        AIInsight.tenant_id == tenant_id,
                        AIInsight.shop_id == shop_id,
                        AIInsight.type == item.type,
                        AIInsight.period_start == period.start,
                        AIInsight.period_end == period.end,
                    )
                )
                if row is None:
                    row = AIInsight(
                        id=str(uuid.uuid4()),
                        tenant_id=tenant_id,
                        shop_id=shop_id,
                        type=item.type,
                        period_start=period.start,
                        period_end=period.end,
                    )
                    session.add(row)
                row.severity = item.severity
                row.title = item.title
                row.summary = item.summary
                row.recommendation = item.recommendation
                row.evidence = item.evidence
                row.status = "new"
                row.created_at = now
                row.data_hash = data_hash
                rows.append(row)
            session.flush()
            return [_stored(row) for row in rows]

    def update_status(
        self,
        tenant_id: str,
        shop_id: str,
        insight_id: str,
        status: InsightStatus,
    ) -> StoredInsight | None:
        with self.database.session() as session:
            row = session.scalar(
                select(AIInsight).where(
                    AIInsight.tenant_id == tenant_id,
                    AIInsight.shop_id == shop_id,
                    AIInsight.id == insight_id,
                )
            )
            if row is None:
                return None
            row.status = status
            session.flush()
            return _stored(row)


_locks_guard = threading.Lock()
_tenant_locks: dict[tuple[str, str], threading.Lock] = {}


def _scope_lock(tenant_id: str, shop_id: str) -> threading.Lock:
    with _locks_guard:
        return _tenant_locks.setdefault((tenant_id, shop_id), threading.Lock())


class InsightService:
    def __init__(
        self,
        database: Database,
        provider: InsightDataProvider,
        llm_client: InsightLLM | None,
    ) -> None:
        self.repository = InsightRepository(database)
        self.provider = provider
        self.generator = InsightGenerator(llm_client)

    def generate(
        self,
        tenant_id: str,
        shop_id: str,
        period_name: PeriodName = "30d",
        *,
        force: bool = False,
    ) -> tuple[list[StoredInsight], str | None]:
        with _scope_lock(tenant_id, shop_id):
            period = PeriodRange.ending_on(period_name)
            metrics = collect_metrics(tenant_id, period, self.provider)
            digest = metrics_hash(metrics)
            if metrics.current.orders == 0:
                self.repository.upsert_period(tenant_id, shop_id, period, digest, [])
                return [], "not_enough_data"
            if not force:
                cached = self.repository.cached(tenant_id, shop_id, period, digest)
                if cached:
                    return cached, None
            candidates = evaluate_rules(metrics)
            priority = {"critical": 0, "warning": 1, "positive": 2, "info": 3}
            candidates.sort(key=lambda item: priority[item.severity])
            generated = self.generator.generate(candidates[:5])
            stored = self.repository.upsert_period(
                tenant_id, shop_id, period, digest, generated
            )
            empty_reason = "not_enough_data" if not stored else None
            return stored, empty_reason
