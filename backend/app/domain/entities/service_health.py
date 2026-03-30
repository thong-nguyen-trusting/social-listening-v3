from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class ServiceHealth:
    """Framework-free snapshot used by the health endpoint."""

    service: str
    version: str
    environment: str
    status: str
    checked_at: datetime

    @classmethod
    def healthy(cls, service: str, version: str, environment: str) -> "ServiceHealth":
        return cls(
            service=service,
            version=version,
            environment=environment,
            status="ok",
            checked_at=datetime.now(timezone.utc),
        )

