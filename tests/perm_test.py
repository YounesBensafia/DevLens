import ast

code = """
import os
import sys as system
from math import sqrt, pi
"""

tree = ast.parse(code)

for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        for alias in node.names:
            print("Import:", alias.name)
    elif isinstance(node, ast.ImportFrom):
        for alias in node.names:
            print(f"From {node.module} import {alias.name} ")
