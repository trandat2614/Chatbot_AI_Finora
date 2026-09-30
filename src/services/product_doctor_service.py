"""Classify SKU health from backend-calculated metrics."""
from __future__ import annotations

import pandas as pd

from src.schemas.commerce import AnalysisStatus
from src.services.metric_service import cancelled_mask


class ProductDoctorService:
    def analyze(self, frame: pd.DataFrame, sku: str | None = None) -> dict:
        key = "seller_sku" if "seller_sku" in frame.columns else "product_id"
        if frame.empty or key not in frame or frame[key].dropna().empty:
            return {"status": AnalysisStatus.INSUFFICIENT_DATA.value, "products": [], "missing_fields": [key]}
        data = frame.copy()
        if sku:
            data = data.loc[data[key].astype(str) == sku]
        products = []
        for identifier, group in data.groupby(key, dropna=True):
            quantity = pd.to_numeric(group["quantity"], errors="coerce").fillna(0)
            prices = pd.to_numeric(group["selling_price"], errors="coerce").fillna(0)
            revenue = float((quantity * prices).sum())
            orders = int(group["order_id"].astype(str).nunique())
            cancellation = int(group.loc[cancelled_mask(group), "order_id"].astype(str).nunique()) / max(orders, 1) * 100
            refunds = pd.to_numeric(group["refund_amount"], errors="coerce").fillna(0)
            refund_rate = int(group.loc[refunds > 0, "order_id"].astype(str).nunique()) / max(orders, 1) * 100
            discount = pd.to_numeric(group["seller_discount"], errors="coerce").fillna(0).sum()
            discount_rate = float(discount / revenue * 100) if revenue > 0 else 0
            if orders < 3:
                classification = "TEST"
            elif cancellation >= 15 or refund_rate >= 15:
                classification = "FIX"
            elif discount_rate >= 30:
                classification = "REDUCE"
            elif orders >= 10 and cancellation < 5 and refund_rate < 5:
                classification = "SCALE"
            elif orders >= 5:
                classification = "PUSH"
            else:
                classification = "MONITOR"
            products.append({
                "sku": str(identifier), "classification": classification,
                "metrics": {"revenue": round(revenue, 2), "order_count": orders, "units_sold": int(quantity.sum()),
                            "cancellation_rate": round(cancellation, 4), "refund_rate": round(refund_rate, 4),
                            "discount_dependency": round(discount_rate, 4)},
                "confidence": round(min(1.0, 0.4 + orders / 20), 2),
            })
        return {"status": AnalysisStatus.OK.value if products else AnalysisStatus.INSUFFICIENT_DATA.value, "products": products}
