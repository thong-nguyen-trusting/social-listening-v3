from __future__ import annotations

from pydantic import BaseModel, Field


class ThemeSchema(BaseModel):
    theme_id: str
    label: str
    dominant_sentiment: str
    post_count: int
    sample_quotes: list[str] = Field(default_factory=list)


class ThemeAnalysisResponse(BaseModel):
    run_id: str
    audience_filter: str
    taxonomy_version: str
    posts_crawled: int
    posts_included: int
    posts_excluded: int
    excluded_by_label_count: int
    excluded_breakdown: dict[str, int] = Field(default_factory=dict)
    themes: list[ThemeSchema] = Field(default_factory=list)
    warning: str | None = None
