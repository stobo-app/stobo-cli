"""stobo audit — run SEO/AEO audits."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.status import Status

from stobo.client import StoboAPIError, StoboClient, normalize_url
from stobo.formatters import (
    format_audit_list,
    format_audit_result,
    format_error,
    format_site_audit_result,
    print_json,
)

app = typer.Typer(help="Run and manage SEO/AEO audits.")
console = Console()


def _get_client(ctx: typer.Context) -> StoboClient:
    return ctx.obj["client"]


def _use_json(ctx: typer.Context) -> bool:
    return ctx.obj.get("json", False)


@app.command("run")
def run_audit(
    ctx: typer.Context,
    url: str = typer.Argument(..., help="URL to audit"),
    seo_only: bool = typer.Option(False, "--seo-only", help="SEO checks only"),
    aeo_only: bool = typer.Option(False, "--aeo-only", help="AEO checks only"),
    keyword: str | None = typer.Option(None, "--keyword", "-k", help="Target keyword"),
    playwright: bool = typer.Option(False, "--playwright", help="Force Playwright for JS-rendered SPAs"),
) -> None:
    """Run an audit on a URL."""
    url = normalize_url(url)
    client = _get_client(ctx)
    label = "SEO" if seo_only else "AEO" if aeo_only else "SEO + AEO"

    try:
        with Status(f"[cyan]Running {label} audit on {url}...[/]", console=console):
            if seo_only:
                result = client.audit_seo(url, keyword=keyword)
            elif aeo_only:
                result = client.audit_aeo(url)
            else:
                result = client.audit_article(url, keyword=keyword, use_playwright=playwright)

        if _use_json(ctx):
            print_json(result)
        else:
            format_audit_result(result)
    except StoboAPIError as e:
        format_error(e.status_code, e.detail)
        raise typer.Exit(1)


@app.command("site")
def site_audit(
    ctx: typer.Context,
    url: str = typer.Argument(..., help="Website URL to audit"),
) -> None:
    """Run a full site audit (SEO + AEO + blog detection + sitemap discovery)."""
    url = normalize_url(url)
    client = _get_client(ctx)
    try:
        with Status("[cyan]Running site audit (SEO + AEO + blog + discovery)...[/]", console=console):
            result = client.audit_site(url)

        if _use_json(ctx):
            print_json(result)
        else:
            format_site_audit_result(result)
    except StoboAPIError as e:
        format_error(e.status_code, e.detail)
        raise typer.Exit(1)


@app.command("get")
def get_audit(
    ctx: typer.Context,
    audit_id: str = typer.Argument(..., help="Audit UUID"),
) -> None:
    """Get a specific audit by ID."""
    client = _get_client(ctx)
    try:
        result = client.get_audit(audit_id)
        if _use_json(ctx):
            print_json(result)
        else:
            format_audit_result(result)
    except StoboAPIError as e:
        format_error(e.status_code, e.detail)
        raise typer.Exit(1)


@app.command("get-url")
def get_audit_by_url(
    ctx: typer.Context,
    url: str = typer.Argument(..., help="URL to look up"),
) -> None:
    """Get the most recent audit for a URL."""
    url = normalize_url(url)
    client = _get_client(ctx)
    try:
        result = client.get_audit_by_url(url)
        if _use_json(ctx):
            print_json(result)
        else:
            format_audit_result(result)
    except StoboAPIError as e:
        format_error(e.status_code, e.detail)
        raise typer.Exit(1)


@app.command("list")
def list_audits(
    ctx: typer.Context,
    limit: int = typer.Option(20, "--limit", "-n", help="Max results"),
) -> None:
    """List recent audits."""
    client = _get_client(ctx)
    try:
        results = client.list_audits(limit=limit)
        if _use_json(ctx):
            print_json(results)
        else:
            format_audit_list(results)
    except StoboAPIError as e:
        format_error(e.status_code, e.detail)
        raise typer.Exit(1)
