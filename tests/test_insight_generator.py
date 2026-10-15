"""Validation, retry, fallback and tenant prompt isolation tests."""
from __future__ import annotations

from services.insights.generator import InsightGenerator
from services.insights.rules import InsightCandidate


class SequenceLLM:
    def __init__(self, responses: list[object]) -> None:
        self.responses = list(responses)
        self.prompts: list[str] = []

    def generate_response(self, user_message: str, **kwargs) -> str:
        self.prompts.append(user_message)
        value = self.responses.pop(0)
        if isinstance(value, Exception):
            raise value
        return str(value)


def _candidate(product: str = "tenant-a-product") -> InsightCandidate:
    return InsightCandidate(
        type="product_concentration",
        severity="warning",
        evidence={"product": product, "share_pct": 75.0, "revenue": 1000, "units": 10},
    )


def test_generator_accepts_valid_json_and_preserves_evidence() -> None:
    llm = SequenceLLM(
        [
            '{"items":[{"type":"product_concentration","title":"Tập trung sản phẩm",'
            '"summary":"Một sản phẩm đang chiếm tỷ trọng cao.",'
            '"recommendation":"Thử bán kèm một sản phẩm khác."}]}'
        ]
    )
    result = InsightGenerator(llm).generate([_candidate()])
    assert result[0].title == "Tập trung sản phẩm"
    assert result[0].evidence["share_pct"] == 75.0


def test_invalid_json_retries_once_then_falls_back() -> None:
    llm = SequenceLLM(["not-json", RuntimeError("timeout")])
    result = InsightGenerator(llm).generate([_candidate()])
    assert len(llm.prompts) == 2
    assert result[0].type == "product_concentration"
    assert result[0].title


def test_prompt_contains_only_current_tenant_candidate_data() -> None:
    llm = SequenceLLM(["broken", "broken-again"])
    InsightGenerator(llm).generate([_candidate("private-tenant-a-product")])
    assert all("private-tenant-a-product" in prompt for prompt in llm.prompts)
    assert all("private-tenant-b-product" not in prompt for prompt in llm.prompts)
