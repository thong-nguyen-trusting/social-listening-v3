from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request

from app.schemas.labels import LabelAuditResponse, LabelJobSummaryResponse

router = APIRouter(prefix="/api/runs", tags=["labels"])


@router.post("/{run_id}/labels/jobs", response_model=LabelJobSummaryResponse)
async def create_label_job(run_id: str, http_request: Request) -> LabelJobSummaryResponse:
    try:
        payload = await http_request.app.state.label_job_service.ensure_job_for_run(run_id, auto_start=True)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return LabelJobSummaryResponse(**payload)


@router.get("/{run_id}/labels/summary", response_model=LabelJobSummaryResponse)
async def get_label_summary(run_id: str, http_request: Request) -> LabelJobSummaryResponse:
    try:
        payload = http_request.app.state.label_job_service.get_summary(run_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return LabelJobSummaryResponse(**payload)


@router.get("/{run_id}/records", response_model=LabelAuditResponse)
async def get_label_audit_records(
    run_id: str,
    http_request: Request,
    label_filter: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=50),
) -> LabelAuditResponse:
    try:
        payload = http_request.app.state.label_job_service.get_record_samples(
            run_id,
            label_filter=label_filter,
            limit=limit,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return LabelAuditResponse(**payload)
