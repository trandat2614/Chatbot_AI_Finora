"""Versioned private knowledge upload endpoint."""
from __future__ import annotations

import hashlib
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile

from config.settings import settings
from rag.document_loader import SUPPORTED_EXTENSIONS, load_all_documents
from rag.text_splitter import split_documents
from rag.vector_store import create_vector_store
from src.api.dependencies.context import require_auth_context, require_write_role
from src.api.routes.common import meta, tenant_rag_store
from src.schemas.api import (
    KnowledgeUploadData,
    KnowledgeUploadResponse,
)
from src.security.audit import audit_event
from src.security.auth import AuthContext
from src.security.uploads import UnsafeUploadError, validate_upload

router = APIRouter(prefix="/api/v1/knowledge", tags=["v1-knowledge"])


@router.post("/upload", response_model=KnowledgeUploadResponse)
async def upload_knowledge(
    request: Request,
    file: UploadFile = File(...),
    context: AuthContext = Depends(require_auth_context),
) -> KnowledgeUploadResponse:
    require_write_role(context)
    contents = await file.read(settings.MAX_UPLOAD_BYTES + 1)
    await file.close()
    try:
        filename = validate_upload(
            file.filename or "", file.content_type, contents, settings.MAX_UPLOAD_BYTES
        )
    except UnsafeUploadError as exc:
        status_code = 413 if len(contents) > settings.MAX_UPLOAD_BYTES else 415
        raise HTTPException(
            status_code=status_code,
            detail={"code": "UNSAFE_UPLOAD", "message": str(exc)},
        ) from exc
    if Path(filename).suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail={"code": "UNSUPPORTED_KNOWLEDGE", "message": "Định dạng không được hỗ trợ."},
        )

    scope = tenant_rag_store.scope_token(context.tenant_id, context.shop_id)
    knowledge_dir = tenant_rag_store.tenant_knowledge_dir(
        context.tenant_id, context.shop_id
    )
    knowledge_dir.mkdir(parents=True, exist_ok=True)
    destination = (knowledge_dir / filename).resolve()
    if destination.parent != knowledge_dir.resolve():
        raise HTTPException(
            status_code=415,
            detail={"code": "UNSAFE_UPLOAD", "message": "Tên file không an toàn."},
        )
    destination.write_bytes(contents)
    try:
        documents = load_all_documents(
            knowledge_dir,
            tenant_scope=scope,
            tenant_id=context.tenant_id,
            shop_id=context.shop_id,
            visibility="private",
        )
        chunks = split_documents(documents)
        if not chunks:
            raise HTTPException(
                status_code=422,
                detail={"code": "EMPTY_DOCUMENT", "message": "Không đọc được nội dung tài liệu."},
            )
        create_vector_store(
            chunks,
            tenant_rag_store.tenant_vector_dir(context.tenant_id, context.shop_id),
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail={"code": "EMBEDDING_FAILED", "message": "Không thể tạo embeddings."},
        ) from exc

    audit_event(
        "knowledge_upload",
        context,
        resource="rag_document",
        details={
            "filename_hash": hashlib.sha256(filename.encode()).hexdigest()[:16],
            "size": len(contents),
            "record_count": len(chunks),
        },
    )
    return KnowledgeUploadResponse(
        data=KnowledgeUploadData(
            filename=filename,
            documents=len(documents),
            chunks=len(chunks),
            message="Đã upload và lập chỉ mục private knowledge.",
        ),
        meta=meta(request),
    )
