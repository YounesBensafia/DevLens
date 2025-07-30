# DevLens

<div align="center">
  
  <img width="1396" height="366" alt="image" src="https://github.com/user-attachments/assets/d39e940a-059e-4e3a-af9e-b14e51bfd1af" />
  <img width="1396" height="366" alt="image" src="https://github.com/user-attachments/assets/49aef9f4-aa9c-46a3-93e8-e9a3d5d0bbdc" />

  **Illuminate Your Codebase with Powerful Analysis**
</div>

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

⚠️ **Note:** It's available for **Python projects only**... for now 🤫.
DevLens helps engineering teams understand complex codebases quickly and efficiently.
