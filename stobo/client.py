"""StoboClient — thin httpx wrapper mapping 1:1 to REST API."""

from __future__ import annotations

from typing import Any

import httpx


# ── Exceptions ──────────────────────────────────────────────────────


class StoboAPIError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"HTTP {status_code}: {detail}")


class AuthError(StoboAPIError):
    pass


class NotFoundError(StoboAPIError):
    pass


class RateLimitError(StoboAPIError):
    pass


class ServerError(StoboAPIError):
    pass


_ERROR_MAP: dict[int, type[StoboAPIError]] = {
    401: AuthError,
    403: AuthError,
    404: NotFoundError,
    429: RateLimitError,
}


def _raise_for_status(resp: httpx.Response) -> None:
    if resp.is_success:
        return
    detail = resp.text
    try:
        body = resp.json()
        detail = body.get("detail", detail)
    except Exception:
        pass
    exc_cls = _ERROR_MAP.get(resp.status_code, ServerError)
    raise exc_cls(resp.status_code, detail)


# ── Client ──────────────────────────────────────────────────────────


def normalize_url(url: str) -> str:
    """Prepend https:// if no scheme is present. Reject non-HTTP schemes."""
    url = url.strip()
    if not url:
        return url
    if url.startswith(("http://", "https://")):
        return url
    if "://" in url or ":" in url.split("/", 1)[0]:
        raise ValueError(f"Unsupported URL scheme: {url.split(':', 1)[0]}")
    return f"https://{url}"


class StoboClient:
    DEFAULT_USER_AGENT = "stobo-cli/0.3.7"

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.trystobo.com",
        user_agent: str | None = None,
        source: str = "cli",
    ):
        self.base_url = base_url.rstrip("/")
        headers: dict[str, str] = {
            "User-Agent": user_agent or self.DEFAULT_USER_AGENT,
            "X-Audit-Source": source,
        }
        if api_key:
            headers["X-API-Key"] = api_key
        self._http = httpx.Client(
            base_url=self.base_url,
            headers=headers,
            timeout=180.0,
        )

    def close(self) -> None:
        self._http.close()

    # ── helpers ──

    def _get(self, path: str, **params: Any) -> Any:
        resp = self._http.get(path, params={k: v for k, v in params.items() if v is not None})
        _raise_for_status(resp)
        return resp.json()

    def _post(self, path: str, json: dict | None = None, **params: Any) -> Any:
        resp = self._http.post(
            path,
            json=json,
            params={k: v for k, v in params.items() if v is not None},
        )
        _raise_for_status(resp)
        return resp.json()

    def _delete(self, path: str) -> Any:
        resp = self._http.delete(path)
        _raise_for_status(resp)
        if resp.status_code == 204:
            return None
        return resp.json()

    # ── Auth ──

    def get_me(self) -> dict:
        return self._get("/api/v1/auth/me")

    # ── Article Audits (full SEO + AEO) ──

    def audit_article(self, url: str, keyword: str | None = None, use_playwright: bool = False) -> dict:
        body: dict[str, Any] = {"url": url}
        if keyword:
            body["keyword"] = keyword
        if use_playwright:
            body["use_playwright"] = True
        return self._post("/api/v1/article-audit", json=body)

    def get_audit(self, audit_id: str) -> dict:
        return self._get(f"/api/v1/article-audit/{audit_id}")

    def get_audit_by_url(self, url: str) -> dict:
        return self._get("/api/v1/article-audit/by-url", url=url)

    def list_audits(self, skip: int = 0, limit: int = 50) -> list[dict]:
        return self._get("/api/v1/article-audit", skip=skip, limit=limit)

    # ── Site Audit (combined SEO + AEO + blog detection) ──

    def audit_site(self, url: str) -> dict:
        return self._post("/api/v1/site-audit", json={"url": url})

    # ── SEO-only ──

    def audit_seo(self, url: str, keyword: str | None = None) -> dict:
        body: dict[str, Any] = {"url": url}
        if keyword:
            body["keyword"] = keyword
        return self._post("/api/v1/article-seo", json=body)

    # ── AEO-only ──

    def audit_aeo(self, url: str) -> dict:
        return self._post("/api/v1/article-aeo", json={"url": url})

    # ── Tone ──

    def extract_tone(
        self,
        blog_url: str,
        customer_id: str | None = None,
        max_articles: int = 10,
        overwrite: bool = False,
    ) -> dict:
        body: dict[str, Any] = {
            "blog_url": blog_url,
            "max_articles": max_articles,
            "overwrite": overwrite,
        }
        if customer_id:
            body["customer_id"] = customer_id
        return self._post("/api/v1/tone/extract", json=body)

    def get_tone(self, customer_id: str) -> dict:
        return self._get(f"/api/v1/tone/{customer_id}")

    def list_tone_profiles(self) -> list[str]:
        return self._get("/api/v1/tone")

    def delete_tone(self, customer_id: str) -> dict:
        return self._delete(f"/api/v1/tone/{customer_id}")

    # ── Optimize ──

    def optimize(
        self,
        url: str,
        customer_id: str | None = None,
        audit_id: str | None = None,
        sync: bool = False,
    ) -> dict:
        body: dict[str, Any] = {"url": url}
        if customer_id:
            body["customer_id"] = customer_id
        if audit_id:
            body["audit_id"] = audit_id
        return self._post("/api/v1/optimize", json=body, sync=sync)

    def get_job(self, job_id: str) -> dict:
        return self._get(f"/api/v1/optimize/jobs/{job_id}")

    def get_job_preview(self, job_id: str) -> dict:
        return self._get(f"/api/v1/optimize/jobs/{job_id}/preview")

    def list_jobs(self, status: str | None = None, limit: int = 50) -> list[dict]:
        return self._get("/api/v1/optimize/jobs", status=status, limit=limit)

    def delete_job(self, job_id: str) -> dict:
        return self._delete(f"/api/v1/optimize/jobs/{job_id}")

    # ── llms.txt Generator ──

    def generate_llms_txt(self, url: str) -> dict:
        return self._post("/api/v1/llms-txt/generate", json={"url": url})

    # ── robots.txt Generator ──

    def generate_robots_txt(self, url: str) -> dict:
        return self._post("/api/v1/robots-txt/generate", json={"url": url})

    # ── sitemap.xml Generator ──

    def generate_sitemap(self, url: str, max_urls: int = 200) -> dict:
        return self._post("/api/v1/sitemap/generate", json={"url": url, "max_urls": max_urls})

    # ── Freshness Code Generator ──

    def generate_freshness_code(self, url: str) -> dict:
        return self._post("/api/v1/freshness-code/generate", json={"url": url})

    # ── Freshness ──

    def freshness_audit(
        self,
        sitemap_url: str,
        limit: int = 50,
        force_refresh: bool = False,
    ) -> dict:
        return self._post(
            "/api/v1/freshness-audit",
            json={
                "sitemap_url": sitemap_url,
                "limit": limit,
                "force_refresh": force_refresh,
            },
        )

    def get_freshness(self, audit_id: str) -> dict:
        return self._get(f"/api/v1/freshness-audit/{audit_id}")

    # ── Export ──

    def export(
        self,
        customer_id: str,
        data_type: str,
        data: dict | None = None,
        include_recommendations: bool = True,
        force_regenerate: bool = False,
    ) -> dict:
        return self._post(
            "/api/v1/export",
            json={
                "customer_id": customer_id,
                "data_type": data_type,
                "data": data or {},
                "include_recommendations": include_recommendations,
                "force_regenerate": force_regenerate,
            },
        )

    def get_export(self, customer_id: str, data_type: str) -> dict:
        return self._get(f"/api/v1/export/{customer_id}/{data_type}")

    # ── Credits ──

    def get_credits(self) -> dict:
        return self._get("/api/v1/credits/usage")
