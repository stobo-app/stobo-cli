"""stobo llms — generate llms.txt files."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.status import Status

from stobo.client import StoboAPIError, StoboClient, normalize_url
from stobo.formatters import format_error, format_llms_txt_result, print_json, show_credit_line

app = typer.Typer(help="Generate llms.txt files for AI discoverability.")
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
    """Generate a llms.txt file for a website."""
    url = normalize_url(url)
    client = _get_client(ctx)
    try:
        with Status(f"[cyan]Generating llms.txt for {url}...[/]", console=console):
            result = client.generate_llms_txt(url)
        if _use_json(ctx):
            print_json(result)
        else:
            format_llms_txt_result(result, output_file=output)
            show_credit_line(client)
    except StoboAPIError as e:
        format_error(e.status_code, e.detail)
        raise typer.Exit(1)
