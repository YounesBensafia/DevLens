from rich.console import Console

console = Console()

def print_summary(path, summary):
    console.print(f"\n📁 [bold cyan]Analyzing Project:[/bold cyan] {path}")
    console.print("[green]📊 Language Breakdown:[/green]")
    for lang, lines in summary.items():
        console.print(f"  - {lang}: {lines} lines")

def print_ai_summary(summaries):
    console.print("\n🧠 [bold yellow]AI Summary:[/bold yellow]")
    for file, summary in summaries:
        console.print(f"\n[underline]{file}[/underline]\n{summary}")

def print_dead_files(files):
    console.print("\n🧹 [red]Dead Code Detected:[/red]")
    if files:
        for f in files:
            console.print(f"  - {f}")
    else:
        console.print("  ✅ No dead code found!")
