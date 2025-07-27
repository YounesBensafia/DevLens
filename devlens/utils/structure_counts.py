import os
from pathlib import Path

def get_gitignore_patterns(directory: str = "."):
    current_dir = Path(directory).resolve()

    while current_dir != current_dir.parent:  #  at d
        gitignore_path = current_dir / '.gitignore'
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                lines = f.readlines()
            
            patterns = [line.strip() for line in lines 
                      if line.strip() and not line.strip().startswith('#')]
            patterns = [line.strip().replace('/', '') for line in lines 
                      if '/' in line.strip() and not line.strip().startswith('#') and line.strip()]
          

            return patterns, gitignore_path
        
        current_dir = current_dir.parent
    
    return None, None