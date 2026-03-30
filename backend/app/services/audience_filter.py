from __future__ import annotations

from app.domain.label_taxonomy import normalize_audience_filter
from app.models.content_label import ContentLabel


class AudienceFilterPolicy:
    def normalize(self, audience_filter: str | None) -> str:
        return normalize_audience_filter(audience_filter)

    def include(self, audience_filter: str, label: ContentLabel | None) -> tuple[bool, str | None]:
        normalized = self.normalize(audience_filter)
        if label is None:
            return False, "missing_label"
        if label.user_feedback_relevance == "low":
            return False, "low_relevance"
        if normalized == "end_user_only":
            if label.author_role != "end_user":
                return False, label.author_role
            if label.label_confidence < 0.45:
                return False, "low_confidence"
            return True, None
        if normalized == "include_seller":
            if label.author_role in {"brand_official", "community_admin"}:
                return False, label.author_role
            if label.author_role == "unknown" and label.label_confidence < 0.6:
                return False, "low_confidence"
            return True, None
        if label.author_role == "community_admin":
            return False, "community_admin"
        return True, None
