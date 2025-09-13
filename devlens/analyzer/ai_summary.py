import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests
from config.settings import GROQ_API_KEY 
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.align import Align
from rich.layout import Layout
from rich.columns import Columns
from rich import box
from utils.gitignore import list_non_ignored_files
from prompt.ai_summary_prompt import generate_ai_summary_prompt as prompt
from prompt.ai_summary_prompt import system_message as system_msg



GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json",
}
system_msg = system_msg()               

console = Console()


def summarize_code(path: str, max_files=10):
    summaries = []
    console.clear()
    layout = Layout()
    layout.split_column(
        Layout(name="header"),
        Layout(name="body", ratio=8)
    )
    
    header_text = Text("DevLens - AI Code Analyzer", style="bold white on blue")
    header_panel = Panel(
        Align.center(header_text),
        border_style="blue",
        box=box.DOUBLE,
        padding=(1, 2)
    )
    console.print(header_panel)

    files_to_keep = list_non_ignored_files()
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

    
    with Progress(
        SpinnerColumn(style="green"),
        TextColumn("[bold green]{task.description}"),
        BarColumn(complete_style="green", finished_style="green"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
        expand=True
    ) as progress:
        task = progress.add_task("Analyzing files...", total=len(files_to_keep))

        for i, file_path in enumerate(files_to_keep[:max_files]):
            file = os.path.basename(file_path)
            relative_path = os.path.relpath(file_path, path)
            progress.update(task, description=f"� Processing: {file}")

            with open(file_path, "r", encoding='utf-8', errors='ignore') as f:
                content = f.read()[:3000]
                prompt_message = prompt(content) 
                payload = {
                    "model": "meta-llama/llama-4-scout-17b-16e-instruct",  
                    "messages": [
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": prompt_message}
                    ],
                    "temperature": 0.2
                }

                try:
                    response = requests.post(GROQ_API_URL, headers=HEADERS, json=payload)
                    response.raise_for_status()
                    data = response.json()
                    summary = data["choices"][0]["message"]["content"].strip()
                    summaries.append((file, summary))
                    
                    content_text = Text(summary)
                    content_text.stylize("white")
                    
                    result_panel = Panel(
                        content_text,
                        title=f"{file}",
                        subtitle=f"[dim]{relative_path}[/dim]",
                        title_align="left",
                        border_style="green",
                        box=box.ROUNDED,
                        padding=(1, 2)
                    )
                    console.print(result_panel)
                    
                except Exception as e:
                    error_msg = f"❌ Analysis failed: {str(e)}"
                    summaries.append((file, error_msg))
                    
                    error_panel = Panel(
                        Text(error_msg, style="red"),
                        title=f"⚠️  {file}",
                        subtitle=f"[dim]{relative_path}[/dim]",
                        title_align="left",
                        border_style="red",
                        box=box.ROUNDED,
                        padding=(1, 2)
                    )
                    console.print(error_panel)
                
                progress.advance(task)
    
    console.print()
    
    success_count = len([s for s in summaries if not s[1].startswith('❌')])
    error_count = len(summaries) - success_count
    
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
    
    return summaries