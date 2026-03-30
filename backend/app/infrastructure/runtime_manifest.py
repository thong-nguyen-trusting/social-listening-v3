from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from app.infrastructure.config import Settings

REPO_ROOT = Path(__file__).resolve().parents[3]
PHASE_MANIFEST_PATH = REPO_ROOT / ".phase.json"
PHASES_DIR = REPO_ROOT / "docs" / "phases"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _phase_number(phase_id: str | None) -> int | None:
    if not phase_id:
        return None
    match = re.search(r"phase-(\d+)$", phase_id)
    return int(match.group(1)) if match else None


def build_display_name(app_name: str, phase_id: str | None) -> str:
    phase_number = _phase_number(phase_id)
    if phase_number is None:
        return app_name
    return f"{app_name}.{phase_number}"


def load_phase_manifest() -> dict[str, Any]:
    if not PHASE_MANIFEST_PATH.exists():
        return {"current": None, "phases": {}}
    payload = _read_json(PHASE_MANIFEST_PATH)
    if not isinstance(payload, dict):
        return {"current": None, "phases": {}}
    phases = payload.get("phases")
    if not isinstance(phases, dict):
        phases = {}
    return {
        "current": payload.get("current"),
        "phases": phases,
    }


def get_runtime_metadata(settings: Settings) -> dict[str, Any]:
    manifest = load_phase_manifest()
    current_phase = manifest.get("current")
    phases = manifest.get("phases") or {}
    current_phase_payload = phases.get(current_phase) if isinstance(phases, dict) else {}
    if not isinstance(current_phase_payload, dict):
        current_phase_payload = {}
    display_name = build_display_name(settings.app_name, current_phase)
    release_note_path = PHASES_DIR / str(current_phase) / "release-note.json" if current_phase else None
    has_release_notes = bool(release_note_path and release_note_path.exists())
    return {
        "app_name": settings.app_name,
        "display_name": display_name,
        "app_version": settings.app_version,
        "current_phase": current_phase,
        "current_phase_number": _phase_number(current_phase),
        "current_phase_name": current_phase_payload.get("name"),
        "current_phase_summary": current_phase_payload.get("summary"),
        "release_notes_href": f"#/release-notes/{current_phase}" if has_release_notes and current_phase else None,
        "release_notes_available": has_release_notes,
    }


def get_release_note(settings: Settings, phase_id: str | None = None) -> dict[str, Any] | None:
    manifest = load_phase_manifest()
    resolved_phase = phase_id or manifest.get("current")
    if not resolved_phase:
        return None
    release_note_path = PHASES_DIR / resolved_phase / "release-note.json"
    if not release_note_path.exists():
        return None
    payload = _read_json(release_note_path)
    if not isinstance(payload, dict):
        return None
    payload.setdefault("phase", resolved_phase)
    payload.setdefault("display_name", build_display_name(settings.app_name, resolved_phase))
    payload.setdefault("title", payload["display_name"])
    payload.setdefault("summary", "")
    payload.setdefault("hero", {})
    payload.setdefault("highlights", [])
    payload.setdefault("sections", [])
    payload.setdefault("story_refs", [])
    payload.setdefault("cta", {"label": "Open workflow", "href": "#/"})
    return payload
