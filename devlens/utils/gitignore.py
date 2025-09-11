import os
def get_gitignore_folders_files(path: str = "."):
    """Load .gitignore patterns from the specified path"""
    gitignore_path = os.path.join(path, ".gitignore")
    patterns = []
    
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as f:
            patterns = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    else:
        print("WARNING: No .gitignore file found so All files will be analyzed.")
        patterns = []

    return patterns
