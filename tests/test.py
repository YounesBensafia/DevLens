import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from devlens.utils.gitignore import get_gitignore_folders_files
ignore_patterns, patterns_with_asterisks = get_gitignore_folders_files()
path = "."
files = [f for f in os.walk(path) if f not in ignore_patterns]
files_tuples = []
list_of_files_in_dirs = []
# print(patterns_with_asterisks)
# exit(0)
for f in files:
    # print(f[0])
    # continue
    if not f[0] in ignore_patterns and not f[0].endswith(tuple(p for p in ignore_patterns)):
        # print(f[2])
        # continue
        if f[1] != []:
            for file in f[1]:
                if file in ignore_patterns:
                    f[1].remove(file)
                    # print(f)
        if f[2] != []: 
            for file in f[2]:
                string = f[0] + "/" + file
                if string in ignore_patterns:
                    # print(file)
                    f[2].remove(file)
                    # print(f)
        list_of_files_in_dirs.append(f)

for f in list_of_files_in_dirs:
    print(f)
# print(files