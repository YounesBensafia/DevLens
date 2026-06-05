"""
Rich UI for Comprehension Debt Scanner.
Pure display — zero business logic here.
"""

import contextlib
from pathlib import Path

from rich import box
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.progress import (  # type: ignore
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table
from rich.text import Text

from devlens.analyzer.scanner import (
    DEFAULT_WEIGHTS,
    RISK_THRESHOLDS,
    FileReport,
    ProjectReport,
    _compute_final_score,
    _get_risk_level,
    _get_top_issues,
    score_breakdown,
)
from devlens.core.git_signals import get_git_signals, get_repo_root
from devlens.core.history import (
    compare_snapshots,
    load_closest_snapshot,
    load_snapshots,
    save_snapshot,
)
from devlens.core.llm_judge import SYSTEM_PROMPT, build_llm_prompt, parse_llm_response
from devlens.core.metrics import analyze_file

console = Console()

RISK_COLORS = {
    "critical": "bold red",
    "high": "red",
    "medium": "yellow",
    "low": "cyan",
    "good": "green",
}


def _score_bar(score: float, width: int = 20, confidence: str = "") -> str:
    filled = int((score / 100) * width)
    color = "red" if score < 35 else "yellow" if score < 55 else "cyan" if score < 70 else "green"
    bar = "█" * filled + "░" * (width - filled)
    suffix = f" {confidence}" if confidence else ""
    return f"[{color}]{bar}[/] {score:.0f}{suffix}"


def _print_header():
    console.print(
        Panel(
            Align.center(Text("DevLens - Comprehension Debt Scanner", style="bold white")),
            border_style="blue",
            box=box.DOUBLE,
            padding=(1, 2),
            subtitle="[dim]Measures how well your team can understand your codebase[/dim]",
        )
    )


def _print_summary(report: ProjectReport):
    score = report.avg_score
    color = "red" if score < 35 else "yellow" if score < 55 else "cyan" if score < 70 else "green"
    dist = report.risk_distribution

    weight_info = ""
    if report.weights_used and report.weights_used != DEFAULT_WEIGHTS:
        w = report.weights_used
        weight_info = (
            f"\n[dim]weights: mét {w['metrics']:.0%} git {w['git']:.0%} llm {w['llm']:.0%}[/dim]"
        )

    grid = Table.grid(padding=(1, 2))
    grid.add_column(justify="center")
    grid.add_column(justify="center")
    grid.add_column(justify="center")
    grid.add_column(justify="center")

    grid.add_row(
        Panel(f"[{color} bold]{score}[/]\nProject Score{weight_info}", border_style=color, padding=(1, 2)),
        Panel(f"[bold]{len(report.files)}[/]\nFiles Analyzed", border_style="blue", padding=(1, 2)),
        Panel(f"[red bold]{dist.get('critical', 0) + dist.get('high', 0)}[/]\nHigh Risk Files", border_style="red", padding=(1, 2)),
        Panel(f"[yellow bold]{len(report.bus_factor_risks)}[/]\nBus Factor Risks", border_style="yellow", padding=(1, 2)),
    )

    console.print(grid)
    console.print()


def _print_table(report: ProjectReport):
    table = Table(
        title="File Comprehension Scores",
        header_style="bold white on dark_blue",
        box=box.ROUNDED,
        border_style="bright_blue",
        show_lines=True,
    )
    table.add_column("Risk", width=8, justify="center", no_wrap=True)
    table.add_column("File", style="cyan", min_width=28, max_width=50)
    table.add_column("Score", min_width=28)
    table.add_column("CC", justify="right", width=5)
    table.add_column("MI", justify="right", width=5)
    table.add_column("Docs", justify="right", width=5)
    table.add_column("Git", width=14)
    table.add_column("Top Issue", style="dim white", min_width=30, max_width=45)

    prev_risk = None
    for r in report.files:
        if prev_risk is not None and r.risk_level != prev_risk:
            table.add_section()
        prev_risk = r.risk_level

        git_info = ""
        if r.git:
            days = r.git.days_since_last_change
            git_info = f"{days}d ago" if days is not None else "no history"
            if r.git.is_orphan:
                git_info += " [yellow]solo[/]"

        top_issue = r.top_issues[0] if r.top_issues else ""
        if len(top_issue) > 45:
            top_issue = top_issue[:42] + "..."

        color = RISK_COLORS.get(r.risk_level, "white")
        confidence = r.breakdown.confidence_band if r.breakdown else ""
        risk_label = f"[{color}]{r.risk_level.upper()}[/]"
        table.add_row(
            risk_label,
            r.path,
            _score_bar(r.final_score, confidence=confidence),
            str(r.metrics.max_cyclomatic_complexity or "-"),
            str(r.metrics.maintainability_index or "-"),
            f"{int(r.metrics.docstring_ratio * 100)}%",
            git_info,
            top_issue,
        )

    console.print(table)
    console.print()


def _print_critical(report: ProjectReport):
    if not report.most_critical:
        return
    table = Table(
        title="Critical Files",
        header_style="bold white on red",
        box=box.ROUNDED,
        border_style="red",
        show_lines=True,
    )
    table.add_column("#", width=3, justify="center", style="dim")
    table.add_column("File", style="cyan", min_width=28, max_width=50)
    table.add_column("Score", justify="center", width=8)
    table.add_column("Issues Found", style="dim white", min_width=30)

    for i, r in enumerate(report.most_critical, 1):
        score_color = "red" if r.final_score < 50 else "yellow"
        issues = r.top_issues if r.top_issues else ["-"]
        issues_text = "\n".join(issues)
        if r.llm and r.llm.explanation:
            issues_text += f"\n[dim]AI: {r.llm.explanation}[/dim]"
        table.add_row(
            str(i),
            r.path,
            f"[{score_color}]{r.final_score:.0f}[/{score_color}]",
            issues_text,
        )

    console.print(table)
    console.print()


def _print_bus_factor(report: ProjectReport):
    if not report.bus_factor_risks:
        return
    table = Table(
        title="Bus Factor Risks - Solo Maintained Files",
        header_style="bold white on dark_goldenrod",
        box=box.ROUNDED,
        border_style="yellow",
        show_lines=True,
    )
    table.add_column("File", style="cyan", min_width=28, max_width=50)
    table.add_column("Authors", justify="right", width=8)
    table.add_column("Commits", justify="right", width=8)
    table.add_column("Last Change", justify="right", width=12)
    table.add_column("Score", justify="center", width=8)

    for r in report.bus_factor_risks:
        g = r.git
        if g is None:
            continue
        table.add_row(
            r.path,
            str(g.unique_authors),
            str(g.total_commits),
            f"{g.days_since_last_change}d ago",
            f"[yellow]{r.final_score:.0f}[/yellow]",
        )

    console.print(table)
    console.print()


def _print_footer(report: ProjectReport):
    score = report.avg_score
    if score >= 70:
        msg = "Your codebase is in decent shape. Keep documenting and refactoring."
    elif score >= 50:
        msg = "Comprehension debt is building up. Prioritize the red files."
    else:
        msg = "High comprehension debt detected. Your team is at risk of losing context."
    console.print(
        Panel(Align.center(Text(msg, style="bold")), border_style="blue", box=box.ROUNDED)
    )


def _print_trend(snapshots):
    if len(snapshots) < 2:
        return
    table = Table(
        title=f"Score Trend (last {len(snapshots)} scans)",
        header_style="bold white on dark_cyan",
        box=box.ROUNDED,
        border_style="cyan",
        show_lines=True,
    )
    table.add_column("Date", width=12, no_wrap=True)
    table.add_column("Score", justify="center", width=8)
    table.add_column("Bar", min_width=28)
    table.add_column("Delta", justify="right", width=10)

    for i, s in enumerate(snapshots[-6:]):
        ts = s.timestamp[:10] if len(s.timestamp) >= 10 else s.timestamp
        filled = int((s.avg_score / 100) * 25)
        bar = "█" * filled + "░" * (25 - filled)
        bar_color = "green" if s.avg_score >= 70 else "yellow" if s.avg_score >= 50 else "red"

        delta = ""
        if i > 0:
            prev = snapshots[-6:][i - 1]
            d = s.avg_score - prev.avg_score
            d_color = "green" if d > 0 else "red" if d < 0 else "white"
            sign = "+" if d > 0 else ""
            delta = f"[{d_color}]{sign}{d:.1f}[/{d_color}]"

        table.add_row(ts, f"[{bar_color}]{s.avg_score:.0f}[/{bar_color}]", f"[{bar_color}]{bar}[/{bar_color}]", delta)

    console.print(table)
    console.print()


def _print_regressions(deltas):
    regressions = {k: v for k, v in deltas.items() if v["delta"] < -5}
    if not regressions:
        return
    regressions = dict(sorted(regressions.items(), key=lambda x: x[1]["delta"]))
    table = Table(
        title="Regressions",
        header_style="bold white on red",
        box=box.ROUNDED,
        border_style="red",
        show_lines=True,
    )
    table.add_column("File", style="cyan", min_width=28, max_width=55)
    table.add_column("Previous", justify="right", width=10)
    table.add_column("Current", justify="right", width=10)
    table.add_column("Delta", justify="right", width=8)

    for path, d in regressions.items():
        table.add_row(path, f"{d['from']:.0f}", f"{d['to']:.0f}", f"[red]{d['delta']:+.1f}[/red]")
    console.print(table)
    console.print()


def _print_improvements(deltas):
    improvements = {k: v for k, v in deltas.items() if v["delta"] > 5}
    if not improvements:
        return
    improvements = dict(sorted(improvements.items(), key=lambda x: -x[1]["delta"]))
    table = Table(
        title="Improvements",
        header_style="bold white on green",
        box=box.ROUNDED,
        border_style="green",
        show_lines=True,
    )
    table.add_column("File", style="cyan", min_width=28, max_width=55)
    table.add_column("Previous", justify="right", width=10)
    table.add_column("Current", justify="right", width=10)
    table.add_column("Delta", justify="right", width=8)

    for path, d in improvements.items():
        table.add_row(path, f"{d['from']:.0f}", f"{d['to']:.0f}", f"[green]{d['delta']:+.1f}[/green]")
    console.print(table)
    console.print()


def display_scan_results(
    report: ProjectReport,
    show_trend: bool = False,
    show_regression: bool = False,
    since_days: int | None = None,
    weights: dict | None = None,
):
    console.clear()
    _print_header()
    _print_summary(report)

    if show_trend:
        snapshots = load_snapshots(report.project_path)
        _print_trend(snapshots)

    if show_regression and since_days is not None:
        baseline = load_closest_snapshot(report.project_path, since_days)
        if baseline:
            snapshots = load_snapshots(report.project_path)
            current = snapshots[-1] if snapshots else None
            if current:
                deltas = compare_snapshots(baseline, current)
                _print_regressions(deltas)
                _print_improvements(deltas)

    _print_table(report)
    _print_critical(report)
    _print_bus_factor(report)
    _print_footer(report)


def run_scan_with_progress(
    project_path: str,
    use_llm: bool,
    send_request_fn,
    build_payload_fn,
    weights: dict | None = None,
) -> ProjectReport:
    from devlens.utils.structure_the_project import list_non_ignored_files

    console.clear()
    _print_header()

    all_files = list_non_ignored_files(project_path)
    python_files = [f for f in all_files if f.endswith(".py")]
    total = min(len(python_files), 50)

    console.print(f"\n[dim]Found {total} Python files to analyze...[/dim]\n")

    file_reports = []

    with Progress(
        SpinnerColumn(style="blue"),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(complete_style="blue", finished_style="green"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
        expand=True,
    ) as progress:
        task = progress.add_task("Scanning...", total=total)
        repo_root = get_repo_root(project_path)

        for file_path in python_files[:50]:
            progress.update(task, description=f"[dim]{file_path[-50:]}[/dim]")

            metrics = analyze_file(file_path)
            if metrics.error == "empty file":
                progress.advance(task)
                continue

            git = None
            if repo_root:
                with contextlib.suppress(Exception):
                    git = get_git_signals(file_path, repo_root, file_size_lines=metrics.loc)

            llm = None
            if use_llm and send_request_fn and build_payload_fn:
                try:
                    source = Path(file_path).read_text(encoding="utf-8", errors="ignore")
                    prompt = build_llm_prompt(source, file_path)
                    payload = build_payload_fn(SYSTEM_PROMPT, prompt)
                    data = send_request_fn(payload)
                    raw_text = data["choices"][0]["message"]["content"]
                    llm = parse_llm_response(raw_text)
                except Exception:
                    pass

            final_score = _compute_final_score(metrics, git, llm, weights)
            risk_level = _get_risk_level(final_score)
            top_issues = _get_top_issues(metrics, git, llm)
            breakdown = score_breakdown(metrics, git, llm, weights)

            file_reports.append(
                FileReport(
                    path=file_path,
                    metrics=metrics,
                    git=git,
                    llm=llm,
                    final_score=final_score,
                    risk_level=risk_level,
                    top_issues=top_issues,
                    breakdown=breakdown,
                )
            )
            progress.advance(task)

    file_reports.sort(key=lambda r: r.final_score)
    avg_score = (
        sum(r.final_score for r in file_reports) / len(file_reports) if file_reports else 0.0
    )
    risk_dist = {level: 0 for level in RISK_THRESHOLDS}
    for r in file_reports:
        risk_dist[r.risk_level] = risk_dist.get(r.risk_level, 0) + 1

    report = ProjectReport(
        project_path=project_path,
        files=file_reports,
        avg_score=round(avg_score, 1),
        risk_distribution=risk_dist,
        most_critical=file_reports[:5],
        bus_factor_risks=[
            r for r in file_reports if r.git and r.git.is_orphan and r.final_score < 65
        ],
        weights_used=weights,
    )
    with contextlib.suppress(Exception):
        save_snapshot(report)
    return report
