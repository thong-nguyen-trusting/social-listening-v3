from app.domain.entities.service_health import ServiceHealth
from app.domain.interfaces.runtime_info_provider import RuntimeInfoProvider


class GetHealthStatusUseCase:
    """Thin use case for CP0 that keeps HTTP concerns outside the core."""

    def __init__(self, runtime_info_provider: RuntimeInfoProvider) -> None:
        self._runtime_info_provider = runtime_info_provider

    async def execute(self) -> ServiceHealth:
        service = await self._runtime_info_provider.get_service_name()
        version = await self._runtime_info_provider.get_version()
        environment = await self._runtime_info_provider.get_environment()
        return ServiceHealth.healthy(
            service=service,
            version=version,
            environment=environment,
        )

