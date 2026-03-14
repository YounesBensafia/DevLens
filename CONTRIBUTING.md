# Contributing to DevLens

Thank you for your interest in contributing.

## Getting Started

1. Fork the repository and clone your fork.
2. Create a new branch for your change.
3. Set up Python 3.13 or later.
4. Install the project in editable mode:

```bash
python -m pip install -e .
python -m pip install pytest
```

## Development Guidelines

- Keep changes focused and small when possible.
- Add or update tests when behavior changes.
- Prefer clear function names and short docstrings.
- Avoid introducing breaking CLI changes without discussion.

## Running Tests

Run test commands locally before opening a pull request:

```bash
python -m pytest -q
```

## Commit and Pull Request Process

1. Write descriptive commit messages.
2. Push your branch to your fork.
3. Open a pull request against `main`.
4. Describe:
   - What changed
   - Why it changed
   - How it was tested

## Reporting Issues

When filing a bug report, include:

- Expected behavior
- Actual behavior
- Steps to reproduce
- Python version and OS

Thanks for helping improve DevLens.