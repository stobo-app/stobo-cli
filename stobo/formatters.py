"""Rich output formatters for all CLI commands."""

from __future__ import annotations

import json
import sys
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()
err_console = Console(stderr=True)


# ── JSON mode ───────────────────────────────────────────────────────


def print_json(data: Any) -> None:
    print(json.dumps(data, indent=2, default=str))


# ── Audit ───────────────────────────────────────────────────────────


GRADE_COLORS = {"A": "green", "B": "blue", "C": "yellow", "D": "red", "F": "bold red"}


def format_audit_result(data: dict) -> None:
    # SEO-only / AEO-only responses nest scores inside seo_audit / aeo_audit
    sub = data.get("seo_audit") or data.get("aeo_audit") or {}
    grade = data.get("grade") or _pct_to_grade(sub.get("percentage"))
    color = GRADE_COLORS.get(grade, "white")
    pct = data.get("percentage") or sub.get("percentage") or 0
    url = data.get("url", "")

    console.print()
    console.print(Panel(
        f"[bold {color}]{grade}[/]  {pct:.0f}%  —  {url}",
        title="Audit Result",
        border_style=color,
    ))

    # Category breakdown
    categories = data.get("category_scores") or sub.get("category_scores", {})
    if categories:
        table = Table(title="Category Scores", show_lines=False)
        table.add_column("Category", style="bold")
        table.add_column("Score", justify="right")
        for cat, score in sorted(categories.items()):
            table.add_row(cat.replace("_", " ").title(), str(score))
        console.print(table)

    # Top recommendations
    recs = data.get("recommendations") or sub.get("recommendations", [])
    if recs:
        console.print(f"\n[bold]Top Issues ({len(recs)}):[/]")
        for rec in recs[:5]:
            if isinstance(rec, str):
                console.print(f"  [yellow]\u2022[/] {rec}")
            elif isinstance(rec, dict):
                console.print(f"  [yellow]\u2022[/] {rec.get('message', rec)}")


def _pct_to_grade(pct: float | None) -> str:
    if pct is None:
        return "?"
    if pct >= 91:
        return "A"
    if pct >= 76:
        return "B"
    if pct >= 51:
        return "C"
    if pct >= 26:
        return "D"
    return "F"


def format_audit_list(audits: list[dict]) -> None:
    table = Table(title="Recent Audits")
    table.add_column("ID", style="dim", max_width=8)
    table.add_column("URL")
    table.add_column("Grade", justify="center")
    table.add_column("Score", justify="right")
    table.add_column("Date", style="dim")
    for a in audits:
        grade = a.get("grade", "?")
        color = GRADE_COLORS.get(grade, "white")
        pct = a.get("percentage") or 0
        table.add_row(
            str(a.get("id", ""))[:8],
            a.get("url", ""),
            f"[{color}]{grade}[/]",
            f"{pct:.0f}%",
            str(a.get("created_at", ""))[:10],
        )
    console.print(table)


# ── Site Audit ─────────────────────────────────────────────────────

# Ordered list of AEO check keys (matches SiteAEOAudit schema)
_AEO_CHECKS = [
    ("robots_ai", "AI Crawler Access"),
    ("llms_txt", "llms.txt"),
    ("freshness", "Content Freshness"),
    ("faqs", "Visible FAQ Section"),
    ("faq_schema", "FAQ Schema Markup"),
    ("direct_answer", "Direct Answer"),
    ("sitemap", "Sitemap"),
]


def _progress_bar(pct: float, width: int = 20) -> str:
    filled = int((pct / 100) * width)
    return "\u2588" * filled + "\u2591" * (width - filled)


def _status_icon(status: str) -> str:
    return {
        "excellent": "[green]\u2713[/]",
        "good": "[green]\u2713[/]",
        "needs_improvement": "[yellow]~[/]",
        "critical": "[red]\u2717[/]",
    }.get(status, "?")


def format_site_audit_result(data: dict) -> None:
    """Format a full site audit result (SEO + AEO + blog + discovery)."""
    domain = data.get("domain", "")
    combined = data.get("combined_percentage")
    cached = data.get("cached", False)
    seo = data.get("seo_audit") or {}
    aeo = data.get("aeo_audit") or {}
    blog = data.get("blog_detection") or {}
    discovery = data.get("sitemap_discovery")

    # ── Header ──
    grade = _pct_to_grade(combined)
    color = GRADE_COLORS.get(grade, "white")
    cache_tag = "  [dim](cached)[/]" if cached else ""

    console.print()
    console.print(Panel(
        f"[bold]{domain}[/]\n"
        f"[bold {color}]{grade}[/]  {combined or 0:.1f}%  (SEO + AEO combined){cache_tag}",
        title="Site Audit",
        border_style=color,
    ))

    # ── SEO Section ──
    if seo:
        seo_grade = seo.get("grade", "?")
        seo_color = GRADE_COLORS.get(seo_grade, "white")
        seo_pts = seo.get("total_points", 0)
        seo_max = seo.get("max_points", 380)
        console.print(
            f"\n[bold]SEO Audit[/] — [{seo_color}]{seo_grade}[/]"
            f" ({seo_pts}/{seo_max} points)"
        )

        cats = seo.get("category_scores", {})
        if cats:
            table = Table(show_header=True, show_lines=False)
            table.add_column("Category", style="bold")
            table.add_column("Score", justify="right")
            table.add_column("", min_width=22)
            for cat_name, cat_data in cats.items():
                score = cat_data.get("score", 0)
                max_pts = cat_data.get("max_points", 1)
                pct = cat_data.get("percentage", 0)
                bar = _progress_bar(pct)
                pct_color = "green" if pct >= 76 else "yellow" if pct >= 51 else "red"
                table.add_row(
                    cat_name,
                    f"{score}/{max_pts}",
                    f"{bar} [{pct_color}]{pct}%[/]",
                )
            console.print(table)

    elif data.get("seo_error"):
        console.print(f"\n[red]SEO Error:[/] {data['seo_error']}")

    # ── AEO Section ──
    if aeo:
        aeo_score = aeo.get("score", 0)
        aeo_max = aeo.get("max_points", 135)
        aeo_pct = aeo.get("percentage", 0)
        aeo_grade = _pct_to_grade(aeo_pct)
        aeo_color = GRADE_COLORS.get(aeo_grade, "white")
        console.print(
            f"\n[bold]AEO Audit[/] — [{aeo_color}]{aeo_grade}[/]"
            f" ({aeo_score}/{aeo_max} points, {aeo_pct:.0f}%)"
        )

        table = Table(show_header=True, show_lines=False)
        table.add_column("Check", min_width=20)
        table.add_column("Score", justify="right")
        table.add_column("Status")
        table.add_column("Message", max_width=50)
        for key, label in _AEO_CHECKS:
            check = aeo.get(key, {})
            if not isinstance(check, dict):
                continue
            icon = _status_icon(check.get("status", ""))
            table.add_row(
                f"{icon} {label}",
                f"{check.get('score', 0)}/{check.get('max_points', 0)}",
                check.get("status", "").replace("_", " ").title(),
                check.get("message", ""),
            )
        console.print(table)

    elif data.get("aeo_error"):
        console.print(f"\n[red]AEO Error:[/] {data['aeo_error']}")

    # ── Blog Detection ──
    if blog.get("has_blog"):
        console.print("\n[bold]Blog Detection[/]")
        console.print(f"  \u2713 Blog found at {blog.get('blog_url', 'N/A')}")
        console.print(f"  {blog.get('article_count', 0)} articles discovered")
        sitemap = blog.get("sitemap_url")
        if sitemap:
            console.print(f"  Sitemap: {sitemap}")
        console.print("\n  [dim]Next steps:[/]")
        if sitemap:
            console.print(f"  [dim]\u2022 stobo freshness run {sitemap}[/]")
        console.print(f"  [dim]\u2022 stobo audit run <article-url>[/]")

    # ── Sitemap Discovery ──
    if discovery:
        total = discovery.get("total_urls", 0)
        categories = discovery.get("categories", [])
        console.print(f"\n[bold]Sitemap Discovery[/] — {total} pages found")
        for cat in categories:
            name = cat.get("name", cat.get("slug", ""))
            count = len(cat.get("urls", []))
            console.print(f"  \u2022 {name}: {count} pages")

    # ── Recommendations ──
    recs = seo.get("recommendations", []) if seo else []
    if recs:
        console.print(f"\n[bold]Top Recommendations ({min(len(recs), 5)}/{len(recs)}):[/]")
        for rec in recs[:5]:
            priority = rec.get("priority", "medium")
            p_color = "red" if priority == "high" else "yellow"
            console.print(
                f"  [{p_color}]\u2022[/] {rec.get('message', '')}"
                f" [dim][{rec.get('check', '')}][/]"
            )


# ── Tone ────────────────────────────────────────────────────────────


def format_tone_profile(data: dict) -> None:
    profile = data.get("profile", data)
    brand = profile.get("brand_name", "N/A")
    archetype = profile.get("voice_archetype", "N/A")
    pitch = profile.get("elevator_pitch", "N/A")
    extracted = profile.get("extracted_from", "?")

    console.print()
    console.print(Panel(
        f"[bold]Brand:[/] {brand}\n"
        f"[bold]Archetype:[/] {archetype}\n"
        f"[bold]Pitch:[/] {pitch}\n"
        f"[bold]Articles analyzed:[/] {extracted}",
        title="Brand Voice Profile",
        border_style="cyan",
    ))

    # Core traits
    traits = profile.get("core_traits", [])
    if traits:
        console.print("\n[bold]Core Traits:[/]")
        for t in traits:
            if isinstance(t, dict):
                console.print(f"  [cyan]\u2022[/] [bold]{t.get('name', '')}[/]")
            else:
                console.print(f"  [cyan]\u2022[/] {t}")

    # Do's and Don'ts
    dos = profile.get("dos", [])
    donts = profile.get("donts", [])
    if dos or donts:
        table = Table(title="Do's & Don'ts", show_lines=False)
        table.add_column("Do", style="green", max_width=45)
        table.add_column("Don't", style="red", max_width=45)
        for i in range(max(len(dos), len(donts))):
            table.add_row(
                dos[i] if i < len(dos) else "",
                donts[i] if i < len(donts) else "",
            )
        console.print(table)


def format_tone_list(profiles: list[str]) -> None:
    if not profiles:
        console.print("[dim]No tone profiles found.[/]")
        return
    table = Table(title="Tone Profiles")
    table.add_column("#", style="dim", justify="right")
    table.add_column("Customer ID")
    for i, p in enumerate(profiles, 1):
        table.add_row(str(i), p)
    console.print(table)


# ── Optimize / Jobs ─────────────────────────────────────────────────


STATUS_STYLES = {
    "completed": "bold green",
    "failed": "bold red",
    "pending": "yellow",
    "running": "cyan",
    "auditing": "cyan",
    "tone_extracting": "cyan",
    "rewriting": "cyan",
}


def format_job_status(data: dict) -> None:
    status = data.get("status", "unknown")
    style = STATUS_STYLES.get(status, "white")

    console.print()
    console.print(Panel(
        f"[bold]Job:[/] {data.get('job_id', data.get('url', ''))}\n"
        f"[bold]Status:[/] [{style}]{status}[/]\n"
        f"[bold]URL:[/] {data.get('url', 'N/A')}",
        title="Optimization Job",
        border_style="blue",
    ))

    if status == "completed" and data.get("rewrite_result"):
        rw = data["rewrite_result"]
        console.print(f"  Tone alignment: [bold]{rw.get('tone_alignment_score', 0):.0%}[/]")
        console.print(f"  Issues fixed: [green]{len(rw.get('issues_addressed', []))}[/]")
        console.print(f"  Issues skipped: [dim]{len(rw.get('issues_skipped', []))}[/]")


def format_job_list(jobs: list[dict]) -> None:
    table = Table(title="Optimization Jobs")
    table.add_column("Job ID", style="dim", max_width=8)
    table.add_column("URL")
    table.add_column("Status", justify="center")
    table.add_column("Date", style="dim")
    for j in jobs:
        status = j.get("status", "?")
        style = STATUS_STYLES.get(status, "white")
        table.add_row(
            str(j.get("job_id", ""))[:8],
            j.get("url", ""),
            f"[{style}]{status}[/]",
            str(j.get("started_at", ""))[:10],
        )
    console.print(table)


# ── Freshness ───────────────────────────────────────────────────────


def format_freshness_result(data: dict) -> None:
    summary = data.get("summary", {})
    console.print()
    console.print(Panel(
        f"[bold]Domain:[/] {data.get('domain', 'N/A')}\n"
        f"[bold]Total URLs:[/] {data.get('total_urls_found', 0)}\n"
        f"[bold]Blog URLs:[/] {data.get('blog_urls_found', 0)}",
        title="Freshness Audit",
        border_style="green",
    ))

    results = data.get("results", [])
    if results:
        table = Table(title="URL Schema Status")
        table.add_column("URL", max_width=60)
        table.add_column("Schema", justify="center")
        table.add_column("Published", style="dim")
        for r in results[:20]:
            has = "[green]\u2713[/]" if r.get("has_schema") else "[red]\u2717[/]"
            table.add_row(
                r.get("url", "")[:60],
                has,
                str(r.get("published_date", ""))[:10],
            )
        console.print(table)
        if len(results) > 20:
            console.print(f"  [dim]... and {len(results) - 20} more URLs[/]")


# ── Export ──────────────────────────────────────────────────────────


def format_export(data: dict, output_file: str | None = None) -> None:
    md = data.get("markdown", "")
    if output_file:
        with open(output_file, "w") as f:
            f.write(md)
        console.print(f"[green]\u2713[/] Saved to {output_file}")
    else:
        console.print(md)


# ── Errors ──────────────────────────────────────────────────────────


# ── Credits ────────────────────────────────────────────────────────


def format_credits(data: dict) -> None:
    remaining = data.get("remaining", 0)
    total = data.get("total", 0)
    plan = data.get("plan", "N/A")
    reset = str(data.get("reset_date", "N/A"))[:10]

    console.print()
    console.print(Panel(
        f"[bold]Plan:[/] {plan}\n"
        f"[bold]Credits:[/] {remaining:,} / {total:,} remaining\n"
        f"[bold]Resets:[/] {reset}",
        title="Credit Usage",
        border_style="cyan",
    ))

    breakdown = data.get("breakdown", {})
    if breakdown:
        table = Table(title="Breakdown", show_lines=False)
        table.add_column("Action", style="bold")
        table.add_column("Credits", justify="right")
        if isinstance(breakdown, dict):
            for action, credits in breakdown.items():
                table.add_row(
                    action.replace("_", " ").title(),
                    f"{credits:,}",
                )
        else:
            for item in breakdown:
                table.add_row(
                    item.get("action", "").replace("_", " ").title(),
                    f"{item.get('credits', 0):,}",
                )
        console.print(table)


def show_credit_line(client) -> None:
    """Show one-line credit summary after paid operations. Fails silently."""
    try:
        data = client.get_credits()
        remaining = data.get("remaining", 0)
        total = data.get("total", 0)
        reset = str(data.get("reset_date", ""))[:10]
        console.print(
            f"\n[dim]Credits: {remaining:,} / {total:,} remaining"
            f" | Resets {reset}[/]"
        )
    except Exception:
        pass


# ── llms.txt ──────────────────────────────────────────────────────


def format_llms_txt_result(data: dict, output_file: str | None = None) -> None:
    domain = data.get("domain", "")
    title = data.get("title", domain)
    content = data.get("content", "")
    word_count = data.get("word_count", 0)
    sections = data.get("sections", 0)

    console.print()
    console.print(Panel(
        f"[bold]Domain:[/] {domain}\n"
        f"[bold]Title:[/] {title}\n"
        f"[bold]Words:[/] {word_count}  [bold]Sections:[/] {sections}",
        title="llms.txt Generated",
        border_style="green",
    ))

    if output_file:
        with open(output_file, "w") as f:
            f.write(content)
        console.print(f"[green]\u2713[/] Saved to {output_file}")
    else:
        console.print(content)


# ── robots.txt ────────────────────────────────────────────────


def format_robots_txt_result(data: dict, output_file: str | None = None) -> None:
    domain = data.get("domain", "")
    had_existing = data.get("had_existing", False)
    existing_score = data.get("existing_score", 0)
    new_score = data.get("new_score", 0)
    content = data.get("content", "")
    added = data.get("crawlers_added", [])
    kept = data.get("crawlers_kept", [])
    custom = data.get("crawlers_with_custom_rules", [])
    sitemaps = data.get("sitemaps_added", [])

    console.print()
    console.print(Panel(
        f"[bold]Domain:[/] {domain}\n"
        f"[bold]Existing robots.txt:[/] {'Yes' if had_existing else 'No'}\n"
        f"[bold]Score:[/] {existing_score}/25 → [green]{new_score}/25[/]\n"
        f"[bold]Crawlers added:[/] {len(added)}  "
        f"[bold]Kept:[/] {len(kept)}  "
        f"[bold]Custom rules:[/] {len(custom)}",
        title="robots.txt Generated",
        border_style="green",
    ))

    if added:
        console.print(f"\n[bold]Added ({len(added)}):[/] {', '.join(added)}")
    if kept:
        console.print(f"[bold]Kept ({len(kept)}):[/] {', '.join(kept)}")
    if custom:
        console.print(f"[bold]Custom rules preserved ({len(custom)}):[/] {', '.join(custom)}")
    if sitemaps:
        console.print(f"[bold]Sitemaps added:[/] {', '.join(sitemaps)}")

    if output_file:
        with open(output_file, "w") as f:
            f.write(content)
        console.print(f"\n[green]\u2713[/] Saved to {output_file}")
    else:
        console.print(f"\n[dim]{'─' * 60}[/]")
        console.print(content)


# ── sitemap.xml ──────────────────────────────────────────────


def format_sitemap_result(data: dict, output_file: str | None = None) -> None:
    domain = data.get("domain", "")
    url_count = data.get("url_count", 0)
    urls_with_lastmod = data.get("urls_with_lastmod", 0)
    crawl_depth = data.get("crawl_depth", 0)
    had_existing = data.get("had_existing", False)
    existing_url_count = data.get("existing_url_count", 0)
    content = data.get("content", "")

    console.print()
    console.print(Panel(
        f"[bold]Domain:[/] {domain}\n"
        f"[bold]URLs discovered:[/] {url_count}\n"
        f"[bold]With lastmod:[/] {urls_with_lastmod}\n"
        f"[bold]Crawl depth:[/] {crawl_depth}\n"
        f"[bold]Existing sitemap:[/] {'Yes (' + str(existing_url_count) + ' URLs)' if had_existing else 'No'}",
        title="sitemap.xml Generated",
        border_style="green",
    ))

    if output_file:
        with open(output_file, "w") as f:
            f.write(content)
        console.print(f"\n[green]\u2713[/] Saved to {output_file}")
    else:
        console.print(f"\n[dim]{'─' * 60}[/]")
        console.print(content)


# ── Freshness Code ──────────────────────────────────────────────


def format_freshness_code_result(data: dict, output_file: str | None = None) -> None:
    domain = data.get("domain", "")
    url = data.get("url", "")
    schema_type = data.get("schema_type", "Article")
    had_existing = data.get("had_existing_schema", False)
    estimated = data.get("estimated_score", 0)
    content = data.get("content", "")
    title = data.get("extracted_title")
    author = data.get("extracted_author")
    published = data.get("extracted_published")

    console.print()
    console.print(Panel(
        f"[bold]Domain:[/] {domain}\n"
        f"[bold]URL:[/] {url}\n"
        f"[bold]Schema type:[/] {schema_type}\n"
        f"[bold]Existing schema:[/] {'Yes' if had_existing else 'No'}\n"
        f"[bold]Est. freshness score:[/] {estimated}/25",
        title="Freshness Schema Generated",
        border_style="green",
    ))

    meta_parts = []
    if title:
        meta_parts.append(f"Title: {title}")
    if author:
        meta_parts.append(f"Author: {author}")
    if published:
        meta_parts.append(f"Published: {published}")
    if meta_parts:
        console.print(f"\n[bold]Extracted metadata:[/]")
        for part in meta_parts:
            console.print(f"  {part}")

    if output_file:
        with open(output_file, "w") as f:
            f.write(content)
        console.print(f"\n[green]\u2713[/] Saved to {output_file}")
    else:
        console.print(f"\n[dim]{'─' * 60}[/]")
        console.print(content)

    console.print(f"\n[dim]Add this <script> block to your page's <head>.[/]")


# ── Errors ──────────────────────────────────────────────────────


def format_error(status_code: int, message: str) -> None:
    from stobo import config as cfg

    if status_code in (401, 403):
        has_key = bool(cfg.get_api_key())
        if not has_key:
            hint = (
                "No API key configured.\n"
                "Get your free API key at [bold cyan]https://trystobo.com[/]\n"
                "Then run: [bold]stobo auth login[/]"
            )
        else:
            hint = (
                "Your API key is invalid or expired.\n"
                "Get a new one at [bold cyan]https://trystobo.com[/]\n"
                "Then run: [bold]stobo auth login[/]"
            )
        err_console.print(Panel(hint, title="Authentication Error", border_style="red"))
    elif status_code == 402:
        err_console.print(Panel(
            "You've run out of credits.\n"
            "Top up at [bold cyan]https://trystobo.com[/] to continue using premium tools.",
            title="Insufficient Credits",
            border_style="red",
        ))
    elif status_code == 429:
        err_console.print(Panel(
            "Rate limit reached. Please wait a moment and try again.",
            title="Rate Limited",
            border_style="yellow",
        ))
    else:
        err_console.print(Panel(
            f"[bold red]Error {status_code}[/]\n{message}",
            border_style="red",
        ))
