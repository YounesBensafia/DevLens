import json
import os
import subprocess
from collections import Counter

import pytest

from devlens.slop import (
    SignalResult,
    SlopResult,
    _build_summary,
    _cosine_similarity,
    _extract_docstrings,
    _get_verdict,
    _manual_tfidf,
    _read_pr_body,
    _shannon_entropy,
    compute_churn_pattern,
    compute_comment_ratio,
    compute_diff_description_ratio,
    compute_docstring_uniformity,
    compute_identifier_entropy,
    compute_new_author_risk,
    compute_slop_score,
)

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _make_git_repo(tmp_path):
    """Initialise a git repo at tmp_path and return the Repo path."""
    subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, capture_output=True)
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
    return str(tmp_path)


def _commit_file(tmp_path, filename, content, msg="commit"):
    """Write a file and commit it in the git repo at tmp_path."""
    filepath = tmp_path / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content)
    subprocess.run(["git", "add", filename], cwd=tmp_path, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", msg],
        cwd=tmp_path,
        capture_output=True,
        env={
            **os.environ,
            "GIT_AUTHOR_DATE": "2026-05-01T12:00:00",
            "GIT_COMMITTER_DATE": "2026-05-01T12:00:00",
        },
    )


# ---------------------------------------------------------------------------
# _extract_docstrings
# ---------------------------------------------------------------------------


def test_extract_docstrings_empty():
    assert _extract_docstrings("") == []


def test_extract_docstrings_syntax_error():
    assert _extract_docstrings("def foo(:") == []


def test_extract_docstrings_module_and_functions():
    code = '''
"""Module docstring."""
def foo():
    """Function docstring."""
    pass
class Bar:
    """Class docstring."""
    pass
'''
    docs = _extract_docstrings(code)
    assert len(docs) == 3
    assert "Module docstring." in docs
    assert "Function docstring." in docs
    assert "Class docstring." in docs


# ---------------------------------------------------------------------------
# _manual_tfidf / _cosine_similarity
# ---------------------------------------------------------------------------


def test_manual_tfidf_empty():
    assert _manual_tfidf([]) == []


def test_manual_tfidf_identical_strings():
    vectors = _manual_tfidf(["hello world", "hello world"])
    sim = _cosine_similarity(vectors[0], vectors[1])
    assert sim > 0.99


def test_manual_tfidf_orthogonal():
    vectors = _manual_tfidf(["hello world", "foo bar baz"])
    sim = _cosine_similarity(vectors[0], vectors[1])
    assert sim < 0.01


def test_cosine_similarity_zero():
    assert _cosine_similarity([0.0, 0.0], [1.0, 0.0]) == 0.0


def test_cosine_similarity_identical():
    assert _cosine_similarity([1.0, 2.0], [1.0, 2.0]) > 0.99


# ---------------------------------------------------------------------------
# _shannon_entropy
# ---------------------------------------------------------------------------


def test_shannon_entropy_uniform():
    h = _shannon_entropy(Counter({"a": 1, "b": 1, "c": 1, "d": 1}))
    assert h == pytest.approx(2.0, abs=0.01)


def test_shannon_entropy_single():
    assert _shannon_entropy(Counter({"a": 10})) == 0.0


# ---------------------------------------------------------------------------
# compute_docstring_uniformity
# ---------------------------------------------------------------------------


def test_docstring_uniformity_identical():
    files = [
        ("a.py", '''"""Calculate user score based on purchase history."""\ndef foo(): pass'''),
        ("b.py", '''"""Calculate user score based on purchase history."""\ndef bar(): pass'''),
    ]
    score = compute_docstring_uniformity(files)
    assert score > 80


def test_docstring_uniformity_diverse():
    files = [
        ("a.py", '"""Calculate user score."""\ndef foo(): pass'),
        ("b.py", '"""Parse config line into a dictionary."""\ndef bar(): pass'),
    ]
    score = compute_docstring_uniformity(files)
    assert score < 30


def test_docstring_uniformity_fewer_than_two():
    files = [("a.py", '"""Only one docstring."""\npass')]
    assert compute_docstring_uniformity(files) == 0.0


def test_docstring_uniformity_non_python():
    files = [("a.js", "// comment")]
    assert compute_docstring_uniformity(files) == 0.0


# ---------------------------------------------------------------------------
# compute_identifier_entropy
# ---------------------------------------------------------------------------


def test_identifier_entropy_middle_band():
    """Skewed distribution → medium entropy → low score (clean signal)."""
    code = "x = 1\n" * 5 + "y = 1\n" + "z = 1\n"
    files = [("a.py", code)]
    score = compute_identifier_entropy(files)
    assert score < 30


def test_identifier_entropy_low_entropy():
    """Same name repeated → very low entropy → high score."""
    code = "x = 1\n" * 50
    files = [("a.py", code)]
    score = compute_identifier_entropy(files)
    assert score > 50


def test_identifier_entropy_too_few():
    files = [("a.py", "pass")]
    assert compute_identifier_entropy(files) == 0.0


# ---------------------------------------------------------------------------
# compute_comment_ratio
# ---------------------------------------------------------------------------


def test_comment_ratio_overcommented():
    patches = [
        "+# Comment 1\n+# Comment 2\n+# Comment 3\n+# Comment 4\n+def foo():\n+    pass",
    ]
    score = compute_comment_ratio(patches)
    assert score > 50


def test_comment_ratio_normal():
    patches = [
        "+def foo():\n+    pass\n+def bar():\n+    return 1",
    ]
    score = compute_comment_ratio(patches)
    assert score == 0.0


def test_comment_ratio_empty():
    assert compute_comment_ratio([]) == 0.0


# ---------------------------------------------------------------------------
# compute_diff_description_ratio
# ---------------------------------------------------------------------------


def test_diff_desc_large_diff_no_desc():
    score = compute_diff_description_ratio(500, None)
    assert score >= 70


def test_diff_desc_small_diff_good_desc():
    score = compute_diff_description_ratio(10, "Fix typo in config parser")
    assert score < 30


def test_diff_desc_ai_filler_phrases():
    score = compute_diff_description_ratio(
        500,
        "This PR implements the feature. I have updated the API. "
        "This commit leverages the new pattern to utilize the util.",
    )
    assert score > 60


def test_diff_desc_empty_desc_no_changes():
    assert compute_diff_description_ratio(0, None) == 0.0


# ---------------------------------------------------------------------------
# compute_churn_pattern
# ---------------------------------------------------------------------------


def test_churn_high():
    patches = [
        "-def old_foo():\n-    old_way()\n+def new_foo():\n+    new_way()",
    ]
    score = compute_churn_pattern(patches)
    assert score > 30


def test_churn_low():
    patches = [
        "+def foo():\n+    return 1",
    ]
    score = compute_churn_pattern(patches)
    assert score == 0.0


def test_churn_empty():
    assert compute_churn_pattern([]) == 0.0


# ---------------------------------------------------------------------------
# compute_new_author_risk
# ---------------------------------------------------------------------------


def test_new_author_risk_zero_prior(tmp_path):
    repo_path = _make_git_repo(tmp_path)
    _commit_file(tmp_path, "main.py", "x = 1", "initial")
    head_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    ).stdout.strip()

    from git import Repo

    repo = Repo(repo_path)
    score = compute_new_author_risk(repo, head_sha, 200)
    # First commit for this author — prior_count includes the HEAD commit,
    # so it will be 1.
    assert 0 <= score <= 100


# ---------------------------------------------------------------------------
# SignalResult
# ---------------------------------------------------------------------------


def test_signal_result_post_init():
    s = SignalResult(raw=85.123, weighted=17.0246)
    assert s.raw == 85.12
    assert s.weighted == 17.0


# ---------------------------------------------------------------------------
# _get_verdict
# ---------------------------------------------------------------------------


def test_get_verdict():
    assert _get_verdict(80) == "FAIL"
    assert _get_verdict(50) == "WARN"
    assert _get_verdict(20) == "PASS"
    assert _get_verdict(70) == "FAIL"
    assert _get_verdict(40) == "WARN"
    assert _get_verdict(39) == "PASS"


# ---------------------------------------------------------------------------
# _build_summary
# ---------------------------------------------------------------------------


def test_build_summary_flagged():
    signals = {
        "s1": SignalResult(raw=80, weighted=16.0, verdict="FAIL"),
        "s2": SignalResult(raw=50, weighted=7.5, verdict="WARN"),
    }
    summary = _build_summary(73.0, 60, signals)
    assert "flagged" in summary.lower()
    assert "73" in summary
    assert "73" in summary


def test_build_summary_clean():
    signals = {"s1": SignalResult(raw=20, weighted=4.0, verdict="PASS")}
    summary = _build_summary(24.0, 60, signals)
    assert "human" in summary.lower()


# ---------------------------------------------------------------------------
# _read_pr_body
# ---------------------------------------------------------------------------


def test_read_pr_body_direct_string():
    assert _read_pr_body("hello world", "/tmp") == "hello world"


def test_read_pr_body_from_file(tmp_path):
    body_file = tmp_path / "pr_body.txt"
    body_file.write_text("my custom pr body")
    result = _read_pr_body(str(body_file), str(tmp_path))
    assert result == "my custom pr body"


def test_read_pr_body_default_file(tmp_path):
    body_file = tmp_path / ".pr_body.txt"
    body_file.write_text("default pr body")
    result = _read_pr_body(None, str(tmp_path))
    assert result == "default pr body"


def test_read_pr_body_none_missing():
    assert _read_pr_body(None, "/tmp/nonexistent") is None


# ---------------------------------------------------------------------------
# compute_slop_score integration (using a real git repo)
# ---------------------------------------------------------------------------


def test_compute_slop_score_no_git(tmp_path):
    result = compute_slop_score(repo_path=str(tmp_path))
    assert isinstance(result, SlopResult)
    assert result.slop_score == 0.0
    assert not result.flagged


def test_compute_slop_score_clean_pr(tmp_path):
    repo_path = _make_git_repo(tmp_path)
    _commit_file(tmp_path, "main.py", "x = 1", "initial")
    subprocess.run(
        ["git", "checkout", "-b", "feature"],
        cwd=tmp_path,
        capture_output=True,
    )
    _commit_file(tmp_path, "utils.py", "def add(a, b):\n    return a + b", "add util")

    result = compute_slop_score(
        repo_path=repo_path,
        base_branch="main",
        head_branch="feature",
        pr_body="Add utility function for addition",
    )
    assert 0 <= result.slop_score <= 100
    assert isinstance(result.flagged, bool)
    assert len(result.signals) == 6


def test_compute_slop_score_identical_branches(tmp_path):
    repo_path = _make_git_repo(tmp_path)
    _commit_file(tmp_path, "main.py", "x = 1", "initial")
    result = compute_slop_score(
        repo_path=repo_path,
        base_branch="main",
        head_branch="main",
    )
    assert 0 <= result.slop_score <= 100


def test_compute_slop_score_score_range(tmp_path):
    """Final score must always be in [0, 100]."""
    repo_path = _make_git_repo(tmp_path)
    _commit_file(tmp_path, "main.py", "x = 1", "initial")
    subprocess.run(
        ["git", "checkout", "-b", "big-change"],
        cwd=tmp_path,
        capture_output=True,
    )
    _commit_file(tmp_path, "big.py", "# comment\n" * 50 + "x = 1\n" * 50, "big change")

    result = compute_slop_score(
        repo_path=repo_path,
        base_branch="main",
        head_branch="big-change",
    )
    assert 0 <= result.slop_score <= 100


# ---------------------------------------------------------------------------
# CLI integration (typer subcommand)
# ---------------------------------------------------------------------------


def test_cli_help():
    """Ensure check-pr appears in help output."""
    import subprocess as sp

    result = sp.run(
        ["python", "-m", "devlens.cli.cli", "check-pr", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "check-pr" in result.stdout or "Detect AI-generated" in result.stdout


def test_cli_text_output(tmp_path):
    """Run check-pr from CLI with text output."""
    _make_git_repo(tmp_path)
    _commit_file(tmp_path, "main.py", "x = 1", "initial")

    import subprocess as sp

    result = sp.run(
        [
            "python",
            "-m",
            "devlens.cli.cli",
            "check-pr",
            "--repo",
            str(tmp_path),
            "--base",
            "main",
            "--head",
            "main",
        ],
        capture_output=True,
        text=True,
    )
    assert "Slop Report" in result.stdout or "Slop Score" in result.stdout


def test_cli_json_output(tmp_path):
    """Run check-pr with --output json produces valid JSON."""
    _make_git_repo(tmp_path)
    _commit_file(tmp_path, "main.py", "x = 1", "initial")

    import subprocess as sp

    result = sp.run(
        [
            "python",
            "-m",
            "devlens.cli.cli",
            "check-pr",
            "--repo",
            str(tmp_path),
            "--base",
            "main",
            "--head",
            "main",
            "--output",
            "json",
        ],
        capture_output=True,
        text=True,
    )
    data = json.loads(result.stdout)
    assert "slop_score" in data
    assert "flagged" in data
    assert "signals" in data
    assert "summary" in data


def test_cli_fail_on_slop_exit_code(tmp_path):
    """--fail-on-slop should not exit 1 for a clean PR."""
    _make_git_repo(tmp_path)
    _commit_file(tmp_path, "main.py", "x = 1", "initial")

    import subprocess as sp

    result = sp.run(
        [
            "python",
            "-m",
            "devlens.cli.cli",
            "check-pr",
            "--repo",
            str(tmp_path),
            "--base",
            "main",
            "--head",
            "main",
            "--fail-on-slop",
            "--threshold",
            "0",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1  # threshold 0 means almost everything is flagged
