import os
import numpy as np
def get_logical_size_of_the_project(path: str) -> float:
    """Calculate the total size of the project in MB"""
    total_size = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp) and not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return np.round(total_size / (1024)**2, 4)
    
