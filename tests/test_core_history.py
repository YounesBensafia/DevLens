import json

from devlens.core.history import (
    ScanSnapshot,
    compare_snapshots,
    load_closest_snapshot,
    load_snapshots,
    save_snapshot,
)


class FakeReport:
    def __init__(self, project_path: str, avg_score: float, files: list, bus_factor_risks: list):
        self.project_path = project_path
        self.avg_score = avg_score
        self.risk_distribution = {"critical": 0, "high": 0, "medium": 0, "low": 0, "good": 0}
        self.files = files
        self.bus_factor_risks = bus_factor_risks


class FakeFile:
    def __init__(self, path: str, final_score: float, risk_level: str = "good"):
        self.path = path
        self.final_score = final_score
        self.risk_level = risk_level


def test_save_and_load_snapshot(tmp_path):
    files = [FakeFile("a.py", 80.0), FakeFile("b.py", 40.0, "high")]
    report = FakeReport(str(tmp_path), 60.0, files, [files[1]])

    saved_path = save_snapshot(report)
    assert saved_path.exists()
    assert saved_path.suffix == ".json"

    data = json.loads(saved_path.read_text())
    assert data["avg_score"] == 60.0
    assert data["file_count"] == 2
    assert data["critical_count"] == 1
    assert data["bus_factor_count"] == 1
    assert data["per_file_scores"] == {"a.py": 80.0, "b.py": 40.0}


def test_load_snapshots_returns_sorted(tmp_path):
    files = [FakeFile("a.py", 50.0)]
    save_snapshot(FakeReport(str(tmp_path), 50.0, files, []))
    save_snapshot(FakeReport(str(tmp_path), 60.0, files, []))

    snapshots = load_snapshots(str(tmp_path))
    assert len(snapshots) == 2


def test_load_snapshots_empty_directory(tmp_path):
    snapshots = load_snapshots(str(tmp_path))
    assert snapshots == []


def test_load_snapshots_skips_corrupted(tmp_path):
    history = tmp_path / ".devlens" / "history"
    history.mkdir(parents=True)
    (history / "bad.json").write_text("not json")
    (history / "empty.json").write_text("")

    snapshots = load_snapshots(str(tmp_path))
    assert snapshots == []


def test_compare_snapshots_detects_changes():
    baseline = ScanSnapshot(
        timestamp="2026-05-01T00:00:00+00:00",
        git_commit="abc",
        avg_score=50.0,
        risk_distribution={},
        file_count=2,
        critical_count=0,
        bus_factor_count=0,
        per_file_scores={"a.py": 80.0, "b.py": 40.0},
    )
    current = ScanSnapshot(
        timestamp="2026-05-15T00:00:00+00:00",
        git_commit="def",
        avg_score=60.0,
        risk_distribution={},
        file_count=2,
        critical_count=0,
        bus_factor_count=0,
        per_file_scores={"a.py": 85.0, "b.py": 35.0},
    )

    deltas = compare_snapshots(baseline, current)
    assert deltas["a.py"]["delta"] == 5.0
    assert deltas["b.py"]["delta"] == -5.0


def test_compare_snapshots_new_file():
    baseline = ScanSnapshot(
        timestamp="2026-05-01T00:00:00+00:00",
        git_commit="abc",
        avg_score=50.0,
        risk_distribution={},
        file_count=1,
        critical_count=0,
        bus_factor_count=0,
        per_file_scores={"a.py": 80.0},
    )
    current = ScanSnapshot(
        timestamp="2026-05-15T00:00:00+00:00",
        git_commit="def",
        avg_score=50.0,
        risk_distribution={},
        file_count=2,
        critical_count=0,
        bus_factor_count=0,
        per_file_scores={"a.py": 80.0, "c.py": 90.0},
    )

    deltas = compare_snapshots(baseline, current)
    assert "c.py" not in deltas
    assert "a.py" not in deltas


def test_load_closest_snapshot(tmp_path):
    files = [FakeFile("a.py", 50.0)]
    save_snapshot(FakeReport(str(tmp_path), 50.0, files, []))

    result = load_closest_snapshot(str(tmp_path), 0)
    assert result is not None
    assert result.avg_score == 50.0
