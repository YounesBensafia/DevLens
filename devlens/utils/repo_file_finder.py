import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import KEY_FILES, REQUIREMENTS_FILES, CONFIG_FILES

def gather_files(path: str = "."):
    key_files = []
    requirements_files = []
    config_files = []
    for _, _, files in os.walk(path):
        for file in files:
            file_lower = file.lower()
            if file_lower in KEY_FILES:
                key_files.append(file)
            elif file_lower in REQUIREMENTS_FILES:
                requirements_files.append(file)
            elif file_lower in CONFIG_FILES:
                config_files.append(file)

    return key_files, requirements_files, config_files

