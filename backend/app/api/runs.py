from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.schemas.runs import RunResponse, RunStartRequest

router = APIRouter(prefix="/api/runs", tags=["runs"])


@router.post("", response_model=RunResponse)
async def start_run(request: RunStartRequest, http_request: Request) -> RunResponse:
    try:
        payload = await http_request.app.state.runner_service.start_run(request.plan_id, request.grant_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return RunResponse(**payload)


@router.get("/{run_id}", response_model=RunResponse)
async def get_run(run_id: str, http_request: Request) -> RunResponse:
    try:
        payload = http_request.app.state.runner_service.get_run(run_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return RunResponse(**payload)


@router.post("/{run_id}/pause", response_model=RunResponse)
async def pause_run(run_id: str, http_request: Request) -> RunResponse:
    try:
        payload = await http_request.app.state.runner_service.pause_run(run_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return RunResponse(**payload)


@router.post("/{run_id}/resume", response_model=RunResponse)
async def resume_run(run_id: str, http_request: Request) -> RunResponse:
    try:
        payload = await http_request.app.state.runner_service.resume_run(run_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return RunResponse(**payload)


@router.post("/{run_id}/stop", response_model=RunResponse)
async def stop_run(run_id: str, http_request: Request) -> RunResponse:
    try:
        payload = await http_request.app.state.runner_service.stop_run(run_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return RunResponse(**payload)


@router.get("/{run_id}/stream")
async def run_stream(run_id: str, http_request: Request) -> StreamingResponse:
    runner_service = http_request.app.state.runner_service
    history = runner_service.get_event_history(run_id)
    queue = runner_service.subscribe(run_id)
    try:
        snapshot = runner_service.get_run(run_id)
    except ValueError as exc:
        runner_service.unsubscribe(run_id, queue)
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    async def event_stream():
        try:
            for event, payload in history:
                yield f"event: {event}\ndata: {json.dumps(payload)}\n\n"
                if event in {"run_done", "run_failed", "run_cancelled"}:
                    yield (
                        "event: stream_complete\n"
                        f"data: {json.dumps({'run_id': run_id, 'status': payload.get('status', event), 'completion_reason': payload.get('completion_reason')})}\n\n"
                    )
                    return
            if snapshot["status"] in {"DONE", "FAILED", "CANCELLED"}:
                yield (
                    "event: stream_complete\n"
                    f"data: {json.dumps({'run_id': run_id, 'status': snapshot['status'], 'completion_reason': snapshot.get('completion_reason')})}\n\n"
                )
                return
            while True:
                event, payload = await queue.get()
                yield f"event: {event}\ndata: {json.dumps(payload)}\n\n"
                if event in {"run_done", "run_failed", "run_cancelled"}:
                    yield (
                        "event: stream_complete\n"
                        f"data: {json.dumps({'run_id': run_id, 'status': payload.get('status', event), 'completion_reason': payload.get('completion_reason')})}\n\n"
                    )
                    return
        finally:
            runner_service.unsubscribe(run_id, queue)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
