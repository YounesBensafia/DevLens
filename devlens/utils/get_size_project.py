import os


def get_logical_size_of_the_project(path: str) -> float:
    """Calculate the total size of the project in MB, excluding hidden directories."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        # Skip hidden directories like .git, .venv, etc.
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp) and not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return round(total_size / (1024) ** 2, 4)
