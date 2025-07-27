import typer
from devlens.analyzer.ai_summary import summarize_code
app = typer.Typer()

@app.command()
def analyze(path: str = typer.Argument(".", help="Path to analyze")):
    print(f"✅ Hello Younes! Analyzing path: {path}")

@app.command()
def summarize(path: str = typer.Argument(".", help="Path to summarize")):
    summaries = summarize_code(path)
   
    for file, summary in summaries:
        print(f"File: {file}\nSummary: {summary}\n")


def main():
    app()

if __name__ == "__main__":
    main()