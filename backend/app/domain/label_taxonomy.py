from __future__ import annotations

from typing import Any

TAXONOMY_VERSION = "v1"

AUTHOR_ROLES = (
    "end_user",
    "seller_affiliate",
    "brand_official",
    "community_admin",
    "unknown",
)

CONTENT_INTENTS = (
    "experience",
    "question",
    "promotion",
    "support_answer",
    "comparison",
    "other",
)

COMMERCIALITY_LEVELS = ("low", "medium", "high")
USER_FEEDBACK_RELEVANCE_LEVELS = ("high", "medium", "low")
LABEL_SOURCES = ("heuristic", "ai", "hybrid", "fallback")
LABEL_JOB_STATUSES = ("PENDING", "RUNNING", "DONE", "FAILED", "CANCELLED", "PARTIAL")
LABEL_RECORD_STATUSES = ("PENDING", "LABELED", "FALLBACK", "FAILED")
AUDIENCE_FILTERS = ("end_user_only", "include_seller", "include_brand")


def sql_enum(values: tuple[str, ...]) -> str:
    return ",".join(f"'{value}'" for value in values)


def normalize_audience_filter(value: str | None) -> str:
    if not value:
        return "end_user_only"
    normalized = value.strip().lower()
    if normalized not in AUDIENCE_FILTERS:
        raise ValueError("unsupported audience_filter")
    return normalized


def coerce_label_payload(payload: dict[str, Any]) -> dict[str, Any]:
    author_role = str(payload.get("author_role") or "unknown").strip().lower()
    content_intent = str(payload.get("content_intent") or "other").strip().lower()
    commerciality_level = str(payload.get("commerciality_level") or "medium").strip().lower()
    user_feedback_relevance = str(payload.get("user_feedback_relevance") or "low").strip().lower()
    label_source = str(payload.get("label_source") or "fallback").strip().lower()
    label_reason = str(payload.get("label_reason") or "fallback_label_applied").strip()[:240]
    model_name = payload.get("model_name")
    model_version = payload.get("model_version")
    try:
        label_confidence = float(payload.get("label_confidence", 0.5))
    except (TypeError, ValueError):
        label_confidence = 0.5

    if author_role not in AUTHOR_ROLES:
        author_role = "unknown"
    if content_intent not in CONTENT_INTENTS:
        content_intent = "other"
    if commerciality_level not in COMMERCIALITY_LEVELS:
        commerciality_level = "medium"
    if user_feedback_relevance not in USER_FEEDBACK_RELEVANCE_LEVELS:
        user_feedback_relevance = "low"
    if label_source not in LABEL_SOURCES:
        label_source = "fallback"

    return {
        "author_role": author_role,
        "content_intent": content_intent,
        "commerciality_level": commerciality_level,
        "user_feedback_relevance": user_feedback_relevance,
        "label_confidence": max(0.0, min(label_confidence, 1.0)),
        "label_reason": label_reason or "fallback_label_applied",
        "label_source": label_source,
        "model_name": model_name,
        "model_version": model_version,
        "taxonomy_version": str(payload.get("taxonomy_version") or TAXONOMY_VERSION),
    }
