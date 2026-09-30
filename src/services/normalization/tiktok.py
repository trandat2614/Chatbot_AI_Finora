"""TikTok Shop export adapter."""
from src.services.normalization.base import COMMON_ALIASES, MarketplaceAdapter


class TikTokShopAdapter(MarketplaceAdapter):
    platform = "tiktok_shop"
    markers = {"Order ID", "Seller SKU", "Created Time"}
    aliases = {
        **COMMON_ALIASES,
        "platform_fee": (*COMMON_ALIASES["platform_fee"], "Platform Commission Fee"),
        "transaction_fee": (*COMMON_ALIASES["transaction_fee"], "Transaction Fee"),
        "service_fee": (*COMMON_ALIASES["service_fee"], "Affiliate Commission"),
    }
