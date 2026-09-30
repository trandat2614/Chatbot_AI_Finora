"""Facade that composes tenant-scoped deterministic decision services."""
from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone

import pandas as pd

from src.repositories.trend_repository import SQLAlchemyTrendRepository
from src.services.action_plan_service import ActionPlanService
from src.services.business_health_service import BusinessHealthService
from src.services.communication_planner_service import CommunicationPlannerService
from src.services.market_trend_service import MarketTrendService
from src.services.metric_service import MetricService
from src.services.opportunity_matching_service import OpportunityMatchingService
from src.services.product_doctor_service import ProductDoctorService
from src.services.revenue_leakage_service import RevenueLeakageService
from src.services.sales_planner_service import SalesPlannerService
from src.services.tenant_store import TenantDataStore
from src.tools.trend_tools import get_trend_loader


class DecisionIntelligenceService:
    def __init__(self, tenant_id: str, shop_id: str, store: TenantDataStore | None = None) -> None:
        self.tenant_id = tenant_id
        self.shop_id = shop_id
        self.store = store or TenantDataStore()
        self.metrics = MetricService()
        self.health_service = BusinessHealthService()
        self.leakage_service = RevenueLeakageService()
        self.product_service = ProductDoctorService()
        trend_repository = (
            SQLAlchemyTrendRepository(store.database)
            if store is not None and hasattr(store, "database")
            else None
        )
        self.market_service = MarketTrendService(get_trend_loader(), trend_repository)
        self.opportunity_service = OpportunityMatchingService()
        self.action_service = ActionPlanService()
        self.sales_service = SalesPlannerService()
        self.communication_service = CommunicationPlannerService()

    def _period_bounds(self, period: str | None) -> tuple[datetime | None, datetime | None]:
        if not period or period == "all":
            return None, None
        now = datetime.now(timezone.utc)
        end = now
        if period == "today":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "7d":
            start = now - timedelta(days=7)
        elif period == "30d":
            start = now - timedelta(days=30)
        elif period == "month":
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            raise ValueError("Khoảng thời gian phân tích không hợp lệ.")
        return start, end

    def orders(self, period: str | None = None) -> pd.DataFrame:
        frame = self.store.load_orders(self.tenant_id, self.shop_id)
        start, end = self._period_bounds(period)
        if frame.empty or start is None or "created_at" not in frame:
            return frame
        timestamps = pd.to_datetime(frame["created_at"], errors="coerce", utc=True)
        return frame.loc[timestamps.ge(start) & timestamps.le(end)].copy()

    def _source(self, service: str, period: str | None) -> dict:
        start, end = self._period_bounds(period)
        return {
            "type": "postgresql",
            "service": service,
            "tenant_scope": hashlib.sha256(self.tenant_id.encode()).hexdigest()[:16],
            "shop_scope": hashlib.sha256(self.shop_id.encode()).hexdigest()[:16],
            "period": {
                "from": start.isoformat() if start else None,
                "to": end.isoformat() if end else None,
                "selection": period or "all",
            },
        }

    def _ground(
        self,
        result: dict,
        *,
        service: str,
        period: str | None,
        metrics: dict,
    ) -> dict:
        source = self._source(service, period)
        available = [
            {
                "name": name,
                "value": value,
                "status": "AVAILABLE",
                "source": source,
            }
            for name, value in metrics.items()
            if value is not None and not isinstance(value, (dict, list))
        ]
        grounded = dict(result)
        grounded["has_verified_metrics"] = (
            grounded.get("status") == "OK" and bool(available)
        )
        grounded["verified_metrics"] = available
        grounded["provenance"] = source
        return grounded

    def get_business_overview(self, period: str | None = None) -> dict:
        metrics = self.metrics.calculate(self.orders(period))
        payload = {
            "status": metrics.status.value,
            "metrics": metrics.model_dump(mode="json"),
        }
        return self._ground(
            payload,
            service="business_metrics",
            period=period,
            metrics=payload["metrics"],
        )

    def get_business_health(self, period: str | None = None) -> dict:
        frame = self.orders(period)
        result = self.health_service.analyze(self.metrics.calculate(frame))
        return self._ground(
            result,
            service="business_health",
            period=period,
            metrics=result.get("metrics", {}),
        )

    def analyze_product(self, sku: str | None = None, period: str | None = None) -> dict:
        result = self.product_service.analyze(self.orders(period), sku)
        flattened: dict[str, object] = {}
        for index, product in enumerate(result.get("products", [])):
            identifier = product.get("sku", index)
            for name, value in product.get("metrics", {}).items():
                flattened[f"products.{identifier}.{name}"] = value
        return self._ground(
            result,
            service="product_metrics",
            period=period,
            metrics=flattened,
        )

    def analyze_revenue_leakage(self, period: str | None = None) -> dict:
        result = self.leakage_service.analyze(self.orders(period))
        metrics = {
            name: result.get(name)
            for name in (
                "gmv", "collected_revenue", "net_revenue",
                "total_leakage", "leakage_rate",
            )
        }
        return self._ground(
            result,
            service="revenue_leakage",
            period=period,
            metrics=metrics,
        )

    def analyze_orders(self, period: str | None = None) -> dict:
        overview = self.get_business_overview(period)
        selected = {
            name: overview.get("metrics", {}).get(name)
            for name in (
                "order_count", "units_sold", "aov",
                "cancellation_rate", "sales_velocity",
            )
        }
        result = {
            "status": overview["status"],
            "metrics": selected,
            "missing_fields": overview.get("metrics", {}).get("missing_fields", []),
        }
        return self._ground(
            result,
            service="order_metrics",
            period=period,
            metrics=selected,
        )

    def analyze_refunds(self, period: str | None = None) -> dict:
        overview = self.get_business_overview(period)
        selected = {
            name: overview.get("metrics", {}).get(name)
            for name in ("refund_rate", "order_count", "revenue")
        }
        result = {
            "status": overview["status"],
            "metrics": selected,
            "missing_fields": overview.get("metrics", {}).get("missing_fields", []),
        }
        return self._ground(
            result,
            service="refund_metrics",
            period=period,
            metrics=selected,
        )

    def get_market_trends(self, category: str = "nam", period: str = "7d", limit: int = 20) -> dict:
        return self.market_service.get_trends(category, period, limit)

    def find_product_opportunities(self, category: str = "nam", period: str = "7d") -> dict:
        market = self.get_market_trends(category, period)
        result = self.opportunity_service.match(self.orders(), market)
        metrics = {
            f"opportunities.{item.get('sku')}.opportunity_score": item.get("opportunity_score")
            for item in result.get("opportunities", [])
        }
        return self._ground(
            result,
            service="product_opportunities",
            period=None,
            metrics=metrics,
        )

    def generate_action_plan(self, category: str = "nam", period: str = "7d") -> dict:
        frame = self.orders()
        metrics = self.metrics.calculate(frame)
        if metrics.status.value != "OK":
            return self._ground(
                {"status": "INSUFFICIENT_DATA", "actions": [], "missing_fields": metrics.missing_fields},
                service="action_plan",
                period=None,
                metrics={},
            )
        health = self.health_service.analyze(metrics)
        leakage = self.leakage_service.analyze(frame)
        products = self.product_service.analyze(frame)
        opportunities = self.opportunity_service.match(frame, self.get_market_trends(category, period))
        result = self.action_service.generate(health, leakage, products, opportunities)
        return self._ground(
            result,
            service="action_plan",
            period=None,
            metrics=metrics.model_dump(mode="json"),
        )

    def generate_sales_plan(self, category: str = "nam", period: str = "week", objective: str = "conversion") -> dict:
        frame = self.orders()
        metrics = self.metrics.calculate(frame)
        if metrics.status.value != "OK":
            return self._ground(
                {"status": "INSUFFICIENT_DATA", "missing_fields": metrics.missing_fields, "plan": []},
                service="sales_plan",
                period=None,
                metrics={},
            )
        trend_period = "7d" if period == "week" else "30d"
        opportunities = self.opportunity_service.match(frame, self.get_market_trends(category, trend_period))
        products = self.product_service.analyze(frame)
        result = self.sales_service.generate(opportunities, products, period=period, objective=objective)
        return self._ground(
            result,
            service="sales_plan",
            period=None,
            metrics=metrics.model_dump(mode="json"),
        )

    def generate_communication_plan(
        self, category: str = "nam", period: str = "week", objective: str = "conversion",
        sales_plan: dict | None = None,
    ) -> dict:
        verified_plan = sales_plan or self.generate_sales_plan(category, period, objective)
        result = self.communication_service.generate(verified_plan, objective=objective)
        metrics = {
            item["name"]: item["value"]
            for item in verified_plan.get("verified_metrics", [])
            if item.get("status") == "AVAILABLE"
        }
        return self._ground(
            result,
            service="communication_plan",
            period=None,
            metrics=metrics,
        )
