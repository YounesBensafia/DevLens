import os
from rich.console import Console
from rich.panel import Panel

console = Console()

def find_dead_files(path: str):
    all_py_files = set()

    console.print("[bold blue]Starting code analysis...[/bold blue]")
    
    empty_files = []

    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".py"):
                
                full_path = os.path.relpath(os.path.join(root, file), path)
                all_py_files.add(full_path.replace("\\", "/"))
                console.print(f"Analyzing file: [green]{file}[/green]")
                with open(os.path.join(root, file), "r", errors="ignore") as f:
                    content = f.read()
                    if content.strip() == "":
                        console.print(Panel.fit(f"File {file} is empty, skipping...", 
                                              title="Empty File", 
                                              border_style="yellow"))
                        empty_files.append(full_path)
    
    console.print("[bold blue]Analysis complete![/bold blue]")
    console.print(f"Total Python files found: [bold green]{len(all_py_files)}[/bold green]")
    if empty_files:
        console.print("[bold red]Empty files found:[/bold red]")
        for empty_file in empty_files:
            console.print(f"- [yellow]{empty_file}[/yellow]")
    else:
        console.print("[bold green]No empty files found![/bold green]")
