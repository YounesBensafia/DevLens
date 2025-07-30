import os
from rich.console import Console
from rich.panel import Panel

console = Console()

def find_empty_files(path: str):
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
                console.print(f"[bold red]Error reading file {file_path}: {e}[/bold red]")
                return ""

        # For each file that is not empty, read its content
        


def dead_code(path: str, empty_files: list, all_py_files: set):
    # print(all_py_files, empty_files)
    for file in all_py_files:
        if file in empty_files:
            console.print(f"[bold yellow]Skipping empty file: {file}[/bold yellow]")
            continue
        file_content = read_file_content(os.path.join(path, file))
        file_content_splited= file_content.splitlines()
        file_content_import = [line for line in file_content_splited if "import" in line or "from" in line]
        print(f"File: {file}")
        print(f"Content: {file_content_import}")  # Print first
        for empty_file in empty_files:
             for line in file_content_splited:
                if empty_file in line:
                    print(f"Found reference to empty file: {empty_file} in {file}")
                    print(f"Line: {line}")
                    exit(0)
        print(f"======")             
    