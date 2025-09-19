import os
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.layout import Layout
from rich.columns import Columns
from rich import box
from devlens.utils.deadcode_analyze import analyze_python_file
from devlens.utils.structure_the_project import list_non_ignored_files

console = Console()

def analyze_python_files(python_files, dead_files, progress, task):
    total_issues = 0
    for file_path in python_files:
        progress.update(task, description=f"Checking: {file_path}")
        issues = analyze_python_file(file_path)
        if issues:
            dead_files[file_path] = issues
            total_issues += len(issues)
            
        progress.advance(task)
    return total_issues

def get_python_files_and_ignored_count(path):
    non_ignored_files_in_the_repo = list_non_ignored_files(path)
    python_files = [f for f in non_ignored_files_in_the_repo if f.endswith('.py')]
    ignored_files = len(non_ignored_files_in_the_repo) - len(python_files)
    return python_files,ignored_files

def find_dead_files(path: str):
    """Enhanced dead code analysis with comprehensive detection and gitignore support"""
    console.clear()
    layout = Layout()
    layout.split_column(
        Layout(name="header"),
        Layout(name="body", ratio=8)
    )

    header_text = Text("DevLens - Dead Code Analyzer", style="bold white on red")
    header_panel = Panel(
        Align.center(header_text),
        border_style="red",
        box=box.DOUBLE,
        padding=(1, 2)
    )
    console.print(header_panel)

    python_files, ignored_files = get_python_files_and_ignored_count(path)

    if not python_files:
        error_panel = Panel(
            f"No Python files found in the specified path.\n Ignored {ignored_files} files based on patterns.",
            title="Warning",
            border_style="yellow",
            box=box.ROUNDED,
            padding=(1, 2)
        )
        console.print(error_panel)
        return
    
    stats_columns = Columns([
        Panel(f"[cyan bold]{len(python_files)}[/]\n[blue]Python Files", border_style="blue", padding=(1, 2)),
        Panel(f"[yellow bold]{ignored_files}[/]\n[blue]Ignored Files", border_style="blue", padding=(1, 2)),
        Panel(f"[green bold]{os.path.join(os.path.abspath(path))}[/]\n[blue]Project Path", border_style="blue", padding=(1, 2))
    ], expand=True)
    
    console.print(stats_columns)
    
    dead_files = {}
    total_issues = 0
    
    with Progress(
        SpinnerColumn(style="green"),
        TextColumn("[bold green]{task.description}"),
        BarColumn(complete_style="green", finished_style="green"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
        expand=True
    ) as progress:
        task = progress.add_task("Analyzing files...", total=len(python_files))
        total_issues = analyze_python_files(python_files, dead_files, progress, task)
    
    console.print()
    
    if not dead_files:
        success_panel = Panel(
            "No dead code detected! All Python files appear to be in use.",
            title="Clean Code",
            border_style="green",
            box=box.HEAVY,
            padding=(1, 2)
        )
        console.print(success_panel)
    else:
        results_table = Table(
            title="Dead Code Analysis Results",
            show_header=True,
            header_style="bold white on red",
            box=box.ROUNDED,
            title_style="bold red",
            border_style="red"
        )
        results_table.add_column("File", style="cyan", min_width=30)
        results_table.add_column("Issue Type", style="yellow", min_width=15)
        results_table.add_column("Description", style="white", min_width=40)
        
        emoji_map = {
            "empty": "🗑️",
            "comments_only": "💬",
            "imports_only": "📦",
            "unused_imports": "🚫",
            "syntax_error": "❌",
            "read_error": "⚠️"
        }
        
        for file_path, issues in dead_files.items():
            for issue_type, description in issues:
                emoji = emoji_map.get(issue_type, "🔍")
                results_table.add_row(
                    f"{emoji} {file_path}",
                    issue_type.replace("_", " ").title(),
                    description
                )
        
        console.print(results_table)
        
        issue_counts = {}
        for issues in dead_files.values():
            for issue_type, _ in issues:
                issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        summary_columns = Columns([
            Panel(f"[blue bold]{len(python_files)}[/]\n[white]Total Files", border_style="blue", padding=(1, 2)),
            Panel(f"[red bold]{len(dead_files)}[/]\n[white]Files with Issues", border_style="red", padding=(1, 2)),
            Panel(f"[yellow bold]{total_issues}[/]\n[white]Total Issues", border_style="yellow", padding=(1, 2)),
            Panel(f"[green bold]{len(python_files) - len(dead_files)}[/]\n[white]Clean Files", border_style="green", padding=(1, 2))
        ], expand=True)
        
        console.print()
        console.print(summary_columns)
        
        if issue_counts:
            console.print()
            breakdown_table = Table(
                title="Issue Breakdown", 
                show_header=True, 
                header_style="bold white on cyan",
                box=box.ROUNDED,
                border_style="cyan",
                title_style="bold cyan"
            )
            breakdown_table.add_column("Issue Type", style="yellow")
            breakdown_table.add_column("Count", style="red", justify="right")
            breakdown_table.add_column("Description", style="white")
            
            descriptions = {
                "empty": "Completely empty files",
                "comments_only": "Files with only comments",
                "imports_only": "Files with only imports",
                "unused_imports": "Potentially unused imports",
                "syntax_error": "Files with syntax errors",
                "read_error": "Files that couldn't be read"
            }
            
            for issue_type, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True):
                breakdown_table.add_row(
                    issue_type.replace("_", " ").title(),
                    str(count),
                    descriptions.get(issue_type, "Unknown issue")
                )
            
            console.print(breakdown_table)
    
    footer = Panel(
        Align.center(Text("Dead code analysis complete!", style="bold green")),
        border_style="green",
        box=box.ROUNDED
    )
    console.print()
    console.print(footer)


