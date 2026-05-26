"""
Deterministic metrics layer — no LLM, 100% reproducible.
Uses radon for complexity + ast for structural signals.
"""
import ast
from dataclasses import dataclass, field
from pathlib import Path

try:
    from radon.complexity import cc_visit, cc_rank
    from radon.metrics import mi_visit
    from radon.raw import analyze
    from radon.metrics import h_visit
    HAS_RADON = True
except ImportError:
    HAS_RADON = False


@dataclass
class FunctionMetrics:
    name: str
    cyclomatic_complexity: int
    lineno: int
    rank: str


@dataclass
class FileMetrics:
    path: str
    cyclomatic_complexity: float
    max_cyclomatic_complexity: int
    maintainability_index: float
    halstead_effort: float
    loc: int
    lloc: int
    comment_ratio: float
    max_nesting_depth: int
    docstring_ratio: float
    bad_name_ratio: float
    functions: list[FunctionMetrics] = field(default_factory=list)
    comprehension_score: float = 0.0
    error: str | None = None


def _get_nesting_depth(tree: ast.AST) -> int:
    def depth(node, current=0):
        nesting_nodes = (ast.If, ast.For, ast.While, ast.With, ast.Try,
                         ast.ExceptHandler, ast.AsyncFor, ast.AsyncWith)
        if isinstance(node, nesting_nodes):
            current += 1
        return max(
            [current] + [depth(child, current) for child in ast.iter_child_nodes(node)]
        )
    return depth(tree)


def _get_docstring_ratio(tree: ast.AST) -> float:
    total = 0
    documented = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            total += 1
            if (node.body and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)):
                documented += 1
    return documented / total if total > 0 else 1.0


BAD_NAMES = {
    'x', 'y', 'z', 'i', 'j', 'k', 'n', 'm', 'l',
    'tmp', 'temp', 'data', 'val', 'var', 'obj', 'res',
    'result', 'foo', 'bar', 'baz', 'test', 'thing',
    'item', 'elem', 'e', 'ex', 'err', 'f', 'r', 's',
}


def _get_bad_name_ratio(tree: ast.AST) -> float:
    names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.append(node.id)
        elif isinstance(node, ast.arg):
            if node.arg not in ('self', 'cls'):
                names.append(node.arg)
    if not names:
        return 0.0
    bad = sum(1 for n in names if n in BAD_NAMES or (len(n) == 1 and n.isalpha()))
    return bad / len(names)


def _normalize(value: float, min_val: float, max_val: float, invert: bool = False) -> float:
    if max_val == min_val:
        return 50.0
    score = (value - min_val) / (max_val - min_val) * 100
    score = max(0.0, min(100.0, score))
    return (100 - score) if invert else score


def _compute_comprehension_score(m: "FileMetrics") -> float:
    """
    Weighted composite — higher = more comprehensible.
    Based on ScienceDirect 2025 hybrid approach (R²=0.87).

    Weights:
      35% Maintainability Index  (validated gold standard)
      25% Cyclomatic complexity  (inverted)
      20% Documentation          (docstrings + comments)
      20% Structural clarity     (nesting + naming)
    """
    mi_score = max(0.0, min(100.0, m.maintainability_index))
    cc_score = _normalize(m.cyclomatic_complexity, 1, 20, invert=True)
    doc_score = m.docstring_ratio * 70 + m.comment_ratio * 30
    nesting_score = _normalize(m.max_nesting_depth, 0, 8, invert=True)
    naming_score = _normalize(m.bad_name_ratio, 0, 0.5, invert=True)
    structural_score = (nesting_score + naming_score) / 2

    score = (
        0.35 * mi_score +
        0.25 * cc_score +
        0.20 * doc_score +
        0.20 * structural_score
    )
    return round(score, 1)


def analyze_file(file_path: str) -> FileMetrics:
    path = Path(file_path)

    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return FileMetrics(
            path=file_path, cyclomatic_complexity=0, max_cyclomatic_complexity=0,
            maintainability_index=0, halstead_effort=0, loc=0, lloc=0,
            comment_ratio=0, max_nesting_depth=0, docstring_ratio=0,
            bad_name_ratio=0, error=str(e)
        )

    if not source.strip():
        return FileMetrics(
            path=file_path, cyclomatic_complexity=0, max_cyclomatic_complexity=0,
            maintainability_index=0, halstead_effort=0, loc=0, lloc=0,
            comment_ratio=0, max_nesting_depth=0, docstring_ratio=0,
            bad_name_ratio=0, error="empty file"
        )

    cc_avg = 0.0
    cc_max = 0
    functions = []
    mi = 50.0
    halstead_effort = 0.0
    loc = lloc = 0
    comment_ratio = 0.0

    if HAS_RADON:
        try:
            raw = analyze(source)
            loc = raw.loc
            lloc = raw.lloc
            comment_ratio = raw.comments / loc if loc > 0 else 0.0

            cc_results = cc_visit(source)
            if cc_results:
                complexities = [r.complexity for r in cc_results]
                cc_avg = sum(complexities) / len(complexities)
                cc_max = max(complexities)
                functions = [
                    FunctionMetrics(
                        name=r.name,
                        cyclomatic_complexity=r.complexity,
                        lineno=r.lineno,
                        rank=cc_rank(r.complexity)
                    )
                    for r in cc_results
                ]

            mi_result = mi_visit(source, multi=True)
            mi = max(0.0, min(100.0, mi_result))

            h = h_visit(source)
            if h:
                halstead_effort = h[0].total.effort if hasattr(h[0], 'total') else 0.0

        except Exception:
            pass

    max_nesting = 0
    docstring_ratio = 0.0
    bad_name_ratio = 0.0

    try:
        tree = ast.parse(source)
        max_nesting = _get_nesting_depth(tree)
        docstring_ratio = _get_docstring_ratio(tree)
        bad_name_ratio = _get_bad_name_ratio(tree)
    except SyntaxError:
        pass

    m = FileMetrics(
        path=file_path,
        cyclomatic_complexity=round(cc_avg, 1),
        max_cyclomatic_complexity=cc_max,
        maintainability_index=round(mi, 1),
        halstead_effort=round(halstead_effort, 1),
        loc=loc,
        lloc=lloc,
        comment_ratio=round(comment_ratio, 3),
        max_nesting_depth=max_nesting,
        docstring_ratio=round(docstring_ratio, 3),
        bad_name_ratio=round(bad_name_ratio, 3),
        functions=functions,
    )
    m.comprehension_score = _compute_comprehension_score(m)
    return m
