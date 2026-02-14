"""stobo auth — login / logout / status."""

from __future__ import annotations

import typer
from rich.console import Console

from stobo import config
from stobo.client import AuthError, StoboClient
from stobo.formatters import format_error

app = typer.Typer(help="Manage API key authentication.")
console = Console()


@app.command()
def login(
    ctx: typer.Context,
    api_key: str = typer.Argument(..., help="Your Stobo API key (sk_...)"),
) -> None:
    """Save and validate an API key."""
    # Use base_url from parent context (respects --base-url flag)
    parent_client: StoboClient = ctx.obj["client"]
    client = StoboClient(api_key=api_key, base_url=parent_client.base_url)
    try:
        result = client.get_me()
        config.set_api_key(api_key)
        config.set_base_url(parent_client.base_url)
        console.print(f"[green]\u2713[/] Logged in as [bold]{result.get('email', 'API Key')}[/]")
    except AuthError as e:
        format_error(e.status_code, "Invalid API key.")
        raise typer.Exit(1)
    finally:
        client.close()


@app.command()
def logout() -> None:
    """Clear stored API key."""
    config.clear()
    console.print("[green]\u2713[/] Logged out. API key removed.")


@app.command()
def status(ctx: typer.Context) -> None:
    """Show current auth status."""
    key = config.get_api_key()
    if not key:
        console.print("[yellow]Not logged in.[/] Run [bold]stobo auth login <key>[/]")
        raise typer.Exit(1)

    client: StoboClient = ctx.obj["client"]
    try:
        user = client.get_me()
        console.print(f"[green]\u2713[/] Authenticated")
        console.print(f"  Email: [bold]{user.get('email', 'N/A')}[/]")
        console.print(f"  Name:  {user.get('full_name', 'N/A')}")
        console.print(f"  Key:   {key[:12]}...")
    except AuthError:
        console.print("[red]\u2717[/] Stored key is invalid. Run [bold]stobo auth login <key>[/]")
        raise typer.Exit(1)
