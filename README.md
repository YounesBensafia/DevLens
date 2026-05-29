<div align="center">

# DevLens

<img width="100%" src="https://github.com/user-attachments/assets/1883a4eb-2892-4e9d-81cb-dc54cee2b0ea"/>

**Codebase comprehension scanner + AI slop detector**

[![PyPI version](https://img.shields.io/pypi/v/devlens-tool?color=blue&label=PyPI)](https://pypi.org/project/devlens-tool/)
[![Python](https://img.shields.io/pypi/pyversions/devlens-tool?color=blue)](https://pypi.org/project/devlens-tool/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/YounesBensafia/DevLens?style=social)](https://github.com/YounesBensafia/DevLens)

[Installation](#installation) . [Usage](#usage) . [Configuration](#configuration) . [Contributing](#contributing) . [License](#license)

</div>

---

## What it does

Lost in a new codebase? DevLens scans your Python project and scores every file from 0 to 100 based on how hard it is to understand. It uses code complexity metrics, git history signals, and optional AI judgment to pinpoint the files your team will struggle with. It also shows project statistics (languages, lines, directories) and can summarize each file with AI.

DevLens also detects AI-generated or low-effort pull requests using pure heuristic signals: no LLM calls, no API costs, fully deterministic. Drop it in CI to catch slop before it merges.

---

## Why this is useful

- Onboarding a new developer? They know which files to ask about first.
- Planning a sprint? You see which files got worse since the last scan.
- Reporting to a manager? You show a trend line: "Our codebase went from 45 to 62 this quarter."

---

## Quick start

```bash
pip install devlens-tool
```

Set your API key (for AI features):

```bash
export LLM_API_KEY=your_key_here
```

Run a scan:

```bash
cd my-project
devlens -scan .
```

---

## Commands

| Command | What it does |
|---|---|---|
| `devlens -scan <PATH>` | Full scan with all three layers (needs API key) |
| `devlens -scan <PATH> --no-llm` | Scan without AI (deterministic, works in CI) |
| `devlens -scan <PATH> --trend` | Show how the project score changed over time |
| `devlens -scan <PATH> --regression` | List files that got worse since the last scan |
| `devlens -scan <PATH> --since 14` | Compare against a scan from 14 days ago |
| `devlens -st <PATH>` | Project statistics: files, lines, languages, directories |
| `devlens -an <PATH>` | AI-generated one-paragraph summary of each file |
| `devlens check-pr` | Detect AI-generated or low-effort PRs (no LLM needed) |

---

## Scan output example

```
Project Score: 62
Files Analyzed: 47
High Risk Files: 3
Bus Factor Risks: 2

File Comprehension Scores:
  Risk  File                    Score      CC   MI   Docs   Git
  high  src/parser/lexer.py     34  +- 8   18   28    0%    340d solo
  med   src/api/handler.py      52  +- 5   12   45   10%    120d ago
  low   src/models/user.py      72  +- 2    3   82   90%    5d ago
  good  tests/test_utils.py     88  +- 2    1   95  100%    1d ago
```

Each score has a confidence band (+-2, +-5, or +-8) that tells you how much the three layers agree. A high spread means be skeptical of the number.

---

## Slop Detection

DevLens detects likely AI-generated or low-effort pull requests using **6 heuristic signals**: zero LLM calls, zero API cost, fully deterministic.

### Signals

| Signal | Weight | What it catches |
|---|---|---|
| `docstring_uniformity` | 20% | AI-templated docstrings (TF-IDF cosine similarity) |
| `identifier_entropy` | 15% | Suspicious naming patterns (too random or too repetitive) |
| `comment_to_code_ratio` | 15% | Over-commented AI code (>35% comment lines) |
| `diff_size_vs_description_ratio` | 20% | Large diff with tiny description + AI filler phrases |
| `churn_pattern` | 15% | High rewrite ratio (adding lines = deleting lines) |
| `new_author_large_diff` | 15% | New contributor dumping 100+ lines |

### Usage

```bash
# Check a PR branch against main
devlens check-pr --repo . --base main --head my-feature

# With PR description (for diff/description ratio)
devlens check-pr --repo . --base main --head feature --pr-body "Adds user login"

# JSON output for CI parsing
devlens check-pr --repo . --base main --head feature --output json

# Fail CI if slop score >= threshold
devlens check-pr --repo . --base main --head feature --fail-on-slop --threshold 65
```

### Slop output example

```
╔══════════════════════════════════════════════════════════════════════╗
║  DEVENS SLOP REPORT: POSSIBLE AI SLOP                              ║
╚══════════════════════════════════════════════════════════════════════╝
            Slop Score: 73/100  (threshold: 65)
╭─────────────────────────────┬─────────┬──────────┬─────────────╮
│ Signal                      │ Raw Val │ Weighted │   Verdict   │
├─────────────────────────────┼─────────┼──────────┼─────────────┤
│ docstring uniformity        │    87.0 │     17.4 │    FAIL     │
│ identifier entropy          │    12.3 │      1.8 │    PASS     │
│ comment to code ratio       │    55.0 │      8.3 │    WARN     │
│ diff size vs description    │    90.0 │     18.0 │    FAIL     │
│ churn pattern               │    45.0 │      6.8 │    WARN     │
│ new author large diff       │    80.0 │     12.0 │    FAIL     │
├─────────────────────────────┼─────────┼──────────┼─────────────┤
│ Total                       │         │     73.0 │ POSSIBLE AI │
╰─────────────────────────────┴─────────┴──────────┴─────────────╯
```

### CI integration

Add this to `.github/workflows/devlens-slop-check.yml`:

```yaml
name: DevLens Slop Check
on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  slop-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install DevLens
        run: pip install devlens-tool
      - name: Save PR body
        run: echo "${{ github.event.pull_request.body }}" > .pr_body.txt
      - name: Run slop check
        run: |
          devlens check-pr \
            --repo . \
            --base ${{ github.event.pull_request.base.ref }} \
            --head ${{ github.event.pull_request.head.ref }} \
            --output json --fail-on-slop --threshold 65
```

---

## Configuration

You can change how scores are calculated by adding this to your `pyproject.toml`:

```toml
[tool.devlens]
weights = { metrics = 0.70, git = 0.10, llm = 0.20 }
```

The defaults are 50/30/20. The three weights must add up to 1.0.

---

## Using a different AI provider

DevLens works with any OpenAI-compatible API. Set these environment variables:

```bash
# For OpenAI
LLM_API_URL=https://api.openai.com/v1/chat/completions
LLM_API_KEY=sk-your-key
LLM_MODEL=gpt-4o-mini

# For local models (Ollama)
LLM_API_URL=http://localhost:11434/v1/chat/completions
LLM_API_KEY=ollama
LLM_MODEL=llama3.2

# For Groq (default)
LLM_API_URL=https://api.groq.com/openai/v1/chat/completions
LLM_API_KEY=your_groq_key
```

---

## CI integration

Add this to your CI pipeline:

```yaml
- name: Check code comprehension
  run: devlens -scan . --no-llm
```

The `--no-llm` flag makes it fast and deterministic -- no API calls, no network, no randomness.

---

## Roadmap

- [x] Project statistics and language breakdown
- [x] AI-powered file analysis
- [x] Comprehension debt scanning (0-100 scoring)
- [x] Score trend tracking over time
- [x] Configurable scoring weights
- [x] Confidence bands on scores
- [x] Multi-provider LLM support
- [x] AI slop detection (heuristic, zero LLM cost)
- [ ] Dependency graph visualization

---

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/new-thing`)
3. Commit your changes (`git commit -m 'Add new thing'`)
4. Push to the branch (`git push origin feature/new-thing`)
5. Open a Pull Request

---

## License

MIT. See [LICENSE](LICENSE).

---

<div align="center">

**Built by [Younes Bensafia](https://github.com/YounesBensafia)**

If DevLens helps you, consider giving it a star.

</div>
