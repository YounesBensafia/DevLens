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


def main():
    app()


if __name__ == "__main__":
    main()
