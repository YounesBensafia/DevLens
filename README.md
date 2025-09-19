# DevLens

<img width="100%" src="https://github.com/user-attachments/assets/1883a4eb-2892-4e9d-81cb-dc54cee2b0ea"/>

<h2 align="center">How to Use It</h2>
<p align="center"><i>Quick guide to start analyzing your codebase</i></p>

<p align="center">
  <img width="100%" src="https://github.com/user-attachments/assets/45b40043-b9a3-42b0-835e-9f26c68bb63f" />
</p>

---

<h2 align="center">Illuminate Your Codebase with Powerful Analysis</h2>
<p align="center"><i>AI-powered insights & detailed statistics for your repository</i></p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/de411846-3a3a-410d-9061-d9b69a5920a5" width="48%" />
  <img src="https://github.com/user-attachments/assets/09d04c0e-8970-4958-8573-b5c1901743ef" width="48%" />
</p>

---
<h2 align="center">Complete Codebase Insights</h2>
<p align="center"><i>Total files, lines of code, directories, language breakdown, and detailed project structure</i></p>

<p align="center">

  <img src="https://github.com/user-attachments/assets/e86c5b42-8894-4768-af8f-082604353748" width="48%" />
  <img src="https://github.com/user-attachments/assets/54aeefb3-67bb-429e-b8c0-5e7fe729d6e8" width="48%" />
</p>

---
<h2 align="center">Generate a Personalized README.md for Your Repository</h2>
<p align="center"><i>Create a custom template to your project</i></p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/3b8d85e3-ba41-4897-a8f5-7946afd1bc8e" width="100%"/>
</p>

---
<h2 align="center">Identify Unused Files & Imports with Issue Breakdown</h2>
<p align="center"><i>Detect empty files, unused imports, and get a full overview of project issues</i></p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/3ca5b282-1515-4383-a7b2-e8384f770b3b" width="48%" />
  <img src="https://github.com/user-attachments/assets/29052182-1961-428d-94eb-0c9017026d5f" width="48%" />
</p>

## Overview

DevLens delivers comprehensive insights into your codebase, helping teams understand, document, and optimize their software projects with ease.

## Key Features

- **Language Breakdown**: Visualize programming languages distribution (done)
- **Code Metrics**: Analyze lines of code and structural patterns (done)
- **Dependency Mapping**: Generate interactive graphs of module relationships (not yet)
- **AI-Powered Documentation**: Get summaries of files, functions, and classes (done)
- **Dead Code Detection**: Identify unused code to improve maintainability (done)
- **README Generator**: Create comprehensive documentation automatically (done)

## 🚀 DevLens CLI Commands

| Command                   | Description                                                                                                                                                           | Status   |
|---------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| `devlens summary PATH`    | 📊 Generates a comprehensive summary of the project, including **total files**, **total lines**, **directory count**, **language breakdown**, and **project structure**. | ✅ Done   |
| `devlens analyse PATH`    | 🤖 Uses **meta-llama/llama-4-scout-17b-16e-instruct** to analyze each file and provide a high-level summary of what it does.                                             | ✅ Done   |
| `devlens readme PATH`     | 📝 Automatically creates a professional **README.md** tailored to the project's structure and content.                                                                | ✅ Done   |
| `devlens empty PATH`      | 🧹 Scans the project and lists all **empty files** and a full **file inventory**.                                                                                      | ✅ Done   |
| `devlens deadcode PATH`   | 🧠 Detects **unused functions** across the repository to help clean up dead code.                                                                                      | ✅ Done    |
| `devlens graph PATH`      | 📈 Visualizes **module relationships** and project architecture through interactive graphs.                                                                            | ❌ Not yet |

---

## Installation

**Clone the repository:**

```bash
git clone https://github.com/YounesBensafia/DevLens.git
```

---

## Add Devlens (uv tools) to PATH

To make `devlens` accessible from anywhere in the terminal:

**1. Export the api key (set the environment variable GROQ_API_KEY with the value of the key you got from [Groq](https://groq.com/)):**

```bash
export GROQ_API_KEY=your_real_api_key_here
```

**2. Execute this command:**

```bash
uv tool install .
```

**3. After that, execute:**

```bash
devlens --help
```


## Troubleshooting

* If you have issues, please **open an issue** in the repository so we can help.

⚠️ **Note:** Currently, the **`deadecode`** option is available for **Python projects only**.

DevLens is designed to help engineering teams understand complex codebases quickly and efficiently.

---
