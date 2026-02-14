"""stobo credits — view credit usage."""

from __future__ import annotations

import typer
from rich.console import Console

from stobo.client import StoboAPIError, StoboClient
from stobo.formatters import format_credits, format_error, print_json

app = typer.Typer(help="View credit usage and balance.")
console = Console()


def _get_client(ctx: typer.Context) -> StoboClient:
    return ctx.obj["client"]


def _use_json(ctx: typer.Context) -> bool:
    return ctx.obj.get("json", False)


@app.callback(invoke_without_command=True)
def show_credits(ctx: typer.Context) -> None:
    """Show current credit usage."""
    client = _get_client(ctx)
    try:
        result = client.get_credits()
        if _use_json(ctx):
            print_json(result)
        else:
            format_credits(result)
    except StoboAPIError as e:
        format_error(e.status_code, e.detail)
        raise typer.Exit(1)
