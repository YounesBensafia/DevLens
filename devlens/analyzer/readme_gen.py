import os
import requests
from devlens.config import GROQ_API_KEY
from devlens.analyzer.summary import count_lines_by_language, get_project_structure
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.layout import Layout
from rich.columns import Columns
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

console = Console()

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json",
}

def generate_readme(path: str):
    """Generate a comprehensive README.md file for the project"""
    
    console.clear()
    layout = Layout()
    layout.split_column(
        Layout(Panel(
            Align.center(Text("🎯 DevLens README Generator", style="bold white")),
            border_style="bright_magenta",
            box=box.DOUBLE,
            padding=(1, 4),
            title="[bold magenta]README GENERATION[/]",
            subtitle="[italic]Professional Documentation Creator[/]"
        ), name="header", size=5)
    )
    console.print(layout)
    console.print()
    
    with Progress(
        SpinnerColumn("dots", style="magenta"),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=40, style="magenta", complete_style="green"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        analyze_task = progress.add_task("🔍 Analyzing project structure...", total=100)
        progress.advance(analyze_task, 30)
        
        line_counts, file_counts = count_lines_by_language(path)
        progress.advance(analyze_task, 30)
        
        structure = get_project_structure(path)
        progress.advance(analyze_task, 40)
    
    project_name = os.path.basename(os.path.abspath(path))
    
    key_files = []
    requirements_files = []
    config_files = []
    
    for root, dirs, files in os.walk(path):
        for file in files:
            file_lower = file.lower()
            if file_lower in ['package.json', 'setup.py', 'pyproject.toml', 'cargo.toml', 'pom.xml']:
                key_files.append(file)
            elif file_lower in ['requirements.txt', 'package-lock.json', 'yarn.lock', 'pipfile']:
                requirements_files.append(file)
            elif file_lower in ['config.py', '.env', 'settings.py', 'docker-compose.yml', 'dockerfile']:
                config_files.append(file)
    
    project_context = f"""
    Project Name: {project_name}
    Languages Found: {', '.join(line_counts.keys())}
    Total Files: {sum(file_counts.values())}
    Total Lines: {sum(line_counts.values())}
    Key Files: {', '.join(key_files) if key_files else 'None detected'}
    Requirements Files: {', '.join(requirements_files) if requirements_files else 'None detected'}
    Config Files: {', '.join(config_files) if config_files else 'None detected'}
    """
    
    prompt = f"""Create a professional README.md file for this project. Based on the project analysis:

{project_context}

Generate a complete README.md with:
1. Project title and description
2. Features section
3. Installation instructions
4. Usage examples
5. Project structure overview
6. Technologies used
7. Contributing guidelines
8. License section

Make it professional, well-formatted with proper markdown, and include relevant badges if appropriate. The README should be comprehensive but concise."""

    payload = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [
            {
                "role": "system", 
                "content": "You are a technical documentation expert. Create professional, well-structured README.md files with proper markdown formatting."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 2048
    }
    
    try:
        with Progress(
            SpinnerColumn("dots", style="green"),
            TextColumn("[bold green]{task.description}"),
            BarColumn(bar_width=40, style="green", complete_style="cyan"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            api_task = progress.add_task("🤖 Generating README content...", total=100)
            progress.advance(api_task, 30)
            
            response = requests.post(GROQ_API_URL, headers=HEADERS, json=payload)
            progress.advance(api_task, 50)
            
            response.raise_for_status()
            data = response.json()
            readme_content = data["choices"][0]["message"]["content"].strip()
            progress.advance(api_task, 20)
        
        readme_path = os.path.join(path, "README.md")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)
        
        success_columns = Columns([
            Panel(
                "[green bold]✅ SUCCESS[/]\n[white]README Generated", 
                border_style="green", 
                box=box.ROUNDED,
                padding=(1, 2)
            ),
            Panel(
                f"[cyan bold]📄 LOCATION[/]\n[white]{readme_path}", 
                border_style="cyan", 
                box=box.ROUNDED,
                padding=(1, 2)
            )
        ], expand=True)
        
        console.print(success_columns)
        console.print()
        
        preview_panel = Panel(
            readme_content[:500] + "..." if len(readme_content) > 500 else readme_content,
            title="[bold cyan]📖 README Preview[/]",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 2)
        )
        console.print(preview_panel)
        
        return readme_path
        
    except Exception as e:
        error_panel = Panel(
            f"[red bold]❌ FAILED[/]\n[white]{str(e)}",
            title="[bold red]⚠️ Error[/]",
            border_style="red",
            box=box.ROUNDED,
            padding=(1, 2)
        )
        console.print(error_panel)
        return None