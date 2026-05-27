import pytest

from devlens.analyzer.scanner import _compute_final_score, _get_risk_level, _get_top_issues
from devlens.core.git_signals import GitSignals
from devlens.core.llm_judge import LLMJudgment
from devlens.core.metrics import FileMetrics


def _make_metrics(comprehension_score=50.0, cc=5, mi=60, doc_ratio=0.5,
                  nesting=2, bad_name_ratio=0.1, lloc=50):
    return FileMetrics(
        path="test.py",
        cyclomatic_complexity=float(cc),
        max_cyclomatic_complexity=cc,
        maintainability_index=float(mi),
        halstead_effort=100.0,
        loc=100,
        lloc=lloc,
        comment_ratio=0.1,
        max_nesting_depth=nesting,
        docstring_ratio=doc_ratio,
        bad_name_ratio=bad_name_ratio,
        comprehension_score=comprehension_score,
    )


def _make_git(days=30, authors=2, commits=10, orphan=False, staleness=20.0):
    return GitSignals(
        path="test.py",
        days_since_last_change=days,
        unique_authors=authors,
        total_commits=commits,
        is_orphan=orphan,
        staleness_score=staleness,
    )


def _make_llm(score=80.0, clear=True, side_effects=False, junior=True,
              single=True, magic=False, explanation="Clean code."):
    return LLMJudgment(
        function_names_clear=clear,
        undocumented_side_effects=side_effects,
        junior_friendly=junior,
        single_responsibility=single,
        magic_values=magic,
        llm_score=score,
        explanation=explanation,
    )


def test_compute_final_score_all_layers_defaults():
    metrics = _make_metrics(comprehension_score=80.0)
    score = _compute_final_score(metrics, git=None, llm=None)
    expected = 0.50 * 80.0 + 0.30 * 100.0 + 0.20 * 50.0
    assert score == pytest.approx(expected, abs=0.1)


def test_compute_final_score_all_layers():
    metrics = _make_metrics(comprehension_score=80.0)
    git = _make_git(staleness=10.0)
    llm = _make_llm(score=90.0)
    score = _compute_final_score(metrics, git, llm)
    expected = 0.50 * 80.0 + 0.30 * 90.0 + 0.20 * 90.0
    assert score == pytest.approx(expected, abs=0.1)


def test_compute_final_score_orphan_penalty():
    metrics = _make_metrics(comprehension_score=50.0)
    git = _make_git(staleness=20.0, orphan=True)
    llm = None
    score = _compute_final_score(metrics, git, llm)
    orphan_git_score = (100.0 - 20.0) * 0.85
    expected = 0.50 * 50.0 + 0.30 * orphan_git_score + 0.20 * 50.0
    assert score == pytest.approx(expected, abs=0.1)


def test_get_risk_level_boundaries():
    assert _get_risk_level(0) == "critical"
    assert _get_risk_level(35) == "high"
    assert _get_risk_level(55) == "medium"
    assert _get_risk_level(70) == "low"
    assert _get_risk_level(85) == "good"
    assert _get_risk_level(100) == "good"


def test_get_top_issues_max_five():
    metrics = _make_metrics(comprehension_score=30.0, cc=20, mi=30,
                            doc_ratio=0.0, nesting=6, bad_name_ratio=0.5)
    git = _make_git(days=200, authors=1, commits=5, orphan=True)
    llm = _make_llm(score=20.0, side_effects=True, junior=False, magic=True)
    issues = _get_top_issues(metrics, git, llm)
    assert len(issues) <= 5
