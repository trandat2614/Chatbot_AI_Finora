"""Versioned product and Product Doctor endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from src.api.dependencies.context import require_auth_context
from src.api.dependencies.services import commerce_repository
from src.api.routes.common import meta
from src.repositories.commerce_repository import SQLAlchemyCommerceRepository
from src.schemas.api import (
    ProductAnalysisData,
    ProductAnalysisResponse,
    ProductListData,
    ProductListResponse,
    ProductRecord,
    ProductResponse,
)
from src.security.audit import audit_event
from src.security.auth import AuthContext
from src.services.product_doctor_service import ProductDoctorService

router = APIRouter(prefix="/api/v1/products", tags=["v1-products"])


@router.get("", response_model=ProductListResponse)
def list_products(
    request: Request,
    context: AuthContext = Depends(require_auth_context),
    repository: SQLAlchemyCommerceRepository = Depends(commerce_repository),
) -> ProductListResponse:
    products = repository.list_products(context.tenant_id, context.shop_id)
    return ProductListResponse(
        data=ProductListData(
            status="OK" if products else "INSUFFICIENT_DATA",
            products=[ProductRecord(**item) for item in products],
        ),
        meta=meta(request),
    )


@router.get("/{sku}", response_model=ProductResponse)
def get_product(
    sku: str,
    request: Request,
    context: AuthContext = Depends(require_auth_context),
    repository: SQLAlchemyCommerceRepository = Depends(commerce_repository),
) -> ProductResponse:
    product = repository.get_product(context.tenant_id, context.shop_id, sku)
    if product is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "PRODUCT_NOT_FOUND", "message": "Không tìm thấy SKU."},
        )
    return ProductResponse(data=ProductRecord(**product), meta=meta(request))


@router.get("/{sku}/analysis", response_model=ProductAnalysisResponse)
def analyze_product(
    sku: str,
    request: Request,
    context: AuthContext = Depends(require_auth_context),
    repository: SQLAlchemyCommerceRepository = Depends(commerce_repository),
) -> ProductAnalysisResponse:
    result = ProductDoctorService().analyze(
        repository.load_orders(context.tenant_id, context.shop_id), sku
    )
    audit_event("product_analysis", context, resource="analytics", details={"status": result["status"]})
    return ProductAnalysisResponse(data=ProductAnalysisData(**result), meta=meta(request))
