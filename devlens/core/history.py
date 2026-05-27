import json
import subprocess
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

HISTORY_DIR = Path(".devlens/history")


@dataclass
class ScanSnapshot:
    timestamp: str
    git_commit: str
    avg_score: float
    risk_distribution: dict[str, int]
    file_count: int
    critical_count: int
    bus_factor_count: int
    per_file_scores: dict[str, float]


def _get_head_commit(project_path: str) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def save_snapshot(report) -> Path:
    history_path = Path(report.project_path) / HISTORY_DIR
    history_path.mkdir(parents=True, exist_ok=True)

    commit = _get_head_commit(report.project_path)
    snap = ScanSnapshot(
        timestamp=datetime.now(timezone.utc).isoformat(),
        git_commit=commit,
        avg_score=report.avg_score,
        risk_distribution=report.risk_distribution,
        file_count=len(report.files),
        critical_count=sum(
            1 for f in report.files if f.risk_level in ("critical", "high")
        ),
        bus_factor_count=len(report.bus_factor_risks),
        per_file_scores={f.path: f.final_score for f in report.files},
    )

    filename = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}_{commit}.json"
    path = history_path / filename
    path.write_text(json.dumps(asdict(snap), indent=2))
    return path


def load_snapshots(project_path: str) -> list[ScanSnapshot]:
    history_path = Path(project_path) / HISTORY_DIR
    if not history_path.exists():
        return []

    snapshots = []
    for f in sorted(history_path.iterdir()):
        if f.suffix == ".json":
            try:
                data = json.loads(f.read_text())
                snapshots.append(ScanSnapshot(**data))
            except (json.JSONDecodeError, TypeError, KeyError):
                continue
    return snapshots


def load_closest_snapshot(project_path: str, target_age_days: int) -> ScanSnapshot | None:
    target = datetime.now(timezone.utc).timestamp() - target_age_days * 86400
    snapshots = load_snapshots(project_path)

    closest = None
    closest_diff = float("inf")
    for s in snapshots:
        try:
            ts = datetime.fromisoformat(s.timestamp).timestamp()
            diff = abs(ts - target)
            if diff < closest_diff:
                closest_diff = diff
                closest = s
        except (ValueError, TypeError):
            continue
    return closest


def compare_snapshots(
    baseline: ScanSnapshot,
    current: ScanSnapshot,
) -> dict[str, dict[str, float]]:
    all_files = set(baseline.per_file_scores) | set(current.per_file_scores)
    deltas = {}
    for f in all_files:
        old_score = baseline.per_file_scores.get(f)
        new_score = current.per_file_scores.get(f)
        if old_score is not None and new_score is not None:
            delta = round(new_score - old_score, 1)
            if abs(delta) >= 1.0:
                deltas[f] = {"from": old_score, "to": new_score, "delta": delta}
    return deltas
