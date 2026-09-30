"""Repository and business-service dependencies."""
from __future__ import annotations

from fastapi import Request

from src.repositories.commerce_repository import SQLAlchemyCommerceRepository
from src.security.auth import AuthContext
from src.services.decision_intelligence_service import DecisionIntelligenceService


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
