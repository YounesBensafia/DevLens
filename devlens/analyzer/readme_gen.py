import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.layout import Layout
from rich.columns import Columns
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from utils.get_git_root import get_git_root
from utils.repo_file_finder import gather_files
from prompt.readme_gen_prompt import generate_readme_prompt
from prompt.readme_gen_prompt import project_context, system_message
from llm.client import build_payload, send_request
from utils.get_tree_project import git_tree
from utils.questionary_file import confirm_readme_rewrite

# TODO: Support non-Git folders

sys_message = system_message()
console = Console()

def generate_readme() -> str:
    """Generate a comprehensive README.md file for the project"""
    git_root_name, git_root_abs = get_git_root()
    get_tree = git_tree(git_root_abs)
    files_info = gather_files(git_root_abs)
    key_files, requirements_files, config_files = files_info
    readme_path = os.path.join(git_root_abs, "README.md")
    if confirm_readme_rewrite():
        layout = Layout()
        layout.split_column(
            Layout(Panel(
                Align.center(Text("DevLens README Generator", style="bold white")),
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
            analyze_task = progress.add_task("Analyzing project structure...", total=100)
            progress.advance(analyze_task, 30)
            
            progress.advance(analyze_task, 30)
            
            progress.advance(analyze_task, 40)

        context_project = project_context(git_root_name, get_tree, key_files, requirements_files, config_files)
        prompt = generate_readme_prompt(context_project)
        payload = build_payload(sys_message, prompt)
        
        
        try:
            with Progress(
                SpinnerColumn("dots", style="green"),
                TextColumn("[bold green]{task.description}"),
                BarColumn(bar_width=40, style="green", complete_style="cyan"),
                TimeElapsedColumn(),
                console=console
            ) as progress:
                api_task = progress.add_task("Generating README content...", total=100)
                progress.advance(api_task, 30)
                
                progress.advance(api_task, 50)

                data = send_request(payload)
                readme_content = data["choices"][0]["message"]["content"].strip()
                progress.advance(api_task, 20)

            print(f"Writing README to {readme_path}")

            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(readme_content)
            
            success_columns = Columns([
                Panel(
                    "[green bold] SUCCESS[/]\n[white]README Generated", 
                    border_style="green", 
                    box=box.ROUNDED,
                    padding=(1, 2)
                ),
                Panel(
                    f"[cyan bold] LOCATION[/]\n[white]{readme_path}", 
                    border_style="cyan", 
                    box=box.ROUNDED,
                    padding=(1, 2)
                )
            ], expand=True)
            
            console.print(success_columns)
            console.print()
            
            preview_panel = Panel(
                readme_content[:500] + "..." if len(readme_content) > 500 else readme_content,
                title="[bold cyan] README Preview[/]",
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
    else:
        console.print(
        Panel.fit(
            "[bold red] Cancelled by the user[/bold red]",
            border_style="red",
            title="Aborted",
            title_align="left"
        )
    )