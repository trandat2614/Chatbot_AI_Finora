"""Shared route helpers."""
from __future__ import annotations

from fastapi import Request

from rag.vector_store import load_vector_store, vector_store_exists
from src.schemas.api import ResponseMeta
from src.security.auth import AuthContext
from src.services.tenant_store import TenantDataStore

tenant_rag_store = TenantDataStore()


def meta(request: Request) -> ResponseMeta:
    return ResponseMeta(request_id=request.state.request_id)


def tenant_vector_store(context: AuthContext):
    path = tenant_rag_store.tenant_vector_dir(context.tenant_id, context.shop_id)
    if not vector_store_exists(path):
        return None
    return load_vector_store(path)
