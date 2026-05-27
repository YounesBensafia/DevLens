from pathlib import Path

from devlens.config.project_config import load_weights, DEFAULT_WEIGHTS


def test_load_weights_defaults_when_no_pyproject(tmp_path):
    weights = load_weights(str(tmp_path))
    assert weights == DEFAULT_WEIGHTS


def test_load_weights_from_pyproject(tmp_path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[tool.devlens]\n'
        'weights = { metrics = 0.60, git = 0.25, llm = 0.15 }\n'
    )
    weights = load_weights(str(tmp_path))
    assert weights == {"metrics": 0.60, "git": 0.25, "llm": 0.15}


def test_load_weights_invalid_sum_falls_back_to_default(tmp_path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[tool.devlens]\n'
        'weights = { metrics = 0.50, git = 0.50, llm = 0.50 }\n'
    )
    weights = load_weights(str(tmp_path))
    assert weights == DEFAULT_WEIGHTS


def test_load_weights_missing_fields_falls_back(tmp_path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[tool.devlens]\n'
        'weights = { metrics = 1.0 }\n'
    )
    weights = load_weights(str(tmp_path))
    assert weights == DEFAULT_WEIGHTS


def test_load_weights_invalid_toml_falls_back(tmp_path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("not valid toml [[[")
    weights = load_weights(str(tmp_path))
    assert weights == DEFAULT_WEIGHTS
