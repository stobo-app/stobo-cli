"""stobo mcp — install/uninstall MCP server for Claude Desktop & Cursor."""

from __future__ import annotations

import json
import platform
from pathlib import Path
from shutil import which

import typer
from rich.console import Console

from stobo import config

app = typer.Typer(help="Manage the Stobo MCP server for Claude Desktop & Cursor.")
console = Console()

TARGETS = {
    "claude": "Claude Desktop",
    "cursor": "Cursor",
}


def _config_path(target: str) -> Path:
    """Return the MCP config path for the given target."""
    system = platform.system()
    if target == "cursor":
        return Path.home() / ".cursor" / "mcp.json"
    # Claude Desktop
    if system == "Darwin":
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    elif system == "Windows":
        return Path.home() / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
    else:
        return Path.home() / ".config" / "Claude" / "claude_desktop_config.json"


def _find_stobo_mcp() -> str | None:
    """Find the stobo-mcp binary path."""
    return which("stobo-mcp")


def _build_server_entry(mcp_bin: str, key: str) -> dict:
    """Build the mcpServers entry for stobo."""
    env = {"STOBO_BASE_URL": "https://api.trystobo.com"}
    if key:
        env["STOBO_API_KEY"] = key
    return {"command": mcp_bin, "env": env}


def _install_target(target: str, mcp_bin: str, key: str) -> bool:
    """Install into a single target. Returns True if successful."""
    label = TARGETS[target]
    cfg_path = _config_path(target)
    cfg_path.parent.mkdir(parents=True, exist_ok=True)

    data = json.loads(cfg_path.read_text()) if cfg_path.exists() else {}
    data.setdefault("mcpServers", {})
    data["mcpServers"]["stobo"] = _build_server_entry(mcp_bin, key)
    cfg_path.write_text(json.dumps(data, indent=2) + "\n")

    console.print(f"  [green]\u2713[/] {label}")
    return True


def _uninstall_target(target: str) -> bool:
    """Uninstall from a single target. Returns True if removed."""
    label = TARGETS[target]
    cfg_path = _config_path(target)

    if not cfg_path.exists():
        return False

    data = json.loads(cfg_path.read_text())
    if "stobo" not in data.get("mcpServers", {}):
        return False

    del data["mcpServers"]["stobo"]
    cfg_path.write_text(json.dumps(data, indent=2) + "\n")
    console.print(f"  [green]\u2713[/] Removed from {label}")
    return True


@app.command()
def install(
    api_key: str = typer.Option(None, "--api-key", "-k", help="Stobo API key (optional — free tools work without one)"),
) -> None:
    """Install Stobo MCP server into Claude Desktop & Cursor."""
    key = api_key or config.get_api_key() or ""

    mcp_bin = _find_stobo_mcp()
    if not mcp_bin:
        console.print("[red]stobo-mcp not found.[/] Install it with: [bold]pip install stobo-mcp[/]")
        raise typer.Exit(1)

    console.print("[bold]Installing Stobo MCP server...[/]")
    installed = []
    for target in TARGETS:
        _install_target(target, mcp_bin, key)
        installed.append(target)

    console.print()
    if key:
        console.print("  API key: [dim]configured — all tools available[/]")
    else:
        console.print("  Free tools: [green]audit_site, audit_article, robots.txt, sitemap, freshness_code[/]")
        console.print("  [dim]Add an API key later with:[/] stobo mcp install --api-key sk_...")
    console.print()
    console.print("[yellow]Restart Claude Desktop / Cursor[/] for the changes to take effect.")


@app.command()
def uninstall() -> None:
    """Remove Stobo MCP server from Claude Desktop & Cursor."""
    removed = []
    for target in TARGETS:
        if _uninstall_target(target):
            removed.append(target)

    if not removed:
        console.print("[yellow]Stobo MCP server not found in any config.[/]")
        raise typer.Exit(0)

    console.print()
    console.print("[yellow]Restart Claude Desktop / Cursor[/] for the changes to take effect.")
