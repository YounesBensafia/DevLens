import os
import requests
import fnmatch
from config import GROQ_API_KEY 
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.align import Align
from rich.layout import Layout
from rich.style import Style
from rich.tree import Tree
from rich.columns import Columns
from rich import box



GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json",
}

console = Console()

def load_gitignore_patterns(path: str):
    """Load patterns from .gitignore file"""
    gitignore_path = os.path.join(path, '.gitignore')
    patterns = []
    
    default_patterns = ['__pycache__/', '*.pyc', '*.pyo', '*.pyd', '.Python', 'build/', 'develop-eggs/', 'dist/', 'downloads/', 'eggs/', '.eggs/', 'lib/',
        'lib64/', 'parts/', 'sdist/', 'var/', 'wheels/', '*.egg-info/', '.installed.cfg', '*.egg', 'venv/', 'env/', 'ENV/', '.venv/', '.env', '.idea/', '.vscode/',
        '*.swp', '*.swo', '.DS_Store', 'Thumbs.db', 'node_modules/', '.git/', '.pytest_cache/', '.coverage', '.tox/', 'htmlcov/', '*.log', 'temp/', 'tmp/',
        'cache/', 'output/'
    ]
    
    patterns.extend(default_patterns)
    
    if os.path.exists(gitignore_path):
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(line)
        except Exception:
            pass  
    
    return patterns

def should_ignore_path(file_path: str, base_path: str, patterns: list):
    """Check if a file path should be ignored based on gitignore patterns"""
    relative_path = os.path.relpath(file_path, base_path)
    
    relative_path = relative_path.replace('\\', '/')
    
    for pattern in patterns:
        if not pattern.strip():
            continue
            
        if pattern.endswith('/'):
            path_parts = relative_path.split('/')
            for i in range(len(path_parts)):
                partial_path = '/'.join(path_parts[:i+1]) + '/'
                if fnmatch.fnmatch(partial_path, pattern):
                    return True
        else:
            if fnmatch.fnmatch(relative_path, pattern):
                return True
            filename = os.path.basename(relative_path)
            if fnmatch.fnmatch(filename, pattern):
                return True
    
    return False

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
    
    ignore_patterns = load_gitignore_patterns(path)
    console.print(f"[dim]Loaded {len(ignore_patterns)} ignore patterns (including defaults)[/dim]")

    python_files = []
    ignored_files = 0
    
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if not should_ignore_path(os.path.join(root, d), path, ignore_patterns)]
        
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                if not should_ignore_path(file_path, path, ignore_patterns):
                    python_files.append(file_path)
                else:
                    ignored_files += 1
    
    total_files = min(len(python_files), max_files)
    
    if total_files == 0:
        error_panel = Panel(
            f"No Python files found in the specified path.\nIgnored {ignored_files} files based on patterns.",
            title="Warning",
            border_style="yellow",
            box=box.ROUNDED,
            padding=(1, 2)
        )
        console.print(error_panel)
        return summaries
    
    stats_columns = Columns([
        Panel(f"[cyan bold]{len(python_files)}[/]\n[blue]Found Files", border_style="blue", padding=(1, 2)),
        Panel(f"[yellow bold]{ignored_files}[/]\n[blue]Ignored Files", border_style="blue", padding=(1, 2)),
        Panel(f"[green bold]{total_files}[/]\n[blue]To Analyze", border_style="blue", padding=(1, 2)),
        Panel(f"[magenta bold]{path}[/]\n[blue]Project Path", border_style="blue", padding=(1, 2))
    ], expand=True)
    
    console.print(stats_columns)
    console.print()
    
    with Progress(
        SpinnerColumn(style="green"),
        TextColumn("[bold green]{task.description}"),
        BarColumn(complete_style="green", finished_style="green"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
        expand=True
    ) as progress:
        task = progress.add_task("Analyzing files...", total=total_files)
        
        for i, file_path in enumerate(python_files[:max_files]):
            file = os.path.basename(file_path)
            relative_path = os.path.relpath(file_path, path)
            progress.update(task, description=f"� Processing: {file}")

            with open(file_path, "r", encoding='utf-8', errors='ignore') as f:
                content = f.read()[:3000]
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