import os
import sys
from xml.etree.ElementPath import find
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from devlens.analyzer.deadcode import find_dead_files
find_dead_files("tests")
# younes