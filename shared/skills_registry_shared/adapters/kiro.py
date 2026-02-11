"""Kiro IDE/CLI adapter implementation."""

import json
import os
import shutil
from pathlib import Path

from .base import BaseAdapter, Scope, InstallMethod, InstallSummary
from ..schemas.agent import AgentInstallPackage

CACHE_DIR = ".skills-registry/cache"


class KiroAdapter(BaseAdapter):
    agent_type = "kiro"
    config_dir_name = ".kiro"

    def _home(self) -> Path:
        return Path.home()

    def get_skills_dir(self, scope: Scope) -> Path:
        if scope == Scope.GLOBAL:
            return self._home() / ".kiro" / "skills"
        return Path(".kiro") / "skills"

    def get_mcp_config_path(self, scope: Scope) -> Path:
        if scope == Scope.GLOBAL:
            return self._home() / ".kiro" / "settings" / "mcp.json"
        return Path(".kiro") / "settings" / "mcp.json"

    def get_agents_dir(self, scope: Scope) -> Path:
        if scope == Scope.GLOBAL:
            return self._home() / ".kiro" / "agents"
        return Path(".kiro") / "agents"

    def install_skill(
        self,
        skill_files: dict[str, str],
        name: str,
        scope: Scope,
        method: InstallMethod,
    ) -> Path:
        target_dir = self.get_skills_dir(scope) / name

        if method == InstallMethod.SYMLINK:
            cache_dir = Path(CACHE_DIR) / name
            cache_dir.mkdir(parents=True, exist_ok=True)
            # Write files to cache
            for rel_path, content in skill_files.items():
                file_path = cache_dir / rel_path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content, encoding="utf-8")
            # Create symlink
            target_dir.parent.mkdir(parents=True, exist_ok=True)
            if target_dir.is_symlink() or target_dir.exists():
                if target_dir.is_symlink():
                    target_dir.unlink()
                else:
                    shutil.rmtree(target_dir)
            target_dir.symlink_to(cache_dir.resolve())
        else:
            # Direct copy
            if target_dir.exists():
                shutil.rmtree(target_dir)
            target_dir.mkdir(parents=True, exist_ok=True)
            for rel_path, content in skill_files.items():
                file_path = target_dir / rel_path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content, encoding="utf-8")

        return target_dir

    def install_mcp(self, config: dict, scope: Scope) -> None:
        mcp_path = self.get_mcp_config_path(scope)
        mcp_path.parent.mkdir(parents=True, exist_ok=True)

        existing: dict = {}
        if mcp_path.exists():
            existing = json.loads(mcp_path.read_text(encoding="utf-8"))

        if "mcpServers" not in existing:
            existing["mcpServers"] = {}

        # Merge — overwrites existing server with same name
        existing["mcpServers"].update(config)
        mcp_path.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")

    def install_agent_config(
        self,
        package: AgentInstallPackage,
        scope: Scope,
        method: InstallMethod,
    ) -> InstallSummary:
        summary = InstallSummary(agent_type=self.agent_type)

        # 1. Install embedded skills
        for skill in package.embedded_skills:
            self.install_skill(skill.files, skill.name, scope, method)
            summary.skills_installed.append(skill.name)

        # 2. Install embedded MCPs
        for mcp in package.embedded_mcps:
            self.install_mcp(mcp.config, scope)
            summary.mcps_installed.append(mcp.name)

        # 3. Write agent config file
        agents_dir = self.get_agents_dir(scope)
        agents_dir.mkdir(parents=True, exist_ok=True)
        agent_file = agents_dir / f"{package.name}.json"

        agent_json = {
            "name": package.name,
            "prompt": package.prompt,
            "resources": [f"skill://.kiro/skills/**/SKILL.md"],
        }
        agent_file.write_text(json.dumps(agent_json, indent=2, ensure_ascii=False), encoding="utf-8")
        summary.agent_config_path = str(agent_file)
        summary.hints = self.get_post_install_hints()

        return summary

    def get_post_install_hints(self) -> str:
        return (
            "Kiro IDE: Skills installed — IDE will auto-discover them.\n"
            "Kiro CLI: Add to agent resources: \"skill://.kiro/skills/**/SKILL.md\""
        )
