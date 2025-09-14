import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import SUPPORTED_FILE_TYPES
from utils.structure_the_project import list_non_ignored_files

files = []

def get_language(file_path: str) -> str:
    split_name = os.path.splitext(file_path)
    for extension in split_name:
        if extension in SUPPORTED_FILE_TYPES.keys():
            return SUPPORTED_FILE_TYPES[extension]
    return "N/A"

def count_lines_in_file(content: str) -> int:
    return sum(1 for _ in content.splitlines())

def count_lines_by_language(files: list[str]):
    abs_files = [os.path.abspath(file) for file in files]
    for file in abs_files:
        if os.path.exists(file):
            lang = get_language(file)
            if lang != "N/A":
                content = get_content_of_file(file)
                if content:
                    line_count = count_lines_in_file(content)
                    files.append((line_count, lang))
    return files

def get_content_of_file(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        non_comment_lines = []
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line.startswith('#') and line:
                non_comment_lines.append(line)
        return '\n'.join(non_comment_lines)

print(count_lines_by_language(list_non_ignored_files("devlens")))
