import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.layout import Layout
from rich.columns import Columns
from rich import box    
from devlens.config.settings import LEVEL_OF_TREE
from devlens.utils.get_tree_project import git_tree_with_styles
from devlens.utils.count_lines_and_files import count_lines_by_language_in_project
from devlens.utils.structure_the_project import list_non_ignored_files
from devlens.utils.count_folders import count_directories
from devlens.utils.get_size_project import get_logical_size_of_the_project

console = Console()

# TODO: to enhace with more stats

def display_code_summary(path: str):
    """Display a comprehensive code summary with professional styling"""
    console.clear()
    layout = Layout()
    layout.split_column(
        Layout(name="header"),
        Layout(name="body", ratio=8)
    )

    header_text = Text("DevLens - Project Summary", style="bold white on cyan")
    header_panel = Panel(
        Align.center(header_text),
        border_style="cyan",
        box=box.DOUBLE,
        padding=(1, 2)
    )
    console.print(header_panel)
    console.print()
    line_counts_by_language = count_lines_by_language_in_project(path)
    project_structure = git_tree_with_styles(path, LEVEL_OF_TREE)

    if line_counts_by_language is None:
        error_panel = Panel(
            "No supported code files found in the specified path.",
            title="Warning",
            border_style="yellow",
            box=box.ROUNDED,
            padding=(1, 2)
        )
        console.print(error_panel)
        return
    total_files = sum(list_non_ignored_files(path).__len__() for _ in [0])

    total_lines = 0
    for line_count in line_counts_by_language.values():
        total_lines += line_count[0]
        
    # styling
    stats_columns = Columns([
        Panel(f"[green bold]{total_files}[/]\n[blue]Total Files", border_style="blue", padding=(1, 2)),
        Panel(f"[cyan bold]{total_lines}[/]\n[blue]Total Lines", border_style="blue", padding=(1, 2)),
        Panel(f"[yellow bold]{count_directories(path)}[/]\n[blue]Directories", border_style="blue", padding=(1, 2)),
        Panel(f"[magenta bold]{len(line_counts_by_language)}[/]\n[blue]Languages", border_style="blue", padding=(1, 2))
    ], expand=True)
    
    console.print(stats_columns)
    console.print()
    
    lang_table = Table(
        title="Language Breakdown", 
        show_header=True, 
        header_style="bold white on magenta",
        box=box.ROUNDED,
        border_style="magenta",
        title_style="bold magenta"
    )
    lang_table.add_column("Language", style="cyan", no_wrap=True)
    lang_table.add_column("Lines", justify="right", style="green")
    lang_table.add_column("Percentage", justify="right", style="yellow")
    
    # styling
    console.print(Panel(
        project_structure,
        title="[bold cyan]Project Structure[/bold cyan]",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(1, 2),
        expand=False
    ))
    
    sorted_languages = sorted(line_counts_by_language.items(), key=lambda x: x[1][0], reverse=True)

    for i in sorted_languages:
        percentage = (i[1][0] / total_lines) * 100 if total_lines > 0 else 0
        lang_table.add_row(
            f"{i[0].upper()}",
            f"{i[1][0]}",
            f"{percentage:.1f}%"
        )

    # styling
    console.print(lang_table)
    console.print()    
    console.print(Panel(
        f"Analysis complete! Found [green]{total_files}[/green] files with [blue]{total_lines:,}[/blue] lines of code across [cyan]{len(line_counts_by_language)}[/cyan] languages (Markdown + Programming Languages).",
        title="Summary",
        border_style="green",
        padding=(1, 2)
    ))
    console.print()
    console.print(Panel(
        f"Logical Size of the Project: [bold yellow]{get_logical_size_of_the_project(path)} MB[/bold yellow]",
        title="Project Size",
        border_style="yellow",
        padding=(1, 2)
    ))
