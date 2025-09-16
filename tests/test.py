import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from devlens.utils.deadcode_analyze import analyze_python_file
analyze_python_file("tests/perm_test.py")
# younes