"""
Comprehension Debt Scanner — orchestrates all 3 layers.

Final score formula:
  50% deterministic metrics (radon + AST)
  30% git signals
  20% LLM qualitative judgment (binary questions)
"""
from dataclasses import dataclass, field
from pathlib import Path

from devlens.core.metrics import FileMetrics, analyze_file
from devlens.core.git_signals import GitSignals, get_git_signals, get_repo_root
from devlens.core.llm_judge import LLMJudgment, build_llm_prompt, parse_llm_response, SYSTEM_PROMPT


RISK_THRESHOLDS = {
    "critical": (0, 35),
    "high":     (35, 55),
    "medium":   (55, 70),
    "low":      (70, 85),
    "good":     (85, 100),
}


@dataclass
class FileReport:
    path: str
    metrics: FileMetrics
    git: GitSignals | None
    llm: LLMJudgment | None
    final_score: float
    risk_level: str
    top_issues: list[str] = field(default_factory=list)


@dataclass
class ProjectReport:
    project_path: str
    files: list[FileReport]
    avg_score: float
    risk_distribution: dict[str, int]
    most_critical: list[FileReport]
    bus_factor_risks: list[FileReport]


def _compute_final_score(
    metrics: FileMetrics,
    git: GitSignals | None,
    llm: LLMJudgment | None,
) -> float:
    base = metrics.comprehension_score

    git_score = 100.0
    if git is not None:
        git_score = 100.0 - git.staleness_score
        if git.is_orphan:
            git_score *= 0.85

    llm_score = llm.llm_score if llm is not None else 50.0

    final = (
        0.50 * base +
        0.30 * git_score +
        0.20 * llm_score
    )
    return round(final, 1)


def _get_risk_level(score: float) -> str:
    for level, (low, high) in RISK_THRESHOLDS.items():
        if low <= score < high:
            return level
    return "good"


def _get_top_issues(
    metrics: FileMetrics,
    git: GitSignals | None,
    llm: LLMJudgment | None,
) -> list[str]:
    issues = []

    if metrics.max_cyclomatic_complexity > 15:
        worst = max(metrics.functions, key=lambda f: f.cyclomatic_complexity, default=None)
        fn = f" (worst: `{worst.name}`)" if worst else ""
        issues.append(f"Very high cyclomatic complexity: {metrics.max_cyclomatic_complexity}{fn}")

    if metrics.maintainability_index < 40:
        issues.append(f"Low maintainability index: {metrics.maintainability_index}/100")

    if metrics.docstring_ratio < 0.2 and metrics.lloc > 30:
        pct = int(metrics.docstring_ratio * 100)
        issues.append(f"Only {pct}% of functions/classes are documented")

    if metrics.max_nesting_depth >= 5:
        issues.append(f"Deep nesting: {metrics.max_nesting_depth} levels")

    if metrics.bad_name_ratio > 0.3:
        pct = int(metrics.bad_name_ratio * 100)
        issues.append(f"{pct}% of variable names are generic or single-character")

    if git and git.is_orphan and git.total_commits > 0:
        issues.append(f"Bus factor = 1 (only 1 author, {git.total_commits} commits)")

    if git and git.days_since_last_change and git.days_since_last_change > 180:
        issues.append(f"Not touched in {git.days_since_last_change} days")

    if llm and llm.undocumented_side_effects:
        issues.append("Likely undocumented side effects")

    if llm and llm.magic_values:
        issues.append("Magic numbers or unexplained string constants")

    if llm and not llm.junior_friendly:
        issues.append(f"Hard to onboard: {llm.explanation}")

    return issues[:5]
