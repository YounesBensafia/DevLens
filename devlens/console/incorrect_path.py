from rich.console import Console
from rich.panel import Panel
from rich import box

console = Console()

def show_path_error():
    console.print(Panel(
        "[bold red]❌ INVALID PATH[/]\n\n"
        "[yellow]The specified path does not exist.[/]\n"
        "[cyan]Please check:[/]\n"
        "• The path is spelled correctly\n"
        "• The file or directory exists",
        title="[bold white on red] ERROR [/]",
        border_style="red",
        box=box.DOUBLE,
        expand=False,
        padding=(1, 2)
    ))
