from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, Query, Request

from app.schemas.insights import ThemeAnalysisResponse

router = APIRouter(prefix="/api/runs", tags=["insights"])
SKILLS_DIR = Path(__file__).resolve().parents[1] / "skills"


@router.get("/{run_id}/themes", response_model=ThemeAnalysisResponse)
async def get_themes(
    run_id: str,
    http_request: Request,
    audience_filter: str = Query(default="end_user_only"),
) -> ThemeAnalysisResponse:
    try:
        payload = await http_request.app.state.insight_service.analyze_themes(
            run_id,
            (SKILLS_DIR / "theme_classification.md").read_text(encoding="utf-8"),
            audience_filter,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ThemeAnalysisResponse(**payload)
