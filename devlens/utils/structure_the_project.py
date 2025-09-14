import subprocess
from pathlib import Path

def list_non_ignored_files(folder="."):
    folder = Path(folder)
    result = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", "--cached"],
        cwd=folder,
        stdout=subprocess.PIPE,
        text=True
    )
    files = result.stdout.strip().split("\n")
    return [str(folder / f) for f in files if f]
