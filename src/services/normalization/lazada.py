"""Lazada export adapter."""
from src.services.normalization.base import COMMON_ALIASES, MarketplaceAdapter


class LazadaAdapter(MarketplaceAdapter):
    platform = "lazada"
    markers = {"orderNumber", "paidPrice", "itemName"}
    aliases = {
        **COMMON_ALIASES,
        "created_at": (*COMMON_ALIASES["created_at"], "createTime"),
        "platform_fee": (*COMMON_ALIASES["platform_fee"], "commission"),
        "transaction_fee": (*COMMON_ALIASES["transaction_fee"], "paymentFee"),
    }
