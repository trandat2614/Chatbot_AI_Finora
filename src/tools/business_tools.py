"""Tenant-bound read-only tools available to the chatbot."""
from __future__ import annotations

import json
from typing import Callable

from langchain_core.tools import StructuredTool

from src.services.decision_intelligence_service import DecisionIntelligenceService


def _json(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, default=str)


def build_business_tools(service: DecisionIntelligenceService) -> tuple[StructuredTool, ...]:
    """Create closures bound to an already-authorized tenant/shop scope."""

    def get_business_overview(period: str = "") -> str:
        return _json(service.get_business_overview(period or None))

    def get_business_health(period: str = "") -> str:
        return _json(service.get_business_health(period or None))

    def analyze_product(sku: str = "", period: str = "") -> str:
        return _json(service.analyze_product(sku or None, period or None))

    def analyze_orders(period: str = "") -> str:
        return _json(service.analyze_orders(period or None))

    def analyze_refunds(period: str = "") -> str:
        return _json(service.analyze_refunds(period or None))

    def analyze_revenue_leakage(period: str = "") -> str:
        return _json(service.analyze_revenue_leakage(period or None))

    def get_market_trends(category: str = "nam", period: str = "7d") -> str:
        return _json(service.get_market_trends(category, period))

    def find_product_opportunities(category: str = "nam", period: str = "7d") -> str:
        return _json(service.find_product_opportunities(category, period))

    def generate_action_plan(category: str = "nam", period: str = "7d") -> str:
        return _json(service.generate_action_plan(category, period))

    def generate_sales_plan(category: str = "nam", period: str = "week", objective: str = "conversion") -> str:
        return _json(service.generate_sales_plan(category, period, objective))

    def generate_communication_plan(category: str = "nam", period: str = "week", objective: str = "conversion") -> str:
        return _json(service.generate_communication_plan(category, period, objective))

    definitions: tuple[tuple[str, Callable, str], ...] = (
        ("get_business_overview", get_business_overview, "Read verified shop KPI overview."),
        ("get_business_health", get_business_health, "Read-only shop health analysis."),
        ("analyze_product", analyze_product, "Read-only SKU diagnosis."),
        ("analyze_orders", analyze_orders, "Read verified order and cancellation metrics."),
        ("analyze_refunds", analyze_refunds, "Read verified shop refund metrics."),
        ("analyze_revenue_leakage", analyze_revenue_leakage, "Read-only GMV-to-net analysis."),
        ("get_market_trends", get_market_trends, "Read public marketplace trend snapshots."),
        ("find_product_opportunities", find_product_opportunities, "Match authorized shop data to trends."),
        ("generate_action_plan", generate_action_plan, "Generate 3-5 recommendation-only actions."),
        ("generate_sales_plan", generate_sales_plan, "Generate a recommendation-only sales plan."),
        ("generate_communication_plan", generate_communication_plan, "Generate a recommendation-only communication plan."),
    )
    return tuple(
        StructuredTool.from_function(func=func, name=name, description=description)
        for name, func, description in definitions
    )
