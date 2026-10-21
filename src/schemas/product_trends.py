"""Product trend contracts matching the Node backend export (camelCase)."""
from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.schemas.base import APIModel, ResponseMeta
from utils.text import fold_text, normalise_timeframe

CATEGORIES = {
    "100534": ("dong_ho", "Đồng Hồ"),
    "100012": ("giay_dep_nam", "Giày Dép Nam"),
    "100532": ("giay_dep_nu", "Giày Dép Nữ"),
    "100009": ("phu_kien_thoi_trang", "Phụ Kiện Thời Trang"),
    "100011": ("thoi_trang_nam", "Thời Trang Nam"),
    "100017": ("thoi_trang_nu", "Thời Trang Nữ"),
    "100633": ("thoi_trang_tre_em_so_sinh", "Thời trang trẻ em & trẻ sơ sinh"),
    "100533": ("tui_vi_nam", "Túi Ví Nam"),
    "100016": ("tui_vi_nu", "Túi Ví Nữ"),
}


def category_id(value: str | None) -> str | None:
    if value is None or fold_text(value) in {"all", "tat ca"}:
        return None
    folded = fold_text(value).replace("_", " ")
    aliases = {"nam": "100011", "nu": "100017"}
    if folded in aliases:
        return aliases[folded]
    for key, (slug, label) in CATEGORIES.items():
        if str(value) == key or folded in {slug.replace("_", " "), fold_text(label)}:
            return key
    raise ValueError("Ngành hàng không thuộc 9 ngành xu hướng sản phẩm.")


class ExportModel(BaseModel):
    # Ignore backend persistence metadata (_id, createdAt, ...), never execute it.
    model_config = ConfigDict(extra="ignore", allow_inf_nan=False)


class PricePoint(ExportModel):
    date: date
    price: float = Field(ge=0)


class RankChange(ExportModel):
    type: Literal["new", "up", "down", "same", "unchanged", "stable"]
    value: int | None = None


class TrendProduct(ExportModel):
    itemId: str = Field(min_length=1, max_length=200)
    categoryId: str
    categoryName: str = ""
    title: str = Field(min_length=1, max_length=4000)
    shopId: str | None = None
    shopName: str | None = None
    price: float | None = Field(default=None, ge=0)
    salesIncrease: int | None = None
    sold30d: int | None = Field(default=None, ge=0)
    totalSold: int | None = Field(default=None, ge=0)
    commissionPct: float | None = Field(default=None, ge=0, le=100)
    discountPct: float | None = Field(default=None, ge=0, le=100)
    rating: float | None = Field(default=None, ge=0, le=5)
    rank: int | None = Field(default=None, ge=1)
    rankChange: RankChange | None = None
    productUrl: str | None = Field(default=None, max_length=2000)
    imageUrl: str | None = Field(default=None, max_length=2000)
    sourceFile: str | None = Field(default=None, max_length=1000)
    snapshotDate: date | None = None
    period: str | None = None
    priceHistory: list[PricePoint] = Field(default_factory=list, max_length=400)

    @field_validator("categoryId")
    @classmethod
    def validate_category(cls, value):
        result = category_id(value)
        if result is None:
            raise ValueError("Sản phẩm phải có ngành hàng cụ thể.")
        return result

    @field_validator("period")
    @classmethod
    def validate_period(cls, value):
        return normalise_timeframe(value) if value is not None else None


class Pagination(ExportModel):
    total: int = Field(ge=0)
    page: int = Field(default=1, ge=1)
    limit: int = Field(ge=1)
    pages: int = Field(ge=1)

    @model_validator(mode="after")
    def consistent(self):
        expected = max(1, (self.total + self.limit - 1) // self.limit)
        if self.pages != expected or self.page > self.pages:
            raise ValueError("pagination không nhất quán.")
        return self


class KPIs(ExportModel):
    salesIncreaseTotal: int | None = None
    estimatedRevenue: float | None = None
    medianPrice: float | None = Field(default=None, ge=0)
    productCount: int | None = Field(default=None, ge=0)
    avgCommissionPct: float | None = Field(default=None, ge=0, le=100)
    shopCount: int | None = Field(default=None, ge=0)


class CategoryShare(ExportModel):
    categoryId: str
    categoryName: str
    salesIncrease: int
    pct: float = Field(ge=0, le=100)

    @field_validator("categoryId")
    @classmethod
    def validate_category(cls, value):
        return TrendProduct.validate_category(value)


class PriceBucket(ExportModel):
    id: str
    label: str
    pct: float = Field(ge=0, le=100)


class RevenueProduct(ExportModel):
    itemId: str
    title: str
    categoryName: str
    price: float = Field(ge=0)
    salesIncrease: int
    estimatedRevenue: float


class TrendExportData(ExportModel):
    period: str
    date: date
    scrapedAt: datetime | None = None
    categoryId: str | None = None
    items: list[TrendProduct] = Field(max_length=20000)
    pagination: Pagination | None = None
    kpis: KPIs | None = None
    priceBuckets: list[PriceBucket] = Field(default_factory=list, max_length=20)
    categories: list[CategoryShare] = Field(default_factory=list, max_length=9)
    topRevenue: list[RevenueProduct] = Field(default_factory=list, max_length=100)

    @field_validator("period")
    @classmethod
    def validate_period(cls, value):
        return normalise_timeframe(value)

    @field_validator("categoryId")
    @classmethod
    def validate_category(cls, value):
        return category_id(value)

    @model_validator(mode="after")
    def validate_scope(self):
        for item in self.items:
            if item.snapshotDate is not None and item.snapshotDate != self.date:
                raise ValueError("snapshotDate khác ngày của snapshot.")
            if item.period is not None and item.period != self.period:
                raise ValueError("period của sản phẩm khác snapshot.")
            if self.categoryId is not None and item.categoryId != self.categoryId:
                raise ValueError("Sản phẩm nằm ngoài ngành hàng của snapshot.")
        if self.pagination:
            start = (self.pagination.page - 1) * self.pagination.limit
            expected = min(self.pagination.limit, max(0, self.pagination.total - start))
            if len(self.items) != expected:
                raise ValueError("Số items không khớp pagination.")
            if self.kpis and self.kpis.productCount is not None and self.kpis.productCount != self.pagination.total:
                raise ValueError("productCount không khớp pagination.total.")
        elif self.kpis and self.kpis.productCount is not None and self.kpis.productCount != len(self.items):
            raise ValueError("Thiếu pagination khi items chỉ là một phần danh sách.")
        identities = [(x.shopId, x.itemId) for x in self.items]
        if len(set(identities)) != len(identities):
            raise ValueError("Trùng sản phẩm trong cùng một trang.")
        return self


class TrendExport(APIModel):
    success: Literal[True] = True
    data: TrendExportData


class ProductTrendResponse(APIModel):
    success: Literal[True] = True
    data: dict
    meta: ResponseMeta
