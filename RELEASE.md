# DevLens v0.2.0

[![PyPI version](https://img.shields.io/pypi/v/devlens-tool?color=blue&label=PyPI)](https://pypi.org/project/devlens-tool/)
[![Python](https://img.shields.io/pypi/pyversions/devlens-tool?color=blue)](https://pypi.org/project/devlens-tool/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/YounesBensafia/DevLens?style=social)](https://github.com/YounesBensafia/DevLens)

A CLI tool that delivers AI-powered insights into your codebase — project statistics, language breakdown, dead code detection, and automatic README generation. Powered by [Groq](https://groq.com/)'s Llama models.

## What's New in v0.2.0

This release focuses on **correctness**, **dependency cleanup**, and **wider compatibility**.

## Bug Fixes

| Issue | Description | Impact |
|-------|-------------|--------|
| **Data corruption on repeated runs** | Line count statistics were accumulated in a module-level global list that was never cleared between calls | Fixed: moved to local variable, each run starts clean |
| **Crash when `GROQ_API_KEY` is unset** | AI commands silently sent `Bearer None` as auth, producing a cryptic API error | Fixed: clear error message with link to get a free key |
| **Inflated project size (93 MB → 0.28 MB)** | `get_logical_size_of_the_project` walked into `.git`, `.venv`, and other hidden directories | Fixed: hidden directories are now excluded |
| **Inflated directory count (8 → 4)** | `count_directories` included `.git`, `.venv`, `.pytest_cache`, etc. | Fixed: hidden directories filtered out |
| **`BOLD_GREEN` type error** | `(".py")` evaluates to a string, not a tuple; breaks `endswith()` checks | Fixed: changed to `(".py",)` |
| **Redundant path operation** | `os.path.join(os.path.abspath(path))` — `join` with one argument is a no-op | Fixed: simplified to `os.path.abspath(path)` |

## Improvements

| Change | Before | After |
|--------|--------|-------|
| **Removed `numpy` dependency** | 16 MB install for a single `np.round()` call | Uses Python's built-in `round()` — zero extra bytes |
| **Python version requirement** | `>= 3.13` (only latest Python) | `>= 3.10` (covers 4 major versions) |
| **API auth headers** | Baked at import time with potentially `None` key | Lazy-loaded via `get_headers()` function |
| **Developer Experience** | Missing `pytest` in dev environment | Added `pytest` to `dependency-groups` for easy testing |
| **Package name** | `devlens-cli` (owned by another account) | `devlens-tool` |

## Install / Upgrade

```bash
pip install devlens-tool --upgrade
```

or

```bash
uv tool install devlens-tool --upgrade
```

## Commands

| Command | Description |
|---------|-------------|
| `devlens -st <PATH>` | Project summary — files, lines, directories, language breakdown, structure |
| `devlens -an <PATH>` | AI-powered file analysis using meta-llama/llama-4-scout-17b-16e-instruct |
| `devlens -rd` | Auto-generate a professional README.md |
| `devlens -deadcode <PATH>` | Detect unused functions and imports |

## Full Changelog

https://github.com/YounesBensafia/DevLens/compare/v0.1.0...v0.2.0

---

<div align="center">

**Built by [Younes Bensafia](https://github.com/YounesBensafia)**

</div>
