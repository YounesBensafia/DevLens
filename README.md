<div align="center">

# DevLens

<img width="100%" src="https://github.com/user-attachments/assets/1883a4eb-2892-4e9d-81cb-dc54cee2b0ea"/>

**Illuminate your codebase with AI-powered analysis**

[![PyPI version](https://img.shields.io/pypi/v/devlens-tool?color=blue&label=PyPI)](https://pypi.org/project/devlens-tool/)
[![Python](https://img.shields.io/pypi/pyversions/devlens-tool?color=blue)](https://pypi.org/project/devlens-tool/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/YounesBensafia/DevLens?style=social)](https://github.com/YounesBensafia/DevLens)

[Installation](#installation) · [Features](#features) · [Usage](#usage) · [Contributing](#contributing) · [License](#license)

</div>

---

## Overview

DevLens is a powerful CLI tool that delivers comprehensive insights into your codebase. It helps developers and teams **understand**, **document**, and **optimize** their software projects — powered by AI through [Groq](https://groq.com/)'s Llama models.

Whether you need a quick project summary, AI-generated documentation, or dead code detection, DevLens has you covered.

---

## Quick Demo

<p align="center">
  <img width="100%" src="https://github.com/user-attachments/assets/b0e6681b-9c2d-4cae-b3dd-71d599594abf" />
</p>

---

## Features

<table>
  <tr>
    <td width="50%">
      <h3 align="center">AI-Powered Code Analysis</h3>
      <p align="center"><i>Get intelligent summaries of every file in your project</i></p>
      <p align="center">
        <img src="https://github.com/user-attachments/assets/b8e9fdb9-2b19-4ff6-9c6d-72d785ce02e6" width="100%"/>
      </p>
    </td>
    <td width="50%">
      <h3 align="center">Codebase Statistics</h3>
      <p align="center"><i>Language breakdown, line counts, and project structure</i></p>
      <p align="center">
        <img src="https://github.com/user-attachments/assets/990308a1-83a2-40ba-bb99-182b5ba41434" width="100%"/>
      </p>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3 align="center">Complete Project Insights</h3>
      <p align="center"><i>Total files, directories, and detailed structure visualization</i></p>
      <p align="center">
        <img src="https://github.com/user-attachments/assets/88402183-93e9-48f2-bce5-2a9ae79d8fb0" width="100%"/>
      </p>
    </td>
    <td width="50%">
      <h3 align="center">Language Breakdown</h3>
      <p align="center"><i>See exactly how your codebase is distributed across languages</i></p>
      <p align="center">
        <img src="https://github.com/user-attachments/assets/c32a43d2-1d00-4ea3-bec2-186efe2ea74e" width="100%"/>
      </p>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3 align="center">README Generator</h3>
      <p align="center"><i>Auto-generate professional documentation for your project</i></p>
      <p align="center">
        <img src="https://github.com/user-attachments/assets/085614d7-3b5f-42b8-8cb4-4e821937ef82" width="100%"/>
      </p>
    </td>
    <td width="50%">
      <h3 align="center">Generated Output</h3>
      <p align="center"><i>Clean, well-structured README tailored to your project</i></p>
      <p align="center">
        <img src="https://github.com/user-attachments/assets/52b7ae01-62a2-486b-89cd-af5e55d67b4d" width="100%"/>
      </p>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3 align="center">Dead Code Detection</h3>
      <p align="center"><i>Find unused functions and imports to keep your code clean</i></p>
      <p align="center">
        <img src="https://github.com/user-attachments/assets/9ba1ed63-2809-41b5-94a3-9c8e8c25a50f" width="100%"/>
      </p>
    </td>
    <td width="50%">
      <h3 align="center">Issue Breakdown</h3>
      <p align="center"><i>Get a full overview of empty files and project issues</i></p>
      <p align="center">
        <img src="https://github.com/user-attachments/assets/1ac36c69-7e68-4e93-af23-1c344b8de47a" width="100%"/>
      </p>
    </td>
  </tr>
</table>

---

## Installation

### From PyPI (Recommended)

```bash
pip install devlens-tool
```

### Using uv

```bash
uv tool install devlens-tool
```

### From Source

```bash
git clone https://github.com/YounesBensafia/DevLens.git
cd DevLens
uv tool install .
```

---

## Setup

DevLens uses [Groq](https://groq.com/) for AI-powered features. You'll need a free API key.

**1. Get your API key** from [console.groq.com](https://console.groq.com/keys)

**2. Set the environment variable:**

```bash
export GROQ_API_KEY=your_api_key_here
```

> **Tip:** Add the export line to your `~/.bashrc` or `~/.zshrc` to make it permanent.

---

## Usage

```bash
devlens --help
```

### Commands

| Command | Description |
|---|---|
| `devlens -st <PATH>` | Generate a comprehensive **project summary** — total files, lines, directories, language breakdown, and project structure |
| `devlens -an <PATH>` | **AI-powered analysis** of each file using meta-llama/llama-4-scout-17b-16e-instruct |
| `devlens -rd` | Auto-generate a professional **README.md** tailored to your project |
| `devlens -deadcode <PATH>` | Detect **unused functions** and imports across the codebase |

### Examples

```bash
# Analyze the current directory
devlens -st .

# Get AI summaries for a specific project
devlens -an /path/to/your/project

# Generate a README for the current project
devlens -rd

# Find dead code
devlens -deadcode .
```

---

## Roadmap

- [x] Project statistics and language breakdown
- [x] AI-powered file analysis
- [x] Automatic README generation
- [x] Dead code detection
- [ ] Dependency graph visualization
- [ ] Support for more languages in dead code detection

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built by [Younes Bensafia](https://github.com/YounesBensafia)**

If DevLens helps you, consider giving it a star.

</div>
