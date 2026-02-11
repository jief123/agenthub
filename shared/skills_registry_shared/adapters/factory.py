"""Adapter factory — returns the appropriate adapter for a given agent type."""

from .base import BaseAdapter
from .kiro import KiroAdapter


class UnsupportedAgentError(Exception):
    """Raised when an unsupported agent type is requested."""


_ADAPTERS: dict[str, type[BaseAdapter]] = {
    "kiro": KiroAdapter,
}


class AdapterFactory:
    @staticmethod
    def get_adapter(agent_type: str) -> BaseAdapter:
        cls = _ADAPTERS.get(agent_type)
        if cls is None:
            supported = ", ".join(_ADAPTERS.keys())
            raise UnsupportedAgentError(
                f"Unsupported agent type: '{agent_type}'. Supported: {supported}"
            )
        return cls()

    @staticmethod
    def detect_installed_agents() -> list[str]:
        """Detect which agents are installed in the current workspace."""
        return [name for name, cls in _ADAPTERS.items() if cls().is_installed()]

    @staticmethod
    def get_supported_agents() -> list[str]:
        return list(_ADAPTERS.keys())
