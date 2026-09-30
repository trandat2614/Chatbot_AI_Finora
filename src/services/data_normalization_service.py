"""Backward-compatible imports for the marketplace adapter normalization service."""

from src.services.normalization.service import DataNormalizationService, NormalizationResult

__all__ = ["DataNormalizationService", "NormalizationResult"]
