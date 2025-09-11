import os
from pathlib import Path
from typing import List, Set

def scan_project_files(
    root_dir: str = ".",
    extensions: Set[str] = {".py"},
    ignore_dirs: Set[str] = {"venv", "node_modules", "__pycache__", ".git", ".idea", ".vscode", "build", "dist"},
) -> List[str]:
    matched_files = []
    
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in files:
            file_path = os.path.join(root, file)
            if Path(file).suffix.lower() in extensions:
                matched_files.append(file_path)
    
    return matched_files


def get_python_files(project_dir: str = ".") -> List[str]:
    return scan_project_files(project_dir, extensions={".py"})


def read_content(file_path: str) -> str:
    """Read the content of a file and return it as a string."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            content = content.strip()
            if not content:
                return "This file is empty."
            if "import " not in content and "from " not in content:
                return "No imports found in this file."
            import_lines = []
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('import ') or line.startswith('from '):
                    import_lines.append(line)

            if import_lines:
                content = '\n'.join(import_lines)
            else:
                return "No imports found in this file."
            return content
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""



if __name__ == "__main__":
    project_path = os.getcwd()
    python_files = get_python_files(project_path)
    
    if python_files:
        for file in python_files:
            content = read_content(file)
            print(f"Content of {file}:\n{content}\n")
    else:
        print(f"No Python files found in '{project_path}'.")