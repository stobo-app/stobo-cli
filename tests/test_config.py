"""Tests for stobo/config.py."""

from __future__ import annotations

import json
import os

from stobo import config


def test_load_empty(tmp_config):
    """load() returns empty dict when no config file."""
    assert config.load() == {}


def test_save_and_load(tmp_config):
    """save() persists data, load() reads it back."""
    config.save({"api_key": "sk_test", "base_url": "http://localhost"})
    data = config.load()
    assert data["api_key"] == "sk_test"
    assert data["base_url"] == "http://localhost"


def test_set_and_get_api_key(tmp_config):
    """set_api_key stores, get_api_key retrieves."""
    config.set_api_key("sk_abc123")
    assert config.get_api_key() == "sk_abc123"


def test_env_var_overrides_file(tmp_config, monkeypatch):
    """STOBO_API_KEY env var takes priority over config file."""
    config.set_api_key("sk_from_file")
    monkeypatch.setenv("STOBO_API_KEY", "sk_from_env")
    assert config.get_api_key() == "sk_from_env"


def test_get_base_url_default(tmp_config):
    """Default base URL when nothing is set."""
    assert config.get_base_url() == "https://api.trystobo.com"


def test_base_url_env_override(tmp_config, monkeypatch):
    """STOBO_BASE_URL env var overrides config."""
    config.set_base_url("https://stored.example.com")
    monkeypatch.setenv("STOBO_BASE_URL", "https://env.example.com")
    assert config.get_base_url() == "https://env.example.com"


def test_clear(tmp_config):
    """clear() removes config file."""
    _, config_file = tmp_config
    config.save({"api_key": "sk_test"})
    assert config_file.exists()
    config.clear()
    assert not config_file.exists()


def test_clear_no_file(tmp_config):
    """clear() is a no-op when no config file exists."""
    config.clear()  # Should not raise
