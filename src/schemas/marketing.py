"""Internal BE → AI contracts. Identity comes exclusively from the signed JWT."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import ConfigDict, Field, StringConstraints, field_validator, model_validator

from config.settings import settings
from src.schemas.base import APIModel, ResponseMeta

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=4000)]
Short = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=300)]
Identifier = Annotated[str, StringConstraints(pattern=r"^[\w.:-]{1,120}$")]
Channel = Literal["facebook", "tiktok", "shopee"]
Objective = Literal["introduce_product", "drive_sales", "promote_offer", "answer_questions"]
ProductionMode = Literal["on_camera", "hands_only", "voiceover", "text_only"]
VideoStyle = Literal["product_demo", "tutorial", "unboxing", "faq", "objection_handling", "scenario", "presenter", "ugc_style"]

VALID_TARGETS = (
    ("facebook", "feed", "caption"),
    ("tiktok", "short_video", "video_script"),
    ("shopee", "product_listing", "listing"),
    ("facebook", "reels", "video_script"),
    ("shopee", "video", "video_script"),
)
LEGACY_TARGETS = {row[0]: row for row in VALID_TARGETS[:3]}


class Target(APIModel):
    model_config = ConfigDict(extra="forbid", json_schema_extra={"oneOf": [
        {"properties": {"channel": {"const": c}, "placement": {"const": p}, "content_type": {"const": t}}}
        for c, p, t in VALID_TARGETS]})
    channel: Channel
    placement: Literal["feed", "short_video", "product_listing", "reels", "video"]
    content_type: Literal["caption", "listing", "video_script"]

    @model_validator(mode="after")
    def valid_combination(self):
        if self.key not in VALID_TARGETS:
            raise ValueError("Tổ hợp channel/placement/content_type không được hỗ trợ.")
        return self

    @property
    def key(self) -> tuple[str, str, str]:
        return self.channel, self.placement, self.content_type


class ContentTarget(Target):
    variants: int | None = Field(default=None, ge=1, le=3)
    duration_seconds: Literal[15, 30, 60] | None = None
    production_mode: ProductionMode | None = None
    video_style: VideoStyle | None = None
    cta_type: Literal["view_product", "message", "comment", "choose_variant", "attached_product"] | None = None
    include_post_caption: bool | None = None
    include_shot_list: bool | None = None


class Attribute(APIModel):
    key: Identifier
    value: Short
    source: Short


class Offer(APIModel):
    description: Text
    conditions: Text
    starts_at: datetime
    ends_at: datetime
    source: Short

    @model_validator(mode="after")
    def valid_period(self):
        if self.starts_at.tzinfo is None or self.ends_at.tzinfo is None:
            raise ValueError("Ưu đãi cần thời gian có timezone.")
        if self.ends_at <= self.starts_at:
            raise ValueError("ends_at phải sau starts_at.")
        return self


class ProductSnapshot(APIModel):
    sku: Short
    name: Short
    source: Short
    updated_at: datetime
    industry: Short = "general"
    attributes: list[Attribute] = Field(default_factory=list, max_length=30)
    price: Decimal | None = Field(default=None, ge=0, max_digits=15, decimal_places=2)
    currency: Annotated[str, StringConstraints(pattern=r"^[A-Z]{3}$")] = "VND"
    product_url: Annotated[str, StringConstraints(max_length=1000)] | None = None
    offer: Offer | None = None
    # Sales/stock/reviews are supplied by BE as confirmed, sourced evidence.
    evidence: list[Attribute] = Field(default_factory=list, max_length=15)

    @field_validator("product_url")
    @classmethod
    def valid_url(cls, value):
        if value is not None:
            from urllib.parse import urlsplit
            parsed = urlsplit(value)
            if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
                raise ValueError("product_url phải là URL http(s), không chứa credentials.")
        return value

    @field_validator("updated_at")
    @classmethod
    def timezone_required(cls, value):
        if value.tzinfo is None:
            raise ValueError("updated_at cần timezone.")
        return value

    @model_validator(mode="after")
    def unique_keys(self):
        for entries in (self.attributes, self.evidence):
            if len({a.key for a in entries}) != len(entries):
                raise ValueError("Fact key bị trùng.")
        return self


class BrandProfile(APIModel):
    name: Short = "Shop"
    voice: Short = "thân thiện, tự nhiên, rõ ý"
    address_as: Short = "bạn"
    avoid_terms: list[Short] = Field(default_factory=list, max_length=30)


class Resources(APIModel):
    people: int = Field(default=1, ge=1, le=10)
    locations: list[Short] = Field(default_factory=list, max_length=10)
    props: list[Short] = Field(default_factory=list, max_length=20)
    supplied_assets: list[Short] = Field(default_factory=list, max_length=20)
    equipment: list[Short] = Field(default_factory=lambda: ["điện thoại"], max_length=10)


class CommerceContext(APIModel):
    channel: Channel
    product_attachment: Literal["confirmed", "unavailable", "unknown"] = "unknown"
    messaging_supported: bool = False
    listing_reference: Short | None = None


class Selection(APIModel):
    targets: list[ContentTarget] | None = Field(default=None, min_length=1, max_length=5)
    channels: list[Channel] | None = Field(default=None, min_length=1, max_length=3)
    variants: int = Field(default=3, ge=1, le=3)

    @model_validator(mode="after")
    def target_selection(self):
        if (self.targets is None) == (self.channels is None):
            raise ValueError("Cung cấp targets hoặc channels; không cung cấp đồng thời.")
        keys = [t.key for t in self.selected_targets()]
        if len(set(keys)) != len(keys):
            raise ValueError("Mỗi target/channel chỉ được xuất hiện một lần.")
        if sum(t.variants or self.variants for t in self.selected_targets()) > settings.MARKETING_MAX_WORKLOAD:
            raise ValueError("Tổng số phương án vượt MARKETING_MAX_WORKLOAD.")
        return self

    def selected_targets(self) -> list[ContentTarget]:
        return self.targets if self.targets is not None else [
            ContentTarget(channel=LEGACY_TARGETS[c][0], placement=LEGACY_TARGETS[c][1],
                          content_type=LEGACY_TARGETS[c][2]) for c in self.channels or []
        ]


class GenerationRequest(Selection):
    product: ProductSnapshot
    objective: Objective
    brand: BrandProfile = Field(default_factory=BrandProfile)
    audience: Short = "khách đang cân nhắc sản phẩm"
    tone: Literal["friendly", "professional", "youthful", "concise"] = "friendly"
    length: Literal["short", "standard"] = "standard"
    emoji_limit: int = Field(default=0, ge=0, le=2)
    include_hashtags: bool = False
    instructions: Text | None = None
    opening_requirement: Short | None = None
    cta: Short | None = None
    cta_type: Literal["view_product", "message", "comment", "choose_variant", "attached_product"] = "view_product"
    duration_seconds: Literal[15, 30, 60] = 30
    video_style: VideoStyle = "product_demo"
    production_mode: ProductionMode = "hands_only"
    resources: Resources | None = None
    commerce_context: list[CommerceContext] = Field(default_factory=list, max_length=3)
    include_post_caption: bool = True
    include_shot_list: bool = True
    # Retry only explicitly selected failed slots; variant numbers are 1-based.
    retry_slots: list["RetrySlot"] = Field(default_factory=list, max_length=15)
    previous_request_id: Short | None = None

    @model_validator(mode="after")
    def retry_selection(self):
        if len({c.channel for c in self.commerce_context}) != len(self.commerce_context):
            raise ValueError("commerce_context trùng kênh.")
        selected = {t.key: t.variants or self.variants for t in self.selected_targets()}
        slots = [(s.target.key, s.variant) for s in self.retry_slots]
        if len(slots) != len(set(slots)):
            raise ValueError("retry_slots bị trùng.")
        if any(key not in selected or variant > selected[key] for key, variant in slots):
            raise ValueError("retry_slots phải nằm trong targets/variants yêu cầu.")
        if self.retry_slots and not self.previous_request_id:
            raise ValueError("retry_slots cần previous_request_id.")
        return self


class RetrySlot(APIModel):
    target: Target
    variant: int = Field(ge=1, le=3)


class Caption(APIModel):
    content_type: Literal["caption"] = "caption"
    angle: Short
    hook: Short
    body: Text
    cta: Short
    hashtags: list[Short] = Field(default_factory=list, max_length=5)
    plain_text: str = Field(default="", max_length=12000)


class Listing(APIModel):
    content_type: Literal["listing"] = "listing"
    angle: Short
    title: Short
    short_description: Text
    highlights: list[Short] = Field(min_length=1, max_length=12)
    detailed_description: Text
    attributes: list["SourcedAttribute"] = Field(default_factory=list, max_length=30)
    cta: Short
    plain_text: str = Field(default="", max_length=16000)


class SourcedAttribute(APIModel):
    fact_ref: Short
    value: Short


class Scene(APIModel):
    scene_id: Identifier
    start_seconds: float = Field(ge=0, le=60, allow_inf_nan=False)
    end_seconds: float = Field(gt=0, le=60, allow_inf_nan=False)
    duration_seconds: float = Field(gt=0, le=60, allow_inf_nan=False)
    visual_action: Text
    shot_type: Short
    camera_direction: Short
    dialogue: Text | None = None
    voiceover: Text | None = None
    on_screen_text: Annotated[str, StringConstraints(max_length=500)] = ""
    audio_direction: Short
    editing_notes: Short
    people_required: int = Field(default=1, ge=0, le=10)
    shows_face: bool = False


class VideoCTA(APIModel):
    text: Short
    action: Literal["view_product", "message", "comment", "choose_variant", "attached_product"]
    display_condition: Short


class ProductionPlan(APIModel):
    shot_list: list[Short] = Field(default_factory=list, max_length=15)
    props: list[Short] = Field(default_factory=list, max_length=15)
    location: Short
    actors: int = Field(ge=1, le=10)
    filming_checklist: list[Short] = Field(min_length=1, max_length=15)
    editing_guide: list[Short] = Field(min_length=1, max_length=15)


class VideoScript(APIModel):
    content_type: Literal["video_script"] = "video_script"
    title: Short
    concept: Text
    angle: Short
    objective: Objective
    audience: Short
    hook: Short
    key_message: Short
    total_duration_seconds: Literal[15, 30, 60]
    production_mode: ProductionMode
    video_style: VideoStyle
    scenes: list[Scene] = Field(min_length=1, max_length=12)
    cta: VideoCTA
    product_attachment_note: Short | None = None
    post_caption: Annotated[str, StringConstraints(max_length=1200)] | None = None
    hashtags: list[Short] = Field(default_factory=list, max_length=5)
    cover_text: Short
    production: ProductionPlan | None = None
    plain_text: str = Field(default="", max_length=20000)


Content = Annotated[Caption | Listing | VideoScript, Field(discriminator="content_type")]


class SourceContent(APIModel):
    client_reference: Short
    version_reference: Short
    target: Target
    sku: Short
    content: Content
    product_snapshot: ProductSnapshot | None = None

    @model_validator(mode="after")
    def matching_type(self):
        if self.target.content_type != self.content.content_type:
            raise ValueError("Source content không khớp target.")
        if self.product_snapshot is not None and self.product_snapshot.sku != self.sku:
            raise ValueError("Source snapshot không khớp SKU.")
        return self


class RewriteRequest(GenerationRequest):
    source: SourceContent
    instructions: Text

    @model_validator(mode="after")
    def single_source(self):
        if self.product.sku != self.source.sku:
            raise ValueError("Rewrite phải dùng cùng SKU.")
        if len(self.selected_targets()) != 1 or self.selected_targets()[0].key != self.source.target.key:
            raise ValueError("Rewrite dùng đúng một target của source; chuyển kênh dùng adapt.")
        if self.variants != 1 or (self.selected_targets()[0].variants or 1) != 1 or self.retry_slots:
            raise ValueError("Rewrite chỉ tạo một phiên bản.")
        return self


class AdaptRequest(GenerationRequest):
    source: SourceContent

    @model_validator(mode="after")
    def video_source(self):
        if self.source.sku != self.product.sku or self.source.content.content_type != "video_script":
            raise ValueError("Adapt cần video source cùng SKU.")
        if any(t.content_type != "video_script" for t in self.selected_targets()):
            raise ValueError("Adapt chỉ hỗ trợ video targets.")
        return self


class DraftReference(APIModel):
    client_reference: Short
    draft_reference: Short | None = None
    version_reference: Short
    sku: Short
    target: Target
    status: Literal["draft", "ready", "archived"] = "draft"


class CalendarRequest(GenerationRequest):
    start_date: date
    timezone: Short = "Asia/Ho_Chi_Minh"
    references: list[DraftReference] = Field(default_factory=list, max_length=30)
    generate_content: bool = False

    @field_validator("timezone")
    @classmethod
    def valid_timezone(cls, value):
        try:
            ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError) as exc:
            raise ValueError("Timezone IANA không hợp lệ.") from exc
        return value

    @model_validator(mode="after")
    def valid_references(self):
        targets = {t.key for t in self.selected_targets()}
        if any(r.sku != self.product.sku or r.target.key not in targets for r in self.references):
            raise ValueError("Reference phải khớp SKU và target yêu cầu.")
        if self.retry_slots:
            raise ValueError("Calendar không nhận retry_slots; retry qua generate.")
        return self


class StrategyRequest(APIModel):
    shop_context: Text
    objective: Objective
    products: list[ProductSnapshot] = Field(min_length=1, max_length=5)
    audience: Short | None = None
    budget: Decimal | None = Field(default=None, ge=0, max_digits=15, decimal_places=2)
    resources: Resources | None = None
    brand: BrandProfile = Field(default_factory=BrandProfile)


class FactClaim(APIModel):
    text: Text
    fact_refs: list[Short] = Field(min_length=1, max_length=10)


class ModelDraft(APIModel):
    content: Content
    fact_claims: list[FactClaim] = Field(default_factory=list, max_length=40)
    warnings: list[Short] = Field(default_factory=list, max_length=15)
    assumptions: list[Short] = Field(default_factory=list, max_length=15)


class KnowledgeSource(APIModel):
    doc_id: str
    chunk_id: str
    version: str
    content_hash: str
    source_ids: list[str]
    scope: Literal["public", "private"]


class MarketingItem(APIModel):
    client_reference: str
    variant: int
    target: Target
    sku: str
    status: Literal["draft"] = "draft"
    content: Content
    source_client_reference: str | None = None
    source_version_reference: str | None = None
    change_summary: str | None = None
    fact_claims: list[FactClaim]
    warnings: list[str]
    assumptions: list[str]
    missing_fields: list[str] = Field(default_factory=list)
    sources: list[KnowledgeSource] = Field(default_factory=list)


class ItemError(APIModel):
    target: Target | None = None
    variant: int | None = None
    client_reference: str | None = None
    code: str
    message: str
    retryable: bool = False
    fields: list[str] = Field(default_factory=list)


class CalendarEntry(APIModel):
    date: date
    timezone: str
    target: Target
    sku: str
    objective: Objective
    topic: str
    angle: str
    cta: str
    client_reference: str | None = None
    draft_reference: str | None = None
    version_reference: str | None = None
    status: Literal["needs_generation", "draft", "ready"]
    video_style: VideoStyle | None = None
    duration_seconds: int | None = None
    preparation: list[str]


class StrategyOption(APIModel):
    priority: int = Field(ge=1, le=3)
    name: Short
    problem: Text
    suitable_when: Text
    conditions: list[Short] = Field(min_length=1, max_length=8)
    message: Text
    channels: list[Channel] = Field(min_length=1, max_length=3)
    actions: list[Text] = Field(min_length=3, max_length=5)
    resources: list[Short] = Field(min_length=1, max_length=10)
    assumptions: list[Short] = Field(default_factory=list, max_length=10)
    kpis_to_measure: list[Short] = Field(min_length=1, max_length=8)
    experiment: Text
    stop_or_adjust_when: Text


class StrategyOutput(APIModel):
    strategies: list[StrategyOption] = Field(min_length=2, max_length=3)
    assumptions: list[Short] = Field(default_factory=list, max_length=15)


class MarketingMetadata(APIModel):
    prompt_version: str
    knowledge_version: str | None = None
    sources: list[KnowledgeSource] = Field(default_factory=list)
    model: str | None = None
    usage: list[dict] = Field(default_factory=list)
    duration_ms: float = 0
    idempotency_replayed: bool = False
    requires_human_review: bool = True


class MarketingResponse(APIModel):
    request_id: str
    status: Literal["success", "partial_success", "failed", "needs_input"]
    items: list[MarketingItem] = Field(default_factory=list)
    errors: list[ItemError] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)
    metadata: MarketingMetadata
    calendar: list[CalendarEntry] = Field(default_factory=list)
    strategies: list[StrategyOption] = Field(default_factory=list)


class MarketingValidationIssue(APIModel):
    path: str
    type: str


class MarketingValidationDetail(APIModel):
    code: str
    message: str
    fields: list[MarketingValidationIssue] = Field(default_factory=list)


class MarketingValidationError(APIModel):
    success: Literal[False] = False
    error: MarketingValidationDetail
    meta: ResponseMeta


class MarketingChatAction(APIModel):
    """Explicit tool intent selected by BE; chat never accepts a raw snapshot."""
    sku: Short
    targets: list[ContentTarget] = Field(min_length=1, max_length=5)
    objective: Objective = "introduce_product"
    variants: int = Field(default=1, ge=1, le=3)


GenerationRequest.model_rebuild()
