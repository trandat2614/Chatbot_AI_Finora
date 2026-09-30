"""Rule-based fashion attribute extraction without hallucination."""
from __future__ import annotations

import re
import unicodedata


def _fold(value: str) -> str:
    text = unicodedata.normalize("NFKD", value)
    return "".join(char for char in text if not unicodedata.combining(char)).lower()


VOCABULARY = {
    "product_type": ("ao thun", "ao so mi", "ao khoac", "quan jean", "quan kaki", "dam", "vay", "hoodie"),
    "style": ("basic", "streetwear", "vintage", "minimalist", "cong so", "the thao"),
    "fit": ("oversize", "slim fit", "regular fit", "boxy", "form rong", "ong rong", "croptop"),
    "material": ("cotton", "linen", "denim", "kaki", "voan", "lua", "ni", "len", "polyester"),
    "sleeve": ("tay ngan", "tay dai", "sat nach", "tay lo"),
    "color": ("den", "trang", "do", "xanh", "be", "nau", "hong", "tim", "xam"),
    "pattern": ("ke soc", "caro", "hoa tiet", "tron", "cham bi"),
    "season": ("he", "thu dong", "mua dong", "mua he"),
}


class FashionNLPService:
    def extract(self, product_name: str) -> dict[str, str | None]:
        folded = _fold(product_name)
        result: dict[str, str | None] = {}
        for attribute, terms in VOCABULARY.items():
            result[attribute] = next(
                (term for term in terms if re.search(rf"\b{re.escape(term)}\b", folded)), None
            )
        return result
