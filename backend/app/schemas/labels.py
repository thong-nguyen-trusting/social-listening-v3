from __future__ import annotations

from pydantic import BaseModel, Field


class LabelJobSummaryResponse(BaseModel):
    run_id: str
    label_job_id: str | None = None
    status: str
    taxonomy_version: str
    records_total: int
    records_labeled: int
    records_fallback: int
    records_failed: int
    counts_by_author_role: dict[str, int] = Field(default_factory=dict)
    warning: str | None = None


class LabelRecordAuditSchema(BaseModel):
    post_id: str
    record_type: str
    content: str
    source_url: str | None = None
    label: dict | None = None


class LabelAuditResponse(BaseModel):
    run_id: str
    label_filter: str | None = None
    records: list[LabelRecordAuditSchema] = Field(default_factory=list)
