"""stobo freshness-code — generate Article/BlogPosting JSON-LD schema."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.status import Status

from stobo.client import StoboAPIError, StoboClient, normalize_url
from stobo.formatters import format_error, format_freshness_code_result, print_json

app = typer.Typer(help="Generate Article/BlogPosting JSON-LD freshness schema.")
console = Console()


def _get_client(ctx: typer.Context) -> StoboClient:
    return ctx.obj["client"]


def _use_json(ctx: typer.Context) -> bool:
    return ctx.obj.get("json", False)


@app.command("generate")
def generate(
    ctx: typer.Context,
    url: str = typer.Argument(..., help="Page URL to generate schema for"),
    output: str | None = typer.Option(None, "--output", "-o", help="Save to file"),
) -> None:
    """Generate Article/BlogPosting JSON-LD schema with datePublished/dateModified."""
    url = normalize_url(url)
    client = _get_client(ctx)
    try:
        with Status(f"[cyan]Extracting metadata from {url}...[/]", console=console):
            result = client.generate_freshness_code(url)
        if _use_json(ctx):
            print_json(result)
        else:
            format_freshness_code_result(result, output_file=output)
    except StoboAPIError as e:
        format_error(e.status_code, e.detail)
        raise typer.Exit(1)
