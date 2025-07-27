import os

def count_lines_by_language(path: str):
    summary = {}
    for root, _, files in os.walk(path):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in [".py", ".js", ".ts", ".java", ".cpp", ".html", ".css"]:
                lang = ext.lstrip(".")
                summary.setdefault(lang, 0)
                with open(os.path.join(root, file), "r", errors="ignore") as f:
                    summary[lang] += sum(1 for _ in f)
    return summary
