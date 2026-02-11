"""Agent Adapter layer — abstracts IDE/agent file path and config format differences."""

from .base import BaseAdapter, Scope, InstallMethod, InstallSummary
from .kiro import KiroAdapter
from .factory import AdapterFactory

__all__ = [
    "BaseAdapter", "Scope", "InstallMethod", "InstallSummary",
    "KiroAdapter", "AdapterFactory",
]
