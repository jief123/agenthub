"""Git operations — shallow clone, skill discovery, cleanup."""

import asyncio
import shutil
import tempfile
from pathlib import Path

from ..config import settings

_semaphore = asyncio.Semaphore(settings.GIT_MAX_CONCURRENT)


class GitError(Exception):
    pass


async def clone_shallow(url: str, ref: str | None = None) -> Path:
    """Shallow-clone a git repo to a temp directory."""
    async with _semaphore:
        tmp = Path(tempfile.mkdtemp(prefix="skills-"))
        cmd = ["git", "clone", "--depth", "1"]
        if ref:
            cmd += ["--branch", ref]
        cmd += [url, str(tmp)]

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=settings.GIT_CLONE_TIMEOUT
            )
            if proc.returncode != 0:
                raise GitError(f"git clone failed: {stderr.decode().strip()}")
        except asyncio.TimeoutError:
            cleanup(tmp)
            raise GitError(f"git clone timed out after {settings.GIT_CLONE_TIMEOUT}s")
        except FileNotFoundError:
            cleanup(tmp)
            raise GitError("git is not installed or not in PATH")

        return tmp


async def get_commit_hash(repo_dir: Path) -> str:
    proc = await asyncio.create_subprocess_exec(
        "git", "rev-parse", "HEAD",
        cwd=str(repo_dir),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    return stdout.decode().strip()


async def discover_skills(repo_dir: Path) -> list[dict]:
    """Find all SKILL.md files in a repo (same patterns as skills.sh)."""
    import glob

    patterns = [
        "SKILL.md",
        "skills/**/SKILL.md",
        ".kiro/skills/**/SKILL.md",
        ".claude/skills/**/SKILL.md",
        ".agents/skills/**/SKILL.md",
    ]
    found = []
    for pattern in patterns:
        for match in glob.glob(str(repo_dir / pattern), recursive=True):
            p = Path(match)
            rel = p.parent.relative_to(repo_dir)
            found.append({"path": str(rel), "skill_md": str(p)})

    return found


def cleanup(repo_dir: Path) -> None:
    """Remove a temporary repo directory."""
    if repo_dir.exists():
        shutil.rmtree(repo_dir, ignore_errors=True)
