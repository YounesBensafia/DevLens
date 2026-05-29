# DevLens v0.4.0

[![PyPI version](https://img.shields.io/pypi/v/devlens-tool?color=blue&label=PyPI)](https://pypi.org/project/devlens-tool/)
[![Python](https://img.shields.io/pypi/pyversions/devlens-tool?color=blue)](https://pypi.org/project/devlens-tool/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/YounesBensafia/DevLens?style=social)](https://github.com/YounesBensafia/DevLens)

Scores every Python file from 0 to 100 based on how hard it is to understand, using code metrics, git signals, and optional AI.

## What's New in v0.4.0

### AI Slop Detection (`devlens check-pr`)

A new heuristic command that detects AI-generated or low-effort pull requests using 6 deterministic signals, zero LLM calls, zero network:

| Signal | Weight | What it measures |
|--------|--------|------------------|
| Docstring Uniformity | 20% | Repetitive, templated docstrings |
| Identifier Entropy | 15% | Low-variance variable/function names |
| Comment-to-Code Ratio | 15% | Over-commenting (>35%) |
| Diff Size vs Description | 20% | Large diff with tiny/no PR body |
| Churn Pattern | 15% | One file edited many times in the diff |
| New Author Large Diff | 15% | First-time contributor with massive diff |

```bash
devlens check-pr --repo . --base main --head feature-branch
```

Supports `--output json`, `--fail-on-slop`, and `--pr-body` for CI integration. Ships with a GitHub Actions workflow.

## What's New in v0.3.0

### Comprehension Debt Scanner (`devlens -scan`)

Scores Python files 0-100 based on readability metrics, with optional AI-powered analysis via Groq's Llama models.

### Snapshots + Trends (`devlens -st`)

Track project history over time with `--snapshot`, `--trend`, and `--regression` commands. Powered by `.devlens/` local state.

## Bug Fixes

- Fixed score bar confidence display
- Fixed mypy types across the entire codebase
- Fixed `GROQ_API_KEY` handling for CI safety
- Fixed coverage and linting pipeline

## Install / Upgrade

```bash
pip install devlens-tool --upgrade
```

## Commands

| Command | Description |
|---------|-------------|
| `devlens -st <PATH>` | Project summary with optional snapshot/trend/regression |
| `devlens -an <PATH>` | AI-powered file analysis using meta-llama/llama-4-scout-17b-16e-instruct |
| `devlens -scan <PATH>` | Comprehension debt scan — scores files 0-100 |
| `devlens -scan <PATH> --no-llm` | Scan without AI (deterministic, CI-safe) |
| `devlens check-pr` | Heuristic AI slop detection for pull requests |

## Full Changelog

https://github.com/YounesBensafia/DevLens/compare/v0.2.0...v0.4.0

---

<div align="center">

**Built by [Younes Bensafia](https://github.com/YounesBensafia)**

</div>
