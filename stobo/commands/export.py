"""stobo export — generate markdown reports."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.status import Status

from stobo.client import StoboAPIError, StoboClient
from stobo.formatters import format_error, format_export, print_json, show_credit_line

app = typer.Typer(help="Generate and retrieve markdown export reports.")
console = Console()

VALID_TYPES = ["brand_voice", "seo_audit", "article_rewrite"]


def _get_client(ctx: typer.Context) -> StoboClient:
    return ctx.obj["client"]


def _use_json(ctx: typer.Context) -> bool:
    return ctx.obj.get("json", False)


@app.command("run")
def run_export(
    ctx: typer.Context,
    customer_id: str = typer.Argument(..., help="Customer ID"),
    data_type: str = typer.Argument(..., help=f"Export type: {', '.join(VALID_TYPES)}"),
    output: str | None = typer.Option(None, "--output", "-o", help="Save to file"),
    force: bool = typer.Option(False, "--force", help="Regenerate even if cached"),
) -> None:
    """Generate a markdown export report."""
    if data_type not in VALID_TYPES:
        console.print(f"[red]Invalid type:[/] {data_type}. Must be one of: {', '.join(VALID_TYPES)}")
        raise typer.Exit(1)

    client = _get_client(ctx)
    try:
        # Auto-fetch data if not already cached
        data: dict = {}
        with Status(f"[cyan]Generating {data_type} export...[/]", console=console):
            if data_type == "brand_voice":
                data = client.get_tone(customer_id)
            result = client.export(customer_id, data_type, data=data, force_regenerate=force)
        if _use_json(ctx):
            print_json(result)
        else:
            format_export(result, output_file=output)
            show_credit_line(client)
    except StoboAPIError as e:
        format_error(e.status_code, e.detail)
        raise typer.Exit(1)


@app.command("get")
def get_export(
    ctx: typer.Context,
    customer_id: str = typer.Argument(..., help="Customer ID"),
    data_type: str = typer.Argument(..., help=f"Export type: {', '.join(VALID_TYPES)}"),
    output: str | None = typer.Option(None, "--output", "-o", help="Save to file"),
) -> None:
    """Get a cached export report."""
    client = _get_client(ctx)
    try:
        result = client.get_export(customer_id, data_type)
        if _use_json(ctx):
            print_json(result)
        else:
            format_export(result, output_file=output)
    except StoboAPIError as e:
        format_error(e.status_code, e.detail)
        raise typer.Exit(1)
