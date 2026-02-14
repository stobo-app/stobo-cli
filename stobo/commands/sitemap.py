"""stobo sitemap — generate sitemap.xml files."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.status import Status

from stobo.client import StoboAPIError, StoboClient, normalize_url
from stobo.formatters import format_error, format_sitemap_result, print_json

app = typer.Typer(help="Generate sitemap.xml files by crawling a website.")
console = Console()


def _get_client(ctx: typer.Context) -> StoboClient:
    return ctx.obj["client"]


def _use_json(ctx: typer.Context) -> bool:
    return ctx.obj.get("json", False)


@app.command("generate")
def generate(
    ctx: typer.Context,
    url: str = typer.Argument(..., help="Website URL to crawl"),
    output: str | None = typer.Option(None, "--output", "-o", help="Save to file"),
    max_urls: int = typer.Option(200, "--max-urls", "-n", help="Max URLs to discover (10-500)"),
) -> None:
    """Generate a sitemap.xml by crawling a website's internal pages."""
    url = normalize_url(url)
    client = _get_client(ctx)
    try:
        with Status(f"[cyan]Crawling {url} for sitemap.xml...[/]", console=console):
            result = client.generate_sitemap(url, max_urls=max_urls)
        if _use_json(ctx):
            print_json(result)
        else:
            format_sitemap_result(result, output_file=output)
    except StoboAPIError as e:
        format_error(e.status_code, e.detail)
        raise typer.Exit(1)
