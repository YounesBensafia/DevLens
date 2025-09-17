import subprocess
from config.settings import LEVEL_OF_TREE
def git_tree(path: str, level: int = LEVEL_OF_TREE) -> str:
    try:
        result = subprocess.run(
            ["git", "ls-files", "--others", "--cached", "--exclude-standard"],
            cwd=path,
            capture_output=True,
            text=True,
            check=True
        )
        files = result.stdout.strip().split("\n")
        files = [f for f in files if f]

        tree = {}
        for f in files:
            parts = f.split("/")
            d = tree
            for p in parts:
                d = d.setdefault(p, {})

        def format_tree(d, prefix="", depth=1):
            if depth > level:
                return ""
            result_lines = []
            entries = sorted(d.keys())
            for i, name in enumerate(entries):
                connector = "└── " if i == len(entries) - 1 else "├── "
                result_lines.append(prefix + connector + name)
                extension = "    " if i == len(entries) - 1 else "│   "
                result_lines.append(format_tree(d[name], prefix + extension, depth + 1))
            return "\n".join(filter(None, result_lines))

        return f"{path}\n{format_tree(tree)}"

    except subprocess.CalledProcessError as e:
        return f"Git error: {e.stderr}"


# Example output:
# devlens
# ├── analyzer
# │   ├── ai_summary.py
# │   ├── deadcode.py
# │   ├── dependencies.py
# │   ├── readme_gen.py
# │   ├── summary.py
# │   ├── tech_stack.py
# │   └── test.js
# ├── cli
# │   ├── cli.py
# │   └── questionary_readme.py


def git_tree_with_styles(path: str, level: int = LEVEL_OF_TREE) -> str:
    try:
        result = subprocess.run(
            ["git", "ls-files", "--others", "--cached", "--exclude-standard"],
            cwd=path,
            capture_output=True,
            text=True,
            check=True
        )
        files = result.stdout.strip().split("\n")
        files = [f for f in files if f]

        tree = {}
        for f in files:
            parts = f.split("/")
            d = tree
            for p in parts:
                d = d.setdefault(p, {})

        def format_tree(d, prefix="", depth=1):
            if depth > level:
                return ""
            result_lines = []
            entries = sorted(d.keys())
            
            for i, name in enumerate(entries):
                connector = "[yellow]└── [/]" if i == len(entries) - 1 else "[yellow]├── [/]"
                file_style = get_file_style(name)
                result_lines.append(prefix + connector + file_style)
                extension = "    " if i == len(entries) - 1 else "[yellow]│[/]   "
                result_lines.append(format_tree(d[name], prefix + extension, depth + 1))
            return "\n".join(filter(None, result_lines))


        def get_file_style(name):
            """Apply appropriate styling based on file type"""
            if "." not in name:
                return f"[bold cyan]{name}[/]"
            elif name.endswith((".py")):
                return f"[bold green]{name}[/]"
            elif name.endswith((".js", ".ts", ".jsx", ".tsx")):
                return f"[bold yellow]{name}[/]"
            elif name.endswith((".json", ".toml", ".yaml", ".yml")):
                return f"[bold magenta]{name}[/]"  
            elif name.endswith((".md", ".txt")):
                return f"[bold blue]{name}[/]"
            else:
                return f"[red]{name}[/]"  

        return f"{path}\n{format_tree(tree)}"

    except subprocess.CalledProcessError as e:
        return f"Git error: {e.stderr}"
