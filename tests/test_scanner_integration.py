from pathlib import Path

from devlens.analyzer.scan_display import run_scan_with_progress


FIXTURES = str(Path(__file__).parent / "fixtures")


def test_scan_fixtures_directory():
    report = run_scan_with_progress(
        project_path=FIXTURES,
        use_llm=False,
        send_request_fn=None,
        build_payload_fn=None,
    )
    assert report.project_path == FIXTURES
    assert report.avg_score >= 0.0
    assert report.avg_score <= 100.0
    assert len(report.files) > 0
    assert "critical" in report.risk_distribution
    assert "good" in report.risk_distribution
    for f in report.files:
        assert f.final_score >= 0.0
        assert f.final_score <= 100.0
        assert f.risk_level in report.risk_distribution
