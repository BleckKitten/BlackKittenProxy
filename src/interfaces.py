"""Core interfaces used by the proxy components."""

from abc import ABC, abstractmethod


class IBlacklistManager(ABC):
    @abstractmethod
    def is_blocked(self, domain: str) -> bool:
        ...

    @abstractmethod
    async def check_domain(self, domain: bytes) -> None:
        ...


class ILogger(ABC):
    @abstractmethod
    def log_access(self, message: str) -> None:
        ...

    @abstractmethod
    def log_error(self, message: str) -> None:
        ...

    @abstractmethod
    def info(self, message: str) -> None:
        ...

    @abstractmethod
    def error(self, message: str) -> None:
        ...


class IStatistics(ABC):
    @abstractmethod
    def increment_total_connections(self) -> None:
        ...

    @abstractmethod
    def increment_allowed_connections(self) -> None:
        ...

    @abstractmethod
    def increment_blocked_connections(self) -> None:
        ...

    @abstractmethod
    def increment_error_connections(self) -> None:
        ...

    @abstractmethod
    def update_traffic(self, incoming: int, outgoing: int) -> None:
        ...

    @abstractmethod
    def update_speeds(self) -> None:
        ...

    @abstractmethod
    def get_stats_display(self) -> str:
        ...


class IConnectionHandler(ABC):
    @abstractmethod
    async def handle_connection(self, reader, writer) -> None:
        ...


class IAutostartManager(ABC):
    @staticmethod
    @abstractmethod
    def manage_autostart(action: str) -> None:
        ...
