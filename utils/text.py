"""Text matching helpers with no data loading or filesystem side effects."""
from __future__ import annotations

import re
import unicodedata
from typing import Any, Literal


def fold_text(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", text.replace("đ", "d").replace("Đ", "D")).strip().lower()


def normalise_timeframe(value: str) -> Literal["today", "7d", "30d"]:
    folded = fold_text(value).replace(" ", "")
    aliases = {
        "today": "today", "1d": "today", "homnay": "today", "ngay": "today",
        "7d": "7d", "7day": "7d", "7days": "7d", "7ngay": "7d", "week": "7d",
        "30d": "30d", "30day": "30d", "30days": "30d", "30ngay": "30d", "month": "30d",
    }
    if folded not in aliases:
        raise ValueError("period phải là 'today', '7d' hoặc '30d'.")
    return aliases[folded]
