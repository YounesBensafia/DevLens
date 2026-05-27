import tomllib
from pathlib import Path


DEFAULT_WEIGHTS = {"metrics": 0.50, "git": 0.30, "llm": 0.20}


def load_weights(project_path: str) -> dict[str, float]:
    cfg = Path(project_path) / "pyproject.toml"
    if not cfg.exists():
        return DEFAULT_WEIGHTS
    try:
        with cfg.open("rb") as f:
            data = tomllib.load(f)
        weights = data.get("tool", {}).get("devlens", {}).get("weights", {})
        if weights and all(k in weights for k in ("metrics", "git", "llm")):
            total = sum(weights.values())
            if abs(total - 1.0) < 0.01:
                return weights
        return DEFAULT_WEIGHTS
    except (tomllib.TOMLDecodeError, KeyError, TypeError):
        return DEFAULT_WEIGHTS
