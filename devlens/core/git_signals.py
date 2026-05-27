"""
Git signals — facts from version control history.
Completely deterministic, no LLM.
"""

import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class GitSignals:
    path: str
    days_since_last_change: int | None
    unique_authors: int
    total_commits: int
    is_orphan: bool
    staleness_score: float


def _run_git(args: list[str], cwd: str) -> str:
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=10,
        )
        return result.stdout.strip()
    except Exception:
        return ""


def get_git_signals(file_path: str, repo_root: str) -> GitSignals:
    rel_path = str(Path(file_path).relative_to(Path(repo_root)))

    last_date_str = _run_git(
        ["log", "-1", "--format=%ci", "--follow", "--", rel_path], cwd=repo_root
    )
    days_since = None
    if last_date_str:
        try:
            last_date = datetime.fromisoformat(last_date_str.split(" +")[0].split(" -")[0])
            last_date = last_date.replace(tzinfo=timezone.utc)
            now = datetime.now(tz=timezone.utc)
            days_since = (now - last_date).days
        except Exception:
            pass

    authors_out = _run_git(["log", "--follow", "--format=%ae", "--", rel_path], cwd=repo_root)
    authors = set(a for a in authors_out.splitlines() if a)
    unique_authors = len(authors)
    total_commits = len(authors_out.splitlines()) if authors_out else 0
    is_orphan = unique_authors == 1

    staleness = 0.0
    if days_since is not None:
        staleness = min(100.0, (days_since / 180) * 100)
        if is_orphan and days_since > 90:
            staleness = min(100.0, staleness * 1.3)

    return GitSignals(
        path=file_path,
        days_since_last_change=days_since,
        unique_authors=unique_authors,
        total_commits=total_commits,
        is_orphan=is_orphan,
        staleness_score=round(staleness, 1),
    )


def get_repo_root(path: str) -> str | None:
    result = _run_git(["rev-parse", "--show-toplevel"], cwd=str(Path(path).parent))
    return result if result else None
