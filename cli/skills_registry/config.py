"""CLI configuration management — ~/.skills-registry/config.toml"""

import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".agenthub"
CONFIG_FILE = CONFIG_DIR / "config.toml"


def _ensure_config():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(
            '[registry]\nurl = "http://localhost:8000"\napi_key = ""\n',
            encoding="utf-8",
        )


def get_config() -> dict:
    _ensure_config()
    # Simple TOML parser (avoid extra dependency)
    config = {"registry": {"url": "http://localhost:8000", "api_key": ""}}
    for line in CONFIG_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("url"):
            config["registry"]["url"] = line.split("=", 1)[1].strip().strip('"')
        elif line.startswith("api_key"):
            config["registry"]["api_key"] = line.split("=", 1)[1].strip().strip('"')
    return config


def set_config(key: str, value: str):
    _ensure_config()
    config = get_config()
    parts = key.split(".")
    if len(parts) == 2 and parts[0] == "registry":
        config["registry"][parts[1]] = value
    content = f'[registry]\nurl = "{config["registry"]["url"]}"\napi_key = "{config["registry"]["api_key"]}"\n'
    CONFIG_FILE.write_text(content, encoding="utf-8")


def get_registry_url() -> str:
    return os.getenv("SKILLS_REGISTRY_URL", get_config()["registry"]["url"])


def get_api_key() -> str:
    return os.getenv("SKILLS_REGISTRY_API_KEY", get_config()["registry"]["api_key"])
