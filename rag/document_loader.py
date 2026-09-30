"""
Document loader for RAG pipeline.

Supports Markdown (.md), plain text (.txt), PDF (.pdf), and Excel exports.
Each document preserves metadata: source, filename, file_type.
"""
from __future__ import annotations

import logging
import hashlib
from pathlib import Path
from typing import Optional

from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_core.documents import Document

from utils.file_helpers import list_files
from src.security.privacy import sanitize_text
from src.security.uploads import neutralize_spreadsheet_formula

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = [".md", ".txt", ".pdf", ".xlsx", ".xls", ".csv"]

SENSITIVE_COLUMN_MARKERS = (
    "phone", "email", "address", "customername", "customer name", "buyer", "recipient",
    "người mua", "người nhận", "số điện thoại", "địa chỉ", "tên người",
)


def _marketplace_name(columns: list[str]) -> str | None:
    names = set(columns)
    if "Mã đơn hàng" in names:
        return "Shopee"
    if "orderNumber" in names:
        return "Lazada"
    if "Order ID" in names:
        return "TikTok Shop"
    return None


def _number(value: object) -> float:
    """Parse marketplace currency cells without treating blanks as zero text."""
    import re
    text = re.sub(r"[^0-9,.-]", "", str(value))
    if not text:
        return 0.0
    if text.count(",") == 1 and text.count(".") == 0:
        text = text.replace(",", ".")
    else:
        text = text.replace(",", "")
    try:
        return float(text)
    except ValueError:
        return 0.0


def _load_spreadsheet(file_path: Path) -> list[Document]:
    """Convert each Excel worksheet into one RAG document.

    The full tabular content is retained as CSV-style text so a question can
    retrieve individual orders, products, dates, and metrics. Empty rows and
    columns are ignored.
    """
    import pandas as pd

    sheets = pd.read_excel(file_path, sheet_name=None, dtype=str)
    documents: list[Document] = []
    for sheet_name, frame in sheets.items():
        frame = frame.dropna(axis=0, how="all").dropna(axis=1, how="all").fillna("")
        if frame.empty:
            continue
        marketplace = _marketplace_name(list(frame.columns))
        if marketplace:
            logger.warning("Skipped structured marketplace sheet; use /api/data/import instead")
            continue
        safe_columns = [
            column for column in frame.columns
            if not any(marker in str(column).lower() for marker in SENSITIVE_COLUMN_MARKERS)
        ]
        safe_frame = frame[safe_columns].map(neutralize_spreadsheet_formula)
        csv_content = safe_frame.to_csv(index=False)
        content = sanitize_text((
            f"DỮ LIỆU EXCEL: {file_path.name}\n"
            f"SÀN: {marketplace or 'Chưa xác định'}\n"
            f"SHEET: {sheet_name}\n"
            f"SỐ DÒNG: {len(frame)} | SỐ CỘT: {len(safe_frame.columns)}\n\n"
            f"{csv_content}"
        ), block_prompt_injection=True)
        documents.append(Document(
            page_content=content,
            metadata={
                "source": str(file_path),
                "filename": file_path.name,
                "file_type": file_path.suffix.lower().lstrip("."),
                "sheet_name": str(sheet_name),
                "rows": len(frame),
            },
        ))
    return documents


def _marketplace_summary(files: list[Path]) -> list[Document]:
    """Create one deterministic cross-platform summary for marketplace exports."""
    import pandas as pd

    configs = {
        "Shopee": ("Mã đơn hàng", "Tổng giá trị đơn hàng (VND)", "Số lượng", "Tên sản phẩm", "Trạng Thái Đơn Hàng"),
        "Lazada": ("orderNumber", "paidPrice", None, "itemName", "status"),
        "TikTok Shop": ("Order ID", "Order Amount", "Quantity", "Product Name", "Order Status"),
    }
    summaries: list[str] = []
    total_orders = 0
    total_revenue = 0.0
    for file_path in files:
        try:
            for _sheet, frame in pd.read_excel(file_path, sheet_name=None, dtype=str).items():
                platform = _marketplace_name(list(frame.columns))
                if not platform:
                    continue
                order_col, amount_col, qty_col, product_col, status_col = configs[platform]
                frame = frame.dropna(axis=0, how="all").fillna("")
                if frame.empty or order_col not in frame or amount_col not in frame:
                    continue
                amounts = frame[amount_col].map(_number)
                # Marketplace exports repeat order-level totals for every SKU.
                by_order = pd.DataFrame({"order": frame[order_col], "amount": amounts}).groupby("order", dropna=True)["amount"]
                revenue = by_order.max().sum() if platform in ("Shopee", "TikTok Shop") else by_order.sum().sum()
                orders = int(frame[order_col].replace("", pd.NA).dropna().nunique())
                quantity = int(frame[qty_col].map(_number).sum()) if qty_col and qty_col in frame else len(frame)
                top_product = "Chưa xác định"
                if product_col in frame:
                    top_product = str(frame[product_col].replace("", pd.NA).dropna().value_counts().index[0]) if frame[product_col].replace("", pd.NA).dropna().any() else top_product
                statuses = frame[status_col].replace("", pd.NA).dropna().value_counts().head(5).to_dict() if status_col in frame else {}
                summaries.append(
                    f"Sàn: {platform}; File: {file_path.name}; Đơn: {orders:,}; "
                    f"Doanh thu theo file: {revenue:,.0f} VND; Số lượng: {quantity:,}; "
                    f"Sản phẩm xuất hiện nhiều nhất: {top_product}; Trạng thái: {statuses}"
                )
                total_orders += orders
                total_revenue += revenue
        except Exception as exc:
            logger.warning(
                "Could not summarize marketplace file hash=%s type=%s",
                hashlib.sha256(file_path.name.encode()).hexdigest()[:12], type(exc).__name__,
            )
    if not summaries:
        return []
    content = (
        "TỔNG HỢP DỮ LIỆU ĐA SÀN\n"
        "Lưu ý: Doanh thu được tổng hợp theo mã đơn để tránh cộng lặp đơn có nhiều SKU. "
        "Chỉ so sánh các file khi cùng khoảng thời gian và định nghĩa trạng thái.\n\n"
        + "\n".join(summaries)
        + f"\n\nTỔNG CỘNG CÁC FILE: {total_orders:,} đơn; {total_revenue:,.0f} VND."
    )
    return [Document(page_content=content, metadata={"source": "marketplace_aggregate", "filename": "marketplace_aggregate", "file_type": "summary"})]


def load_document(
    file_path: Path,
    tenant_scope: str = "public",
    *,
    tenant_id: str = "__public__",
    shop_id: str = "__public__",
    visibility: str | None = None,
) -> list[Document]:
    """Load a single document and attach metadata.

    Args:
        file_path: Absolute path to the document.

    Returns:
        List of LangChain Document objects (PDF may return multiple pages).
    """
    ext = file_path.suffix.lower()

    if ext in (".md", ".txt", ".csv"):
        loader = TextLoader(str(file_path), encoding="utf-8")
        docs = loader.load()
    elif ext == ".pdf":
        loader = PyPDFLoader(str(file_path))
        docs = loader.load()
    elif ext in (".xlsx", ".xls"):
        docs = _load_spreadsheet(file_path)
    else:
        logger.warning("Unsupported document extension: %s", ext)
        return []

    # Attach structured metadata
    safe_filename = (
        file_path.name if tenant_scope == "public"
        else hashlib.sha256(file_path.name.encode()).hexdigest()[:16] + ext
    )
    selected_visibility = visibility or ("public" if tenant_scope == "public" else "private")
    document_id = hashlib.sha256(file_path.read_bytes()).hexdigest()
    for doc in docs:
        if tenant_scope != "public":
            doc.page_content = doc.page_content.replace(file_path.name, safe_filename)
        doc.page_content = sanitize_text(doc.page_content, block_prompt_injection=True)
        doc.metadata.update({
            "source": str(file_path) if tenant_scope == "public" else safe_filename,
            "filename": safe_filename,
            "file_type": ext.lstrip("."),
            "tenant_scope": tenant_scope,
            "tenant_id": tenant_id,
            "shop_id": shop_id,
            "visibility": selected_visibility,
            "document_id": document_id,
        })

    return docs


def load_all_documents(
    directory: Path | str,
    tenant_scope: str = "public",
    *,
    tenant_id: str = "__public__",
    shop_id: str = "__public__",
    visibility: str | None = None,
) -> list[Document]:
    """Load all supported documents from a directory.

    Args:
        directory: Path to the knowledge base directory.

    Returns:
        All loaded Document objects.
    """
    d = Path(directory)
    if not d.is_dir():
        logger.error("Knowledge directory not found: %s", d)
        return []

    files = list_files(d, extensions=SUPPORTED_EXTENSIONS)
    logger.info("Found %d documents in %s", len(files), d)

    all_docs: list[Document] = []
    for file_path in files:
        try:
            docs = load_document(
                file_path,
                tenant_scope=tenant_scope,
                tenant_id=tenant_id,
                shop_id=shop_id,
                visibility=visibility,
            )
            all_docs.extend(docs)
            logger.debug("Loaded %d document page(s)", len(docs))
        except Exception as exc:
            logger.warning("Failed to load document type=%s", type(exc).__name__)

    logger.info("Total documents loaded: %d", len(all_docs))
    return all_docs
