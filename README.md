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

| Command                  | Description                                                                                                                                 |
|--------------------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| `devlens summary PATH`   | Provides an overview of the project including **total files**, **total lines**, **directory count**, **language breakdown**, and **project structure**. |
| `devlens analyse PATH`   | Uses the AI model **meta-llama/llama-4-scout-17b-16e-instruct** to summarize what each file in the given path is doing.                  |
| `devlens readme PATH`    | Generates a professional **README** for the specified project path based on its structure and contents.                                  |
| `devlens empty PATH`  | Detects and lists **empty files** and **all files** in the given path, helping identify potential dead code.                                |


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
    <td><img src="https://github.com/user-attachments/assets/6e5fa11c-3c38-4907-8170-c4977c8aaaca" alt="image" width="100%"></td>
    <td><img src="https://github.com/user-attachments/assets/2f83a7ea-8b22-45b1-a3a8-3f5413844ada" alt="image" width="100%"></td>
</td>    
  </tr>
</table>


DevLens helps engineering teams understand complex codebases quickly and efficiently.
