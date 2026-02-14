"""stobo optimize — run full audit-tone-rewrite pipeline."""

from __future__ import annotations

import time

import typer
from rich.console import Console
from rich.status import Status

from stobo.client import StoboAPIError, StoboClient, normalize_url
from stobo.formatters import (
    format_error,
    format_job_list,
    format_job_status,
    print_json,
    show_credit_line,
)

app = typer.Typer(help="Run full optimization pipeline (audit + tone + rewrite).")
console = Console()

TERMINAL_STATUSES = {"completed", "failed"}
POLL_INTERVAL = 3


def _get_client(ctx: typer.Context) -> StoboClient:
    return ctx.obj["client"]


def _use_json(ctx: typer.Context) -> bool:
    return ctx.obj.get("json", False)


def _poll_job(client: StoboClient, job_id: str) -> dict:
    """Poll until job reaches a terminal status."""
    with Status("[cyan]Optimizing...[/]", console=console) as status:
        while True:
            result = client.get_job(job_id)
            current = result.get("status", "unknown")
            status.update(f"[cyan]Optimizing... ({current})[/]")
            if current in TERMINAL_STATUSES:
                return result
            time.sleep(POLL_INTERVAL)


@app.command("run")
def run_optimize(
    ctx: typer.Context,
    url: str = typer.Argument(..., help="URL to optimize"),
    customer_id: str | None = typer.Option(None, "--customer-id", "-c", help="Customer ID for tone"),
    audit_id: str | None = typer.Option(None, "--audit-id", help="Reuse existing audit"),
    no_wait: bool = typer.Option(False, "--no-wait", help="Return job ID without polling"),
) -> None:
    """Start a full optimization job."""
    url = normalize_url(url)
    client = _get_client(ctx)
    try:
        resp = client.optimize(url, customer_id=customer_id, audit_id=audit_id)
        job_id = resp.get("job_id", "")

        if no_wait:
            if _use_json(ctx):
                print_json(resp)
            else:
                console.print(f"[green]\u2713[/] Job started: [bold]{job_id}[/]")
                console.print(f"  Check status: [dim]stobo optimize status {job_id}[/]")
            return

        result = _poll_job(client, job_id)
        if _use_json(ctx):
            print_json(result)
        else:
            format_job_status(result)
            show_credit_line(client)
    except StoboAPIError as e:
        format_error(e.status_code, e.detail)
        raise typer.Exit(1)


@app.command("status")
def job_status(
    ctx: typer.Context,
    job_id: str = typer.Argument(..., help="Job UUID"),
) -> None:
    """Check optimization job status."""
    client = _get_client(ctx)
    try:
        result = client.get_job(job_id)
        if _use_json(ctx):
            print_json(result)
        else:
            format_job_status(result)
    except StoboAPIError as e:
        format_error(e.status_code, e.detail)
        raise typer.Exit(1)


@app.command("preview")
def job_preview(
    ctx: typer.Context,
    job_id: str = typer.Argument(..., help="Job UUID"),
) -> None:
    """Show before/after preview for a completed job."""
    client = _get_client(ctx)
    try:
        result = client.get_job_preview(job_id)
        if _use_json(ctx):
            print_json(result)
        else:
            console.print()
            orig = result.get("original", {})
            rewr = result.get("rewritten", {})
            console.print(f"[bold]Original title:[/] {orig.get('title', 'N/A')}")
            console.print(f"[bold]Rewritten title:[/] [green]{rewr.get('title', 'N/A')}[/]")
            console.print(f"\nChanges: [bold]{result.get('changes_count', 0)}[/]  "
                          f"Fixed: [green]{result.get('issues_fixed', 0)}[/]  "
                          f"Skipped: [dim]{result.get('issues_skipped', 0)}[/]")
    except StoboAPIError as e:
        format_error(e.status_code, e.detail)
        raise typer.Exit(1)


@app.command("jobs")
def list_jobs(
    ctx: typer.Context,
    status_filter: str | None = typer.Option(None, "--status", "-s", help="Filter by status"),
    limit: int = typer.Option(20, "--limit", "-n", help="Max results"),
) -> None:
    """List optimization jobs."""
    client = _get_client(ctx)
    try:
        results = client.list_jobs(status=status_filter, limit=limit)
        if _use_json(ctx):
            print_json(results)
        else:
            format_job_list(results)
    except StoboAPIError as e:
        format_error(e.status_code, e.detail)
        raise typer.Exit(1)
