from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RuntimeMetadataResponse(BaseModel):
    app_name: str
    display_name: str
    app_version: str
    current_phase: str | None
    current_phase_number: int | None
    current_phase_name: str | None
    current_phase_summary: str | None
    release_notes_href: str | None
    release_notes_available: bool


class ReleaseNoteResponse(BaseModel):
    phase: str
    display_name: str
    title: str
    summary: str
    published_at: str | None = None
    status: str | None = None
    hero: dict[str, Any] = Field(default_factory=dict)
    highlights: list[dict[str, Any]] = Field(default_factory=list)
    sections: list[dict[str, Any]] = Field(default_factory=list)
    story_refs: list[str] = Field(default_factory=list)
    cta: dict[str, Any] = Field(default_factory=dict)
