"""stobo robots — generate optimized robots.txt files."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.status import Status

from stobo.client import StoboAPIError, StoboClient, normalize_url
from stobo.formatters import format_error, format_robots_txt_result, print_json

app = typer.Typer(help="Generate AI-crawler-optimized robots.txt files.")
console = Console()


def _get_client(ctx: typer.Context) -> StoboClient:
    return ctx.obj["client"]


def _use_json(ctx: typer.Context) -> bool:
    return ctx.obj.get("json", False)


@app.command("generate")
def generate(
    ctx: typer.Context,
    url: str = typer.Argument(..., help="Website URL"),
    output: str | None = typer.Option(None, "--output", "-o", help="Save to file"),
) -> None:
    """Generate an AI-crawler-optimized robots.txt for a website."""
    url = normalize_url(url)
    client = _get_client(ctx)
    try:
        with Status(f"[cyan]Generating robots.txt for {url}...[/]", console=console):
            result = client.generate_robots_txt(url)
        if _use_json(ctx):
            print_json(result)
        else:
            format_robots_txt_result(result, output_file=output)
    except StoboAPIError as e:
        format_error(e.status_code, e.detail)
        raise typer.Exit(1)
