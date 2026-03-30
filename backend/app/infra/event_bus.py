from __future__ import annotations

import inspect
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable


@dataclass
class HealthChangedEvent:
    new_status: str
    signal_type: str
    cooldown_until: datetime | None


@dataclass
class HealthSignal:
    signal_type: str
    detected_at: datetime | None = None
    raw_signal: dict[str, Any] | None = None


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[type, list[Callable[..., Any]]] = {}

    def subscribe(self, event_type: type, handler: Callable[..., Any]) -> None:
        self._subscribers.setdefault(event_type, []).append(handler)

    async def emit(self, event: Any) -> None:
        for handler in self._subscribers.get(type(event), []):
            result = handler(event)
            if inspect.isawaitable(result):
                await result

