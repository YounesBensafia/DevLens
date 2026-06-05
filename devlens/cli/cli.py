import typer

from devlens.analyzer.ai_summary import ai_summarize_code
from devlens.analyzer.stats import display_code_summary
from devlens.utils.check_the_path import check_path

app = typer.Typer(
    add_completion=False,
    help="DevLens: Comprehension debt scanner + AI code analysis",
)


@app.callback(invoke_without_command=True)
def _root(
    ctx: typer.Context,
    st: str | None = typer.Option(
        None, "-st", "--st", metavar="PATH", help="Generate project statistics"
    ),
    an: str | None = typer.Option(
        None,
        "-an",
        "--an",
        metavar="PATH",
        help="Analyze code with AI-powered summaries",
    ),
    scan: str | None = typer.Option(
        None,
        "-scan",
        "--scan",
        metavar="PATH",
        help="Scan comprehension debt - score every file by how hard it is to understand",
    ),
    no_llm: bool = typer.Option(
        False, "--no-llm", help="Run -scan without LLM (faster, fully deterministic)"
    ),
    trend: bool = typer.Option(
        False, "--trend", help="Show score trajectory across past snapshots"
    ),
    regression: bool = typer.Option(
        False, "--regression", help="Flag files that worsened since last scan"
    ),
    since: int | None = typer.Option(
        None,
        "--since",
        metavar="DAYS",
        help="Compare against snapshot from N days ago (implies --regression)",
    ),
):
    chosen = sum([st is not None, an is not None, scan is not None])
    if chosen > 1:
        raise typer.BadParameter("Choose only one option at a time.")

    if st is not None:
        check_path(st)
        display_code_summary(st)
        raise typer.Exit()

    if an is not None:
        check_path(an)
        ai_summarize_code(an)
        raise typer.Exit()

    if scan is not None:
        check_path(scan)
        _run_scan(
            scan,
            use_llm=not no_llm,
            show_trend=trend,
            show_regression=regression or since is not None,
            since_days=since,
        )
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


def _run_scan(
    path: str,
    use_llm: bool,
    show_trend: bool = False,
    show_regression: bool = False,
    since_days: int | None = None,
):
    from devlens.analyzer.scan_display import display_scan_results, run_scan_with_progress
    from devlens.config.project_config import load_weights
    from devlens.llm.client import build_payload, send_request

    weights = load_weights(path)

    report = run_scan_with_progress(
        project_path=path,
        use_llm=use_llm,
        send_request_fn=send_request if use_llm else None,
        build_payload_fn=build_payload if use_llm else None,
        weights=weights,
    )
    display_scan_results(
        report,
        show_trend=show_trend,
        show_regression=show_regression,
        since_days=since_days,
    )


@app.command()
def check_pr(
    repo: str = typer.Option(".", "--repo", help="Path to the git repository"),
    base: str = typer.Option("main", "--base", help="Base branch (e.g. main)"),
    head: str | None = typer.Option(None, "--head", help="Head branch (default: current branch)"),
    threshold: int = typer.Option(60, "--threshold", help="Slop score threshold (0–100)"),
    output: str = typer.Option("text", "--output", help="Output format: text or json"),
    fail_on_slop: bool = typer.Option(
        False,
        "--fail-on-slop",
        help="Exit with code 1 if slop score >= threshold",
    ),
    pr_body: str | None = typer.Option(
        None,
        "--pr-body",
        help="PR description text or path to file containing it",
    ),
):
    """Detect AI-generated or low-effort PRs using heuristic signals (no LLM)."""
    from rich import box
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    from devlens.slop import compute_slop_score

    result = compute_slop_score(
        repo_path=repo,
        base_branch=base,
        head_branch=head,
        pr_body=pr_body,
        threshold=threshold,
    )

    if output == "json":
        import json as j

        data = {
            "slop_score": result.slop_score,
            "threshold": result.threshold,
            "flagged": result.flagged,
            "signals": {
                name: {"raw": s.raw, "weighted": s.weighted, "verdict": s.verdict}
                for name, s in result.signals.items()
            },
            "summary": result.summary,
        }
        print(j.dumps(data, indent=2))
    else:
        console = Console()
        label = "FLAGGED - POSSIBLE AI SLOP" if result.flagged else "PASSED - LOOKS HUMAN"
        color = "red" if result.flagged else "green"

        console.print(
            Panel(
                f"[bold {color}]DevLens Slop Report — {label}[/bold {color}]",
                border_style=color,
                box=box.DOUBLE,
                padding=(1, 2),
            )
        )

        table = Table(
            title=f"Slop Score: {result.slop_score:.0f}/100  (threshold: {threshold})",
            header_style="bold white on dark_blue",
            box=box.ROUNDED,
            border_style="bright_blue",
            show_lines=True,
        )
        table.add_column("Signal", style="cyan", no_wrap=True)
        table.add_column("Raw Value", justify="right")
        table.add_column("Weighted", justify="right")
        table.add_column("Verdict", justify="center")

        verdict_colors = {"FAIL": "bold red", "WARN": "yellow", "PASS": "green"}
        for name, signal in result.signals.items():
            vc = verdict_colors.get(signal.verdict, "white")
            table.add_row(
                name.replace("_", " "),
                f"{signal.raw:.1f}",
                f"{signal.weighted:.1f}",
                f"[{vc}]{signal.verdict}[/{vc}]",
            )

        table.add_row(
            "[bold]Total[/bold]",
            "",
            f"[bold]{result.slop_score:.1f}[/bold]",
            f"[bold {color}]{'FLAGGED' if result.flagged else 'PASSED'}[/bold {color}]",
        )
        console.print(table)
        console.print(
            Panel(
                result.summary,
                border_style="blue",
                box=box.SIMPLE,
                padding=(0, 2),
            )
        )

    if result.flagged and fail_on_slop:
        raise typer.Exit(code=1)


def main():
    app()


if __name__ == "__main__":
    main()
