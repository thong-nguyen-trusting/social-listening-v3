from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.infrastructure.config import get_settings
from app.infrastructure.runtime_manifest import get_release_note, get_runtime_metadata
from app.schemas.runtime import ReleaseNoteResponse, RuntimeMetadataResponse

router = APIRouter(prefix="/api/runtime", tags=["runtime"])


@router.get("/metadata", response_model=RuntimeMetadataResponse)
async def runtime_metadata() -> RuntimeMetadataResponse:
    return RuntimeMetadataResponse.model_validate(get_runtime_metadata(get_settings()))


@router.get("/release-notes/current", response_model=ReleaseNoteResponse)
async def current_release_note() -> ReleaseNoteResponse:
    payload = get_release_note(get_settings())
    if payload is None:
        raise HTTPException(status_code=404, detail="release note not found")
    return ReleaseNoteResponse.model_validate(payload)


@router.get("/release-notes/{phase_id}", response_model=ReleaseNoteResponse)
async def release_note_by_phase(phase_id: str) -> ReleaseNoteResponse:
    payload = get_release_note(get_settings(), phase_id=phase_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="release note not found")
    return ReleaseNoteResponse.model_validate(payload)
