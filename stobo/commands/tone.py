"""stobo tone — extract and manage brand voice profiles."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.status import Status

from stobo.client import StoboAPIError, StoboClient, normalize_url
from stobo.formatters import format_error, format_tone_list, format_tone_profile, print_json, show_credit_line

app = typer.Typer(help="Extract and manage brand voice profiles.")
console = Console()


def _get_client(ctx: typer.Context) -> StoboClient:
    return ctx.obj["client"]


def _use_json(ctx: typer.Context) -> bool:
    return ctx.obj.get("json", False)


@app.command("extract")
def extract(
    ctx: typer.Context,
    blog_url: str = typer.Argument(..., help="Blog URL to scrape"),
    customer_id: str | None = typer.Option(None, "--customer-id", "-c", help="Customer ID"),
    max_articles: int = typer.Option(10, "--max-articles", "-n", help="Max articles to scrape"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing profile"),
) -> None:
    """Extract brand voice from a blog."""
    blog_url = normalize_url(blog_url)
    client = _get_client(ctx)
    try:
        with Status(f"[cyan]Extracting brand voice from {blog_url}...[/]", console=console):
            result = client.extract_tone(
                blog_url,
                customer_id=customer_id,
                max_articles=max_articles,
                overwrite=overwrite,
            )
        if _use_json(ctx):
            print_json(result)
        else:
            console.print(f"[green]\u2713[/] Extracted from {result.get('articles_analyzed', '?')} articles")
            format_tone_profile(result)
            show_credit_line(client)
    except StoboAPIError as e:
        format_error(e.status_code, e.detail)
        raise typer.Exit(1)


@app.command("get")
def get_profile(
    ctx: typer.Context,
    customer_id: str = typer.Argument(..., help="Customer ID"),
) -> None:
    """Get a stored brand voice profile."""
    client = _get_client(ctx)
    try:
        result = client.get_tone(customer_id)
        if _use_json(ctx):
            print_json(result)
        else:
            format_tone_profile(result)
    except StoboAPIError as e:
        format_error(e.status_code, e.detail)
        raise typer.Exit(1)


@app.command("list")
def list_profiles(ctx: typer.Context) -> None:
    """List all brand voice profiles."""
    client = _get_client(ctx)
    try:
        result = client.list_tone_profiles()
        if _use_json(ctx):
            print_json(result)
        else:
            format_tone_list(result)
    except StoboAPIError as e:
        format_error(e.status_code, e.detail)
        raise typer.Exit(1)


@app.command("delete")
def delete_profile(
    ctx: typer.Context,
    customer_id: str = typer.Argument(..., help="Customer ID"),
) -> None:
    """Delete a brand voice profile."""
    client = _get_client(ctx)
    try:
        client.delete_tone(customer_id)
        console.print(f"[green]\u2713[/] Deleted profile for [bold]{customer_id}[/]")
    except StoboAPIError as e:
        format_error(e.status_code, e.detail)
        raise typer.Exit(1)
