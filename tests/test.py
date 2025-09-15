import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from devlens.analyzer.stats import display_code_summary

display_code_summary(".")