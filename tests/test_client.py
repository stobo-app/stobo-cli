"""Tests for stobo/client.py with mocked HTTP."""

from __future__ import annotations

import httpx
import pytest
import respx

from stobo.client import (
    AuthError,
    NotFoundError,
    RateLimitError,
    ServerError,
    StoboClient,
)
from fixtures import SAMPLE_AUDIT, SAMPLE_CREDITS, SAMPLE_JOB, SAMPLE_LLMS_TXT, SAMPLE_ROBOTS_TXT, SAMPLE_SITE_AUDIT, SAMPLE_TONE


@pytest.fixture()
def client():
    with respx.mock(base_url="https://api.trystobo.com") as router:
        c = StoboClient(api_key="sk_test", base_url="https://api.trystobo.com")
        yield c, router
        c.close()


def test_get_me(client):
    c, router = client
    router.get("/api/v1/auth/me").respond(json={"email": "test@example.com", "full_name": "Test"})
    result = c.get_me()
    assert result["email"] == "test@example.com"


def test_audit_article(client):
    c, router = client
    router.post("/api/v1/article-audit").respond(json=SAMPLE_AUDIT, status_code=201)
    result = c.audit_article("https://example.com")
    assert result["grade"] == "C"


def test_get_audit(client):
    c, router = client
    router.get("/api/v1/article-audit/aaaa-bbbb-cccc").respond(json=SAMPLE_AUDIT)
    result = c.get_audit("aaaa-bbbb-cccc")
    assert result["id"] == "aaaa-bbbb-cccc"


def test_list_audits(client):
    c, router = client
    router.get("/api/v1/article-audit").respond(json=[SAMPLE_AUDIT])
    results = c.list_audits()
    assert len(results) == 1


def test_audit_seo(client):
    c, router = client
    router.post("/api/v1/article-seo").respond(json={"url": "https://example.com", "seo_audit": {}}, status_code=201)
    result = c.audit_seo("https://example.com")
    assert "seo_audit" in result


def test_audit_aeo(client):
    c, router = client
    router.post("/api/v1/article-aeo").respond(json={"url": "https://example.com", "aeo_audit": {}}, status_code=201)
    result = c.audit_aeo("https://example.com")
    assert "aeo_audit" in result


def test_audit_site(client):
    c, router = client
    router.post("/api/v1/site-audit").respond(json=SAMPLE_SITE_AUDIT, status_code=201)
    result = c.audit_site("https://phantombuster.com")
    assert result["domain"] == "phantombuster.com"
    assert result["combined_percentage"] == 72.4
    assert result["aeo_audit"]["robots_ai"]["status"] == "excellent"
    assert result["blog_detection"]["has_blog"] is True


def test_extract_tone(client):
    c, router = client
    router.post("/api/v1/tone/extract").respond(json=SAMPLE_TONE)
    result = c.extract_tone("https://blog.example.com")
    assert result["articles_analyzed"] == 8


def test_get_tone(client):
    c, router = client
    router.get("/api/v1/tone/example-com").respond(json=SAMPLE_TONE["profile"])
    result = c.get_tone("example-com")
    assert "tone_descriptors" in result


def test_list_tone_profiles(client):
    c, router = client
    router.get("/api/v1/tone").respond(json=["example-com", "other-brand"])
    result = c.list_tone_profiles()
    assert len(result) == 2


def test_optimize(client):
    c, router = client
    router.post("/api/v1/optimize").respond(json={"job_id": "dddd-eeee-ffff", "status": "pending"})
    result = c.optimize("https://example.com")
    assert result["job_id"] == "dddd-eeee-ffff"


def test_get_job(client):
    c, router = client
    router.get("/api/v1/optimize/jobs/dddd-eeee-ffff").respond(json=SAMPLE_JOB)
    result = c.get_job("dddd-eeee-ffff")
    assert result["status"] == "completed"


def test_freshness_audit(client):
    c, router = client
    router.post("/api/v1/freshness-audit").respond(
        json={"id": "ff-11", "domain": "example.com", "results": []}, status_code=201,
    )
    result = c.freshness_audit("https://example.com/sitemap.xml")
    assert result["domain"] == "example.com"


def test_export(client):
    c, router = client
    router.post("/api/v1/export").respond(json={"markdown": "# Report", "data_type": "brand_voice"})
    result = c.export("example-com", "brand_voice")
    assert "markdown" in result


# ── Error handling ──────────────────────────────────────────────────


def test_401_raises_auth_error(client):
    c, router = client
    router.get("/api/v1/auth/me").respond(json={"detail": "Invalid key"}, status_code=401)
    with pytest.raises(AuthError):
        c.get_me()


def test_404_raises_not_found(client):
    c, router = client
    router.get("/api/v1/article-audit/missing").respond(json={"detail": "Not found"}, status_code=404)
    with pytest.raises(NotFoundError):
        c.get_audit("missing")


def test_429_raises_rate_limit(client):
    c, router = client
    router.post("/api/v1/article-audit").respond(json={"detail": "Too many requests"}, status_code=429)
    with pytest.raises(RateLimitError):
        c.audit_article("https://example.com")


def test_500_raises_server_error(client):
    c, router = client
    router.post("/api/v1/article-audit").respond(json={"detail": "Internal error"}, status_code=500)
    with pytest.raises(ServerError):
        c.audit_article("https://example.com")


# ── Credits ────────────────────────────────────────────────────────


def test_get_credits(client):
    c, router = client
    router.get("/api/v1/credits/usage").respond(json=SAMPLE_CREDITS)
    result = c.get_credits()
    assert result["remaining"] == 9500
    assert result["plan"] == "starter"


# ── llms.txt ──────────────────────────────────────────────────────


def test_generate_llms_txt(client):
    c, router = client
    router.post("/api/v1/llms-txt/generate").respond(json=SAMPLE_LLMS_TXT)
    result = c.generate_llms_txt("https://phantombuster.com")
    assert result["domain"] == "phantombuster.com"
    assert "PhantomBuster" in result["content"]


# ── robots.txt ──────────────────────────────────────────────────


def test_generate_robots_txt(client):
    c, router = client
    router.post("/api/v1/robots-txt/generate").respond(json=SAMPLE_ROBOTS_TXT, status_code=201)
    result = c.generate_robots_txt("https://scorejam.ai")
    assert result["domain"] == "scorejam.ai"
    assert result["new_score"] == 25
    assert "GPTBot" in result["crawlers_added"]
