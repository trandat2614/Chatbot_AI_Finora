"""One grounded pipeline for generate, rewrite, adapt, calendar and chat."""
from __future__ import annotations

import asyncio
import copy
import functools
import hashlib
import json
import logging
import random
import re
import time
import uuid
from datetime import datetime, timedelta, timezone

from pydantic import ValidationError

from config.settings import settings
from core.exceptions import LLMAuthenticationError, LLMClientError, LLMTimeoutError
from src.schemas.marketing import (
    CalendarEntry, MarketingItem, MarketingMetadata, MarketingResponse,
    ItemError, ModelDraft, StrategyOutput, Target, VideoScript,
)
from src.services.marketing.knowledge import MarketingKnowledge, source_metadata
from src.services.marketing.prompts import PROMPT_VERSION, SYSTEM_PROMPT
from src.services.marketing.validation import (
    OutputRejected, common_issues, confirmed_facts, string_values, validate_draft,
)
from src.security.privacy import sanitize_text

logger = logging.getLogger(__name__)
ANGLES = ("Tình huống sử dụng", "Chi tiết sản phẩm", "Giải đáp lựa chọn")


TRANSIENT_STATUS = {408, 429, 500, 502, 503, 504}


def is_transient(exc):
    """Rate limit, overload or connection drop (no status); never auth/timeout/bad request."""
    if isinstance(exc, (LLMTimeoutError, LLMAuthenticationError)):
        return False
    status = getattr(exc, "status_code", None)
    return status is None or status in TRANSIENT_STATUS


def provider_error(exc):
    """(code, message, retryable, fields) shown to BE; never echoes provider text."""
    if getattr(exc, "status_code", None) == 429:
        wait = getattr(exc, "retry_after", None)
        if not wait:
            hint = " Vui lòng thử lại sau."
        elif wait >= 3600:
            hint = f" Có thể thử lại sau khoảng {round(wait / 3600)} giờ."
        else:
            hint = f" Có thể thử lại sau khoảng {max(1, round(wait / 60))} phút."
        return ("PROVIDER_RATE_LIMITED", "Đã chạm hạn mức gọi AI của nhà cung cấp." + hint, True, [])
    return ("UPSTREAM_ERROR", "Dịch vụ AI tạm thời không khả dụng.", True, [])


def target_only(target):
    return Target(channel=target.channel, placement=target.placement, content_type=target.content_type)


@functools.lru_cache(maxsize=None)
def _draft_schema_json(content_type):
    """ModelDraft JSON schema restricted to the requested content type.

    The full discriminated union lets a model answer a caption target with a video
    script (observed live). Output is still validated against the full ModelDraft.
    """
    schema = copy.deepcopy(ModelDraft.model_json_schema())
    content = schema["properties"]["content"]
    schema["properties"]["content"] = {"$ref": content["discriminator"]["mapping"][content_type]}
    defs = schema.pop("$defs")
    refs = lambda node: re.findall(r'"\$ref": "#/\$defs/([^"]+)"', json.dumps(node))
    reachable, pending = set(), refs(schema)
    while pending:
        name = pending.pop()
        if name not in reachable:
            reachable.add(name)
            pending.extend(refs(defs[name]))
    schema["$defs"] = {name: defs[name] for name in defs if name in reachable}
    return json.dumps(schema)


def draft_schema(content_type):
    return json.loads(_draft_schema_json(content_type))


def effective_settings(payload, target):
    return {key: getattr(target, key) if getattr(target, key) is not None else getattr(payload, key)
            for key in ("duration_seconds", "production_mode", "video_style", "cta_type", "include_post_caption", "include_shot_list")}


class MarketingService:
    def __init__(self, llm_client, knowledge=None):
        self.llm = llm_client
        self.knowledge = knowledge or MarketingKnowledge()

    async def _call(self, data, schema, deadline):
        remaining = deadline - time.monotonic()
        if remaining <= .01:
            raise TimeoutError()
        timeout = min(remaining, max(.01, settings.MARKETING_CALL_TIMEOUT_SECONDS))
        def safe_data(value):
            if isinstance(value, str):
                return sanitize_text(value, block_prompt_injection=True)
            if isinstance(value, dict):
                return {key: safe_data(item) for key, item in value.items()}
            if isinstance(value, list):
                return [safe_data(item) for item in value]
            return value
        message = json.dumps({"untrusted_data": safe_data(data),
            "output_json_schema": schema}, ensure_ascii=False, default=str)
        retries = max(0, min(settings.MARKETING_PROVIDER_RETRIES, 5))
        for attempt in range(retries + 1):
            try:
                return await asyncio.wait_for(asyncio.to_thread(
                    self.llm.generate_json, system_prompt=SYSTEM_PROMPT, user_message=message,
                    timeout=timeout, max_tokens=settings.MARKETING_MAX_TOKENS), timeout=timeout)
            except LLMClientError as exc:
                # Bounded backoff for rate limit/overload only; never past the request deadline.
                if not is_transient(exc) or attempt >= retries:
                    raise
                delay = settings.MARKETING_PROVIDER_RETRY_BASE_SECONDS * (2 ** attempt) * random.uniform(.8, 1.2)
                # Honor the provider's own wait (e.g. daily quota: hours) instead of hammering it.
                delay = max(delay, getattr(exc, "retry_after", None) or 0)
                remaining = deadline - time.monotonic()
                if remaining - delay < 1:
                    raise
                logger.info("Marketing provider transient error status=%s; retry %s/%s in %.1fs",
                            getattr(exc, "status_code", None), attempt + 1, retries, delay)
                await asyncio.sleep(delay)
                timeout = min(deadline - time.monotonic(), max(.01, settings.MARKETING_CALL_TIMEOUT_SECONDS))

    async def _retrieve(self, target, context, industry, objective, tone, deadline, content_kind=None):
        try:
            return await asyncio.wait_for(asyncio.to_thread(self.knowledge.retrieve,
                target=target, context=context, industry=industry, objective=objective,
                tone=tone, query=f"{content_kind or target.placement} {target.content_type}", deadline=deadline, content_kind=content_kind),
                timeout=max(.01, deadline - time.monotonic()))
        except Exception as exc:
            # No raw query, source or credentials in logs.
            logger.warning("Marketing RAG fallback error=%s", type(exc).__name__)
            return [], ["RAG marketing không khả dụng trong thời gian cho phép."]

    def _metadata(self):
        return MarketingMetadata(prompt_version=PROMPT_VERSION,
            model=getattr(self.llm, "model", None))

    @staticmethod
    def _reference(context, operation_id, target, variant):
        value = f"{context.tenant_id}:{context.shop_id}:{context.user_id}:{operation_id}:{target.key}:{variant}"
        return "mkt_" + hashlib.sha256(value.encode()).hexdigest()[:32]

    async def generate(self, payload, context, request_id, *, operation="generate", operation_id=None, deadline=None):
        started = time.monotonic()
        deadline = deadline or started + max(.01, settings.MARKETING_TIMEOUT_SECONDS)
        response = MarketingResponse(request_id=request_id, status="failed", metadata=self._metadata())
        operation_id = operation_id or uuid.uuid4().hex
        product = payload.product
        if payload.objective == "promote_offer" and not product.offer:
            response.status = "needs_input"
            response.missing_fields = ["product.offer"]
            response.errors = [ItemError(code="OFFER_REQUIRED", message="Cần ưu đãi và điều kiện đã xác nhận.", fields=["product.offer"])]
            return response
        if product.offer and not (product.offer.starts_at <= datetime.now(timezone.utc) <= product.offer.ends_at):
            response.status = "needs_input"
            response.missing_fields = ["product.offer.starts_at", "product.offer.ends_at"]
            response.errors = [ItemError(code="OFFER_INACTIVE", message="Ưu đãi chưa có hiệu lực hoặc đã hết hạn.", fields=response.missing_fields)]
            return response
        if self.llm is None:
            response.errors = [ItemError(code="LLM_NOT_CONFIGURED", message="Dịch vụ AI chưa được cấu hình.", retryable=True)]
            return response
        response.warnings.append("Nội dung là bản nháp; shop cần kiểm tra facts và cách diễn đạt trước khi sử dụng.")
        source = getattr(payload, "source", None)
        source_changed = bool(source and (source.product_snapshot is None or source.product_snapshot != product))
        if source_changed:
            response.warnings.append("Snapshot nguồn thiếu hoặc khác hiện tại; đã yêu cầu viết theo facts hiện tại và rà soát chi tiết cũ.")
        targets = payload.selected_targets()
        retrieved = await asyncio.gather(*[
            self._retrieve(t, context, product.industry, payload.objective, payload.tone, deadline) for t in targets])
        semaphore = asyncio.Semaphore(3)

        async def slot(target, variant, docs, rag_warnings):
            reference = self._reference(context, operation_id, target, variant)
            error = None
            usage = []
            used_sources = []
            model = None
            async with semaphore:
                data = {"operation": operation, "product": product.model_dump(mode="json"),
                    "confirmed_facts": confirmed_facts(product), "target": target.model_dump(),
                    "effective_settings": effective_settings(payload, target),
                    "objective": payload.objective, "audience": payload.audience,
                    "brand": payload.brand.model_dump(), "tone": payload.tone, "length": payload.length,
                    "emoji_limit": payload.emoji_limit, "include_hashtags": payload.include_hashtags,
                    "instructions": payload.instructions, "opening_requirement": payload.opening_requirement,
                    "cta": payload.cta, "commerce_context": [c.model_dump() for c in payload.commerce_context],
                    "resources": payload.resources.model_dump() if payload.resources else None,
                    "variant": variant, "required_angle": ANGLES[variant - 1],
                    "source_content": source.model_dump(mode="json") if source else None,
                    "knowledge_untrusted_not_product_facts": [{"metadata": source_metadata(d).model_dump(),
                        "content": d.page_content} for d in docs]}
                fields = []
                for attempt in range(max(0, min(settings.MARKETING_MAX_REPAIRS, 2)) + 1):
                    if time.monotonic() >= deadline:
                        error = ("TIMEOUT", "Đã hết tổng thời gian tạo nội dung.", True, fields)
                        break
                    if attempt:
                        # Only this target+variant is repaired. Never re-send successes.
                        data["repair_fields"] = fields
                    try:
                        used_sources = [source_metadata(d) for d in docs]
                        result = await self._call(data, draft_schema(target.content_type), deadline)
                        model = result.get("model")
                        if result.get("usage") is not None:
                            usage.append({"target": target.key, "variant": variant, "attempt": attempt + 1,
                                          **result["usage"]})
                        raw = result["text"].strip()
                        if raw.startswith("```"):
                            raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
                        draft = ModelDraft.model_validate_json(raw)
                        style_warnings = validate_draft(draft, payload, target)
                        assumptions = list(draft.assumptions)
                        if target.content_type == "video_script" and payload.resources is None:
                            assumptions.append("Giả định một người quay bằng điện thoại; dùng sản phẩm và bối cảnh tối giản sẵn có.")
                        item = MarketingItem(client_reference=reference, variant=variant,
                            target=target_only(target), sku=product.sku, content=draft.content,
                            source_client_reference=source.client_reference if source else None,
                            source_version_reference=source.version_reference if source else None,
                            change_summary=("Tạo bản mới theo hướng dẫn và snapshot hiện tại; giữ nguyên tham chiếu nguồn."
                                            if source else None),
                            fact_claims=draft.fact_claims, warnings=list(dict.fromkeys(rag_warnings + draft.warnings + style_warnings)),
                            assumptions=assumptions, sources=used_sources)
                        return item, None, usage, used_sources, model
                    except (ValidationError, ValueError, OutputRejected) as exc:
                        fields = exc.fields if isinstance(exc, OutputRejected) else (
                            # Malformed JSON has an empty loc; label it instead of returning "".
                            [".".join(map(str, e["loc"])) or "json" for e in exc.errors()] if isinstance(exc, ValidationError) else ["json"])
                        # Send only structured error paths, never echo provider output as instruction.
                        error = ("OUTPUT_REJECTED", "Kết quả chưa đạt kiểm tra schema/facts/định dạng.", True, fields)
                    except (TimeoutError, LLMTimeoutError):
                        error = ("TIMEOUT", "Model quá thời gian cho phép.", True, [])
                        break
                    except Exception as exc:
                        logger.warning("Marketing provider failed request_id=%s error=%s status=%s", request_id,
                                       type(exc).__name__, getattr(exc, "status_code", None))
                        error = provider_error(exc)
                        break
            code, message, retryable, fields = error or ("TIMEOUT", "Đã hết thời gian.", True, [])
            return None, ItemError(target=target_only(target), variant=variant, client_reference=reference,
                code=code, message=message, retryable=retryable, fields=fields), usage, used_sources, model

        tasks = []
        allowed_slots = {(s.target.key, s.variant) for s in payload.retry_slots}
        for target, (docs, warnings) in zip(targets, retrieved):
            for variant in range(1, (target.variants or payload.variants) + 1):
                if allowed_slots and (target.key, variant) not in allowed_slots:
                    continue
                tasks.append(slot(target, variant, docs, warnings))
        results = await asyncio.gather(*tasks)
        sources = {}
        for item, error, usage, used, model in results:
            if item:
                # Near-identical variants are not silently passed as distinct alternatives.
                peers = [i for i in response.items if i.target.key == item.target.key]
                if any(i.content.angle.casefold() == item.content.angle.casefold() or
                       i.content.plain_text == item.content.plain_text for i in peers):
                    error = ItemError(target=item.target, variant=item.variant, client_reference=item.client_reference,
                        code="DUPLICATE_ANGLE", message="Phương án chưa khác góc tiếp cận; thử lại riêng phương án này.", retryable=True)
                else:
                    response.items.append(item)
            if error:
                response.errors.append(error)
            response.metadata.usage.extend(usage)
            if model:
                response.metadata.model = model
            sources.update({s.chunk_id: s for s in used})
        response.metadata.sources = list(sources.values())
        response.metadata.knowledge_version = self._knowledge_version(response.metadata.sources)
        response.metadata.duration_ms = round((time.monotonic() - started) * 1000, 1)
        response.status = "partial_success" if response.items and response.errors else "success" if response.items else "failed"
        logger.info("Marketing request_id=%s status=%s model=%s duration_ms=%s items=%s errors=%s",
                    request_id, response.status, response.metadata.model, response.metadata.duration_ms,
                    len(response.items), len(response.errors))
        if response.metadata.usage:
            logger.info("Marketing usage request_id=%s prompt_tokens=%s completion_tokens=%s", request_id,
                sum(u.get("prompt_tokens", 0) or 0 for u in response.metadata.usage),
                sum(u.get("completion_tokens", 0) or 0 for u in response.metadata.usage))
        return response

    @staticmethod
    def _knowledge_version(sources):
        return hashlib.sha256("|".join(sorted(s.content_hash for s in sources)).encode()).hexdigest()[:16] if sources else None

    async def calendar(self, payload, context, request_id, *, operation_id=None):
        started = time.monotonic()
        response = (await self.generate(payload, context, request_id, operation="calendar", operation_id=operation_id)
                    if payload.generate_content else MarketingResponse(request_id=request_id, status="success", metadata=self._metadata()))
        topics = ("Làm quen sản phẩm", "Chi tiết để lựa chọn", "Một tình huống sử dụng", "Giải đáp câu hỏi",
                  "Cách xem phân loại", "Nhắc lại điểm khác biệt", "Tổng hợp thông tin cần xem")
        for day in range(7):
            for target in payload.selected_targets():
                refs = [r for r in payload.references if r.target.key == target.key and r.status != "archived"]
                items = [i for i in response.items if i.target.key == target.key]
                ref = refs[day % len(refs)] if refs else None
                item = items[day % len(items)] if items and not ref else None
                video = target.content_type == "video_script"
                response.calendar.append(CalendarEntry(date=payload.start_date + timedelta(days=day),
                    timezone=payload.timezone, target=target_only(target), sku=payload.product.sku,
                    objective=payload.objective, topic=topics[day], angle=ANGLES[day % 3],
                    cta=("Xem thông tin sản phẩm trong shop." if target.channel == "shopee" else payload.cta or "Xem thông tin sản phẩm."),
                    client_reference=ref.client_reference if ref else item.client_reference if item else None,
                    draft_reference=ref.draft_reference if ref else None,
                    version_reference=ref.version_reference if ref else None,
                    status=ref.status if ref else "draft" if item else "needs_generation",
                    video_style=(target.video_style or payload.video_style) if video else None,
                    duration_seconds=(target.duration_seconds or payload.duration_seconds) if video else None,
                    preparation=["Kiểm tra facts, giá/ưu đãi và phiên bản trước khi dùng."] +
                                (["Chuẩn bị sản phẩm, điện thoại, bối cảnh và quyền dùng âm thanh."] if video else [])))
        response.warnings.append("Lịch là đề xuất 7 ngày, có thể dùng lại nội dung; BE kiểm tra quyền/reference và lưu chính thức. Không tự đăng bài.")
        response.metadata.duration_ms = round((time.monotonic() - started) * 1000, 1)
        return response

    async def strategy(self, payload, context, request_id):
        started = time.monotonic()
        deadline = started + max(.01, settings.MARKETING_TIMEOUT_SECONDS)
        response = MarketingResponse(request_id=request_id, status="failed", metadata=self._metadata())
        if self.llm is None:
            response.errors = [ItemError(code="LLM_NOT_CONFIGURED", message="Dịch vụ AI chưa được cấu hình.", retryable=True)]
            return response
        target = Target(channel="facebook", placement="feed", content_type="caption")
        docs, warnings = await self._retrieve(target, context, payload.products[0].industry, payload.objective, "friendly", deadline, content_kind="strategies")
        response.warnings = warnings + ["KPI là chỉ số đề xuất cần đo, không phải kết quả hoặc cam kết doanh thu."]
        data = {"operation": "strategy", "request": payload.model_dump(mode="json"),
                "confirmed_facts": [confirmed_facts(p) for p in payload.products],
                "knowledge_untrusted": [d.page_content for d in docs]}
        for attempt in range(max(0, min(settings.MARKETING_MAX_REPAIRS, 2)) + 1):
            try:
                response.metadata.sources = [source_metadata(d) for d in docs]
                result = await self._call(data, StrategyOutput.model_json_schema(), deadline)
                if result.get("usage") is not None:
                    response.metadata.usage.append({"attempt": attempt + 1, **result["usage"]})
                response.metadata.model = result.get("model") or response.metadata.model
                output = StrategyOutput.model_validate_json(result["text"])
                priorities = [s.priority for s in output.strategies]
                if sorted(priorities) != list(range(1, len(priorities) + 1)):
                    raise OutputRejected(["strategy_priorities"])
                if len({s.name for s in output.strategies}) != len(output.strategies):
                    raise OutputRejected(["strategy_duplicates"])
                prose = json.dumps(output.model_dump(), ensure_ascii=False)
                if any(term in prose.lower() for term in ("cam kết tăng", "chắc chắn tăng", "đã đạt", "đảm bảo doanh thu")):
                    raise OutputRejected(["unsupported_kpi_promise"])
                # Check combined facts for all products; strategy must not invent actual metrics.
                combined = payload.products[0].model_copy(deep=True)
                from src.schemas.marketing import Attribute
                for index, p in enumerate(payload.products[1:], 1):
                    combined.evidence.extend(Attribute(key=f"p{index}.{key}", value=str(value)[:300], source=p.source)
                        for key, value in confirmed_facts(p).items())
                for index, s in enumerate(output.strategies):
                    check_text = "\n".join(string_values(s.model_dump(exclude={"priority", "kpis_to_measure", "experiment", "stop_or_adjust_when"})))
                    issues = common_issues(check_text, combined)
                    if issues:
                        raise OutputRejected(issues)
                response.strategies = sorted(output.strategies, key=lambda s: s.priority)
                omitted = []
                if payload.audience is None:
                    omitted.append("Chưa có audience được xác nhận; cần kiểm tra nhóm khách trước khi chọn thông điệp.")
                if payload.budget is None:
                    omitted.append("Chưa có ngân sách; đề xuất công việc nội dung, chưa dự toán chi phí hoặc chạy ads.")
                if payload.resources is None:
                    omitted.append("Giả định nguồn lực tối giản: một người và điện thoại; shop cần xác nhận khả năng thực hiện.")
                for strategy in response.strategies:
                    strategy.assumptions = list(dict.fromkeys(list(strategy.assumptions) + omitted))
                response.warnings.extend(output.assumptions)
                response.status = "success"
                break
            except (ValidationError, OutputRejected, ValueError):
                data["repair_fields"] = ["strategies_schema_facts_and_no_promises"]
                response.errors = [ItemError(code="OUTPUT_REJECTED", message="Chiến lược chưa đạt kiểm tra cấu trúc/facts.", retryable=True)]
            except Exception as exc:
                logger.warning("Marketing strategy provider failed request_id=%s error=%s status=%s", request_id,
                               type(exc).__name__, getattr(exc, "status_code", None))
                if isinstance(exc, (TimeoutError, LLMTimeoutError)):
                    code, message = "TIMEOUT", "Chưa thể tạo chiến lược trong thời gian cho phép."
                else:
                    code, message, _, _ = provider_error(exc)
                response.errors = [ItemError(code=code, message=message, retryable=True)]
                break
        if response.status == "success":
            response.errors = []
        response.metadata.knowledge_version = self._knowledge_version(response.metadata.sources)
        response.metadata.duration_ms = round((time.monotonic() - started) * 1000, 1)
        return response
