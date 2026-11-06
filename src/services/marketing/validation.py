"""Deterministic schema, arithmetic, reference, number and style guardrails.

These checks are deliberately conservative; semantic entailment of arbitrary
Vietnamese prose still requires shop review, recorded in every response.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from decimal import Decimal

import regex

from config.settings import settings
from src.schemas.marketing import Caption, Listing, VideoScript
from utils.text import fold_text


class OutputRejected(ValueError):
    def __init__(self, fields: list[str]):
        self.fields = fields
        super().__init__(", ".join(fields))


def confirmed_facts(product):
    facts = {"product.sku": product.sku, "product.name": product.name}
    facts.update({f"attributes.{a.key}": a.value for a in product.attributes})
    facts.update({f"evidence.{a.key}": a.value for a in product.evidence})
    if product.price is not None:
        facts["product.price"] = str(product.price)
        facts["product.currency"] = product.currency
    if product.product_url:
        facts["product.product_url"] = product.product_url
    if product.offer:
        facts.update({f"offer.{key}": str(value) for key, value in product.offer.model_dump().items() if key != "source"})
    return facts


def emoji_count(text: str) -> int:
    return sum(bool(regex.search(r"\p{Extended_Pictographic}|\p{Regional_Indicator}|\u20e3", group))
               for group in regex.findall(r"\X", text))


def render_content(content):
    if isinstance(content, Caption):
        return "\n\n".join(filter(None, [content.hook, content.body, content.cta, " ".join(content.hashtags)]))
    if isinstance(content, Listing):
        return "\n\n".join([content.title, content.short_description,
            "\n".join(f"- {h}" for h in content.highlights), content.detailed_description, content.cta])
    lines = [content.title, content.hook,
             "Thời gian — Cảnh quay — Lời thoại/voiceover — Chữ trên màn hình — Ghi chú dựng"]
    for scene in content.scenes:
        lines.append(f"{scene.start_seconds:g}–{scene.end_seconds:g}s — {scene.visual_action} — "
                     f"{scene.dialogue or scene.voiceover or ''} — {scene.on_screen_text} — {scene.editing_notes}")
    lines.extend([content.cta.text, content.post_caption or "", " ".join(content.hashtags)])
    return "\n\n".join(line for line in lines if line)


def string_values(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from string_values(v)
    elif isinstance(value, list):
        for v in value:
            yield from string_values(v)


def _numbers(text):
    # Covers spaced thousands, decimals, 199k and 1.5 triệu without equating
    # an unrelated numeric attribute with a price (money is checked separately).
    values = set()
    for match in re.finditer(r"(?<!\w)(\d+(?:[.,]\d+)*)(?:\s*(k|nghìn|ngàn|triệu))?(?![\d.,])", text, re.I):
        raw, suffix = match.groups()
        if suffix:
            raw = raw.replace(",", ".")
            try:
                values.add(Decimal(raw) * (1000000 if suffix.lower() == "triệu" else 1000))
            except Exception:
                continue
        else:
            normalized = re.sub(r"[.,](?=\d{3}(?:[.,]|$))", "", raw).replace(",", ".")
            try:
                values.add(Decimal(normalized))
            except Exception:
                continue
    return values


def common_issues(text, product, *, allowed_numbers=None):
    issues = []
    facts = confirmed_facts(product)
    source_text = "\n".join(facts.values())
    folded = fold_text(text)
    trusted = fold_text(source_text)
    # Known high-risk product claims must actually appear in confirmed input.
    groups = (
        ("cotton", "polyester", "silicone", "inox", "thep khong gi", "da that", "go soi", "vai lua", "lua to tam", "vai lanh", "go tre", "chat lieu nhom", "da bo", "vai canvas"),
        ("viet nam", "nhat ban", "han quoc", "trung quoc", "nhap khau", "xuat xu"),
        ("bao hanh", "chong nuoc", "chong tham", "khang khuan", "tri mun", "giam can", "an toan tuyet doi"),
        ("ban chay nhat", "hang nghin khach", "chi con", "sap het hang", "so 1", "tot nhat", "100%", "chinh hang"),
        ("khach hang noi", "khach hang danh gia", "minh da dung", "minh dung mot thang", "truoc va sau"),
    )
    for group in groups:
        for phrase in group:
            if re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", folded) and phrase not in trusted:
                issues.append("unsupported_claim:" + phrase)
    for match in re.findall(r"https?://[^\s<>\])]+", text):
        if match.rstrip(".,;") != product.product_url:
            issues.append("unprovided_url")
    for code in re.findall(r"\b[A-Z]{1,10}[-_]?\d+[A-Z0-9_-]*\b", text):
        if code not in source_text:
            issues.append("wrong_sku_or_code")
    for color in re.findall(r"\bmau (den|trang|do|vang|xanh|tim|hong|cam|nau|xam|kem|be)\b", folded):
        if color not in trusted:
            issues.append("unprovided_color")
    for percentage in re.findall(r"\d+(?:[.,]\d+)?\s*%", text):
        if percentage not in source_text:
            issues.append("unprovided_percentage")
    # No promotion claims without an actual, currently valid offer.
    promo = re.search(r"\b(?:giam gia|giam \d|voucher|freeship|free ship|mien phi van chuyen|tang qua|mua \d.+tang|uu dai|khuyen mai|chi hom nay|chi con hom nay)\b", folded)
    if promo:
        if not product.offer:
            issues.append("unprovided_offer")
        elif not (product.offer.starts_at <= datetime.now(timezone.utc) <= product.offer.ends_at):
            issues.append("inactive_offer")
        else:
            offer_text = fold_text(product.offer.description + " " + product.offer.conditions)
            for term in ("voucher", "freeship", "mien phi van chuyen", "tang qua"):
                if term in folded and term not in offer_text:
                    issues.append("unprovided_offer_detail:" + term)
            if fold_text(product.offer.conditions) not in folded:
                issues.append("missing_offer_conditions")
            if product.offer.ends_at.date().isoformat() not in text:
                issues.append("missing_offer_expiry")
    money = list(re.finditer(r"(?<!\w)(\d+(?:[.,]\d+)*(?:\s\d{3})*)\s*(₫|đ|vnd|usd|eur|\$|k|nghìn|ngàn|triệu)(?!\w)", text, re.I))
    for m in money:
        if product.price is None:
            issues.append("unprovided_price")
            continue
        amount = m.group(1).replace(" ", "")
        currency = m.group(2).lower()
        actual = _numbers(amount + (currency if currency in {"k", "nghìn", "ngàn", "triệu"} else ""))
        if actual != {product.price}:
            issues.append("wrong_price")
        expected = "VND" if currency in {"₫", "đ", "vnd", "k", "nghìn", "ngàn", "triệu"} else "USD" if currency in {"$", "usd"} else "EUR"
        if product.currency != expected:
            issues.append("wrong_currency")
    if product.price is None and re.search(r"\b(?:gia|chi tu)\s+\d|\b(?:tram|trieu|nghin|ngan)\s+(?:dong|vnd)\b", folded):
        issues.append("unprovided_price")
    permissible = _numbers(source_text) | (allowed_numbers or set())
    if _numbers(text) - permissible:
        issues.append("unprovided_numbers")
    if re.search(r"\b(?:AIDA|PAS|FAB)\b|system prompt|api[_ -]?key|chain.of.thought|điểm tự chấm|\[REDACTED_|\[BLOCKED_UNTRUSTED", text, re.I):
        issues.append("internal_analysis_or_secret")
    for secret in (settings.FINORA_SERVICE_KEY, settings.WEB_TOKEN_SECRET, settings.active_api_key()):
        if secret and len(secret) >= 16 and secret in text:
            issues.append("secret_in_output")
    if "!!" in text or "[điền" in text.lower() or "[giá" in text.lower():
        issues.append("style_or_placeholder")
    if any(0x1D400 <= ord(c) <= 0x1D7FF for c in text):
        issues.append("decorative_unicode")
    letters = [c for c in text if c.isalpha()]
    if len(letters) > 40 and sum(c.isupper() for c in letters) / len(letters) > .85:
        issues.append("all_caps")
    for term in ("siêu phẩm", "bùng nổ", "đỉnh của chóp", "chốt đơn ngay kẻo lỡ"):
        if term in text.lower():
            issues.append("cliche:" + term)
    return issues


def validate_draft(draft, payload, target):
    content = draft.content
    issues = []
    warnings = []
    if content.content_type != target.content_type:
        raise OutputRejected(["content_type"])
    facts = confirmed_facts(payload.product)
    # Do not trust a model-provided plain_text or allow it to smuggle extra copy.
    content.plain_text = ""
    semantic = content.model_dump(exclude={"plain_text"})
    if isinstance(content, VideoScript):
        semantic.pop("total_duration_seconds")
        semantic.pop("production_mode")
        semantic.pop("video_style")
        # Technical production directions may mention 9:16 etc.; validate the
        # actual product copy/visual actions separately from these suggestions.
        semantic.pop("production")
        for scene in semantic["scenes"]:
            for key in ("scene_id", "shot_type", "camera_direction", "audio_direction", "editing_notes"):
                scene.pop(key)
    prose = "\n".join(string_values(semantic))
    issues.extend(common_issues(prose, payload.product))
    for claim in draft.fact_claims:
        if claim.text not in prose or any(ref not in facts for ref in claim.fact_refs):
            issues.append("invalid_fact_reference")
        elif _numbers(claim.text) - _numbers(" ".join(facts[ref] for ref in claim.fact_refs)):
            issues.append("claim_number_without_evidence")
    if not draft.fact_claims:
        issues.append("missing_fact_claims")
    if any(term.lower() in prose.lower() for term in payload.brand.avoid_terms):
        issues.append("brand_avoid_terms")
    hashtags = getattr(content, "hashtags", [])
    if not payload.include_hashtags and (hashtags or re.search(r"(?<!\w)#[\w]+", prose)):
        issues.append("hashtags_disabled")
    if isinstance(content, Listing):
        if len(content.title) > settings.MARKETING_SHOPEE_TITLE_CHARS:
            issues.append("listing_title_length")
        if emoji_count(content.title) or "#" in content.title or re.search(r"\b(?:giam gia|mien phi|ban chay|san pham hot|voucher|freeship)\b", fold_text(content.title)):
            issues.append("listing_title_promotion")
        if re.search(r"\d\s*(?:k|₫|đ|vnd|usd|eur|\$)(?!\w)|\bgia\b", fold_text(content.title)):
            issues.append("listing_title_price")
        from collections import Counter
        title_words = [w for w in fold_text(content.title).split() if len(w) > 2]
        if any(count > 3 for count in Counter(title_words).values()):
            issues.append("listing_title_keyword_stuffing")
        for attr in content.attributes:
            if attr.fact_ref not in facts or attr.value != facts[attr.fact_ref]:
                issues.append("listing_attribute_source")
    if isinstance(content, VideoScript):
        duration = target.duration_seconds or payload.duration_seconds
        mode = target.production_mode or payload.production_mode
        if content.total_duration_seconds != duration or content.production_mode != mode:
            issues.append("video_duration_or_mode")
        if content.objective != payload.objective or content.audience != payload.audience:
            issues.append("video_objective_or_audience")
        if content.video_style != (target.video_style or payload.video_style):
            issues.append("video_style")
        cursor = 0.0
        if len({s.scene_id for s in content.scenes}) != len(content.scenes):
            issues.append("duplicate_scene_id")
        people = payload.resources.people if payload.resources else 1
        for scene in content.scenes:
            if abs(scene.start_seconds - cursor) > .001 or abs(scene.end_seconds - scene.start_seconds - scene.duration_seconds) > .001:
                issues.append("scene_timeline")
            cursor = scene.end_seconds
            if mode == "text_only" and (scene.dialogue or scene.voiceover):
                issues.append("text_only_speech")
            if mode in {"hands_only", "voiceover"} and (scene.dialogue or scene.shows_face):
                issues.append("faceless_mode")
            if scene.dialogue and scene.voiceover:
                issues.append("duplicate_speech")
            if mode != "on_camera" and re.search(r"(?:nhìn|nói).{0,15}(?:camera|máy quay)|cận mặt|lộ mặt", scene.visual_action, re.I):
                issues.append("faceless_visual_action")
            if len((scene.dialogue or scene.voiceover or "").split()) > scene.duration_seconds * settings.MARKETING_SPEECH_UNITS_PER_SECOND * .8:
                issues.append("speech_too_long")
            if scene.people_required > people:
                issues.append("people_budget")
        if abs(cursor - duration) > .001:
            issues.append("video_total_timeline")
        commerce = next((c for c in payload.commerce_context if c.channel == target.channel), None)
        if content.cta.action == "attached_product" and (not commerce or commerce.product_attachment != "confirmed"):
            issues.append("unconfirmed_product_attachment")
        if content.cta.action == "message" and (not commerce or not commerce.messaging_supported):
            issues.append("unconfirmed_messaging")
        if not (target.include_post_caption if target.include_post_caption is not None else payload.include_post_caption) and content.post_caption:
            issues.append("post_caption_disabled")
        want_production = target.include_shot_list if target.include_shot_list is not None else payload.include_shot_list
        if bool(content.production) != want_production:
            issues.append("production_details_selection")
        if content.production and content.production.actors > people:
            issues.append("production_people_budget")
        if not commerce or commerce.product_attachment == "unknown":
            warnings.append("Chưa xác nhận khả năng gắn sản phẩm; shop kiểm tra CTA trước khi dùng.")
    if target.channel == "shopee":
        if re.search(r"\b(?:zalo|facebook|website|nhan tin ngoai san|chuyen khoan)\b", fold_text(prose)):
            issues.append("shopee_off_platform_cta")
        from urllib.parse import urlsplit
        for url in re.findall(r"https?://[^\s<>]+", prose):
            host = urlsplit(url).hostname or ""
            if host != "shopee.vn" and not host.endswith(".shopee.vn"):
                issues.append("shopee_external_url")
    commerce = next((c for c in payload.commerce_context if c.channel == target.channel), None)
    if re.search(r"bam gio hang|san pham (?:da |duoc )?gan|link san pham gan", fold_text(prose)):
        if not commerce or commerce.product_attachment != "confirmed":
            issues.append("attachment_claim_without_confirmation")
    content.plain_text = render_content(content)
    if emoji_count(content.plain_text) > payload.emoji_limit:
        issues.append("emoji_limit")
    if isinstance(content, Caption):
        maximum = settings.MARKETING_FACEBOOK_SHORT_UNITS if payload.length == "short" else settings.MARKETING_FACEBOOK_STANDARD_UNITS
        if len(content.plain_text.split()) > maximum:
            warnings.append("Bài dài hơn mục tiêu biên tập Finora; cân nhắc rút gọn.")
    if issues:
        raise OutputRejected(sorted(set(issues)))
    return warnings
