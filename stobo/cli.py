"""Stobo CLI — AI-powered SEO/AEO audit tool."""

from __future__ import annotations

from typing import Optional

import typer

from stobo import __version__
from stobo import config as cfg
from stobo.client import StoboClient
from stobo.commands import audit, auth, credits, export, freshness, freshness_code, llms, mcp, optimize, robots, sitemap, tone

app = typer.Typer(
    name="stobo",
    help="Stobo CLI — AI-powered SEO/AEO audit tool.",
    no_args_is_help=True,
)

# Register subcommand groups
app.add_typer(auth.app, name="auth")
app.add_typer(audit.app, name="audit")
app.add_typer(tone.app, name="tone")
app.add_typer(optimize.app, name="optimize")
app.add_typer(freshness.app, name="freshness")
app.add_typer(export.app, name="export")
app.add_typer(credits.app, name="credits")
app.add_typer(llms.app, name="llms")
app.add_typer(robots.app, name="robots")
app.add_typer(sitemap.app, name="sitemap")
app.add_typer(freshness_code.app, name="freshness-code")
app.add_typer(mcp.app, name="mcp")


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"stobo {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="STOBO_API_KEY", help="API key"),
    base_url: Optional[str] = typer.Option(None, "--base-url", help="API base URL"),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
    version: bool = typer.Option(False, "--version", callback=_version_callback, is_eager=True, help="Show version"),
) -> None:
    """Global options applied before any subcommand."""
    # Priority: CLI flag > env var > config file
    resolved_key = api_key or cfg.get_api_key()
    resolved_url = base_url or cfg.get_base_url()

    ctx.ensure_object(dict)
    ctx.obj["json"] = json_output
    ctx.obj["client"] = StoboClient(api_key=resolved_key, base_url=resolved_url)


if __name__ == "__main__":
    app()
