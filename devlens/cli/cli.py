import typer
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analyzer.ai_summary import summarize_code
from analyzer.stats import display_code_summary
from analyzer.readme_gen import generate_readme
from analyzer.deadcode import find_dead_files
from utils.check_the_path import check_path
app = typer.Typer(add_completion=False, help="DevLens: AI-powered code analysis and documentation tool")

@app.command()
def analyze(path: str = typer.Argument(".", show_default=True)):
    """Analyze code with AI-powered summaries"""
    check_path(path)
    summarize_code(path)

@app.command()
def stats(path: str = typer.Argument(".", show_default=True)):
    """Generate project statistics (alias for summary)"""
    check_path(path)
    display_code_summary(path)

@app.command()
# FIXME: more tests for this function
def readme():
    """Generate a professional README.md file"""
    generate_readme()

@app.command()
def deadcode(
    path: str = typer.Argument(".", show_default=True),
):
    """Find dead code, empty files, and unused imports"""
    check_path(path)
    find_dead_files(path)

def main():
    app()

if __name__ == "__main__":
    main()