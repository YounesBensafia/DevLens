import subprocess

def git_tree(path: str, level: int = 3) -> str:
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
#