"""Skills Registry CLI — main entry point."""

import subprocess
import sys
from pathlib import Path

import httpx
import typer
from rich.console import Console
from rich.table import Table

from .client import RegistryClient
from .config import set_config, get_config, get_registry_url
from skills_registry_shared.parsers import parse_skill_md_file
from skills_registry_shared.adapters import AdapterFactory, Scope, InstallMethod

app = typer.Typer(name="agenthub", help="AgentHub CLI — AI Agent Skills Registry", pretty_exceptions_enable=False)
mcp_app = typer.Typer(name="mcp", help="MCP Server commands", pretty_exceptions_enable=False)
agent_app = typer.Typer(name="agent", help="Agent config commands", pretty_exceptions_enable=False)
config_app = typer.Typer(name="config", help="CLI configuration", pretty_exceptions_enable=False)
app.add_typer(mcp_app)
app.add_typer(agent_app)
app.add_typer(config_app)

console = Console(stderr=True)


def _client() -> RegistryClient:
    return RegistryClient()


def _handle_error(e: Exception) -> None:
    """Print a friendly error message and exit."""
    if isinstance(e, httpx.ConnectError):
        url = get_registry_url()
        console.print(f"[red]✗ Cannot connect to registry at {url}[/red]")
        console.print(f"  Is the server running? Try: [dim]skills config show[/dim]")
    elif isinstance(e, RuntimeError) and "API error" in str(e):
        console.print(f"[red]✗ {e}[/red]")
    elif isinstance(e, httpx.TimeoutException):
        console.print(f"[red]✗ Request timed out. The server may be slow or unreachable.[/red]")
    else:
        console.print(f"[red]✗ {e}[/red]")
    raise typer.Exit(1)


# ── Config ──────────────────────────────────────────

@config_app.command("set")
def config_set(key: str, value: str):
    """Set a config value (e.g. registry.url, registry.api_key)."""
    set_config(key, value)
    console.print(f"✓ Set {key}")


@config_app.command("show")
def config_show():
    """Show current configuration."""
    cfg = get_config()
    console.print(f"Registry URL: {cfg['registry']['url']}")
    api_key = cfg["registry"]["api_key"]
    masked = api_key[:6] + "..." if len(api_key) > 6 else "(not set)"
    console.print(f"API Key: {masked}")


# ── Skills ──────────────────────────────────────────

@app.command()
def publish():
    """Publish a skill from the current directory."""
    skill_md = Path("SKILL.md")
    if not skill_md.exists():
        console.print("[red]✗ SKILL.md not found in current directory.[/red]")
        raise typer.Exit(1)

    try:
        meta = parse_skill_md_file(skill_md)
    except Exception as e:
        console.print(f"[red]✗ Failed to parse SKILL.md: {e}[/red]")
        raise typer.Exit(1)

    try:
        git_url = subprocess.check_output(
            ["git", "remote", "get-url", "origin"], text=True
        ).strip()
        commit_hash = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        console.print("[red]✗ Not a git repository or git not installed.[/red]")
        raise typer.Exit(1)

    repo_root = Path(
        subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
    )
    skill_path = str(skill_md.parent.resolve().relative_to(repo_root))
    if skill_path == ".":
        skill_path = ""

    data = {
        "name": meta.name,
        "description": meta.description,
        "version": meta.version,
        "tags": meta.metadata.get("tags", []),
        "git_url": git_url,
        "git_ref": None,
        "commit_hash": commit_hash,
        "skill_path": skill_path,
        "readme_content": skill_md.read_text(encoding="utf-8"),
    }

    try:
        result = _client().create_skill(data)
        console.print(f"✓ Published [bold]{result['name']}[/bold] (id: {result['id']})")
    except Exception as e:
        _handle_error(e)


@app.command()
def add(name: str, agent: str = "kiro", method: str = "copy", scope: str = "workspace"):
    """Install a skill from the registry."""
    try:
        client = _client()
        results = client.search_skills(keyword=name)
        items = results.get("items", [])
        if not items:
            console.print(f"[yellow]No skill found matching '{name}'[/yellow]")
            raise typer.Exit(1)

        skill = items[0]
        package = client.get_skill_install(skill["id"])

        adapter = AdapterFactory.get_adapter(agent)
        s = Scope(scope)
        m = InstallMethod(method)
        path = adapter.install_skill(package["files"], package["name"], s, m)

        client.record_skill_install(skill["id"], agent_type=agent)
        console.print(f"✓ Installed [bold]{package['name']}[/bold] → {path}")
        console.print(adapter.get_post_install_hints())
    except typer.Exit:
        raise
    except Exception as e:
        _handle_error(e)


@app.command()
def find(keyword: str = typer.Argument("")):
    """Search for skills."""
    try:
        if keyword:
            results = _client().search_all(keyword)
        else:
            results = {"skills": _client().search_skills()}

        found = False
        for asset_type, data in results.items():
            items = data.get("items", []) if isinstance(data, dict) else []
            if not items:
                continue
            found = True
            table = Table(title=asset_type.capitalize())
            table.add_column("Name")
            table.add_column("Description")
            table.add_column("Installs", justify="right")
            for item in items[:20]:
                table.add_row(item["name"], item["description"][:60], str(item.get("installs", 0)))
            console.print(table)

        if not found:
            console.print(f"[yellow]No results found{' for ' + repr(keyword) if keyword else ''}.[/yellow]")
    except Exception as e:
        _handle_error(e)


@app.command("list")
def list_installed():
    """List locally installed skills."""
    table = Table(title="Installed Skills")
    table.add_column("Name")
    table.add_column("Scope")
    table.add_column("Path")

    for scope_name, base in [("workspace", Path(".kiro/skills")), ("global", Path.home() / ".kiro/skills")]:
        if base.exists():
            for d in base.iterdir():
                if d.is_dir() and (d / "SKILL.md").exists():
                    table.add_row(d.name, scope_name, str(d))

    console.print(table)


@app.command()
def remove(name: str):
    """Remove an installed skill."""
    import shutil
    for base in [Path(".kiro/skills"), Path.home() / ".kiro/skills"]:
        target = base / name
        if target.exists() or target.is_symlink():
            if target.is_symlink():
                target.unlink()
            else:
                shutil.rmtree(target)
            # Also clean cache
            cache = Path(f".skills-registry/cache/{name}")
            if cache.exists():
                shutil.rmtree(cache)
            console.print(f"✓ Removed [bold]{name}[/bold]")
            return
    console.print(f"[yellow]Skill '{name}' not found locally.[/yellow]")


# ── MCP ─────────────────────────────────────────────

@mcp_app.command("list")
def mcp_list():
    """List available MCP servers."""
    try:
        results = _client().search_mcps()
        items = results.get("items", [])
        table = Table(title="MCP Servers")
        table.add_column("Name")
        table.add_column("Description")
        table.add_column("Transport")
        for item in items:
            table.add_row(item["name"], item["description"][:60], item.get("transport", ""))
        console.print(table)
    except Exception as e:
        _handle_error(e)


@mcp_app.command("add")
def mcp_add(name: str, scope: str = "workspace"):
    """Install an MCP server config."""
    try:
        client = _client()
        results = client.search_mcps(keyword=name)
        items = results.get("items", [])
        if not items:
            console.print(f"[yellow]No MCP server found matching '{name}'[/yellow]")
            raise typer.Exit(1)

        mcp = items[0]
        config = client.get_mcp_install(mcp["id"])

        adapter = AdapterFactory.get_adapter("kiro")
        inner = config["config"].get("mcpServers", {})
        adapter.install_mcp(inner, Scope(scope))

        client.record_mcp_install(mcp["id"])
        console.print(f"✓ Added MCP Server [bold]{config['name']}[/bold] to mcp.json")
        if config.get("env_vars_needed"):
            console.print(f"  Environment variables to configure: {', '.join(config['env_vars_needed'])}")
    except typer.Exit:
        raise
    except Exception as e:
        _handle_error(e)


# ── Agent ───────────────────────────────────────────

@agent_app.command("list")
def agent_list():
    """List available agent configs."""
    try:
        results = _client().search_agents()
        items = results.get("items", [])
        table = Table(title="Agent Configs")
        table.add_column("Name")
        table.add_column("Description")
        table.add_column("Skills")
        table.add_column("MCPs")
        for item in items:
            table.add_row(
                item["name"],
                item["description"][:60],
                str(len(item.get("embedded_skills", []))),
                str(len(item.get("embedded_mcps", []))),
            )
        console.print(table)
    except Exception as e:
        _handle_error(e)


@agent_app.command("add")
def agent_add(name: str, scope: str = "workspace", method: str = "copy"):
    """Install an agent config (full package)."""
    try:
        client = _client()
        results = client.search_agents(keyword=name)
        items = results.get("items", [])
        if not items:
            console.print(f"[yellow]No agent config found matching '{name}'[/yellow]")
            raise typer.Exit(1)

        agent = items[0]
        package_data = client.get_agent_install(agent["id"])

        from skills_registry_shared.schemas.agent import AgentInstallPackage
        package = AgentInstallPackage(**package_data)

        adapter = AdapterFactory.get_adapter("kiro")
        summary = adapter.install_agent_config(package, Scope(scope), InstallMethod(method))

        client.record_agent_install(agent["id"])
        console.print(f"✓ Installed Agent: [bold]{package.name}[/bold]")
        console.print(f"  Skills: {len(summary.skills_installed)} installed")
        console.print(f"  MCP Servers: {len(summary.mcps_installed)} configured")
        console.print(summary.hints)
    except typer.Exit:
        raise
    except Exception as e:
        _handle_error(e)


if __name__ == "__main__":
    app()
