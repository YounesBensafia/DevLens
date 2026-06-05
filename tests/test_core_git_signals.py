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
        cwd=tmp_path,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Tester"],
        cwd=tmp_path,
        capture_output=True,
    )
    test_file = tmp_path / "main.py"
    test_file.write_text("x = 1\n")
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "initial"],
        cwd=tmp_path,
        capture_output=True,
        env={
            **os.environ,
            "GIT_AUTHOR_DATE": "2026-05-01T12:00:00",
            "GIT_COMMITTER_DATE": "2026-05-01T12:00:00",
        },
    )
    signals = get_git_signals(str(test_file), str(tmp_path), file_size_lines=1)
    # 1 commit + 1 line: does not meet the orphan thresholds (≥10 commits, ≥50 lines)
    assert signals.is_orphan is False
    assert signals.unique_authors == 1
    assert signals.total_commits == 1
    assert signals.days_since_last_change is not None


def test_two_authors(tmp_path):
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
    test_file = tmp_path / "shared.py"
    test_file.write_text("y = 2\n")
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.email=alice@devlens.io",
            "-c",
            "user.name=Alice",
            "commit",
            "-m",
            "alice commit",
        ],
        cwd=tmp_path,
        capture_output=True,
    )
    test_file.write_text("y = 3\n")
    subprocess.run(
        [
            "git",
            "-c",
            "user.email=bob@devlens.io",
            "-c",
            "user.name=Bob",
            "commit",
            "-am",
            "bob commit",
        ],
        cwd=tmp_path,
        capture_output=True,
    )
    signals = get_git_signals(str(test_file), str(tmp_path))
    assert signals.is_orphan is False
    assert signals.unique_authors == 2


def _commit_n_times(tmp_path, test_file, content_template, n, user_email="solo@devlens.io"):
    """Commit the same file n times with a single author."""
    import os

    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", user_email], cwd=tmp_path, capture_output=True
    )
    subprocess.run(["git", "config", "user.name", "Solo Dev"], cwd=tmp_path, capture_output=True)
    for i in range(n):
        test_file.write_text(content_template.format(i=i))
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", f"commit {i}"],
            cwd=tmp_path,
            capture_output=True,
            env={
                **os.environ,
                "GIT_AUTHOR_DATE": "2025-01-01T12:00:00",
                "GIT_COMMITTER_DATE": "2025-01-01T12:00:00",
            },
        )


def test_orphan_below_threshold(tmp_path):
    """1 author, 3 commits, 30 lines → should NOT be flagged as orphan."""
    test_file = tmp_path / "small.py"
    content = "\n".join(f"x_{i} = {i}" for i in range(30))  # 30 lines
    _commit_n_times(tmp_path, test_file, content + "  # v{i}", n=3)

    signals = get_git_signals(str(test_file), str(tmp_path), file_size_lines=30)
    assert signals.total_commits == 3
    assert signals.unique_authors == 1
    # Fails orphan check: total_commits(3) < 10
    assert signals.is_orphan is False


def test_orphan_above_threshold(tmp_path):
    """1 author, 15 commits, 200 lines → SHOULD be flagged as orphan."""
    test_file = tmp_path / "big.py"
    content = "\n".join(f"x_{i} = {i}" for i in range(200))  # 200 lines
    _commit_n_times(tmp_path, test_file, content + "  # v{i}", n=15)

    signals = get_git_signals(str(test_file), str(tmp_path), file_size_lines=200)
    assert signals.total_commits == 15
    assert signals.unique_authors == 1
    # Meets all three thresholds: authors==1, commits>=10, lines>=50
    assert signals.is_orphan is True
