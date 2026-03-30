from app.domain.interfaces.runtime_info_provider import RuntimeInfoProvider
from app.infrastructure.config import Settings


class SettingsRuntimeInfoProvider(RuntimeInfoProvider):
    """Infrastructure adapter backed by application settings."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def get_service_name(self) -> str:
        return self._settings.app_name

    async def get_version(self) -> str:
        return self._settings.app_version

    async def get_environment(self) -> str:
        return self._settings.environment

