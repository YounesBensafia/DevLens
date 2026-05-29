<div align="center">

# DevLens

<img width="100%" src="https://github.com/user-attachments/assets/1883a4eb-2892-4e9d-81cb-dc54cee2b0ea"/>

**Codebase comprehension scanner**

[![PyPI version](https://img.shields.io/pypi/v/devlens-tool?color=blue&label=PyPI)](https://pypi.org/project/devlens-tool/)
[![Python](https://img.shields.io/pypi/pyversions/devlens-tool?color=blue)](https://pypi.org/project/devlens-tool/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/YounesBensafia/DevLens?style=social)](https://github.com/YounesBensafia/DevLens)

[Installation](#installation) . [Usage](#usage) . [Configuration](#configuration) . [Contributing](#contributing) . [License](#license)

</div>

---

## What it does

Lost in a new codebase? DevLens scans your Python project and scores every file from 0 to 100 based on how hard it is to understand. It uses code complexity metrics, git history signals, and optional AI judgment to pinpoint the files your team will struggle with. It also shows project statistics (languages, lines, directories) and can summarize each file with AI.

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
|---|---|
| `devlens -scan <PATH>` | Full scan with all three layers (needs API key) |
| `devlens -scan <PATH> --no-llm` | Scan without AI (deterministic, works in CI) |
| `devlens -scan <PATH> --trend` | Show how the project score changed over time |
| `devlens -scan <PATH> --regression` | List files that got worse since the last scan |
| `devlens -scan <PATH> --since 14` | Compare against a scan from 14 days ago |
| `devlens -st <PATH>` | Project statistics: files, lines, languages, directories |
| `devlens -an <PATH>` | AI-generated one-paragraph summary of each file |

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
