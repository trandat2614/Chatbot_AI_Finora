"""Match shop SKUs to public trend evidence with explicit confidence penalties."""
from __future__ import annotations

import math
from collections import Counter

import pandas as pd

from src.schemas.commerce import AnalysisStatus
from src.services.fashion_nlp_service import FashionNLPService
from src.services.metric_service import MetricService
from src.services.product_doctor_service import ProductDoctorService
from src.services.trend_service import fold_text


def _tokens(value: str) -> Counter[str]:
    return Counter(token for token in fold_text(value).split() if len(token) > 1)


def _similarity(left: str, right: str) -> float:
    a, b = _tokens(left), _tokens(right)
    if not a or not b:
        return 0.0
    dot = sum(count * b.get(key, 0) for key, count in a.items())
    denominator = math.sqrt(sum(v * v for v in a.values()) * sum(v * v for v in b.values()))
    return dot / denominator if denominator else 0.0


class OpportunityMatchingService:
    def __init__(self) -> None:
        self.doctor = ProductDoctorService()
        self.nlp = FashionNLPService()

    def match(self, orders: pd.DataFrame, market: dict, *, limit: int = 20) -> dict:
        diagnosis = self.doctor.analyze(orders)
        if diagnosis["status"] != AnalysisStatus.OK.value or not market.get("items"):
            return {"status": AnalysisStatus.INSUFFICIENT_DATA.value, "opportunities": [],
                    "missing_fields": ["shop_products or market_trends"]}
        by_sku = {str(item["sku"]): item for item in diagnosis["products"]}
        opportunities = []
        for sku, group in orders.groupby("seller_sku", dropna=True):
            name = str(group["product_name"].dropna().iloc[0]) if group["product_name"].notna().any() else str(sku)
            best = max(market["items"], key=lambda item: _similarity(name, item["product_name"]))
            similarity = _similarity(name, best["product_name"])
            metrics = by_sku[str(sku)]["metrics"]
            shop_price = float(pd.to_numeric(group["selling_price"], errors="coerce").median())
            market_price = float(best.get("price") or 0)
            price_position = (shop_price - market_price) / market_price * 100 if market_price > 0 else None
            market_growth = float(best.get("sales_growth") or 0)
            market_growth_score = min(max(market_growth / 100, -1), 1)
            dated_group = group.copy()
            dated_group["created_at"] = pd.to_datetime(
                dated_group["created_at"], errors="coerce", utc=True
            )
            shop_growth = MetricService._growth(dated_group.dropna(subset=["created_at"]))
            shop_growth_score = min(max((shop_growth or 0) / 100, -1), 1)
            risk_penalty = min((metrics["refund_rate"] + metrics["cancellation_rate"] + metrics["discount_dependency"]) / 100, 0.6)
            score = max(
                0.0,
                min(
                    100.0,
                    (
                        0.4 * similarity
                        + 0.3 * market_growth_score
                        + 0.2 * shop_growth_score
                        + 0.1 * (1 if price_position is not None else 0)
                        - risk_penalty
                    )
                    * 100,
                ),
            )
            missing = []
            if "margin" not in group or group["margin"].dropna().empty:
                missing.append("margin")
            if "inventory" not in group or group["inventory"].dropna().empty:
                missing.append("inventory")
            available = 7 - len(missing)
            confidence = min(
                0.95,
                0.25 + available / 12 + min(metrics["order_count"], 20) / 100,
            )
            if score >= 65:
                recommendation = "Thử mở rộng có kiểm soát sau khi xác nhận tồn kho và biên lợi nhuận."
            elif score >= 40:
                recommendation = "Chạy thử nghiệm nhỏ và theo dõi conversion, refund, cancellation."
            else:
                recommendation = "Chưa ưu tiên mở rộng; tiếp tục thu thập dữ liệu và xử lý tín hiệu rủi ro."
            opportunities.append({
                "sku": str(sku), "product_name": name,
                "fashion_attributes": self.nlp.extract(name),
                "matched_market_product": best["product_name"],
                "trend_state": best["trend_state"],
                "opportunity_score": round(score, 2),
                "confidence": round(confidence, 2),
                "recommendation": recommendation,
                "missing_metrics": missing,
                "evidence": {
                    "name_similarity": round(similarity, 4), "market_sales_growth": best.get("sales_growth"),
                    "shop_order_count": metrics["order_count"], "refund_rate": metrics["refund_rate"],
                    "cancellation_rate": metrics["cancellation_rate"], "discount_dependency": metrics["discount_dependency"],
                    "shop_sales_growth": round(shop_growth, 4) if shop_growth is not None else None,
                    "price_position_percent": round(price_position, 2) if price_position is not None else None,
                },
            })
        opportunities.sort(key=lambda item: (item["opportunity_score"], item["confidence"]), reverse=True)
        return {"status": AnalysisStatus.OK.value, "opportunities": opportunities[:limit]}
