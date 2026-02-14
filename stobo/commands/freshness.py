"""stobo freshness — sitemap schema audit."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.status import Status

from stobo.client import StoboAPIError, StoboClient, normalize_url
from stobo.formatters import format_error, format_freshness_result, print_json

app = typer.Typer(help="Audit sitemap freshness and schema markup.")
console = Console()


def _get_client(ctx: typer.Context) -> StoboClient:
    return ctx.obj["client"]


def _use_json(ctx: typer.Context) -> bool:
    return ctx.obj.get("json", False)


@app.command("run")
def run_freshness(
    ctx: typer.Context,
    sitemap_url: str = typer.Argument(..., help="Sitemap URL to audit"),
    limit: int = typer.Option(50, "--limit", "-n", help="Max URLs to check"),
    force_refresh: bool = typer.Option(False, "--force", help="Bypass 24h cache"),
) -> None:
    """Run a freshness audit on a sitemap."""
    sitemap_url = normalize_url(sitemap_url)
    client = _get_client(ctx)
    try:
        with Status(f"[cyan]Scanning {sitemap_url}...[/]", console=console):
            result = client.freshness_audit(sitemap_url, limit=limit, force_refresh=force_refresh)
        if _use_json(ctx):
            print_json(result)
        else:
            format_freshness_result(result)
    except StoboAPIError as e:
        format_error(e.status_code, e.detail)
        raise typer.Exit(1)


@app.command("get")
def get_freshness(
    ctx: typer.Context,
    audit_id: str = typer.Argument(..., help="Freshness audit UUID"),
) -> None:
    """Get a freshness audit by ID."""
    client = _get_client(ctx)
    try:
        result = client.get_freshness(audit_id)
        if _use_json(ctx):
            print_json(result)
        else:
            format_freshness_result(result)
    except StoboAPIError as e:
        format_error(e.status_code, e.detail)
        raise typer.Exit(1)
