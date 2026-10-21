"""Stateless insights from the JSON returned by the web backend."""
from fastapi import APIRouter, Depends, Request

from src.api.dependencies.context import require_auth_context
from src.api.routes.common import meta
from src.schemas.product_trends import ProductTrendResponse, TrendExport
from src.security.audit import audit_event
from src.security.auth import AuthContext
from src.services.product_trend_service import ProductTrendService

router = APIRouter(prefix="/api/v1/market/product-trends", tags=["v1-product-trends"])


@router.post("/insights", response_model=ProductTrendResponse)
def insights(payload: TrendExport, request: Request, context: AuthContext = Depends(require_auth_context)):
    service = ProductTrendService(llm_client=request.app.state.llm_client)
    evidence = service.evidence(snapshot=payload.data)
    result = service.summarize(evidence)
    audit_event("product_trend_insight", context, resource="backend_json", details={"status": result["status"]})
    return ProductTrendResponse(data=result, meta=meta(request))
