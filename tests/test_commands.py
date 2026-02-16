"""Tests for CLI commands via typer.testing.CliRunner."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from stobo.cli import app
from fixtures import SAMPLE_AUDIT, SAMPLE_CREDITS, SAMPLE_LLMS_TXT, SAMPLE_ME, SAMPLE_ROBOTS_TXT, SAMPLE_SITE_AUDIT, SAMPLE_TONE

runner = CliRunner()


def _invoke(args: list[str], api_key: str = "sk_test") -> object:
    """Invoke CLI with patched config and client."""
    with (
        patch("stobo.config.get_api_key", return_value=api_key),
        patch("stobo.config.get_base_url", return_value="https://api.trystobo.com"),
    ):
        return runner.invoke(app, args)


# ── Version & help ──────────────────────────────────────────────────


def test_version():
    from stobo import __version__
    result = _invoke(["--version"])
    assert __version__ in result.output


def test_help():
    result = _invoke(["--help"])
    assert "audit" in result.output
    assert "tone" in result.output


# ── Auth ────────────────────────────────────────────────────────────


def test_auth_login():
    with patch("stobo.commands.auth.StoboClient") as MockClient:
        instance = MockClient.return_value
        instance.get_me.return_value = SAMPLE_ME
        with patch("stobo.config.set_api_key") as mock_save:
            result = runner.invoke(app, ["auth", "login", "--api-key", "sk_new_key"])
            assert result.exit_code == 0
            assert "Logged in" in result.output
            mock_save.assert_called_once_with("sk_new_key")


def test_auth_status():
    with (
        patch("stobo.client.StoboClient.get_me", return_value=SAMPLE_ME),
        patch("stobo.config.get_api_key", return_value="sk_test_key123"),
        patch("stobo.config.get_base_url", return_value="https://api.trystobo.com"),
    ):
        result = runner.invoke(app, ["auth", "status"])
        assert result.exit_code == 0
        assert "user@example.com" in result.output


def test_auth_logout():
    with patch("stobo.config.clear") as mock_clear:
        result = runner.invoke(app, ["auth", "logout"])
        assert result.exit_code == 0
        assert "Logged out" in result.output
        mock_clear.assert_called_once()


# ── Audit ───────────────────────────────────────────────────────────


def test_audit_run():
    with patch("stobo.client.StoboClient.audit_article", return_value=SAMPLE_AUDIT):
        result = _invoke(["audit", "run", "https://example.com"])
        assert result.exit_code == 0
        assert "C" in result.output  # grade


def test_audit_run_json():
    with patch("stobo.client.StoboClient.audit_article", return_value=SAMPLE_AUDIT):
        result = _invoke(["--json", "audit", "run", "https://example.com"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["grade"] == "C"


def test_audit_run_seo_only():
    with patch("stobo.client.StoboClient.audit_seo", return_value={"url": "https://example.com", "seo_audit": {}}):
        result = _invoke(["audit", "run", "https://example.com", "--seo-only"])
        assert result.exit_code == 0


def test_audit_list():
    with patch("stobo.client.StoboClient.list_audits", return_value=[SAMPLE_AUDIT]):
        result = _invoke(["audit", "list"])
        assert result.exit_code == 0
        assert "example.com" in result.output


# ── Site Audit ─────────────────────────────────────────────────────


def test_audit_site():
    with patch("stobo.client.StoboClient.audit_site", return_value=SAMPLE_SITE_AUDIT):
        result = _invoke(["audit", "site", "https://phantombuster.com"])
        assert result.exit_code == 0
        assert "phantombuster.com" in result.output
        assert "72.4" in result.output  # combined_percentage


def test_audit_site_json():
    with patch("stobo.client.StoboClient.audit_site", return_value=SAMPLE_SITE_AUDIT):
        result = _invoke(["--json", "audit", "site", "https://phantombuster.com"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["domain"] == "phantombuster.com"
        assert data["combined_percentage"] == 72.4


# ── Tone ────────────────────────────────────────────────────────────


def test_tone_extract():
    with patch("stobo.client.StoboClient.extract_tone", return_value=SAMPLE_TONE):
        result = _invoke(["tone", "extract", "https://blog.example.com"])
        assert result.exit_code == 0
        assert "Extracted" in result.output


def test_tone_list():
    with patch("stobo.client.StoboClient.list_tone_profiles", return_value=["example-com"]):
        result = _invoke(["tone", "list"])
        assert result.exit_code == 0
        assert "example-com" in result.output


# ── Optimize ────────────────────────────────────────────────────────


def test_optimize_no_wait():
    with patch("stobo.client.StoboClient.optimize", return_value={"job_id": "abc-123", "status": "pending"}):
        result = _invoke(["optimize", "run", "https://example.com", "--no-wait"])
        assert result.exit_code == 0
        assert "abc-123" in result.output


# ── Credits ────────────────────────────────────────────────────────


def test_credits():
    with patch("stobo.client.StoboClient.get_credits", return_value=SAMPLE_CREDITS):
        result = _invoke(["credits"])
        assert result.exit_code == 0
        assert "9,500" in result.output
        assert "starter" in result.output


# ── llms.txt ──────────────────────────────────────────────────────


def test_llms_generate():
    with patch("stobo.client.StoboClient.generate_llms_txt", return_value=SAMPLE_LLMS_TXT):
        result = _invoke(["llms", "generate", "https://phantombuster.com"])
        assert result.exit_code == 0
        assert "phantombuster.com" in result.output


def test_llms_generate_json():
    with patch("stobo.client.StoboClient.generate_llms_txt", return_value=SAMPLE_LLMS_TXT):
        result = _invoke(["--json", "llms", "generate", "https://phantombuster.com"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["domain"] == "phantombuster.com"


# ── robots.txt ──────────────────────────────────────────────────


def test_robots_generate():
    with patch("stobo.client.StoboClient.generate_robots_txt", return_value=SAMPLE_ROBOTS_TXT):
        result = _invoke(["robots", "generate", "https://scorejam.ai"])
        assert result.exit_code == 0
        assert "scorejam.ai" in result.output
        assert "25/25" in result.output


def test_robots_generate_json():
    with patch("stobo.client.StoboClient.generate_robots_txt", return_value=SAMPLE_ROBOTS_TXT):
        result = _invoke(["--json", "robots", "generate", "https://scorejam.ai"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["domain"] == "scorejam.ai"
        assert data["new_score"] == 25
