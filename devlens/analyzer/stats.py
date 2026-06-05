from rich import box
from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from devlens.utils.count_folders import count_directories
from devlens.utils.count_lines_and_files import count_lines_by_language_in_project
from devlens.utils.get_size_project import get_logical_size_of_the_project
from devlens.utils.structure_the_project import list_non_ignored_files

console = Console()


def display_code_summary(path: str):
    console.clear()

    header_text = Text("DevLens - Project Summary", style="bold white on cyan")
    header_panel = Panel(
        Align.center(header_text), border_style="cyan", box=box.DOUBLE, padding=(1, 2)
    )
    console.print(header_panel)
    console.print()

    line_counts_by_language = count_lines_by_language_in_project(path)

    if line_counts_by_language is None:
        error_panel = Panel(
            "No supported code files found in the specified path.",
            title="Warning",
            border_style="yellow",
            box=box.ROUNDED,
            padding=(1, 2),
        )
        console.print(error_panel)
        return

    total_files = len(list_non_ignored_files(path))
    total_lines = sum(v[0] for v in line_counts_by_language.values())

    stats_columns = Columns(
        [
            Panel(
                f"[green bold]{total_files}[/]\nTotal Files",
                border_style="green",
                padding=(1, 2),
            ),
            Panel(
                f"[cyan bold]{total_lines}[/]\nTotal Lines",
                border_style="cyan",
                padding=(1, 2),
            ),
            Panel(
                f"[yellow bold]{count_directories(path)}[/]\nDirectories",
                border_style="yellow",
                padding=(1, 2),
            ),
            Panel(
                f"[magenta bold]{len(line_counts_by_language)}[/]\nLanguages",
                border_style="magenta",
                padding=(1, 2),
            ),
        ],
        expand=True,
    )

    console.print(stats_columns)
    console.print()

    lang_table = Table(
        title="Language Breakdown",
        show_header=True,
        header_style="bold white on magenta",
        box=box.ROUNDED,
        border_style="magenta",
        title_style="bold magenta",
        show_lines=True,
    )
    lang_table.add_column("Language", style="cyan", no_wrap=True)
    lang_table.add_column("Lines", justify="right", style="green")
    lang_table.add_column("Percentage", justify="right", style="yellow")

    sorted_languages = sorted(line_counts_by_language.items(), key=lambda x: x[1][0], reverse=True)

    for lang, (count, *_) in sorted_languages:
        percentage = (count / total_lines) * 100 if total_lines > 0 else 0
        lang_table.add_row(lang.upper(), str(count), f"{percentage:.1f}%")

    console.print(lang_table)
    console.print()

    console.print(
        Panel(
            f"Analysis complete: [green]{total_files}[/green] files, [blue]{total_lines:,}[/blue] lines, [cyan]{len(line_counts_by_language)}[/cyan] languages.",
            title="Summary",
            border_style="green",
            padding=(1, 2),
        )
    )
    console.print()

    size_mb = get_logical_size_of_the_project(path)
    console.print(
        Panel(
            f"Logical Size: [bold yellow]{size_mb} MB[/bold yellow]",
            title="Project Size",
            border_style="yellow",
            padding=(1, 2),
        )
    )
