"""SKILL.md parser — extracts YAML frontmatter and markdown body."""

import re
import yaml
from pathlib import Path

from ..schemas.skill import SkillMetadata

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)", re.DOTALL)
NAME_RE = re.compile(r"^[a-z0-9-]+$")


class SkillParseError(Exception):
    """Raised when SKILL.md parsing fails."""

    def __init__(self, message: str, line: int | None = None):
        self.line = line
        super().__init__(message)


def parse_skill_md(content: str) -> SkillMetadata:
    """Parse SKILL.md content and return structured metadata.

    Args:
        content: Raw SKILL.md file content.

    Returns:
        SkillMetadata with extracted frontmatter fields and markdown body.

    Raises:
        SkillParseError: If frontmatter is missing, malformed, or required fields are absent.
    """
    content = content.strip()
    if not content:
        raise SkillParseError("SKILL.md is empty")

    match = FRONTMATTER_RE.match(content)
    if not match:
        raise SkillParseError("SKILL.md must start with YAML frontmatter (--- delimiters)", line=1)

    yaml_str, body = match.group(1), match.group(2).strip()

    try:
        data = yaml.safe_load(yaml_str)
    except yaml.YAMLError as e:
        raise SkillParseError(f"Invalid YAML in frontmatter: {e}") from e

    if not isinstance(data, dict):
        raise SkillParseError("Frontmatter must be a YAML mapping")

    name = data.get("name")
    if not name:
        raise SkillParseError("'name' is required in frontmatter")
    if not isinstance(name, str) or not NAME_RE.match(name):
        raise SkillParseError("'name' must be lowercase alphanumeric with hyphens only")
    if len(name) > 64:
        raise SkillParseError("'name' must be at most 64 characters")

    description = data.get("description")
    if not description:
        raise SkillParseError("'description' is required in frontmatter")
    if not isinstance(description, str):
        raise SkillParseError("'description' must be a string")
    if len(description) > 1024:
        raise SkillParseError("'description' must be at most 1024 characters")

    # Extract known fields, rest goes to metadata
    known_keys = {"name", "description", "version", "license", "compatibility", "metadata"}
    extra_metadata = data.get("metadata", {})
    if not isinstance(extra_metadata, dict):
        raise SkillParseError("'metadata' must be a key-value mapping")

    # Collect unknown top-level keys into metadata
    for key in data:
        if key not in known_keys:
            extra_metadata[key] = data[key]

    return SkillMetadata(
        name=name,
        description=description,
        version=str(data["version"]) if data.get("version") is not None else None,
        license=data.get("license"),
        compatibility=data.get("compatibility"),
        metadata=extra_metadata,
        body=body,
    )


def parse_skill_md_file(path: Path) -> SkillMetadata:
    """Parse a SKILL.md file from disk."""
    if not path.exists():
        raise SkillParseError(f"File not found: {path}")
    content = path.read_text(encoding="utf-8")
    return parse_skill_md(content)
