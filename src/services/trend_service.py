"""Load, normalise, persist, and query Shopee fashion trend exports."""
from __future__ import annotations

import logging
import math
import re
import sqlite3
import unicodedata
import hashlib
from datetime import datetime, timezone
from collections import Counter
from pathlib import Path
from typing import Any, Literal

import pandas as pd
from pandas.errors import EmptyDataError, ParserError

from config.settings import settings

logger = logging.getLogger(__name__)

Gender = Literal["nam", "nu"]
Timeframe = Literal["today", "7d", "30d"]

PRODUCT_COLUMN = "Sản phẩm"
PRICE_COLUMN = "Giá"
SALES_GROWTH_COLUMN = "Lượt bán tăng"
SOLD_30D_COLUMN = "Đã bán 30 ngày"
COMMISSION_COLUMN = "Hoa hồng %"
MALL_COLUMN = "Shop Mall"

EXPECTED_COLUMNS = (
    "Hạng",
    PRODUCT_COLUMN,
    "Shop",
    MALL_COLUMN,
    "Ngành",
    SALES_GROWTH_COLUMN,
    PRICE_COLUMN,
    SOLD_30D_COLUMN,
    COMMISSION_COLUMN,
    "Đánh giá",
    "Link",
)

_INTEGER_COLUMNS = (PRICE_COLUMN, SALES_GROWTH_COLUMN, SOLD_30D_COLUMN)
_TOKEN_RE = re.compile(r"[0-9a-zA-ZÀ-ỹ]+", flags=re.UNICODE)
_STOPWORDS = {
    "ao", "quan", "nam", "nu", "cho", "va", "voi", "cua", "co", "the", "san",
    "pham", "hang", "mau", "moi", "cao", "cap", "dep", "thoi", "trang", "mac",
    "phong", "cach", "chinh", "hang", "sale", "voucher", "deal", "size", "free",
}

_DOMAIN_KEYWORDS: tuple[tuple[str, str, str], ...] = (
    ("cotton 250gsm", r"cotton\s*250\s*gsm|250\s*gsm\s*cotton", "material"),
    ("nỉ 2 lớp", r"ni\s*2\s*lop|ni\s*hai\s*lop", "material"),
    ("su lạnh", r"su\s*lanh", "material"),
    ("ống rộng", r"ong\s*rong", "fit"),
    ("form rộng", r"form\s*rong", "fit"),
    ("form suông", r"form\s*suong|dang\s*suong", "fit"),
    ("boxy", r"\bboxy\b", "fit"),
    ("raglan", r"\braglan\b", "fit"),
    ("oversize", r"\boversi(?:ze|zed)\b", "fit"),
    ("croptop", r"\bcrop\s*top\b|\bcroptop\b", "fit"),
    ("slim fit", r"\bslim\s*fit\b", "fit"),
    ("cotton", r"\bcotton\b", "material"),
    ("kaki", r"\bkaki\b", "material"),
    ("denim", r"\bdenim\b|\bjean\b", "material"),
    ("voan", r"\bvoan\b", "material"),
    ("đũi", r"\bdui\b", "material"),
    ("linen", r"\blinen\b", "material"),
    ("lụa", r"\blua\b", "material"),
    ("len", r"\blen\b", "material"),
    ("nỉ", r"\bni\b", "material"),
)


def fold_text(value: Any) -> str:
    """Return lowercase, accent-free text suitable for matching."""
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", text.replace("đ", "d").replace("Đ", "D")).strip().lower()


def normalise_gender(value: str) -> Gender:
    """Normalise a category/gender label to ``nam`` or ``nu``."""
    folded = fold_text(value)
    if folded in {"nu", "female", "women", "woman", "thoi trang nu", "ttnu"} or " nu" in f" {folded}":
        return "nu"
    if folded in {"nam", "male", "men", "man", "thoi trang nam", "ttn"} or " nam" in f" {folded}":
        return "nam"
    raise ValueError("category/gender phải là 'nam', 'nu', 'thời trang nam' hoặc 'thời trang nữ'.")


def normalise_timeframe(value: str) -> Timeframe:
    """Normalise a timeframe alias to ``today``, ``7d``, or ``30d``."""
    folded = fold_text(value).replace(" ", "")
    aliases: dict[str, Timeframe] = {
        "today": "today", "1d": "today", "homnay": "today", "ngay": "today",
        "7d": "7d", "7day": "7d", "7days": "7d", "7ngay": "7d", "week": "7d",
        "30d": "30d", "30day": "30d", "30days": "30d", "30ngay": "30d", "month": "30d",
    }
    if folded not in aliases:
        raise ValueError("timeframe phải là 'today', '7d' hoặc '30d'.")
    return aliases[folded]


def _parse_number(value: Any, *, integer: bool) -> float | int | None:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    text = fold_text(value).replace("₫", "").replace("%", "").replace(" ", "")
    if not text or text in {"nan", "none", "-", "n/a", "na"}:
        return None

    multiplier = 1.0
    if text.endswith("k") or text.endswith("nghin"):
        multiplier, text = 1_000.0, re.sub(r"(?:k|nghin)$", "", text)
    elif text.endswith("tr") or text.endswith("trieu") or text.endswith("m"):
        multiplier, text = 1_000_000.0, re.sub(r"(?:tr|trieu|m)$", "", text)

    text = re.sub(r"[^0-9,.-]", "", text)
    if not text or text in {"-", ".", ","}:
        return None

    if integer:
        sign = -1 if text.startswith("-") else 1
        unsigned = text.lstrip("-")
        separators = unsigned.count(".") + unsigned.count(",")
        groups = re.split(r"[.,]", unsigned)
        looks_like_thousands = separators > 0 and all(len(group) == 3 for group in groups[1:])
        if multiplier != 1.0 or (separators == 1 and not looks_like_thousands):
            numeric = unsigned.replace(",", ".")
        else:
            numeric = re.sub(r"[.,]", "", unsigned)
        try:
            return int(round(sign * float(numeric) * multiplier))
        except ValueError:
            return None

    if "," in text and "." in text:
        decimal_separator = "," if text.rfind(",") > text.rfind(".") else "."
        thousands_separator = "." if decimal_separator == "," else ","
        text = text.replace(thousands_separator, "").replace(decimal_separator, ".")
    elif "," in text:
        text = text.replace(",", ".")
    try:
        return float(text) * multiplier
    except ValueError:
        return None


class TrendDataLoader:
    """Load Shopee trend CSVs into a query-ready DataFrame and SQLite table.

    CSV files are read as UTF-8 with optional BOM. Invalid rows are skipped by
    pandas, malformed numeric cells become zero, and a warning is recorded in
    :attr:`warnings`. Calling :meth:`load` replaces the SQLite table atomically
    within a transaction and creates indexes for the common filters.
    """

    def __init__(
        self,
        data_dir: str | Path | None = None,
        database_path: str | Path | None = None,
        *,
        auto_load: bool = True,
    ) -> None:
        project_root = Path(__file__).resolve().parents[2]
        self.data_dir = Path(data_dir) if data_dir else project_root / "data" / "trends"
        self.database_path = (
            Path(database_path) if database_path else self.data_dir / "shopee_trends.sqlite3"
        )
        self._data = pd.DataFrame()
        self.warnings: list[str] = []
        self.loaded_files: list[Path] = []
        if auto_load:
            self.load()

    @property
    def data(self) -> pd.DataFrame:
        """Return a defensive copy of all normalised records."""
        return self._data.copy()

    def scan_csv_files(self) -> list[Path]:
        """Return all CSV files in the configured trend directory."""
        if not self.data_dir.exists():
            return []
        return sorted(path for path in self.data_dir.glob("*.csv") if path.is_file())

    def load(self, *, persist: bool = True) -> pd.DataFrame:
        """Read every CSV, normalise records, and optionally refresh SQLite."""
        self.warnings = []
        self.loaded_files = []
        frames: list[pd.DataFrame] = []
        for path in self.scan_csv_files():
            frame = self._read_csv(path)
            if frame is not None and not frame.empty:
                frames.append(frame)
                self.loaded_files.append(path)

        self._data = pd.concat(frames, ignore_index=True) if frames else self._empty_frame()
        if persist:
            self._persist_sqlite()
        return self.data

    def _read_csv(self, path: Path) -> pd.DataFrame | None:
        try:
            frame = pd.read_csv(
                path,
                encoding="utf-8-sig",
                dtype=str,
                keep_default_na=False,
                on_bad_lines="skip",
            )
        except UnicodeDecodeError:
            try:
                frame = pd.read_csv(
                    path,
                    encoding="utf-8",
                    dtype=str,
                    keep_default_na=False,
                    on_bad_lines="skip",
                )
            except (UnicodeDecodeError, EmptyDataError, ParserError) as exc:
                self.warnings.append(f"Không đọc được {path.name}: {exc}")
                return None
        except (EmptyDataError, ParserError, OSError) as exc:
            self.warnings.append(f"Không đọc được {path.name}: {exc}")
            return None

        frame.columns = [str(column).lstrip("\ufeff").strip() for column in frame.columns]
        if PRODUCT_COLUMN not in frame.columns:
            self.warnings.append(f"Bỏ qua {path.name}: thiếu cột '{PRODUCT_COLUMN}'.")
            return None

        for column in EXPECTED_COLUMNS:
            if column not in frame.columns:
                frame[column] = ""
                self.warnings.append(f"{path.name}: thiếu cột '{column}', đã dùng giá trị mặc định.")

        frame = frame.loc[:, list(EXPECTED_COLUMNS)].copy()
        frame = frame[frame[PRODUCT_COLUMN].astype(str).str.strip().ne("")].copy()
        for column in _INTEGER_COLUMNS:
            parsed = frame[column].map(lambda value: _parse_number(value, integer=True))
            invalid_count = int(parsed.isna().sum() - frame[column].astype(str).str.strip().eq("").sum())
            if invalid_count > 0:
                self.warnings.append(f"{path.name}: {invalid_count} giá trị sai ở cột '{column}' đã đặt thành 0.")
            frame[column] = parsed.fillna(0).astype("int64")

        commission = frame[COMMISSION_COLUMN].map(lambda value: _parse_number(value, integer=False))
        invalid_commission = int(
            commission.isna().sum() - frame[COMMISSION_COLUMN].astype(str).str.strip().eq("").sum()
        )
        if invalid_commission > 0:
            self.warnings.append(
                f"{path.name}: {invalid_commission} giá trị sai ở cột '{COMMISSION_COLUMN}' đã đặt thành 0."
            )
        frame[COMMISSION_COLUMN] = commission.fillna(0.0).astype(float)
        frame[MALL_COLUMN] = frame[MALL_COLUMN].map(
            lambda value: fold_text(value) in {"co", "yes", "true", "1"}
        ).astype(bool)

        try:
            gender, timeframe = self._metadata_from_filename(path.name)
        except ValueError as exc:
            self.warnings.append(str(exc))
            return None
        frame["gender"] = gender
        frame["timeframe"] = timeframe
        capture_date = self._capture_date(path)
        frame["capture_date"] = capture_date
        frame["source_file"] = path.name
        frame["source_row"] = range(2, len(frame) + 2)
        frame["snapshot_id"] = [
            hashlib.sha256(f"{path.name}:{capture_date}:{row}".encode()).hexdigest()
            for row in frame["source_row"]
        ]
        return frame

    def _capture_date(self, path: Path) -> str:
        match = re.search(r"(?<!\d)(\d{1,2})-(\d{1,2})(?:-(\d{2,4}))?(?!\d)", path.stem)
        modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        explicit_import_date = None
        if settings.TREND_IMPORT_DATE:
            try:
                explicit_import_date = datetime.fromisoformat(
                    settings.TREND_IMPORT_DATE
                ).date()
            except ValueError:
                self.warnings.append(
                    "TREND_IMPORT_DATE không hợp lệ; yêu cầu định dạng YYYY-MM-DD."
                )
        if not match:
            if explicit_import_date is not None:
                return explicit_import_date.isoformat()
            self.warnings.append(
                f"{path.name}: không có capture date; tạm dùng file mtime và cần import lại với TREND_IMPORT_DATE."
            )
            return modified.date().isoformat()
        day, month = int(match.group(1)), int(match.group(2))
        if match.group(3):
            year = int(match.group(3))
        elif explicit_import_date is not None:
            year = explicit_import_date.year
        else:
            year = modified.year
            self.warnings.append(
                f"{path.name}: filename thiếu năm; dùng năm từ file mtime. "
                "Đặt TREND_IMPORT_DATE khi import chính thức."
            )
        year = year + 2000 if year < 100 else year
        try:
            return datetime(year, month, day, tzinfo=timezone.utc).date().isoformat()
        except ValueError:
            return modified.date().isoformat()

    @staticmethod
    def _metadata_from_filename(filename: str) -> tuple[Gender, Timeframe]:
        folded = fold_text(Path(filename).stem)
        if "ttnu" in folded or "thoi trang nu" in folded:
            gender: Gender = "nu"
        elif re.search(r"(?:^|\s)ttn(?:\s|$)", folded) or "thoi trang nam" in folded:
            gender = "nam"
        else:
            raise ValueError(f"Không xác định được gender từ tên file: {filename}")

        if re.search(r"30\s*days?|30\s*ngay", folded):
            timeframe: Timeframe = "30d"
        elif re.search(r"7\s*days?|7\s*ngay", folded):
            timeframe = "7d"
        else:
            timeframe = "today"
        return gender, timeframe

    @staticmethod
    def _empty_frame() -> pd.DataFrame:
        columns = [*EXPECTED_COLUMNS, "gender", "timeframe", "capture_date", "source_file", "source_row", "snapshot_id"]
        return pd.DataFrame(columns=columns)

    def _persist_sqlite(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.database_path) as connection:
            connection.execute("BEGIN")
            exists = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='trends'"
            ).fetchone()
            if not exists:
                self._data.to_sql("trends", connection, if_exists="append", index=False)
            else:
                existing_columns = {
                    row[1] for row in connection.execute("PRAGMA table_info(trends)").fetchall()
                }
                if "capture_date" not in existing_columns:
                    connection.execute('ALTER TABLE trends ADD COLUMN "capture_date" TEXT')
                if "snapshot_id" not in existing_columns:
                    connection.execute('ALTER TABLE trends ADD COLUMN "snapshot_id" TEXT')
                # Legacy rows had no immutable snapshot identity and are the same
                # generated cache that is being re-imported below.
                connection.execute("DELETE FROM trends WHERE snapshot_id IS NULL")

                # A filename is part of snapshot_id. When an operator renames a
                # source file, deleting by snapshot_id alone leaves the same
                # capture duplicated under its old name. Replace every capture
                # date present in this import, while retaining genuinely older
                # capture dates for historical queries.
                capture_dates = sorted(
                    {
                        str(value)
                        for value in self._data["capture_date"].dropna().tolist()
                        if str(value).strip()
                    }
                )
                connection.executemany(
                    "DELETE FROM trends WHERE capture_date = ?",
                    [(value,) for value in capture_dates],
                )
                self._data.to_sql("trends", connection, if_exists="append", index=False)
            connection.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_trends_snapshot ON trends(snapshot_id)"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_trends_gender_timeframe ON trends(gender, timeframe)"
            )
            connection.execute(
                f'CREATE INDEX IF NOT EXISTS idx_trends_growth ON trends("{SALES_GROWTH_COLUMN}")'
            )
            connection.commit()

    def select_history(self, gender: str, timeframe: str) -> pd.DataFrame:
        """Read all retained snapshots using a parameterized query."""
        selected_gender = normalise_gender(gender)
        selected_timeframe = normalise_timeframe(timeframe)
        if not self.database_path.exists():
            return self._empty_frame()
        with sqlite3.connect(self.database_path) as connection:
            return pd.read_sql_query(
                "SELECT * FROM trends WHERE gender = ? AND timeframe = ? ORDER BY capture_date, source_row",
                connection,
                params=(selected_gender, selected_timeframe),
            )

    def select(self, gender: str, timeframe: str) -> pd.DataFrame:
        """Return records matching a normalised gender and timeframe."""
        selected_gender = normalise_gender(gender)
        selected_timeframe = normalise_timeframe(timeframe)
        if self._data.empty:
            return self._data.copy()
        mask = (self._data["gender"] == selected_gender) & (
            self._data["timeframe"] == selected_timeframe
        )
        return self._data.loc[mask].copy()

    def query_top_keywords(
        self,
        gender: str,
        timeframe: str,
        top_k: int = 10,
    ) -> list[dict[str, Any]]:
        """Extract common fit/material phrases using domain patterns and n-grams."""
        if top_k < 1:
            raise ValueError("top_k phải lớn hơn hoặc bằng 1.")
        frame = self.select(gender, timeframe)
        if frame.empty:
            return []

        names = frame[PRODUCT_COLUMN].astype(str).tolist()
        growth = frame[SALES_GROWTH_COLUMN].clip(lower=0).astype(int).tolist()
        matches: dict[str, dict[str, Any]] = {}
        for display, pattern, keyword_type in _DOMAIN_KEYWORDS:
            indexes = [index for index, name in enumerate(names) if re.search(pattern, fold_text(name))]
            if indexes:
                matches[display] = {
                    "keyword": display,
                    "type": keyword_type,
                    "occurrences": len(indexes),
                    "growth_score": int(sum(growth[index] for index in indexes)),
                }

        ranked = sorted(
            matches.values(),
            key=lambda item: (item["growth_score"], item["occurrences"], item["keyword"]),
            reverse=True,
        )
        if len(ranked) >= top_k:
            return ranked[:top_k]

        ngrams: Counter[str] = Counter()
        ngram_growth: Counter[str] = Counter()
        for name, row_growth in zip(names, growth):
            tokens = [
                token for token in _TOKEN_RE.findall(fold_text(name))
                if len(token) > 1 and token not in _STOPWORDS and not token.isdigit()
            ]
            unique_phrases = {
                " ".join(tokens[start : start + size])
                for size in (2, 3)
                for start in range(0, len(tokens) - size + 1)
            }
            for phrase in unique_phrases:
                ngrams[phrase] += 1
                ngram_growth[phrase] += row_growth

        existing = {item["keyword"] for item in ranked}
        for phrase, occurrences in sorted(
            ngrams.items(),
            key=lambda item: (ngram_growth[item[0]], item[1], item[0]),
            reverse=True,
        ):
            if occurrences < 2 or phrase in existing:
                continue
            ranked.append(
                {
                    "keyword": phrase,
                    "type": "ngram",
                    "occurrences": int(occurrences),
                    "growth_score": int(ngram_growth[phrase]),
                }
            )
            if len(ranked) >= top_k:
                break
        return ranked[:top_k]

    def get_category_metrics(self, gender: str, timeframe: str) -> dict[str, Any]:
        """Return median price, growth-weighted price sweet spot, and commission."""
        frame = self.select(gender, timeframe)
        if frame.empty:
            return {
                "gender": normalise_gender(gender),
                "timeframe": normalise_timeframe(timeframe),
                "record_count": 0,
                "median_price": None,
                "sweet_spot": None,
                "average_affiliate_rate": None,
            }

        prices = frame.loc[frame[PRICE_COLUMN] > 0, PRICE_COLUMN].astype(float)
        commission = frame[COMMISSION_COLUMN].astype(float)
        sweet_spot: dict[str, Any] | None = None
        if not prices.empty:
            priced_frame = frame.loc[prices.index]
            weights = priced_frame[SALES_GROWTH_COLUMN].clip(lower=0).astype(float)
            if float(weights.sum()) <= 0:
                weights = priced_frame[SOLD_30D_COLUMN].clip(lower=0).astype(float)
            if float(weights.sum()) <= 0:
                weights = pd.Series(1.0, index=priced_frame.index)
            low = self._weighted_quantile(prices, weights, 0.25)
            high = self._weighted_quantile(prices, weights, 0.75)
            sweet_spot = {
                "min": int(round(low)),
                "max": int(round(high)),
                "method": "Khoảng phân vị 25%-75% theo trọng số lượt bán tăng",
            }

        return {
            "gender": normalise_gender(gender),
            "timeframe": normalise_timeframe(timeframe),
            "record_count": int(len(frame)),
            "median_price": int(round(float(prices.median()))) if not prices.empty else None,
            "sweet_spot": sweet_spot,
            "average_affiliate_rate": round(float(commission.mean()), 2) if not commission.empty else None,
        }

    @staticmethod
    def _weighted_quantile(values: pd.Series, weights: pd.Series, quantile: float) -> float:
        ordered = pd.DataFrame({"value": values, "weight": weights}).sort_values("value")
        cumulative = ordered["weight"].cumsum()
        cutoff = float(ordered["weight"].sum()) * quantile
        matches = ordered.loc[cumulative >= cutoff, "value"]
        return float(matches.iloc[0] if not matches.empty else ordered["value"].iloc[-1])

    def get_top_products(
        self,
        gender: str,
        timeframe: str,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Return top products ranked by sales growth, then 30-day sales."""
        if limit < 1:
            raise ValueError("limit phải lớn hơn hoặc bằng 1.")
        frame = self.select(gender, timeframe).sort_values(
            [SALES_GROWTH_COLUMN, SOLD_30D_COLUMN], ascending=[False, False]
        )
        products: list[dict[str, Any]] = []
        for _, row in frame.head(limit).iterrows():
            products.append(
                {
                    "product_name": str(row[PRODUCT_COLUMN]),
                    "shop": str(row["Shop"]),
                    "is_mall": bool(row[MALL_COLUMN]),
                    "sales_growth": int(row[SALES_GROWTH_COLUMN]),
                    "price": int(row[PRICE_COLUMN]),
                    "sold_30d": int(row[SOLD_30D_COLUMN]),
                    "affiliate_rate": float(row[COMMISSION_COLUMN]),
                    "link": str(row["Link"]),
                }
            )
        return products
