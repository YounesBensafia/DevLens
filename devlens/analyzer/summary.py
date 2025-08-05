import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.layout import Layout
from rich.style import Style
from rich.tree import Tree
from rich.columns import Columns
from rich import box
import os
from pathlib import Path
from devlens.utils.structure_counts import get_gitignore_patterns

console = Console()



def count_lines_by_language(path: str):
    summary = {}
    file_count = {}
    patterns, gitignore_path = get_gitignore_patterns(path)
    for root, _, files in os.walk(path):
        for file in files:
            if file in patterns:
                exit()
            ext = os.path.splitext(file)[1].lower()
            if ext in [".py", ".js", ".ts", ".java", ".cpp", ".html", ".css", ".json", ".md", ".txt", ".yml", ".yaml", ".xml"]:
                lang = ext.lstrip(".")
                summary.setdefault(lang, 0)
                file_count.setdefault(lang, 0)
                file_count[lang] += 1
                
                try:
                    with open(os.path.join(root, file), "r", errors="ignore") as f:
                        lines = sum(1 for line in f if line.strip())
                        summary[lang] += lines
                except:
                    continue
                    
    return summary, file_count

def get_project_structure(path: str, max_depth=3):
    structure = {}
    
    for root, dirs, files in os.walk(path):
        depth = root.replace(path, '').count(os.sep)
        if depth >= max_depth:
            dirs[:] = [] 
            continue
            
        rel_path = os.path.relpath(root, path)
        if rel_path == '.':
            rel_path = 'root'
            
        structure[rel_path] = {
            'files': len(files),
            'dirs': len(dirs)
        }
    
    return structure

def display_code_summary(path: str):
    """Display a comprehensive code summary with professional styling"""
    
    console.clear()
    layout = Layout()
    layout.split_column(
        Layout(name="header"),
        Layout(name="body", ratio=8)
    )
    
    header_text = Text("✨ DevLens - Project Summary ✨", style="bold white on cyan")
    header_panel = Panel(
        Align.center(header_text),
        border_style="cyan",
        box=box.DOUBLE,
        padding=(1, 2)
    )
    console.print(header_panel)
    console.print()
    
    line_counts, file_counts = count_lines_by_language(path)
    structure = get_project_structure(path)
    
    if not line_counts:
        error_panel = Panel(
            "❌ No supported code files found in the specified path.",
            title="⚠️  Warning",
            border_style="yellow",
            box=box.ROUNDED,
            padding=(1, 2)
        )
        console.print(error_panel)
        return
    
    total_files = sum(file_counts.values())
    total_lines = sum(line_counts.values())
    
    stats_columns = Columns([
        Panel(f"[green bold]{total_files}[/]\n[blue]Total Files", border_style="blue", padding=(1, 2)),
        Panel(f"[cyan bold]{total_lines:,}[/]\n[blue]Total Lines", border_style="blue", padding=(1, 2)),
        Panel(f"[yellow bold]{len(structure)}[/]\n[blue]Directories", border_style="blue", padding=(1, 2)),
        Panel(f"[magenta bold]{len(line_counts)}[/]\n[blue]Languages", border_style="blue", padding=(1, 2))
    ], expand=True)
    
    console.print(stats_columns)
    console.print()
    
    lang_table = Table(
        title="📋 Language Breakdown", 
        show_header=True, 
        header_style="bold white on magenta",
        box=box.ROUNDED,
        border_style="magenta",
        title_style="bold magenta"
    )
    lang_table.add_column("Language", style="cyan", no_wrap=True)
    lang_table.add_column("Files", justify="right", style="green")
    lang_table.add_column("Lines", justify="right", style="blue")
    lang_table.add_column("Percentage", justify="right", style="yellow")
    
    sorted_languages = sorted(line_counts.items(), key=lambda x: x[1], reverse=True)
    
    for lang, lines in sorted_languages:
        files = file_counts.get(lang, 0)
        percentage = (lines / total_lines) * 100 if total_lines > 0 else 0
        
        lang_table.add_row(
            f"{lang.upper()}",
            str(files),
            f"{lines:,}",
            f"{percentage:.1f}%"
        )
    
    console.print(lang_table)
    console.print()
    
    if len(structure) > 1:
        struct_table = Table(
            title="🏗️  Project Structure", 
            show_header=True, 
            header_style="bold white on cyan",
            box=box.ROUNDED,
            border_style="cyan",
            title_style="bold cyan"
        )
        struct_table.add_column("Directory", style="cyan")
        struct_table.add_column("Files", justify="right", style="green")
        struct_table.add_column("Subdirs", justify="right", style="yellow")
        
        for dir_path, info in sorted(structure.items()):
            if dir_path != 'root':
                struct_table.add_row(
                    dir_path,
                    str(info['files']),
                    str(info['dirs'])
                )
        
        console.print(struct_table)
        console.print()
    
    console.print(Panel(
        f"✅ Analysis complete! Found [green]{total_files}[/green] files with [blue]{total_lines:,}[/blue] lines of code across [cyan]{len(line_counts)}[/cyan] languages.",
        title="🎯 Summary",
        border_style="green",
        padding=(1, 2)
    ))
    
    return {
        'total_files': total_files,
        'total_lines': total_lines,
        'languages': dict(sorted_languages),
        'file_counts': file_counts
    }
