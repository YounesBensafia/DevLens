import os

def find_dead_files(path: str):
    all_py_files = set()
    imported_files = set()

    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.relpath(os.path.join(root, file), path)
                all_py_files.add(full_path.replace("\\", "/"))

                with open(os.path.join(root, file), "r", errors="ignore") as f:
                    for line in f:
                        if "import" in line or "from" in line:
                            parts = line.split()
                            if len(parts) >= 2:
                                imported_files.add(parts[1].split(".")[0] + ".py")

    dead_files = sorted([f for f in all_py_files if os.path.basename(f) not in imported_files])
    return dead_files
