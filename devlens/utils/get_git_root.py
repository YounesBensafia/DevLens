import subprocess

def get_git_root(path="") -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", path, "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True
        )
        repo_name_abs = result.stdout.strip()
        repo_name = repo_name_abs.split('/')[-1]
        return repo_name, repo_name_abs
    except subprocess.CalledProcessError:
        return None, None