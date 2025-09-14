import os
def has_readme(git_root: str) -> bool:
    """Check if the project has a README.md file."""
    readme_path = os.path.join(git_root, "README.md")
    return os.path.isfile(readme_path)
