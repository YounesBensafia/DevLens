import typer
from devlens.analyzer.ai_summary import summarize_code
from devlens.analyzer.summary import display_code_summary

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
def stats(path: str = typer.Argument(".", help="Path to get statistics")):
    """Quick project statistics"""
    display_code_summary(path)


def main():
    app()

if __name__ == "__main__":
    main()