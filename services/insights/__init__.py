"""Tenant-scoped AI business insights pipeline."""

from services.insights.data_provider import DefaultDataProvider, InsightDataProvider

__all__ = ["DefaultDataProvider", "InsightDataProvider"]
