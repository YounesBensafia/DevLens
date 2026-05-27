import os
import subprocess

from devlens.core.git_signals import get_git_signals, get_repo_root


def test_no_git_repo(tmp_path):
    root = get_repo_root(str(tmp_path))
    assert root is None


def test_single_commit_single_author(tmp_path):
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@devlens.io"],
        cwd=tmp_path, capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Tester"],
        cwd=tmp_path, capture_output=True,
    )
    test_file = tmp_path / "main.py"
    test_file.write_text("x = 1\n")
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "initial"],
        cwd=tmp_path, capture_output=True,
        env={**os.environ, "GIT_AUTHOR_DATE": "2026-05-01T12:00:00",
             "GIT_COMMITTER_DATE": "2026-05-01T12:00:00"},
    )
    signals = get_git_signals(str(test_file), str(tmp_path))
    assert signals.is_orphan is True
    assert signals.unique_authors == 1
    assert signals.total_commits == 1
    assert signals.days_since_last_change is not None


def test_two_authors(tmp_path):
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
    test_file = tmp_path / "shared.py"
    test_file.write_text("y = 2\n")
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.email=alice@devlens.io",
         "-c", "user.name=Alice", "commit", "-m", "alice commit"],
        cwd=tmp_path, capture_output=True,
    )
    test_file.write_text("y = 3\n")
    subprocess.run(["git", "-c", "user.email=bob@devlens.io",
                    "-c", "user.name=Bob", "commit", "-am", "bob commit"],
                   cwd=tmp_path, capture_output=True,
                   )
    signals = get_git_signals(str(test_file), str(tmp_path))
    assert signals.is_orphan is False
    assert signals.unique_authors == 2
