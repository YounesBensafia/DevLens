"""
Rich UI for Comprehension Debt Scanner.
Pure display — zero business logic here.
"""

import contextlib
from pathlib import Path

from rich import box
from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text

from devlens.analyzer.scanner import (
    RISK_THRESHOLDS,
    FileReport,
    ProjectReport,
    _compute_final_score,
    _get_risk_level,
    _get_top_issues,
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

RISK_EMOJI = {
    "critical": "critical",
    "high": "high",
    "medium": "medium",
    "low": "low",
    "good": "good",
}


def _score_bar(score: float, width: int = 20) -> str:
    filled = int((score / 100) * width)
    color = "red" if score < 35 else "yellow" if score < 55 else "cyan" if score < 70 else "green"
    bar = "█" * filled + "░" * (width - filled)
    return f"[{color}]{bar}[/] {score:.0f}"


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

    console.print(
        Columns(
            [
                Panel(
                    f"[{color} bold]{score}[/]\n[white]Project Score",
                    border_style=color,
                    padding=(1, 2),
                ),
                Panel(
                    f"[white bold]{len(report.files)}[/]\n[white]Files Analyzed",
                    border_style="blue",
                    padding=(1, 2),
                ),
                Panel(
                    f"[red bold]{dist.get('critical', 0) + dist.get('high', 0)}[/]\n[white]High Risk Files",
                    border_style="red",
                    padding=(1, 2),
                ),
                Panel(
                    f"[yellow bold]{len(report.bus_factor_risks)}[/]\n[white]Bus Factor Risks",
                    border_style="yellow",
                    padding=(1, 2),
                ),
            ],
            expand=True,
        )
    )
    console.print()


def _print_table(report: ProjectReport):
    table = Table(
        title="File Comprehension Scores",
        header_style="bold white on dark_blue",
        box=box.ROUNDED,
        border_style="blue",
        show_lines=True,
    )
    table.add_column("Risk", width=6, justify="center")
    table.add_column("File", style="cyan", min_width=30)
    table.add_column("Score", min_width=26)
    table.add_column("CC", justify="right", width=5)
    table.add_column("MI", justify="right", width=6)
    table.add_column("Docs", justify="right", width=6)
    table.add_column("Git", width=16)
    table.add_column("Top Issue", style="dim white", min_width=35)

    for r in report.files:
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
        table.add_row(
            f"[{color}]{RISK_EMOJI.get(r.risk_level, '')}[/]",
            r.path,
            _score_bar(r.final_score),
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
    console.print(
        Panel(
            "[bold red]Critical Files - Fix These First[/bold red]",
            border_style="red",
            box=box.HEAVY,
        )
    )
    for i, r in enumerate(report.most_critical, 1):
        issues_text = "\n".join(f"  - {issue}" for issue in r.top_issues)
        llm_note = ""
        if r.llm and r.llm.explanation:
            llm_note = f"\n  [dim italic]AI: {r.llm.explanation}[/dim italic]"
        console.print(
            Panel(
                f"[yellow]Score: {r.final_score}/100[/yellow]\n{issues_text}{llm_note}",
                title=f"[red]#{i} {r.path}[/red]",
                title_align="left",
                border_style="red",
                box=box.ROUNDED,
                padding=(0, 2),
            )
        )
    console.print()


def _print_bus_factor(report: ProjectReport):
    if not report.bus_factor_risks:
        return
    console.print(
        Panel(
            "[bold yellow]Bus Factor Risks - Only 1 Person Understands These[/bold yellow]",
            border_style="yellow",
            box=box.HEAVY,
        )
    )
    for r in report.bus_factor_risks:
        g = r.git
        console.print(
            f"  [yellow]solo[/yellow]  [cyan]{r.path}[/cyan]  "
            f"[dim]({g.unique_authors} author, {g.total_commits} commits, "
            f"last: {g.days_since_last_change}d ago, score: {r.final_score})[/dim]"
        )
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
    score_color = _trend_color
    lines = ["Project Score Trend (last {} scans):".format(len(snapshots))]
    for i, s in enumerate(snapshots[-6:]):
        ts = s.timestamp[:10] if len(s.timestamp) >= 10 else s.timestamp
        filled = int((s.avg_score / 100) * 25)
        bar = "█" * filled + "░" * (25 - filled)
        delta = ""
        if i > 0:
            prev = snapshots[-6:][i - 1]
            d = s.avg_score - prev.avg_score
            symbol = "▲" if d > 0 else "▼" if d < 0 else "─"
            delta = f"  {symbol} {abs(d):+.1f}"
        marker = "  ← current" if i == len(snapshots[-6:]) - 1 else ""
        lines.append(f"  {ts}  {bar}  {s.avg_score:.0f}{delta}{marker}")
    console.print(Panel("\n".join(lines), title="Trend", border_style="cyan"))
    console.print()


def _trend_color(score: float) -> str:
    return "green" if score >= 70 else "yellow" if score >= 50 else "red"


def _print_regressions(deltas):
    regressions = {k: v for k, v in deltas.items() if v["delta"] < -5}
    if not regressions:
        return
    regressions = dict(sorted(regressions.items(), key=lambda x: x[1]["delta"]))
    lines = []
    for path, d in regressions.items():
        lines.append(f"  [red]✗[/] {path}  {d['from']:.0f} → {d['to']:.0f}  [red]{d['delta']:+.1f}[/]")
    console.print(Panel("\n".join(lines), title="Regressions", border_style="red"))
    console.print()


def _print_improvements(deltas):
    improvements = {k: v for k, v in deltas.items() if v["delta"] > 5}
    if not improvements:
        return
    improvements = dict(sorted(improvements.items(), key=lambda x: -x[1]["delta"]))
    lines = []
    for path, d in improvements.items():
        lines.append(f"  [green]✓[/] {path}  {d['from']:.0f} → {d['to']:.0f}  [green]{d['delta']:+.1f}[/]")
    console.print(Panel("\n".join(lines), title="Improvements", border_style="green"))
    console.print()


def display_scan_results(
    report: ProjectReport,
    show_trend: bool = False,
    show_regression: bool = False,
    since_days: int | None = None,
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
                    git = get_git_signals(file_path, repo_root)

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

            final_score = _compute_final_score(metrics, git, llm)
            risk_level = _get_risk_level(final_score)
            top_issues = _get_top_issues(metrics, git, llm)

            file_reports.append(
                FileReport(
                    path=file_path,
                    metrics=metrics,
                    git=git,
                    llm=llm,
                    final_score=final_score,
                    risk_level=risk_level,
                    top_issues=top_issues,
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
    )
    with contextlib.suppress(Exception):
        save_snapshot(report)
    return report
