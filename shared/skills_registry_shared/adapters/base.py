"""Base adapter interface for agent-specific file operations."""

from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from pydantic import BaseModel

from ..schemas.agent import AgentInstallPackage


class Scope(str, Enum):
    WORKSPACE = "workspace"
    GLOBAL = "global"


class InstallMethod(str, Enum):
    SYMLINK = "symlink"
    COPY = "copy"


class InstallSummary(BaseModel):
    agent_type: str
    skills_installed: list[str] = []
    mcps_installed: list[str] = []
    agent_config_path: str | None = None
    hints: str = ""


class BaseAdapter(ABC):
    """Abstract base class for agent adapters."""

    agent_type: str = ""
    config_dir_name: str = ""  # e.g. ".kiro", ".claude"

    @abstractmethod
    def get_skills_dir(self, scope: Scope) -> Path:
        """Return the skills directory path for the given scope."""

    @abstractmethod
    def get_mcp_config_path(self, scope: Scope) -> Path:
        """Return the mcp.json config file path."""

    @abstractmethod
    def get_agents_dir(self, scope: Scope) -> Path:
        """Return the agents config directory path."""

    @abstractmethod
    def install_skill(
        self,
        skill_files: dict[str, str],
        name: str,
        scope: Scope,
        method: InstallMethod,
    ) -> Path:
        """Install skill files to the agent's skills directory."""

    @abstractmethod
    def install_mcp(self, config: dict, scope: Scope) -> None:
        """Merge MCP server config into the agent's mcp.json."""

    @abstractmethod
    def install_agent_config(
        self,
        package: AgentInstallPackage,
        scope: Scope,
        method: InstallMethod,
    ) -> InstallSummary:
        """Install a complete agent package (skills + mcps + agent config)."""

    @abstractmethod
    def get_post_install_hints(self) -> str:
        """Return post-install hints for the user."""

    def is_installed(self) -> bool:
        """Check if this agent's config directory exists in the current workspace."""
        return Path(self.config_dir_name).is_dir()
