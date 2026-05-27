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
        _run_scan(scan, use_llm=not no_llm)
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


def _run_scan(path: str, use_llm: bool):
    from devlens.analyzer.scan_display import display_scan_results, run_scan_with_progress
    from devlens.llm.client import build_payload, send_request

    report = run_scan_with_progress(
        project_path=path,
        use_llm=use_llm,
        send_request_fn=send_request if use_llm else None,
        build_payload_fn=build_payload if use_llm else None,
    )
    display_scan_results(report)


def main():
    app()


if __name__ == "__main__":
    main()
