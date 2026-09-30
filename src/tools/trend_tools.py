"""LangChain tools for Shopee market-trend and product-gap analysis."""
from __future__ import annotations

import json
import math
import threading
from collections import Counter
from functools import lru_cache
from typing import Any

from langchain_core.tools import tool

from src.services.trend_service import (
    COMMISSION_COLUMN,
    PRICE_COLUMN,
    PRODUCT_COLUMN,
    SALES_GROWTH_COLUMN,
    SOLD_30D_COLUMN,
    TrendDataLoader,
    fold_text,
    normalise_gender,
)

_LOADER_LOCK = threading.Lock()
_STYLE_MATERIAL_TERMS = {
    "boxy", "raglan", "ong", "rong", "form", "suong", "oversize", "croptop",
    "cotton", "250gsm", "su", "lanh", "ni", "lop", "kaki", "denim", "voan",
    "dui", "linen", "lua", "len",
}


@lru_cache(maxsize=1)
def get_trend_loader() -> TrendDataLoader:
    """Return the process-wide loader; initialisation also refreshes SQLite."""
    with _LOADER_LOCK:
        return TrendDataLoader()


def reset_trend_loader_cache() -> None:
    """Clear the loader singleton after source CSVs change."""
    get_trend_loader.cache_clear()


def _json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)


@tool
def get_shopee_fashion_trends(
    category: str,
    timeframe: str = "7d",
    limit: int = 5,
) -> str:
    """Tra cứu xu hướng thời trang Shopee từ database nội bộ.

    Args:
        category: Giới tính/ngành hàng, ví dụ ``nam``, ``nữ``,
            ``thời trang nam`` hoặc ``thời trang nữ``.
        timeframe: Chu kỳ dữ liệu ``today``, ``7d`` hoặc ``30d``.
        limit: Số sản phẩm tiêu biểu cần trả về, từ 1 đến 20.

    Returns:
        Chuỗi JSON tiếng Việt gồm top từ khóa form dáng/chất liệu, giá trung
        vị, khoảng giá bán chạy, hoa hồng affiliate trung bình và danh sách
        sản phẩm đứng đầu theo lượt bán tăng. Mọi số liệu đều lấy từ CSV đã
        chuẩn hóa, không phải ước lượng của mô hình ngôn ngữ.
    """
    bounded_limit = max(1, min(int(limit), 20))
    loader = get_trend_loader()
    gender = normalise_gender(category)
    metrics = loader.get_category_metrics(gender, timeframe)
    return _json(
        {
            "source": "Shopee trend database",
            "category": gender,
            "timeframe": metrics["timeframe"],
            "top_keywords": loader.query_top_keywords(gender, timeframe, top_k=10),
            "metrics": metrics,
            "top_products": loader.get_top_products(gender, timeframe, bounded_limit),
            "data_warnings": loader.warnings,
        }
    )


def _tokens(value: str) -> Counter[str]:
    return Counter(token for token in fold_text(value).split() if len(token) > 1)


def _cosine(left: Counter[str], right: Counter[str]) -> float:
    if not left or not right:
        return 0.0
    dot = sum(count * right.get(token, 0) for token, count in left.items())
    left_norm = math.sqrt(sum(count * count for count in left.values()))
    right_norm = math.sqrt(sum(count * count for count in right.values()))
    return dot / (left_norm * right_norm) if left_norm and right_norm else 0.0


def _normalise_rate(rate: float) -> float:
    if rate < 0:
        raise ValueError("affiliate_rate không được âm.")
    return rate * 100.0 if 0 < rate < 1.0 else rate


def _comparison_payload(
    product_name: str,
    current_price: float,
    cogs: float,
    affiliate_rate: float,
    category: str,
) -> dict[str, Any]:
    if not product_name.strip():
        raise ValueError("product_name không được để trống.")
    if current_price <= 0:
        raise ValueError("current_price phải lớn hơn 0.")
    if cogs < 0:
        raise ValueError("cogs không được âm.")

    rate = _normalise_rate(float(affiliate_rate))
    if rate >= 88.0:
        raise ValueError("affiliate_rate phải nhỏ hơn 88% để còn dư địa cho phí sàn.")
    gender = normalise_gender(category)
    loader = get_trend_loader()
    market = loader.select(gender, "7d")
    query_tokens = _tokens(product_name)
    style_terms = set(query_tokens).intersection(_STYLE_MATERIAL_TERMS)

    scored: list[tuple[float, int, Any]] = []
    for index, row in market.iterrows():
        candidate_tokens = _tokens(str(row[PRODUCT_COLUMN]))
        cosine = _cosine(query_tokens, candidate_tokens)
        candidate_style = set(candidate_tokens).intersection(_STYLE_MATERIAL_TERMS)
        overlap = len(style_terms.intersection(candidate_style)) / max(len(style_terms), 1)
        score = 0.8 * cosine + 0.2 * overlap
        scored.append((score, int(row[SALES_GROWTH_COLUMN]), index))
    scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
    selected_indexes = [index for score, _, index in scored[:5] if score > 0]
    similar = market.loc[selected_indexes].copy() if selected_indexes else market.head(0).copy()

    benchmark = similar if not similar.empty else market
    market_median = float(benchmark[PRICE_COLUMN].median()) if not benchmark.empty else 0.0
    market_affiliate = (
        float(benchmark[COMMISSION_COLUMN].mean()) if not benchmark.empty else 0.0
    )
    price_gap = current_price - market_median if market_median else None
    price_gap_percent = price_gap / market_median * 100.0 if market_median else None

    def margin_at(price: float, platform_rate: float) -> dict[str, float]:
        net_profit = price - cogs - price * (rate / 100.0) - price * platform_rate
        return {
            "platform_fee_rate": round(platform_rate * 100.0, 2),
            "estimated_net_profit": round(net_profit, 2),
            "estimated_net_margin_percent": round(net_profit / price * 100.0, 2),
        }

    current_margin = [margin_at(current_price, platform_rate) for platform_rate in (0.08, 0.12)]
    trend_margin = [margin_at(market_median, platform_rate) for platform_rate in (0.08, 0.12)] if market_median else []
    conservative_trend_profit = trend_margin[-1]["estimated_net_profit"] if trend_margin else None
    denominator = 1.0 - 0.12 - rate / 100.0
    break_even_price = cogs / denominator if denominator > 0 else None

    products = []
    for score, _, index in scored[:5]:
        if score <= 0:
            continue
        row = market.loc[index]
        products.append(
            {
                "product_name": str(row[PRODUCT_COLUMN]),
                "similarity": round(float(score), 4),
                "price": int(row[PRICE_COLUMN]),
                "sales_growth": int(row[SALES_GROWTH_COLUMN]),
                "sold_30d": int(row[SOLD_30D_COLUMN]),
                "affiliate_rate": float(row[COMMISSION_COLUMN]),
            }
        )

    warnings: list[str] = []
    if conservative_trend_profit is not None and conservative_trend_profit < 0:
        warnings.append(
            "Không nên hạ giá về trung vị trend: biên lợi nhuận ước tính âm ở kịch bản phí sàn 12%."
        )
    if current_margin[-1]["estimated_net_profit"] < 0:
        warnings.append("Giá hiện tại đang cho lợi nhuận ước tính âm ở kịch bản phí sàn 12%.")

    return {
        "source": "Shopee trend database - timeframe 7d",
        "shop_product": {
            "product_name": product_name,
            "current_price": round(float(current_price), 2),
            "cogs": round(float(cogs), 2),
            "affiliate_rate": round(rate, 2),
            "category": gender,
        },
        "market_benchmark": {
            "sample_size": int(len(benchmark)),
            "median_price": round(market_median, 2) if market_median else None,
            "average_affiliate_rate": round(market_affiliate, 2) if not benchmark.empty else None,
        },
        "gap_analysis": {
            "price_gap": round(price_gap, 2) if price_gap is not None else None,
            "price_gap_percent": round(price_gap_percent, 2) if price_gap_percent is not None else None,
            "affiliate_gap_percentage_points": round(rate - market_affiliate, 2) if not benchmark.empty else None,
        },
        "profit_margin_check": {
            "current_price_scenarios": current_margin,
            "market_median_price_scenarios": trend_margin,
            "break_even_price_at_12pct_platform_fee": round(break_even_price, 2) if break_even_price else None,
            "formula": "price - COGS - price*affiliate_rate - price*platform_fee_rate",
        },
        "similar_products": products,
        "warnings": warnings,
    }


@tool
def compare_shop_product_with_trends(
    product_name: str,
    current_price: float,
    cogs: float,
    affiliate_rate: float,
    category: str,
) -> str:
    """So sánh một sản phẩm của shop với xu hướng Shopee 7 ngày.

    Args:
        product_name: Tên sản phẩm, nên chứa form dáng và chất liệu.
        current_price: Giá bán hiện tại bằng VND, ví dụ ``120000``.
        cogs: Giá vốn hàng bán bằng VND, chưa gồm phí sàn và hoa hồng.
        affiliate_rate: Hoa hồng affiliate dạng phần trăm (``5``) hoặc tỷ lệ
            thập phân (``0.05``); công cụ tự chuẩn hóa về phần trăm.
        category: ``nam``, ``nữ``, ``thời trang nam`` hoặc ``thời trang nữ``.

    Returns:
        Chuỗi JSON gồm các sản phẩm tương đồng, chênh lệch giá, chênh lệch
        hoa hồng và biên lợi nhuận ở hai kịch bản phí sàn 8%/12%. Công cụ cảnh
        báo nếu hạ về giá trung vị thị trường làm lợi nhuận ước tính âm.
    """
    return _json(
        _comparison_payload(
            product_name=product_name,
            current_price=float(current_price),
            cogs=float(cogs),
            affiliate_rate=float(affiliate_rate),
            category=category,
        )
    )
