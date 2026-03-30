from functools import lru_cache

from app.application.use_cases.get_health_status import GetHealthStatusUseCase
from app.domain.interfaces.runtime_info_provider import RuntimeInfoProvider
from app.infrastructure.config import Settings, get_settings
from app.infrastructure.runtime_info import SettingsRuntimeInfoProvider


@lru_cache
def get_runtime_info_provider() -> RuntimeInfoProvider:
    settings = get_settings()
    return SettingsRuntimeInfoProvider(settings=settings)


def get_health_status_use_case() -> GetHealthStatusUseCase:
    return GetHealthStatusUseCase(
        runtime_info_provider=get_runtime_info_provider(),
    )


def get_app_settings() -> Settings:
    return get_settings()

