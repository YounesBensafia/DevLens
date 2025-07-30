import os
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

console = Console()

def find_empty_files(path: str):
    all_py_files = set()
    
    console.print(Panel.fit("[bold blue]Starting code analysis...[/bold blue]", 
                          border_style="blue", 
                          title="DevLens Analysis"))
    
    empty_files = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
    ) as progress:
        scan_task = progress.add_task("Scanning files...", total=100)
        
        file_count = 0
        for _, _, files in os.walk(path):
            for file in files:
                if file.endswith(".py"):
                    file_count += 1
        
        current_count = 0
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.relpath(os.path.join(root, file), path)
                    all_py_files.add(full_path.replace("\\", "/"))
                    with open(os.path.join(root, file), "r", errors="ignore") as f:
                        content = f.read()
                        if content.strip() == "":
                            empty_files.append(full_path)
                    
                    current_count += 1
                    progress.update(scan_task, completed=int(100 * current_count / file_count))
    
    console.print(Panel.fit("[bold blue]Analysis complete![/bold blue]", 
                          border_style="blue", 
                          title="Results"))
    console.print(f"Total Python files found: [bold green]{len(all_py_files)}[/bold green]")
    
    if empty_files:
        empty_tree = Tree("[bold red]Empty files found:[/bold red]")
        for empty_file in empty_files:
            empty_tree.add(Text(f"{empty_file}", style="yellow"))
        console.print(empty_tree)
    else:
        console.print(Text("No empty files found!", style="bold green"))

    return all_py_files, empty_files

def read_file_content(file_path: str) -> str:
    """
    Read and return the content of a file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: Content of the file
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        console.print(Text(f"Error reading file {file_path}: {e}", style="bold red"))
        return ""

def dead_code(path: str, empty_files: list, all_py_files: set):
    console.print(Panel.fit("[bold magenta]Analyzing code usage patterns...[/bold magenta]", 
                          border_style="magenta", 
                          title="Dead Code Detection"))
    
    all_functions = []
    references_found = False
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold magenta]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
    ) as progress:
        analyze_task = progress.add_task("Analyzing functions...", total=len(all_py_files))
        
        for file in all_py_files:
            if file in empty_files:
                progress.update(analyze_task, advance=1)
                continue
                
            file_content = read_file_content(os.path.join(path, file))
            file_content_splited = file_content.splitlines()
            function_names = []
        
            for line in file_content_splited:
                if line.strip().startswith("def "):
                    function_name = line.split("def ")[1].split("(")[0].strip()
                    function_names.append(function_name)
                    all_functions.append(function_name)

            for empty_file in empty_files:
                for i, line in enumerate(file_content_splited):
                    if empty_file in line:
                        if not references_found:
                            console.print(Text("\nReferences to empty files:", style="bold yellow"))
                            references_found = True
                        console.print(Panel(
                            f"[yellow]{line}[/yellow]",
                            title=f"[bold cyan]{file}[/bold cyan] line {i+1}",
                            subtitle=f"References empty file: [bold red]{empty_file}[/bold red]"
                        ))
            
            progress.update(analyze_task, advance=1)

    console.rule("[bold]Function Analysis Results[/bold]")
    if not all_functions:
        console.print(Text("No functions found in the analyzed files.", style="bold red"))
    else:
        function_tree = Tree(Text("Functions found in the analyzed files:", style="bold green"))
        for func in sorted(set(all_functions)):
            function_tree.add(Text(func, style="blue"))
        console.print(function_tree)