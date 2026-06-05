"""Heuristic slop detection engine — no LLM, zero network, 100% deterministic."""

import ast
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from git import InvalidGitRepositoryError, Repo

# Kept strictly to phrases that are distinctly AI/corporate-template language.
# Common English words like "adds", "fixes", "implements" were removed — they
# appear in perfectly legitimate PR descriptions and caused false positives.
AI_FILLER_PHRASES = [
    "leverage",
    "utilize",
    "as per",
    "going forward",
    "moving forward",
    "please note that",
    "it is worth noting",
    "in order to",
    "this pr implements",
    "this commit introduces",
]


@dataclass
class SignalResult:
    raw: float
    weighted: float
    verdict: str = "PASS"

    def __post_init__(self):
        self.weighted = round(self.weighted, 1)
        self.raw = round(self.raw, 2)


@dataclass
class SlopResult:
    slop_score: float
    threshold: int
    flagged: bool
    signals: dict[str, SignalResult]
    summary: str


def _manual_tfidf(docstrings: list[str]) -> list[list[float]]:
    """Compute TF-IDF vectors for a list of docstrings without sklearn."""
    if not docstrings:
        return []

    tokenized = []
    for doc in docstrings:
        tokens = re.findall(r"[a-z]+", doc.lower())
        tokenized.append(Counter(tokens))

    vocab_set: set[str] = set()
    for counter in tokenized:
        vocab_set.update(counter.keys())
    vocab_list = sorted(vocab_set)
    n_docs = len(docstrings)

    idf: dict[str, float] = {}
    for term in vocab_list:
        df = sum(1 for c in tokenized if c[term] > 0)
        idf[term] = math.log((n_docs + 1) / (df + 1)) + 1

    vectors: list[list[float]] = []
    for counter in tokenized:
        total = sum(counter.values())
        if total == 0:
            vectors.append([0.0] * len(vocab_list))
            continue
        vec = []
        for term in vocab_list:
            tf = counter[term] / total
            vec.append(tf * idf[term])
        vectors.append(vec)

    return vectors


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(ai * bi for ai, bi in zip(a, b, strict=False))
    na = math.sqrt(sum(ai * ai for ai in a))
    nb = math.sqrt(sum(bi * bi for bi in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _extract_docstrings(source: str) -> list[str]:
    """Extract all docstrings from Python source using AST."""
    docstrings: list[str] = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return docstrings
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = node.body
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
                doc = body[0].value.value
                if isinstance(doc, str):
                    docstrings.append(doc)
    return docstrings


def _shannon_entropy(freqs: Counter) -> float:
    total = sum(freqs.values())
    if total == 0:
        return 0.0
    entropy = 0.0
    for count in freqs.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def _get_verdict(raw: float) -> str:
    if raw >= 70:
        return "FAIL"
    if raw >= 40:
        return "WARN"
    return "PASS"


def _read_pr_body(pr_body: str | None, repo_path: str) -> str | None:
    if pr_body:
        body_path = Path(pr_body)
        if body_path.is_file():
            return body_path.read_text(encoding="utf-8", errors="ignore")
        return pr_body
    default_path = Path(repo_path) / ".pr_body.txt"
    if default_path.is_file():
        return default_path.read_text(encoding="utf-8", errors="ignore")
    return None


def compute_docstring_uniformity(changed_files: list[tuple[str, str]]) -> float:
    """Score 0–100: high similarity between docstrings → high score."""
    all_docs: list[str] = []
    for filepath, source in changed_files:
        if not filepath.endswith(".py"):
            continue
        all_docs.extend(_extract_docstrings(source))

    if len(all_docs) < 2:
        return 0.0

    vectors = _manual_tfidf(all_docs)
    if len(vectors) < 2:
        return 0.0

    similarities = []
    for i in range(len(vectors)):
        for j in range(i + 1, len(vectors)):
            similarities.append(_cosine_similarity(vectors[i], vectors[j]))

    if not similarities:
        return 0.0

    avg_sim = sum(similarities) / len(similarities)
    if avg_sim > 0.85:
        return 100.0
    if avg_sim < 0.30:
        return 0.0
    return (avg_sim - 0.30) / (0.85 - 0.30) * 100.0


def compute_identifier_entropy(changed_files: list[tuple[str, str]]) -> float:
    """Score 0–100: very low or very high entropy → high score."""
    identifiers: list[str] = []
    for filepath, source in changed_files:
        if not filepath.endswith(".py"):
            continue
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                identifiers.append(node.id)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                identifiers.append(node.name)
            if isinstance(node, ast.ClassDef):
                identifiers.append(node.name)
            if isinstance(node, ast.arg) and node.arg not in ("self", "cls"):
                identifiers.append(node.arg)

    if len(identifiers) < 5:
        return 0.0

    freq = Counter(identifiers)
    entropy = _shannon_entropy(freq)
    max_entropy = math.log2(len(freq))
    norm = entropy / max_entropy if max_entropy > 0 else 0.0

    if norm < 0.3:
        return max(0, (1.0 - norm / 0.3) * 100.0)
    if norm > 0.8:
        return min(100, (norm - 0.8) / 0.2 * 100.0)
    return 0.0


def compute_comment_ratio(diff_patches: list[str]) -> float:
    """Score 0–100: too many or too few comments → high score."""
    added_comment_lines = 0
    added_code_lines = 0

    for patch in diff_patches:
        for line in patch.split("\n"):
            if line.startswith("+") and not line.startswith("+++"):
                stripped = line[1:].strip()
                if not stripped:
                    continue
                if stripped.startswith("#"):
                    added_comment_lines += 1
                else:
                    added_code_lines += 1

    total = added_comment_lines + added_code_lines
    if total == 0:
        return 0.0

    ratio = added_comment_lines / total
    if ratio < 0.35:
        return 0.0
    if ratio < 0.50:
        return (ratio - 0.35) / 0.15 * 50.0
    return 50.0 + (ratio - 0.50) / 0.50 * 50.0


def compute_diff_description_ratio(changed_lines: int, description: str | None) -> float:
    """Score 0–100: large diff + tiny description + filler phrases → high."""
    desc = (description or "").strip()

    if not desc:
        return 80.0 if changed_lines > 0 else 0.0

    word_count = len(desc.split())
    if word_count == 0:
        return 80.0

    ratio = changed_lines / word_count

    if ratio < 5:
        score = 0.0
    elif ratio < 20:
        score = (ratio - 5) / 15 * 50
    elif ratio < 50:
        score = 50 + (ratio - 20) / 30 * 30
    else:
        score = 80.0

    desc_lower = desc.lower()
    filler_count = sum(1 for phrase in AI_FILLER_PHRASES if phrase in desc_lower)
    if filler_count > 2:
        score = min(100.0, score + 15)

    return min(100.0, max(0.0, score))


def compute_churn_pattern(diff_patches: list[str]) -> float:
    """Score 0–100: high ratio of removed-to-added lines → high score."""
    total_added = 0
    total_removed = 0

    for patch in diff_patches:
        for line in patch.split("\n"):
            if line.startswith("+") and not line.startswith("+++"):
                total_added += 1
            elif line.startswith("-") and not line.startswith("---"):
                total_removed += 1

    total = total_removed + total_added
    if total == 0:
        return 0.0

    churn_ratio = total_removed / total
    if churn_ratio < 0.2:
        return 0.0
    if churn_ratio < 0.6:
        return (churn_ratio - 0.2) / 0.4 * 50
    return 50 + (churn_ratio - 0.6) / 0.4 * 50


def compute_new_author_risk(repo: Repo, head_commit_hexsha: str, added_lines: int) -> float:
    """
    Score 0–100: new author + large diff = high risk.

    Uses a smooth multiplicative formula instead of binary cliff-edge thresholds:

        score = 100 * exp(-prior_count / 3) * (added_lines / (300 + added_lines))

    Familiarity factor  exp(-prior_count / 3):
      decays from 1.0 at 0 prior commits to ~0.05 at 10 commits — risk halves
      roughly every 3 commits, so a veteran contributor scores near 0.

    Size factor  added_lines / (300 + added_lines):
      a saturating (soft-sigmoid) function that reaches 0.50 at the
      300-line "large diff" baseline and asymptotes to 1.0 — never a cliff.

    Multiplying both means a large diff from a veteran ≈ 0, while a small
    diff from a brand-new author scores low-to-mid rather than zero.

    Sample outputs:
      prior_count=0,  added_lines=50   → ~14
      prior_count=0,  added_lines=200  → ~40
      prior_count=2,  added_lines=199  → ~20
      prior_count=3,  added_lines=100  → ~9
      prior_count=10, added_lines=500  → ~2
    """
    import math

    try:
        head_commit = repo.commit(head_commit_hexsha)
        author_email = head_commit.author.email
    except (ValueError, AttributeError):
        return 0.0

    if not author_email:
        return 0.0

    try:
        prior_count = sum(1 for _ in repo.iter_commits(author=author_email, max_count=1000))
    except Exception:
        prior_count = 1

    familiarity = math.exp(-prior_count / 3)
    size_factor = added_lines / (300 + added_lines) if added_lines > 0 else 0.0
    score = 100.0 * familiarity * size_factor
    return round(min(100.0, max(0.0, score)), 1)


def _build_summary(slop_score: float, threshold: int, signals: dict[str, SignalResult]) -> str:
    failing = [name for name, s in signals.items() if s.verdict == "FAIL"]
    warning = [name for name, s in signals.items() if s.verdict == "WARN"]

    parts = []
    if failing:
        parts.append(f"Flagged signals: {', '.join(failing)}")
    if warning:
        parts.append(f"Concerning signals: {', '.join(warning)}")

    if slop_score >= threshold:
        if not parts:
            parts.append("Overall score exceeds threshold")
        parts.append(f"Slop score {slop_score:.0f}/{threshold} — possible AI slop")
    else:
        if not parts:
            parts.append("No suspicious patterns detected")
        parts.append(f"Slop score {slop_score:.0f}/{threshold} — looks human")

    return " | ".join(parts)


def compute_slop_score(
    repo_path: str = ".",
    base_branch: str = "main",
    head_branch: str | None = None,
    pr_body: str | None = None,
    threshold: int = 60,
) -> SlopResult:
    try:
        repo = Repo(repo_path)
    except InvalidGitRepositoryError:
        return SlopResult(
            slop_score=0.0,
            threshold=threshold,
            flagged=False,
            signals={},
            summary="Not a git repository.",
        )

    if repo.bare:
        return SlopResult(
            slop_score=0.0,
            threshold=threshold,
            flagged=False,
            signals={},
            summary="Bare git repository.",
        )

    try:
        head = head_branch or repo.active_branch.name
    except (TypeError, Exception):
        head = "HEAD"

    try:
        merge_base = repo.merge_base(head, base_branch)
    except Exception:
        merge_base = []

    if not merge_base:
        return SlopResult(
            slop_score=0.0,
            threshold=threshold,
            flagged=False,
            signals={},
            summary=f"Cannot find merge base between {head} and {base_branch}.",
        )

    try:
        diffs = repo.commit(head).diff(merge_base[0], create_patch=True)
    except Exception:
        return SlopResult(
            slop_score=0.0,
            threshold=threshold,
            flagged=False,
            signals={},
            summary=f"Could not compute diff between {head} and {base_branch}.",
        )

    changed_files: list[tuple[str, str]] = []
    diff_patches: list[str] = []
    total_added = 0

    for diff_item in diffs:
        path = diff_item.b_path or diff_item.a_path
        if not path:
            continue

        absolute = Path(repo_path) / path

        if path.endswith(".py"):
            try:
                content = absolute.read_text(encoding="utf-8", errors="ignore")
                changed_files.append((path, content))
            except (FileNotFoundError, OSError):
                try:
                    blob = repo.commit(head).tree / path
                    content = blob.data_stream.read().decode("utf-8", errors="ignore")
                    changed_files.append((path, content))
                except Exception:
                    pass

        if diff_item.diff:
            raw_diff = diff_item.diff
            patch = (
                raw_diff.decode("utf-8", errors="ignore")
                if isinstance(raw_diff, bytes)
                else raw_diff
            )
            diff_patches.append(patch)
            for line in patch.split("\n"):
                if line.startswith("+") and not line.startswith("+++"):
                    total_added += 1

    body = _read_pr_body(pr_body, repo_path)

    signals: dict[str, SignalResult] = {}

    raw = compute_docstring_uniformity(changed_files)
    signals["docstring_uniformity"] = SignalResult(
        raw=raw, weighted=raw * 0.20, verdict=_get_verdict(raw)
    )

    raw = compute_identifier_entropy(changed_files)
    signals["identifier_entropy"] = SignalResult(
        raw=raw, weighted=raw * 0.15, verdict=_get_verdict(raw)
    )

    raw = compute_comment_ratio(diff_patches)
    signals["comment_to_code_ratio"] = SignalResult(
        raw=raw, weighted=raw * 0.15, verdict=_get_verdict(raw)
    )

    raw = compute_diff_description_ratio(total_added, body)
    signals["diff_size_vs_description_ratio"] = SignalResult(
        raw=raw, weighted=raw * 0.20, verdict=_get_verdict(raw)
    )

    raw = compute_churn_pattern(diff_patches)
    signals["churn_pattern"] = SignalResult(raw=raw, weighted=raw * 0.15, verdict=_get_verdict(raw))

    try:
        head_commit_hexsha = repo.commit(head).hexsha
    except Exception:
        head_commit_hexsha = "HEAD"

    raw = compute_new_author_risk(repo, head_commit_hexsha, total_added)
    signals["new_author_large_diff"] = SignalResult(
        raw=raw, weighted=raw * 0.15, verdict=_get_verdict(raw)
    )

    slop_score = sum(s.weighted for s in signals.values())
    slop_score = min(100.0, max(0.0, slop_score))
    flagged = slop_score >= threshold
    summary = _build_summary(slop_score, threshold, signals)

    return SlopResult(
        slop_score=round(slop_score, 1),
        threshold=threshold,
        flagged=flagged,
        signals=signals,
        summary=summary,
    )
