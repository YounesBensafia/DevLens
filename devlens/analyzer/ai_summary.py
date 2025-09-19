import os
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.align import Align
from rich.layout import Layout
from rich.columns import Columns
from rich import box
from devlens.utils.structure_the_project import list_non_ignored_files
from devlens.prompt.ai_summary_prompt import generate_ai_summary_prompt as prompt
from devlens.prompt.ai_summary_prompt import system_message
from devlens.llm.client import build_payload
from devlens.llm.client import send_request

console = Console()


def ai_summarize_code(path: str, max_files=10):
    summaries = []
    one_file = False
    if os.path.isfile(path):
        files_to_keep = [path]
        one_file = True

    else:
        files_to_keep = list_non_ignored_files(path)

    console.clear()
    layout = Layout()
    layout.split_column(
        Layout(name="header"),
        Layout(name="body", ratio=8)
    )

    # start styling
    header_text = Text("DevLens - AI Code Analyzer", style="bold white on blue")
    header_panel = Panel(Align.center(header_text), border_style="blue", box=box.DOUBLE, padding=(1, 2))
    console.print(header_panel)
    console.print(f"[dim]Loaded {len(files_to_keep)} files to analyze[/dim]")

    if not files_to_keep:
        error_panel = Panel(
            f"No files found in the specified path.\nIgnored {len(files_to_keep)} files based on patterns.",
            title="Warning",
            border_style="yellow",
            box=box.ROUNDED,
            padding=(1, 2)
        )
        console.print(error_panel)
        return summaries
    # end styling

    # start styling
    if one_file:
        console.print(Panel(f"Analyzing single file: [bold]{os.path.basename(path)}[/bold]", border_style="green", padding=(1, 2)))
    with Progress(
        SpinnerColumn(style="green"),
        TextColumn("[bold green]{task.description}"),
        BarColumn(complete_style="green", finished_style="green"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
        expand=True
    ) as progress:
        # start styling
        task = progress.add_task("Analyzing files...", total=len(files_to_keep))
        # end styling

        for file_path in files_to_keep[:max_files]:
            # start styling
            progress.update(task, description=f"Processing: {file_path}")
            # end styling
            with open(file_path, "r", encoding='utf-8', errors='ignore') as f:
                content = f.read()[:3000]
                payload = build_payload(system_message(), prompt(content, file_path))

                try:
                    data = send_request(payload)
                    summary = data["choices"][0]["message"]["content"].strip()
                    summaries.append((file_path, summary))

                    # start styling
                    content_text = Text(summary)
                    content_text.stylize("white")
                    result_panel = Panel(
                        content_text,
                        title=f"{file_path}",
                        subtitle=f"[dim]{os.path.basename(file_path)}[/dim]",
                        title_align="left",
                        border_style="green",
                        box=box.ROUNDED,
                        padding=(1, 2)
                    )
                    console.print(result_panel)
                    # end styling

                except Exception as e:
                    error_msg = f"❌ Analysis failed: {str(e)}"
                    summaries.append((file_path, error_msg))
                    # start styling
                    error_panel = Panel(
                        Text(error_msg, style="red"),
                        title=f"⚠️  {file_path}",
                        subtitle=f"[dim]{os.path.basename(file_path)}[/dim]",
                        title_align="left",
                        border_style="red",
                        box=box.ROUNDED,
                        padding=(1, 2)
                    )
                    console.print(error_panel)
                progress.advance(task)
    
    console.print()
    # end styling

    success_count = len([s for s in summaries if not s[1].startswith('❌')])
    error_count = len(summaries) - success_count

    # start styling
    if not one_file: 
        final_columns = Columns([
            Panel(f"[green bold]{success_count}[/]\n[white]Successful", border_style="green", padding=(1, 2)),
            Panel(f"[red bold]{error_count}[/]\n[white]Errors", border_style="red", padding=(1, 2)),
            Panel(f"[blue bold]{len(summaries)}[/]\n[white]Total Files", border_style="blue", padding=(1, 2))
        ], expand=True)
        
        console.print(final_columns)
    
        footer = Panel(
            Align.center(Text("AI Code Analysis Complete!", style="bold green")),
            border_style="green",
            box=box.ROUNDED
        )
        console.print()
        console.print(footer)
    # end styling
    return summaries