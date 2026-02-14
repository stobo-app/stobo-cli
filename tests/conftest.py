"""Shared fixtures for CLI tests."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure cli/tests is on sys.path so `import fixtures` works
sys.path.insert(0, str(Path(__file__).parent))

from stobo.client import StoboClient


@pytest.fixture()
def tmp_config(tmp_path: Path):
    """Override config dir to a temp directory."""
    config_dir = tmp_path / ".stobo"
    config_file = config_dir / "config.json"
    with (
        patch("stobo.config.CONFIG_DIR", config_dir),
        patch("stobo.config.CONFIG_FILE", config_file),
    ):
        yield config_dir, config_file


@pytest.fixture()
def mock_client():
    """Return a StoboClient with a mocked httpx transport."""
    import respx

    with respx.mock(base_url="https://api.trystobo.com") as router:
        client = StoboClient(api_key="sk_test_key", base_url="https://api.trystobo.com")
        yield client, router
        client.close()
