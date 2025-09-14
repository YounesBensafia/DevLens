import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from devlens.analyzer.ai_summary import summarize_code
from devlens.analyzer.readme_gen import generate_readme

generate_readme("devlens")