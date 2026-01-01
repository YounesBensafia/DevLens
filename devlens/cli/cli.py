import typer
from devlens.analyzer.ai_summary import ai_summarize_code
from devlens.analyzer.stats import display_code_summary
from devlens.analyzer.readme_gen import generate_readme
from devlens.analyzer.deadcode import find_dead_files
from devlens.utils.check_the_path import check_path

app = typer.Typer(
    add_completion=False,
    help="DevLens: AI-powered code analysis and documentation tool",
)


@app.callback(invoke_without_command=True)
def _root(ctx: typer.Context, 
    
    st: str | None = typer.Option(
        None, 
        "-st", "--st", 
        metavar="PATH", 
        help="Generate project statistics"
    ),

    an: str | None = typer.Option(
        None,
        "-an",
        "--an",
        metavar="PATH",
        help="Analyze code with AI-powered summaries",
    ),
    dc: str | None = typer.Option(
        None,
        "-deadcode",
        "--deadcode",
        metavar="PATH",
        help="Find dead code and unused imports",
    ),
    rd: bool = typer.Option(
        False, "-rd", "--rd", help="Generate a professional README.md file"
    ),
):
    chosen = sum([st is not None, an is not None, dc is not None, rd])
    if chosen > 1:
        raise typer.BadParameter("Choose only one option: -st / -an / -dc / -rd")

    if st is not None:
        check_path(st)
        display_code_summary(st)
        raise typer.Exit()

    if an is not None:
        check_path(an)
        ai_summarize_code(an)
        raise typer.Exit()

    if dc is not None:
        check_path(dc)
        find_dead_files(dc)
        raise typer.Exit()

    if rd:
        generate_readme()
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


def main():
    app()


if __name__ == "__main__":
    main()
