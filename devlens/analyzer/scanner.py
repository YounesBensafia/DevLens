from dataclasses import dataclass, field

from devlens.core.git_signals import GitSignals
from devlens.core.llm_judge import LLMJudgment
from devlens.core.metrics import FileMetrics

RISK_THRESHOLDS = {
    "critical": (0, 35),
    "high": (35, 55),
    "medium": (55, 70),
    "low": (70, 85),
    "good": (85, 100),
}

DEFAULT_WEIGHTS = {"metrics": 0.50, "git": 0.30, "llm": 0.20}


@dataclass
class ScoreBreakdown:
    metrics_score: float
    git_score: float
    llm_score: float
    metrics_weight: float
    git_weight: float
    llm_weight: float
    confidence_band: str
    confidence_label: str


@dataclass
class FileReport:
    path: str
    metrics: FileMetrics
    git: GitSignals | None
    llm: LLMJudgment | None
    final_score: float
    risk_level: str
    top_issues: list[str] = field(default_factory=list)
    breakdown: ScoreBreakdown | None = None


@dataclass
class ProjectReport:
    project_path: str
    files: list[FileReport]
    avg_score: float
    risk_distribution: dict[str, int]
    most_critical: list[FileReport]
    bus_factor_risks: list[FileReport]
    weights_used: dict[str, float] | None = None


def _compute_layer_scores(
    metrics: FileMetrics,
    git: GitSignals | None,
    llm: LLMJudgment | None,
) -> tuple[float, float, float]:
    metrics_score = metrics.comprehension_score

    git_score = 100.0
    if git is not None:
        git_score = 100.0 - git.staleness_score
        if git.is_orphan:
            git_score *= 0.85

    llm_score = llm.llm_score if llm is not None else 50.0

    return metrics_score, git_score, llm_score


def _compute_final_score(
    metrics: FileMetrics,
    git: GitSignals | None,
    llm: LLMJudgment | None,
    weights: dict[str, float] | None = None,
) -> float:
    w = weights or DEFAULT_WEIGHTS
    m_score, g_score, l_score = _compute_layer_scores(metrics, git, llm)
    final = w["metrics"] * m_score + w["git"] * g_score + w["llm"] * l_score
    return round(final, 1)


def compute_confidence_band(
    metrics: FileMetrics,
    git: GitSignals | None,
    llm: LLMJudgment | None,
) -> tuple[str, str]:
    m_score, g_score, l_score = _compute_layer_scores(metrics, git, llm)
    spread = max(m_score, g_score, l_score) - min(m_score, g_score, l_score)
    if spread <= 15:
        return "±2", "high"
    if spread <= 25:
        return "±5", "medium"
    return "±8", "low"


def score_breakdown(
    metrics: FileMetrics,
    git: GitSignals | None,
    llm: LLMJudgment | None,
    weights: dict[str, float] | None = None,
) -> ScoreBreakdown:
    w = weights or DEFAULT_WEIGHTS
    m_score, g_score, l_score = _compute_layer_scores(metrics, git, llm)
    band, label = compute_confidence_band(metrics, git, llm)
    return ScoreBreakdown(
        metrics_score=round(m_score, 1),
        git_score=round(g_score, 1),
        llm_score=round(l_score, 1),
        metrics_weight=w["metrics"],
        git_weight=w["git"],
        llm_weight=w["llm"],
        confidence_band=band,
        confidence_label=label,
    )


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
