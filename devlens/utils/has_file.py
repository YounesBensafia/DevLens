import os
def has_file(file_name: str, git_root: str = ".") -> bool:
    """Check if the project has a specific file"""
    file_path = os.path.join(git_root, file_name)
    return os.path.isfile(file_path)

