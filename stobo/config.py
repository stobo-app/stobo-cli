"""~/.stobo/config.json management."""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path
from typing import Any

CONFIG_DIR = Path.home() / ".stobo"
CONFIG_FILE = CONFIG_DIR / "config.json"
DEFAULT_BASE_URL = "https://api.trystobo.com"
ENV_API_KEY = "STOBO_API_KEY"
ENV_BASE_URL = "STOBO_BASE_URL"


def _ensure_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load() -> dict[str, Any]:
    if not CONFIG_FILE.exists():
        return {}
    return json.loads(CONFIG_FILE.read_text())


def save(data: dict[str, Any]) -> None:
    _ensure_dir()
    CONFIG_FILE.write_text(json.dumps(data, indent=2) + "\n")
    CONFIG_FILE.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 600 — owner-only


def get_api_key() -> str | None:
    """Return API key. Priority: env var > config file."""
    env_key = os.environ.get(ENV_API_KEY)
    if env_key:
        return env_key
    return load().get("api_key")


def set_api_key(key: str) -> None:
    data = load()
    data["api_key"] = key
    save(data)


def get_base_url() -> str:
    """Return base URL. Priority: env var > config file > default."""
    env_url = os.environ.get(ENV_BASE_URL)
    if env_url:
        return env_url
    return load().get("base_url", DEFAULT_BASE_URL)


def set_base_url(url: str) -> None:
    data = load()
    data["base_url"] = url
    save(data)


def clear() -> None:
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
