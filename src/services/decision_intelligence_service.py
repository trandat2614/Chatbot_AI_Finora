"""Facade that composes tenant-scoped deterministic decision services."""
from __future__ import annotations

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

    def orders(self) -> pd.DataFrame:
        return self.store.load_orders(self.tenant_id, self.shop_id)

    def get_business_health(self) -> dict:
        frame = self.orders()
        return self.health_service.analyze(self.metrics.calculate(frame))

    def analyze_product(self, sku: str | None = None) -> dict:
        return self.product_service.analyze(self.orders(), sku)

    def analyze_revenue_leakage(self) -> dict:
        return self.leakage_service.analyze(self.orders())

    def get_market_trends(self, category: str = "nam", period: str = "7d", limit: int = 20) -> dict:
        return self.market_service.get_trends(category, period, limit)

    def find_product_opportunities(self, category: str = "nam", period: str = "7d") -> dict:
        market = self.get_market_trends(category, period)
        return self.opportunity_service.match(self.orders(), market)

    def generate_action_plan(self, category: str = "nam", period: str = "7d") -> dict:
        frame = self.orders()
        metrics = self.metrics.calculate(frame)
        health = self.health_service.analyze(metrics)
        leakage = self.leakage_service.analyze(frame)
        products = self.product_service.analyze(frame)
        opportunities = self.opportunity_service.match(frame, self.get_market_trends(category, period))
        return self.action_service.generate(health, leakage, products, opportunities)

    def generate_sales_plan(self, category: str = "nam", period: str = "week", objective: str = "conversion") -> dict:
        frame = self.orders()
        trend_period = "7d" if period == "week" else "30d"
        opportunities = self.opportunity_service.match(frame, self.get_market_trends(category, trend_period))
        products = self.product_service.analyze(frame)
        return self.sales_service.generate(opportunities, products, period=period, objective=objective)

    def generate_communication_plan(
        self, category: str = "nam", period: str = "week", objective: str = "conversion",
        sales_plan: dict | None = None,
    ) -> dict:
        verified_plan = sales_plan or self.generate_sales_plan(category, period, objective)
        return self.communication_service.generate(verified_plan, objective=objective)
