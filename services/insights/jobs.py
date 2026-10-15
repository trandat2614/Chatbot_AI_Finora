"""Callable refresh hooks for imports, order events and external schedulers."""
from __future__ import annotations

import logging

from sqlalchemy import select

from core.llm_client import LLMClient
from services.insights.data_provider import DefaultDataProvider
from services.insights.service import InsightService, StoredInsight
from src.db.models import Order
from src.db.session import Database, get_database
from src.repositories.commerce_repository import SQLAlchemyCommerceRepository

logger = logging.getLogger(__name__)


def refresh_insights_for_tenant(
    tenant_id: str,
    *,
    shop_id: str | None = None,
    database: Database | None = None,
    repository: SQLAlchemyCommerceRepository | None = None,
    llm_client: LLMClient | None = None,
) -> list[StoredInsight]:
    """Refresh one tenant sequentially, optionally limited to one shop."""
    active_database = database or get_database()
    commerce = repository or SQLAlchemyCommerceRepository(active_database)
    shop_ids = [shop_id] if shop_id else _tenant_shop_ids(active_database, tenant_id)
    refreshed: list[StoredInsight] = []
    for current_shop_id in shop_ids:
        provider = DefaultDataProvider(commerce, current_shop_id)
        service = InsightService(active_database, provider, llm_client)
        items, _ = service.generate(tenant_id, current_shop_id)
        refreshed.extend(items)
    logger.info(
        "insight_refresh_completed shops=%s insights=%s",
        len(shop_ids),
        len(refreshed),
    )
    return refreshed


def refresh_insights_for_tenants(
    tenant_ids: list[str],
    *,
    database: Database | None = None,
    llm_client: LLMClient | None = None,
) -> dict[str, int]:
    """Refresh a batch sequentially to keep provider/LLM load bounded."""
    return {
        tenant_id: len(
            refresh_insights_for_tenant(
                tenant_id, database=database, llm_client=llm_client
            )
        )
        for tenant_id in tenant_ids
    }


def _tenant_shop_ids(database: Database, tenant_id: str) -> list[str]:
    with database.session() as session:
        return list(
            session.scalars(
                select(Order.shop_id)
                .where(Order.tenant_id == tenant_id)
                .distinct()
                .order_by(Order.shop_id)
            ).all()
        )
