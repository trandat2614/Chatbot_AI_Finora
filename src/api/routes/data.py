"""Versioned marketplace import endpoints."""
from __future__ import annotations

import hashlib
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile

from config.settings import settings
from src.api.dependencies.context import require_auth_context, require_write_role
from src.api.dependencies.services import commerce_repository
from src.api.routes.common import meta
from src.repositories.commerce_repository import SQLAlchemyCommerceRepository
from src.schemas.api import DataImportResponse, ErrorResponse, ImportData, ImportStatusResponse
from src.security.audit import audit_event
from src.security.auth import AuthContext
from src.security.privacy import sanitize_text
from src.security.uploads import (
    UnsafeUploadError,
    validate_csv_shape,
    validate_upload,
    validate_xlsx_shape,
)
from src.services.normalization.service import DataNormalizationService
from src.services.raw_upload_service import RawUploadService

router = APIRouter(prefix="/api/v1/data", tags=["v1-data"])


@router.post(
    "/import",
    response_model=DataImportResponse,
    responses={
        413: {"model": ErrorResponse},
        415: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
async def import_data(
    request: Request,
    file: UploadFile = File(...),
    context: AuthContext = Depends(require_auth_context),
    repository: SQLAlchemyCommerceRepository = Depends(commerce_repository),
) -> DataImportResponse:
    require_write_role(context)
    contents = await file.read(settings.MAX_UPLOAD_BYTES + 1)
    await file.close()
    import_id: str | None = None
    duplicate = False
    try:
        filename = validate_upload(
            file.filename or "", file.content_type, contents, settings.MAX_UPLOAD_BYTES
        )
        suffix = Path(filename).suffix.lower()
        if suffix not in {".csv", ".xlsx"}:
            raise UnsafeUploadError("Import đơn hàng chỉ hỗ trợ CSV/XLSX.")
        if suffix == ".csv":
            validate_csv_shape(contents)
        else:
            validate_xlsx_shape(contents)
        normalizer = DataNormalizationService()
        with RawUploadService().temporary_copy(suffix, contents):
            source = normalizer.read_upload(filename, contents)
            safe_filename = sanitize_text(filename)
            platform = normalizer.detect_platform(source)
            file_hash = hashlib.sha256(contents).hexdigest()
            fingerprint = hashlib.sha256(
                (
                    f"{context.tenant_id}\x00{context.shop_id}\x00"
                    f"{file_hash}\x00{platform}"
                ).encode("utf-8")
            ).hexdigest()
            import_id, created = repository.create_import(
                context,
                safe_filename,
                file_hash,
                fingerprint,
                len(source),
            )
            if not created:
                duplicate = True
                record = repository.get_import(context, import_id)
                assert record is not None
                audit_event(
                    "data_import",
                    context,
                    resource="orders",
                    details={
                        "filename_hash": file_hash[:16],
                        "record_count": record["accepted_rows"],
                        "status": record["status"],
                    },
                )
                return DataImportResponse(
                    data=ImportData(**record, duplicate=True),
                    meta=meta(request),
                )
            repository.mark_processing(context, import_id)
            result = normalizer.normalize(source, platform)
            written = repository.replace_orders(context, result.frame, import_id)
            repository.complete_import(
                context,
                import_id,
                platform=result.platform,
                accepted_rows=written.order_items_created,
                rejected_rows=result.rejected_rows,
                orders_created=written.orders_created,
                order_items_created=written.order_items_created,
                warnings=result.warnings,
            )
    except UnsafeUploadError as exc:
        audit_event("data_import", context, outcome="denied", resource="orders")
        status_code = 413 if len(contents) > settings.MAX_UPLOAD_BYTES else 415
        raise HTTPException(
            status_code=status_code,
            detail={"code": "UNSAFE_UPLOAD", "message": str(exc)},
        ) from exc
    except (ValueError, TypeError) as exc:
        if import_id:
            repository.fail_import(context, import_id, "INVALID_IMPORT_DATA")
        audit_event("data_import", context, outcome="invalid", resource="orders")
        raise HTTPException(
            status_code=422,
            detail={"code": "INVALID_IMPORT_DATA", "message": str(exc)},
        ) from exc

    record = repository.get_import(context, import_id)
    assert record is not None
    audit_event(
        "data_import",
        context,
        resource="orders",
        details={"record_count": record["accepted_rows"], "status": record["status"]},
    )
    return DataImportResponse(
        data=ImportData(**record, duplicate=duplicate),
        meta=meta(request),
    )


@router.get("/imports/{import_id}", response_model=ImportStatusResponse)
def import_status(
    import_id: str,
    request: Request,
    context: AuthContext = Depends(require_auth_context),
    repository: SQLAlchemyCommerceRepository = Depends(commerce_repository),
) -> ImportStatusResponse:
    record = repository.get_import(context, import_id)
    if record is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "IMPORT_NOT_FOUND", "message": "Không tìm thấy import job."},
        )
    return ImportStatusResponse(data=ImportData(**record), meta=meta(request))
