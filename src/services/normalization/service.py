"""Marketplace adapter selection and upload parsing."""
from __future__ import annotations

import io
from dataclasses import dataclass, field

import pandas as pd

from src.schemas.commerce import UnifiedOrderItem
from src.services.normalization.base import MarketplaceAdapter
from src.services.normalization.lazada import LazadaAdapter
from src.services.normalization.shopee import ShopeeAdapter
from src.services.normalization.tiktok import TikTokShopAdapter


@dataclass
class NormalizationResult:
    frame: pd.DataFrame
    platform: str
    rejected_rows: int = 0
    warnings: list[str] = field(default_factory=list)
    total_rows: int = 0


class DataNormalizationService:
    def __init__(self, adapters: tuple[MarketplaceAdapter, ...] | None = None) -> None:
        self.adapters = adapters or (
            ShopeeAdapter(),
            TikTokShopAdapter(),
            LazadaAdapter(),
        )

    def read_upload(self, filename: str, contents: bytes) -> pd.DataFrame:
        suffix = filename.lower().rsplit(".", 1)[-1]
        if suffix == "csv":
            return pd.read_csv(io.BytesIO(contents), dtype=str, encoding="utf-8-sig")
        if suffix == "xlsx":
            sheets = pd.read_excel(io.BytesIO(contents), sheet_name=None, dtype=str)
            frames = [item for item in sheets.values() if not item.dropna(how="all").empty]
            if not frames:
                return pd.DataFrame()
            return pd.concat(frames, ignore_index=True)
        raise ValueError("Import đơn hàng chỉ hỗ trợ CSV/XLSX.")

    def detect_adapter(self, frame: pd.DataFrame) -> MarketplaceAdapter:
        if set(UnifiedOrderItem.model_fields).issubset(set(map(str, frame.columns))):
            values = frame["platform"].dropna().astype(str).unique()
            if len(values) == 1:
                for adapter in self.adapters:
                    if adapter.platform == values[0]:
                        return adapter
        ranked = sorted(
            ((adapter.detection_score(frame), adapter) for adapter in self.adapters),
            key=lambda item: item[0],
            reverse=True,
        )
        if not ranked or ranked[0][0] <= 0:
            raise ValueError("Không xác định được marketplace từ schema upload.")
        if len(ranked) > 1 and ranked[0][0] == ranked[1][0]:
            raise ValueError("Schema upload không đủ rõ để xác định marketplace.")
        return ranked[0][1]

    def detect_platform(self, frame: pd.DataFrame) -> str:
        return self.detect_adapter(frame).platform

    def normalize(
        self, frame: pd.DataFrame, platform: str | None = None
    ) -> NormalizationResult:
        if frame.empty:
            raise ValueError("File không có dữ liệu.")
        if platform:
            adapter = next(
                (item for item in self.adapters if item.platform == platform), None
            )
            if adapter is None:
                raise ValueError("Marketplace không được hỗ trợ.")
        else:
            adapter = self.detect_adapter(frame)
        normalized, rejected, warnings = adapter.normalize(frame)
        return NormalizationResult(
            frame=normalized,
            platform=adapter.platform,
            rejected_rows=rejected,
            warnings=warnings,
            total_rows=len(frame),
        )
