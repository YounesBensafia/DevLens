import os
import requests
from devlens.config import GROQ_API_KEY  # Replace with your Groq key storage
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.align import Align
from rich.layout import Layout



GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json",
}

console = Console()

def summarize_code(path: str, max_files=10):
    summaries = []
    
    console.print()
    header_text = Text("DevLens - AI Code Analyzer", style="bold blue")
    header_panel = Panel(
        Align.center(header_text),
        border_style="blue",
        padding=(1, 2)
    )
    console.print(header_panel)
    console.print()
    
    python_files = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    
    total_files = min(len(python_files), max_files)
    
    if total_files == 0:
        error_panel = Panel(
            "❌ No Python files found in the specified path.",
            title="⚠️  Warning",
            border_style="yellow",
            padding=(1, 2)
        )
        console.print(error_panel)
        return summaries
    
    info_table = Table(show_header=False, box=None, padding=(0, 1))
    info_table.add_row("📂 Path:", f"[cyan]{path}[/cyan]")
    info_table.add_row("📄 Files found:", f"[green]{len(python_files)}[/green]")
    info_table.add_row("🔍 Files to analyze:", f"[blue]{total_files}[/blue]")
    
    info_panel = Panel(
        info_table,
        title="📊 Scan Information",
        border_style="cyan",
        padding=(1, 2)
    )
    console.print(info_panel)
    console.print()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
        expand=True
    ) as progress:
        task = progress.add_task("🚀 Analyzing files...", total=total_files)
        
        for i, file_path in enumerate(python_files[:max_files]):
            file = os.path.basename(file_path)
            relative_path = os.path.relpath(file_path, path)
            progress.update(task, description=f"� Processing: {file}")

            with open(file_path, "r") as f:
                content = f.read()[:3000]  # Limit input size
                prompt = f"Summarize what this Python file does:\n\n{content}"
                
                payload = {
                    "model": "meta-llama/llama-4-scout-17b-16e-instruct",  
                    "messages": [
                        {"role": "system", "content": "You are a code analysis assistant. Provide only a concise, direct summary of what the Python file does. Do not show your thinking process or reasoning steps. Just give the final summary in 1-3 sentences."},
                        {"role": "user", "content": prompt}
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
                        title=f"📄 {file}",
                        subtitle=f"[dim]{relative_path}[/dim]",
                        title_align="left",
                        border_style="green",
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
                        padding=(1, 2)
                    )
                    console.print(error_panel)
                
                progress.advance(task)
    
    console.print()
    summary_table = Table(show_header=False, box=None, padding=(0, 1))
    summary_table.add_row("✅ Files processed:", f"[green]{len([s for s in summaries if not s[1].startswith('[ERROR]')])}[/green]")
    summary_table.add_row("⏱️  Total files:", f"[blue]{len(summaries)}[/blue]")
    
    final_panel = Panel(
        summary_table,
        title="🎯 Analysis Complete",
        border_style="green",
        padding=(1, 2)
    )
    console.print(final_panel)
    
    return summaries