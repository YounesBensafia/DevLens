import typer
from devlens.analyzer.ai_summary import summarize_code
from devlens.analyzer.summary import display_code_summary
from devlens.analyzer.readme_gen import generate_readme
from devlens.analyzer.deadcode import find_dead_files

app = typer.Typer()

@app.command()
def analyze(path: str = typer.Argument(".", help="Path to analyze")):
    """Analyze code with AI-powered summaries"""
    summarize_code(path)

@app.command()
def summary(path: str = typer.Argument(".", help="Path to summarize")):
    """Generate comprehensive project summary"""
    display_code_summary(path)

@app.command()
def readme(path: str = typer.Argument(".", help="Path to generate README for")):
    """Generate a professional README.md file"""
    generate_readme(path)

@app.command()
def deadcode(path: str = typer.Argument(".", help="Path to analyze for dead code")):
    find_dead_files(path)


def main():
    app()

if __name__ == "__main__":
    main()