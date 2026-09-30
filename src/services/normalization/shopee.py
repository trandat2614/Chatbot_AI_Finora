"""Shopee export adapter."""
from src.services.normalization.base import COMMON_ALIASES, MarketplaceAdapter


class ShopeeAdapter(MarketplaceAdapter):
    platform = "shopee"
    markers = {"Mã đơn hàng", "Trạng Thái Đơn Hàng", "SKU phân loại hàng"}
    aliases = {
        **COMMON_ALIASES,
        "created_at": (*COMMON_ALIASES["created_at"], "Ngày tạo đơn"),
        "platform_fee": (*COMMON_ALIASES["platform_fee"], "Phí cố định"),
        "service_fee": (*COMMON_ALIASES["service_fee"], "Phí Dịch Vụ"),
    }
