import os
from devlens.config.settings import SUPPORTED_FILE_TYPES
from devlens.utils.structure_the_project import list_non_ignored_files

files_by_language = []

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
                    files_by_language.append((lang, line_count))
    return files_by_language

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
    
def classify_files_by_language(files: list[str]) -> dict[str, list[str]]:
    sum = 0
    classified_files = {lang: [sum] for lang in SUPPORTED_FILE_TYPES.values()}
    for file in files:
        lang, line_count = file
        if lang in classified_files:
            classified_files[lang][0] += line_count
        else:
            classified_files[lang] = [line_count]
    return classified_files


def count_lines_by_language_in_project(path: str) -> dict[str, int]:
    all_files = list_non_ignored_files(path)
    classified_files = count_lines_by_language(all_files)
    classified_files = classify_files_by_language(classified_files)
    classified_files_copy = classified_files.copy()
    for file in classified_files:
        if classified_files_copy[file] == [0]:
            del classified_files_copy[file]
    return classified_files_copy

