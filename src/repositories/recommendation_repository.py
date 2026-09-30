"""Tenant-scoped persistence for generated recommendations."""
from __future__ import annotations

import uuid

from src.db.models import Recommendation, RecommendationResult
from src.db.session import Database, get_database
from src.security.auth import AuthContext
from src.security.privacy import sanitize_for_ai


class SQLAlchemyRecommendationRepository:
    def __init__(self, database: Database | None = None) -> None:
        self.database = database or get_database()

    def save(
        self, context: AuthContext, kind: str, request_data: dict, result_data: dict
    ) -> str:
        recommendation_id = str(uuid.uuid4())
        with self.database.session() as session:
            recommendation = Recommendation(
                id=recommendation_id,
                tenant_id=context.tenant_id,
                shop_id=context.shop_id,
                user_id=context.user_id,
                kind=kind,
                status=str(result_data.get("status", "OK")),
                request_data=sanitize_for_ai(request_data),
            )
            recommendation.results.append(
                RecommendationResult(
                    id=str(uuid.uuid4()),
                    tenant_id=context.tenant_id,
                    shop_id=context.shop_id,
                    result_data=sanitize_for_ai(result_data),
                )
            )
            session.add(recommendation)
        return recommendation_id
