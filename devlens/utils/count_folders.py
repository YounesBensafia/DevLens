import os

def count_directories(path: str) -> int:
    return len([f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))])
