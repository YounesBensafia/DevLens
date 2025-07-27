import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
import os
from pathlib import Path

console = Console()

def get_gitignore_patterns():
    current_dir = Path(os.getcwd())
    
    while current_dir != current_dir.parent:  
        gitignore_path = current_dir / '.gitignore'
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                lines = f.readlines()
            
            patterns = [line.strip() for line in lines 
                      if line.strip() and not line.strip().startswith('#')]
            
            return patterns, gitignore_path
        
        current_dir = current_dir.parent
    
    return None, None

def git_gitignore_main():
    patterns, gitignore_path = get_gitignore_patterns()
    
    if patterns:
        print(f"Found .gitignore at: {gitignore_path}")
        print("\nIgnored patterns:")
        for pattern in patterns:
            print(f"- {pattern}")
    else:
        print("No .gitignore file found in this directory or any parent directories.")

def count_lines_by_language(path: str):
    summary = {}
    for root, _, files in os.walk(path):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in [".py", ".js", ".ts", ".java", ".cpp", ".html", ".css"]:
                lang = ext.lstrip(".")
                summary.setdefault(lang, 0)
                with open(os.path.join(root, file), "r", errors="ignore") as f:
                    summary[lang] += sum(1 for _ in f)
    return summary
