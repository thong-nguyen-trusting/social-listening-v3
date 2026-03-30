from abc import ABC, abstractmethod


class RuntimeInfoProvider(ABC):
    """Port that exposes environment metadata to use cases."""

    @abstractmethod
    async def get_service_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def get_version(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def get_environment(self) -> str:
        raise NotImplementedError

