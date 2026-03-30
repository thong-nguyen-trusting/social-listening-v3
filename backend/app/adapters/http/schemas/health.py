from pydantic import BaseModel

from app.domain.entities.service_health import ServiceHealth


class HealthResponse(BaseModel):
    status: str
    version: str

    @classmethod
    def from_entity(cls, entity: ServiceHealth) -> "HealthResponse":
        return cls(
            status=entity.status,
            version=entity.version,
        )
