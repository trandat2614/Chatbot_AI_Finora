"""Base marketplace adapter converting untrusted exports to unified fields."""
from __future__ import annotations

import hashlib
from abc import ABC
from typing import ClassVar

import pandas as pd
from pydantic import ValidationError

from src.schemas.commerce import UnifiedOrderItem
from src.security.privacy import sanitize_text
from src.security.uploads import neutralize_spreadsheet_formula


COMMON_ALIASES: dict[str, tuple[str, ...]] = {
    "order_id": ("order_id", "Order ID", "Mã đơn hàng", "orderNumber", "Order Number"),
    "order_item_id": ("order_item_id", "Order Item ID", "Mã sản phẩm trong đơn", "orderItemId"),
    "created_at": ("created_at", "Created Time", "Ngày đặt hàng", "Order Date", "createTime"),
    "product_id": ("product_id", "Product ID", "Mã sản phẩm", "itemId"),
    "seller_sku": ("seller_sku", "Seller SKU", "SKU phân loại hàng", "sellerSku"),
    "product_name": ("product_name", "Product Name", "Tên sản phẩm", "itemName"),
    "variation": ("variation", "Variation", "Tên phân loại hàng", "variationName"),
    "quantity": ("quantity", "Quantity", "Số lượng", "qty"),
    "original_price": ("original_price", "Original Price", "Giá gốc", "unitPrice"),
    "selling_price": ("selling_price", "Selling Price", "Giá ưu đãi", "paidPrice", "Giá bán"),
    "seller_discount": ("seller_discount", "Seller Discount", "Người bán trợ giá", "sellerDiscount"),
    "platform_discount": ("platform_discount", "Platform Discount", "Shopee trợ giá", "platformDiscount"),
    "shipping_fee": ("shipping_fee", "Shipping Fee", "Phí vận chuyển", "shippingFee"),
    "platform_fee": ("platform_fee", "Platform Fee", "Phí sàn", "platformFee"),
    "transaction_fee": ("transaction_fee", "Transaction Fee", "Phí thanh toán", "transactionFee"),
    "service_fee": ("service_fee", "Service Fee", "Phí dịch vụ", "serviceFee"),
    "refund_amount": ("refund_amount", "Refund Amount", "Số tiền hoàn", "refundAmount"),
    "order_status": ("order_status", "Order Status", "Trạng Thái Đơn Hàng", "status"),
    "cancel_reason": ("cancel_reason", "Cancel Reason", "Lý do hủy", "cancelReason"),
}


class MarketplaceAdapter(ABC):
    platform: ClassVar[str]
    markers: ClassVar[set[str]]
    aliases: ClassVar[dict[str, tuple[str, ...]]] = COMMON_ALIASES

    def detection_score(self, frame: pd.DataFrame) -> int:
        columns = set(map(str, frame.columns))
        return len(self.markers.intersection(columns))

    def can_handle(self, frame: pd.DataFrame) -> bool:
        return self.detection_score(frame) > 0

    def _pick(self, frame: pd.DataFrame, name: str) -> pd.Series:
        for alias in self.aliases[name]:
            if alias in frame.columns:
                return frame[alias]
        return pd.Series([None] * len(frame), index=frame.index, dtype="object")

    def normalize(self, frame: pd.DataFrame) -> tuple[pd.DataFrame, int, list[str]]:
        normalized = pd.DataFrame(index=frame.index)
        normalized["platform"] = self.platform
        for field in self.aliases:
            normalized[field] = self._pick(frame, field)

        required = [
            "order_id", "created_at", "product_name", "quantity",
            "selling_price", "order_status",
        ]
        missing = [name for name in required if normalized[name].isna().all()]
        if missing:
            raise ValueError("Thiếu cột bắt buộc: " + ", ".join(missing))

        numeric = [
            "quantity", "original_price", "selling_price", "seller_discount",
            "platform_discount", "shipping_fee", "platform_fee", "transaction_fee",
            "service_fee", "refund_amount",
        ]
        for name in numeric:
            normalized[name] = pd.to_numeric(
                normalized[name]
                .astype(str)
                .str.replace(r"[^0-9,.-]", "", regex=True)
                .str.replace(",", "", regex=False),
                errors="coerce",
            )
        normalized["quantity"] = normalized["quantity"].fillna(0).astype(int)
        for name in numeric[1:]:
            normalized[name] = normalized[name].fillna(0.0).clip(lower=0)
        normalized["created_at"] = pd.to_datetime(
            normalized["created_at"], errors="coerce", utc=True
        )

        text_fields = [
            "order_id", "product_id", "seller_sku", "product_name",
            "variation", "order_status", "cancel_reason",
        ]
        for name in text_fields:
            block_instructions = name == "product_name"
            normalized[name] = normalized[name].map(
                lambda value: sanitize_text(
                    str(neutralize_spreadsheet_formula(value)),
                    block_prompt_injection=block_instructions,
                )
                if pd.notna(value)
                else None
            )

        item_ids: list[str] = []
        for index, row in normalized.iterrows():
            value = row.get("order_item_id")
            if pd.isna(value) or not str(value).strip():
                digest = hashlib.sha256(
                    f"{self.platform}:{row['order_id']}:{index}".encode()
                ).hexdigest()[:16]
                value = f"generated-{digest}"
            item_ids.append(sanitize_text(str(neutralize_spreadsheet_formula(value))))
        normalized["order_item_id"] = item_ids

        before = len(normalized)
        normalized = normalized.drop_duplicates(
            subset=["platform", "order_id", "order_item_id"], keep="last"
        )
        duplicate_rows = before - len(normalized)
        records: list[dict] = []
        rejected = 0
        for record in normalized.to_dict(orient="records"):
            try:
                records.append(
                    UnifiedOrderItem.model_validate(record).model_dump(mode="json")
                )
            except ValidationError:
                rejected += 1
        if not records:
            raise ValueError("Không có dòng dữ liệu hợp lệ sau chuẩn hóa.")
        warnings = [f"Đã loại {rejected} dòng không hợp lệ."] if rejected else []
        if duplicate_rows:
            warnings.append(f"Đã loại {duplicate_rows} order item trùng lặp.")
        return pd.DataFrame(records), rejected, warnings
