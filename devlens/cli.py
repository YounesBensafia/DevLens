# devlens/cli.py

import typer
from devlens.analyzer.summary import count_lines_by_language
from devlens.analyzer.ai_summary import summarize_code
from devlens.analyzer.deadcode import find_dead_files
from devlens.render.printer import print_summary, print_ai_summary, print_dead_files

app = typer.Typer()  # this registers subcommands

@app.command()  # ✅ this makes `analyze` a valid subcommand
def analyze(path: str = "."):
    """
    Analyze a codebase at the given path.
    """
    print_summary(path, count_lines_by_language(path))
    print_ai_summary(summarize_code(path))
    print_dead_files(find_dead_files(path))


import sys

def main():
    app(prog_name="devlens", args=sys.argv[1:])

if __name__ == "__main__":
    main()