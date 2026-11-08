"""Scoped, incremental Chroma RAG. Examples are indivisible semantic units."""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import time
from pathlib import Path

from langchain_core.documents import Document

from config.settings import settings
from src.schemas.marketing import KnowledgeSource, VALID_TARGETS
from src.security.privacy import sanitize_text

logger = logging.getLogger(__name__)
REQUIRED = {"doc_id", "title", "language", "scope", "channels", "industries", "objectives",
            "content_kind", "source_ids", "updated_at", "version"}


def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def parse_directory(directory: Path, *, scope="public", tenant_id="", shop_id=""):
    """Front matter uses JSON (a YAML subset), avoiding executable YAML tags.

    Split only at level-two headings: keep facts, timeline, CTA and conditions
    together. One example/strategy/playbook belongs under exactly one heading.
    """
    if scope not in {"public", "private"} or (scope == "private" and (not tenant_id or not shop_id)):
        raise ValueError("Private index requires an explicit tenant and shop.")
    documents = []
    seen = set()
    for path in sorted(directory.glob("*.md")):
        raw = path.read_text(encoding="utf-8-sig")
        match = re.fullmatch(r"---\s*\n(.*?)\n---\s*\n(.*)", raw, re.S)
        if not match:
            raise ValueError(f"Missing front matter: {path.name}")
        front = json.loads(match.group(1))
        if not REQUIRED <= front.keys() or front["scope"] != scope:
            raise ValueError(f"Invalid metadata/scope: {path.name}")
        if not re.fullmatch(r"[a-zA-Z0-9_.-]{1,100}", str(front["doc_id"])) or front["doc_id"] in seen:
            raise ValueError(f"Invalid or duplicate doc_id: {path.name}")
        seen.add(front["doc_id"])
        if scope == "public" and (front.get("tenant_id") or front.get("shop_id")):
            raise ValueError("Public knowledge cannot contain shop-scoped documents.")
        if scope == "private" and (front.get("tenant_id") != tenant_id or front.get("shop_id") != shop_id):
            raise ValueError("Document belongs to a different tenant/shop.")
        for key in ("channels", "industries", "objectives", "source_ids"):
            if not isinstance(front[key], list) or not all(isinstance(v, str) for v in front[key]):
                raise ValueError(f"Invalid list metadata: {path.name}:{key}")
        targets = front.get("targets", [list(t) for t in VALID_TARGETS if t[0] in front["channels"]])
        for index, section in enumerate(re.split(r"(?=^## )", match.group(2), flags=re.M)):
            if not section.strip():
                continue
            # No silent truncation of examples/timelines. Fix oversized units at authoring time.
            if len(section) > settings.MARKETING_CONTEXT_CHARS:
                raise ValueError(f"Semantic unit too large: {path.name}:{index}")
            body = sanitize_text(section.strip(), block_prompt_injection=True)
            unit = re.search(r"```json\s*\n(.*?)\n```", section, re.S)
            example = json.loads(unit.group(1)) if unit else {}
            input_facts = example.get("input_facts", {})
            unit_industry = example.get("industry") or (input_facts.get("industry") if isinstance(input_facts, dict) else None)
            industries = [unit_industry] if unit_industry else front["industries"]
            objectives = [example["objective"]] if example.get("objective") in {
                "introduce_product", "drive_sales", "promote_offer", "answer_questions"} else front["objectives"]
            content_hash = digest(body + json.dumps(front, sort_keys=True, ensure_ascii=False))
            for channel, placement, content_type in targets:
                if (channel, placement, content_type) not in VALID_TARGETS:
                    raise ValueError(f"Invalid target metadata: {path.name}")
                chunk_id = digest(f"{scope}:{tenant_id}:{shop_id}:{front['doc_id']}:{index}:{channel}:{placement}:{content_type}")
                metadata = {"namespace": "marketing", "scope": scope, "tenant_id": tenant_id,
                    "shop_id": shop_id, "doc_id": front["doc_id"], "chunk_id": chunk_id,
                    "content_hash": content_hash, "version": str(front["version"]),
                    "source_ids": json.dumps(front["source_ids"]), "channel": channel,
                    "placement": placement, "content_type": content_type,
                    "industry": json.dumps(industries, ensure_ascii=False),
                    "objective": json.dumps(objectives), "tone": front.get("tone", "all"),
                    "content_kind": front["content_kind"],
                    "synthetic_example": bool(front.get("synthetic_example", False)),
                    "source": path.name}
                documents.append(Document(page_content=body, metadata=metadata))
    return documents


def vector_directory():
    return settings.BASE_DIR / settings.MARKETING_VECTOR_DIR


def open_store():
    # Reuse the existing embedding provider/model; never touch the finance collection.
    from langchain_chroma import Chroma
    from rag.vector_store import _get_embeddings
    return Chroma(collection_name=settings.MARKETING_COLLECTION,
                  persist_directory=str(vector_directory()),
                  embedding_function=_get_embeddings(timeout=settings.MARKETING_EMBEDDING_TIMEOUT_SECONDS, max_retries=0),
                  # Chroma's default L2 distance is nonnegative and unbounded.
                  # Map it monotonically to (0,1]; not a probability or cosine.
                  # The default LangChain unit-vector mapping can become negative.
                  relevance_score_fn=lambda distance: 1.0 / (1.0 + max(0.0, distance)))


def embedding_mismatch(store):
    """(stored_dim, current_dim) when stored vectors came from another embedding model, else None.

    Content hashes alone cannot detect a provider/model switch: unchanged chunks
    would be skipped and every later query would fail on dimensionality.
    One probe embedding is spent only when the collection already has vectors.
    """
    got = store.get(limit=1, include=["embeddings"])
    vectors = got.get("embeddings")
    if vectors is None or len(vectors) == 0:
        return None
    stored = len(vectors[0])
    current = len(store.embeddings.embed_query("finora marketing dimension probe"))
    return None if stored == current else (stored, current)


def scope_filter(scope, tenant_id="", shop_id=""):
    return {"$and": [{"namespace": "marketing"}, {"scope": scope},
                     {"tenant_id": tenant_id}, {"shop_id": shop_id}]}


def sync_index(store, documents, *, scope="public", tenant_id="", shop_id="", dry_run=False):
    """Only delete stale IDs from this exact namespace/scope; never reset a collection.

    Call this with the complete directory for the selected scope. Failed upserts
    stop before deletions. An interrupted batch is safe to upsert again.
    """
    if scope == "private" and (not tenant_id or not shop_id):
        raise ValueError("Private scope requires tenant_id/shop_id.")
    expected = (scope, tenant_id, shop_id)
    if any((d.metadata["scope"], d.metadata["tenant_id"], d.metadata["shop_id"]) != expected for d in documents):
        raise ValueError("Cross-scope index operation rejected.")
    current = store.get(where=scope_filter(*expected), include=["metadatas"])
    old = dict(zip(current["ids"], current["metadatas"]))
    wanted = {d.metadata["chunk_id"]: d for d in documents}
    changed = [d for key, d in wanted.items() if key not in old or old[key].get("content_hash") != d.metadata["content_hash"]]
    stale = sorted(set(old) - set(wanted))
    report = {"total": len(wanted), "upserted": len(changed), "deleted": len(stale), "dry_run": dry_run}
    if dry_run:
        return report
    batch_size = max(1, settings.EMBEDDING_BATCH_SIZE)
    for offset in range(0, len(changed), batch_size):
        batch = changed[offset:offset + batch_size]
        for attempt in range(max(0, settings.MARKETING_EMBEDDING_RETRIES) + 1):
            try:
                store.add_documents(batch, ids=[d.metadata["chunk_id"] for d in batch])
                break
            except Exception:
                if attempt >= settings.MARKETING_EMBEDDING_RETRIES:
                    raise
                time.sleep(min(2 ** attempt, 10))
        if offset + batch_size < len(changed):
            time.sleep(max(0, min(settings.EMBEDDING_REQUEST_INTERVAL_SECONDS, 60)))
    if stale:
        store.delete(ids=stale)
    return report


class MarketingKnowledge:
    def __init__(self, store=None):
        self.store = store

    def retrieve(self, *, target, context, industry, objective, tone, query, deadline=None, content_kind=None):
        if self.store is None:
            return [], ["RAG marketing chưa được nạp; dùng quy tắc cốt lõi và snapshot."]
        selected_kind = content_kind or {"caption": "caption_examples", "listing": "listing_examples", "video_script": "video_examples"}[target.content_type]
        filters = {"$and": [
            {"namespace": "marketing"}, {"channel": target.channel},
            {"placement": target.placement}, {"content_type": target.content_type},
            {"$or": [scope_filter("public"), scope_filter("private", context.tenant_id, context.shop_id)]},
        ]}
        filters["$and"].append({"content_kind": selected_kind})
        try:
            candidates = self.store.similarity_search_with_relevance_scores(
                # No private snapshot in the embedding query. Only bounded category/goal/tone.
                f"{industry[:100]} {objective} {tone} {query[:200]}",
                k=max(1, settings.MARKETING_RAG_TOP_K) * 4, filter=filters)
        except Exception as exc:
            # Type only (e.g. dimension mismatch after an embedding model switch); no query text.
            logger.warning("Marketing retrieval unavailable error=%s", type(exc).__name__)
            return [], ["Truy xuất marketing tạm lỗi; dùng quy tắc cốt lõi và snapshot."]
        eligible = []
        for doc, score in candidates:
            m = doc.metadata
            # Defense in depth if a vector backend ignores/misapplies its filter.
            public = (m.get("scope"), m.get("tenant_id"), m.get("shop_id")) == ("public", "", "")
            private = (m.get("scope"), m.get("tenant_id"), m.get("shop_id")) == ("private", context.tenant_id, context.shop_id)
            if not (public or private) or m.get("namespace") != "marketing":
                continue
            if (m.get("channel"), m.get("placement"), m.get("content_type")) != target.key:
                continue
            if m.get("content_kind") != selected_kind:
                continue
            if score is None or score < settings.MARKETING_RAG_MIN_SCORE:
                continue
            industries, objectives = json.loads(m["industry"]), json.loads(m["objective"])
            rank = float(score) + .15 * (industry in industries) + .1 * (objective in objectives) + .05 * (m.get("tone") == tone)
            eligible.append((rank, doc))
        result, length = [], 0
        hashes = set()
        for _, doc in sorted(eligible, key=lambda item: item[0], reverse=True):
            if doc.metadata["content_hash"] in hashes:
                continue
            if length + len(doc.page_content) > settings.MARKETING_CONTEXT_CHARS:
                continue
            hashes.add(doc.metadata["content_hash"])
            result.append(doc)
            length += len(doc.page_content)
            if len(result) >= max(1, settings.MARKETING_RAG_TOP_K):
                break
        return result, [] if result else ["Không có tri thức phù hợp; chỉ dùng quy tắc cốt lõi và snapshot."]


def source_metadata(doc):
    m = doc.metadata
    return KnowledgeSource(doc_id=m["doc_id"], chunk_id=m["chunk_id"], version=m["version"],
        content_hash=m["content_hash"], source_ids=json.loads(m["source_ids"]), scope=m["scope"])


def main():
    parser = argparse.ArgumentParser(description="Incremental marketing knowledge index")
    parser.add_argument("--directory", type=Path, default=settings.get_knowledge_dir() / "marketing")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--scope", choices=["public", "private"], default="public")
    parser.add_argument("--tenant-id", default="")
    parser.add_argument("--shop-id", default="")
    args = parser.parse_args()
    if not args.directory.is_dir():
        parser.error("Knowledge directory does not exist.")
    if args.scope == "public" and (args.tenant_id or args.shop_id):
        parser.error("Public scope cannot carry tenant/shop identifiers.")
    docs = parse_directory(args.directory, scope=args.scope, tenant_id=args.tenant_id, shop_id=args.shop_id)
    if args.dry_run:
        # Offline validation/counts: no embeddings, provider credentials or collection mutation.
        print(json.dumps({"dry_run": True, "documents": len({d.metadata['doc_id'] for d in docs}),
                          "chunks": len(docs), "provider_called": False}))
        return
    if not settings.is_api_key_configured():
        parser.error("Provider credentials must be configured before embedding.")
    try:
        store = open_store()
        mismatch = embedding_mismatch(store)
        if mismatch:
            print(json.dumps({"status": "failed", "error_type": "EmbeddingModelMismatch",
                              "stored_dimension": mismatch[0], "current_dimension": mismatch[1],
                              "message": ("Vector marketing được tạo bằng embedding model khác cấu hình hiện tại. "
                                          "Đổi MARKETING_VECTOR_DIR/MARKETING_COLLECTION hoặc xóa thư mục vector marketing, "
                                          "rồi index lại public và từng thư mục private.")}, ensure_ascii=False))
            raise SystemExit(1)
        report = sync_index(store, docs, scope=args.scope, tenant_id=args.tenant_id, shop_id=args.shop_id)
    except SystemExit:
        raise
    except Exception as exc:
        print(json.dumps({"status": "failed", "error_type": type(exc).__name__,
                          "message": "Index not completed. Check provider connectivity/configuration; no collection reset performed."}))
        raise SystemExit(1) from None
    print(json.dumps(report))


if __name__ == "__main__":
    main()
