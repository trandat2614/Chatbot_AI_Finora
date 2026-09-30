"""Deterministic bridge from GMV to net revenue."""
from __future__ import annotations

import pandas as pd

from src.schemas.commerce import AnalysisStatus
from src.services.metric_service import cancelled_mask, order_level_values


class RevenueLeakageService:
    def analyze(self, frame: pd.DataFrame) -> dict:
        required = {
            "quantity", "original_price", "selling_price", "seller_discount",
            "platform_discount", "shipping_fee", "platform_fee", "transaction_fee",
            "service_fee", "refund_amount", "order_status",
        }
        missing = sorted(required.difference(frame.columns))
        if frame.empty or missing:
            return {"status": AnalysisStatus.INSUFFICIENT_DATA.value, "missing_fields": missing or ["orders"]}
        data = frame.copy()
        for name in required.difference({"order_status"}):
            data[name] = pd.to_numeric(data[name], errors="coerce").fillna(0).clip(lower=0)
        data = data.loc[~cancelled_mask(data)]
        order_values = order_level_values(data)
        original = data["original_price"].where(data["original_price"] > 0, data["selling_price"])
        gmv = float((original * data["quantity"]).sum())
        collected = float((data["selling_price"] * data["quantity"]).sum())
        components = {
            "price_and_seller_discount": max(gmv - collected, 0.0),
            "seller_discount_reported": float(data["seller_discount"].sum()),
            "platform_discount": float(data["platform_discount"].sum()),
            "refund": float(order_values["refund_amount"].sum()),
            "platform_fee": float(order_values["platform_fee"].sum()),
            "transaction_fee": float(order_values["transaction_fee"].sum()),
            "service_fee": float(order_values["service_fee"].sum()),
            "shipping_fee": float(order_values["shipping_fee"].sum()),
        }
        # Platform-funded discount is disclosed but not deducted from seller net.
        deducted = (
            components["refund"] + components["platform_fee"] + components["transaction_fee"]
            + components["service_fee"] + components["shipping_fee"]
        )
        net = collected - deducted
        return {
            "status": AnalysisStatus.OK.value,
            "gmv": round(gmv, 2),
            "collected_revenue": round(collected, 2),
            "net_revenue": round(net, 2),
            "total_leakage": round(gmv - net, 2),
            "leakage_rate": round((gmv - net) / gmv * 100, 4) if gmv > 0 else None,
            "components": {key: round(value, 2) for key, value in components.items()},
            "assumptions": [
                "platform_discount được xem là khoản sàn tài trợ và không trừ lần hai khỏi seller net",
                "chi phí cấp đơn được tính đúng một lần cho mỗi order_id",
                "chi phí chỉ được tính khi có trong dữ liệu upload",
            ],
        }
