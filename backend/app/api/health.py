from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, HTTPException, Request

from app.infra.event_bus import HealthSignal
from app.schemas.health import HealthResetResponse, HealthStatusResponse

router = APIRouter(prefix="/api/health", tags=["health-monitor"])


async def _read_json_body(request: Request) -> dict[str, Any]:
    raw = await request.body()
    if not raw:
        return {}
    try:
        return json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError:
        return {}


@router.get("/status", response_model=HealthStatusResponse)
async def health_status(request: Request) -> HealthStatusResponse:
    state, log = request.app.state.health_monitor.get_status_snapshot()
    last_signal = None
    if log is not None:
        last_signal = {
            "type": log.signal_type,
            "detected_at": log.detected_at,
        }
    return HealthStatusResponse(
        status=state.status,
        cooldown_until=state.cooldown_until,
        last_signal=last_signal,
    )


@router.post("/acknowledge")
async def acknowledge(request: Request) -> dict[str, bool]:
    payload = await _read_json_body(request)
    signal_log_id = payload.get("signal_log_id")
    if signal_log_id:
        request.app.state.health_monitor.acknowledge(signal_log_id)
    return {"ok": True}


@router.post("/reset", response_model=HealthResetResponse)
async def reset_health(request: Request) -> HealthResetResponse:
    payload = await _read_json_body(request)
    try:
        state = await request.app.state.health_monitor.reset(bool(payload.get("confirm")))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return HealthResetResponse(status=state.status)


@router.post("/_test/signal")
async def emit_test_signal(request: Request) -> dict[str, bool]:
    payload = await _read_json_body(request)
    signal = payload.get("signal", "")
    if not signal:
        raise HTTPException(status_code=400, detail="signal is required")
    await request.app.state.health_monitor.process_signal(
        HealthSignal(signal_type=signal, raw_signal={"source": "test-endpoint"})
    )
    return {"ok": True}
