import os


def count_directories(path: str) -> int:
    """Count visible (non-hidden) directories in the given path."""
    return len([
        f for f in os.listdir(path)
        if os.path.isdir(os.path.join(path, f)) and not f.startswith('.')
    ])
