# DevLens
[![GitHub License](https://img.shields.io/github/license/your-username/DevLens)](https://github.com/your-username/DevLens/blob/main/LICENSE)
[![GitHub Release](https://img.shields.io/github/v/release/your-username/DevLens)](https://github.com/your-username/DevLens/releases)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/downloads/)
[![Codecov](https://codecov.io/gh/your-username/DevLens/graph/badge.svg?token=your-token)](https://codecov.io/gh/your-username/DevLens)

## Project Description
DevLens is a cutting-edge, open-source project analysis tool designed to provide developers with deep insights into their projects. It leverages advanced technologies, including large language models (LLMs), to analyze project structures, dependencies, and code quality. DevLens aims to streamline project maintenance, enhance code readability, and facilitate better decision-making for developers.

## Features
- **Project Analysis**: Analyzes project structures, including directories, files, and dependencies.
- **Code Quality Insights**: Identifies dead code, summarizes codebases, and provides technical stack overviews.
- **Automated README Generation**: Generates detailed README files for projects, enhancing documentation and discoverability.
- **Large Language Model Integration**: Utilizes LLMs for advanced analysis, including AI-generated summaries and insights.

## Installation
To install DevLens, ensure you have Python 3.10 or higher installed on your system. Then, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/DevLens.git
   ```
2. Navigate to the project directory:
   ```bash
   cd DevLens
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   or if you're using `pyproject.toml`:
   ```bash
   pip install .
   ```

## Usage Examples
### Analyzing a Project
To analyze a project, navigate to the project directory and run:
```bash
python main.py analyze --path /path/to/your/project
```
### Generating a README
To generate a README for your project, use:
```bash
python main.py readme --path /path/to/your/project
```

## Project Structure Overview
The DevLens project is structured as follows:
- `devlens/`: Core package containing the analysis and rendering modules.
  - `analyzer/`: Module for analyzing different aspects of a project.
  - `cli.py`: Command-line interface for interacting with DevLens.
  - `llm/`: Module for interacting with large language models.
  - `prompt/`: Prompts for LLM interactions.
  - `render/`: Module for rendering analysis results.
  - `utils/`: Utility functions for project analysis.
- `tests/`: Unit tests and integration tests for DevLens.
- `main.py`: Entry point for running DevLens from the command line.

## Technologies Used
- **Python**: Primary programming language.
- **Large Language Models (LLMs)**: For advanced analysis and insights.
- **Pytest**: For unit testing and integration testing.

## Contributing Guidelines
Contributions to DevLens are welcome! To contribute:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a detailed description of your changes.

## License
DevLens is licensed under the [MIT License](https://opensource.org/licenses/MIT). See [LICENSE](https://github.com/your-username/DevLens/blob/main/LICENSE) for details.

## Acknowledgements
Special thanks to all contributors and the open-source community for their support and contributions to DevLens.