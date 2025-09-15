import os
import typer
from console.incorrect_path import show_path_error

def check_path(path: str):
    exist = os.path.exists(os.path.abspath(path))
    if not exist:
        show_path_error()
        raise typer.Exit(code=1)