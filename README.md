# DevLens

<img width="100%" src="https://github.com/user-attachments/assets/1883a4eb-2892-4e9d-81cb-dc54cee2b0ea"/>

<h2 align="center">Illuminate Your Codebase with Powerful Analysis</h2>
<p align="center"><i>AI-powered insights & detailed statistics for your repository</i></p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/de411846-3a3a-410d-9061-d9b69a5920a5" width="48%" />
  <img src="https://github.com/user-attachments/assets/fd3ddc26-3517-4d2d-bae9-4429c3ed4cdb" width="48%" />
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
| `devlens deadcode PATH`   | 🧠 Detects **unused functions** across the repository to help clean up dead code.                                                                                      | ❌ Not yet    |
| `devlens graph PATH`      | 📈 Visualizes **module relationships** and project architecture through interactive graphs.                                                                            | ❌ Not yet |



## Screenshots

<table>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/8e425469-7222-4eca-b939-b6fb384315ca" alt="image" width="100%"></td>
    <td><img src="https://github.com/user-attachments/assets/6898bbc2-56e7-4594-9656-b80073a993f1" alt="image" width="100%"></td>
  </tr>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/a40e0578-ad2d-4afb-b5cb-b5c3ca11a3b5" alt="image" width="100%"></td>
    <td><img src="https://github.com/user-attachments/assets/90639b81-dde2-4dcd-ae88-8d1fcaac8282" alt="image" width="100%"></td>
  </tr>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/25b74930-b5f5-4047-a171-fdaa07fd5933" alt="image" width="100%"></td>
    <td><img src="https://github.com/user-attachments/assets/641f665f-1a97-4ff2-a959-6ba5425ca4d9" alt="image" width="100%"></td>
  </tr>
  <tr>
    <td><img alt="image" src="https://github.com/user-attachments/assets/cd1183e2-66e3-444a-8483-544e4aa4afb3" width="100%"></td>
    <td><img src="https://github.com/user-attachments/assets/2f83a7ea-8b22-45b1-a3a8-3f5413844ada" alt="image" width="100%"></td>
</td>    
  </tr>
</table>

---

````markdown
# Devlens

Devlens is a developer productivity tool that provides a CLI for project management and utilities.

---

## Installation

Clone the repository and install it with:

```bash
pip install .
````

---

## Environment Configuration

Create a `.env` file (include your Groq API key:) at the root of your project.
You can use `.env.example` as a reference.

---

## Add Devlens to PATH (Windows)

To make `devlens` accessible from anywhere in the terminal:

1. Press **Start** → search for **Environment Variables** → open **"Edit the system environment variables"**.

2. Click **Environment Variables…**.

3. Under **User variables**, select **Path** → **Edit**.

4. Click **New** and paste:

   ```
   C:\Users\<YourUser>\AppData\Roaming\Python\Python313\Scripts
   ```

5. Open a new terminal and run:

   ```bash
   devlens --help
   ```

   You should see the CLI help menu.

---

## Troubleshooting

* **`'devlens' is not recognized`**
  Ensure the `Scripts` folder is correctly added to your PATH and restart your terminal.


⚠️ **Note:** It's available for **Python projects only**... for now 🤫.
DevLens helps engineering teams understand complex codebases quickly and efficiently.
