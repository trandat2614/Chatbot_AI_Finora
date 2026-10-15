"""Repository and business-service dependencies."""
from __future__ import annotations

from fastapi import Request

from src.repositories.commerce_repository import SQLAlchemyCommerceRepository
from src.security.auth import AuthContext
from src.services.decision_intelligence_service import DecisionIntelligenceService
from services.insights.data_provider import DefaultDataProvider
from services.insights.service import InsightService
from fastapi import Depends
from src.api.dependencies.context import require_auth_context


def commerce_repository(request: Request) -> SQLAlchemyCommerceRepository:
    return request.app.state.commerce_repository


def decision_service(
    request: Request, context: AuthContext
) -> DecisionIntelligenceService:
    return DecisionIntelligenceService(
        context.tenant_id,
        context.shop_id,
        request.app.state.commerce_repository,
    )


def insight_data_provider(
    context: AuthContext = Depends(require_auth_context),
    repository: SQLAlchemyCommerceRepository = Depends(commerce_repository),
) -> DefaultDataProvider:
    return DefaultDataProvider(repository, context.shop_id)


def insights_service(
    request: Request,
    provider: DefaultDataProvider = Depends(insight_data_provider),
) -> InsightService:
    return InsightService(
        request.app.state.database,
        provider,
        request.app.state.llm_client,
    )
