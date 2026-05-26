"""Stobo CLI — AI-powered SEO/AEO audit tool."""

from __future__ import annotations

from typing import Optional

import typer

from stobo import __version__

app = typer.Typer(
    name="stobo",
    help="Stobo CLI — retired. The Stobo SEO/AEO audit service has been shut down.",
    no_args_is_help=False,
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"stobo {__version__}")
        raise typer.Exit()


@app.callback(
    invoke_without_command=True,
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def main(
    ctx: typer.Context,
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="STOBO_API_KEY", help="(retired)"),
    base_url: Optional[str] = typer.Option(None, "--base-url", help="(retired)"),
    json_output: bool = typer.Option(False, "--json", help="(retired)"),
    version: bool = typer.Option(False, "--version", callback=_version_callback, is_eager=True, help="Show version"),
) -> None:
    """Stobo has been retired — this CLI no longer connects to any service."""
    # The Stobo SEO/AEO audit service was shut down in May 2026; the API is gone.
    # Every invocation now prints this notice and exits without making any network call.
    del api_key, base_url, json_output  # accepted for backwards-compat, ignored
    typer.secho("Stobo has been retired.", fg=typer.colors.YELLOW, bold=True, err=True)
    typer.echo(
        "The Stobo SEO/AEO audit service was shut down in May 2026 and its API is no "
        "longer available. This release exists only to mark end-of-life.\n"
        "Thank you to everyone who used it.",
        err=True,
    )
    raise typer.Exit(code=0)


if __name__ == "__main__":
    app()
