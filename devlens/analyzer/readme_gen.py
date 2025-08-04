import os
import requests
from devlens.config import GROQ_API_KEY
from devlens.analyzer.summary import count_lines_by_language, get_project_structure
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

console = Console()

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json",
}

def generate_readme(path: str):
    """Generate a comprehensive README.md file for the project"""
    
    console.print()
    header_text = Text("DevLens - README Generator", style="bold magenta")
    header_panel = Panel(
        Align.center(header_text),
        border_style="magenta",
        padding=(1, 2)
    )
    console.print(header_panel)
    console.print()
    
    console.print("🔍 Analyzing project structure...", style="blue")
    line_counts, file_counts = count_lines_by_language(path)
    structure = get_project_structure(path)
    
    project_name = os.path.basename(os.path.abspath(path))
    
    key_files = []
    requirements_files = []
    config_files = []
    
    for root, dirs, files in os.walk(path):
        for file in files:
            file_lower = file.lower()
            if file_lower in ['package.json', 'setup.py', 'pyproject.toml', 'cargo.toml', 'pom.xml']:
                key_files.append(file)
            elif file_lower in ['requirements.txt', 'package-lock.json', 'yarn.lock', 'pipfile']:
                requirements_files.append(file)
            elif file_lower in ['config.py', '.env', 'settings.py', 'docker-compose.yml', 'dockerfile']:
                config_files.append(file)
    
    project_context = f"""
    Project Name: {project_name}
    Languages Found: {', '.join(line_counts.keys())}
    Total Files: {sum(file_counts.values())}
    Total Lines: {sum(line_counts.values())}
    Key Files: {', '.join(key_files) if key_files else 'None detected'}
    Requirements Files: {', '.join(requirements_files) if requirements_files else 'None detected'}
    Config Files: {', '.join(config_files) if config_files else 'None detected'}
    """
    
    prompt = f"""Create a professional README.md file for this project. Based on the project analysis:

{project_context}

Generate a complete README.md with:
1. Project title and description
2. Features section
3. Installation instructions
4. Usage examples
5. Project structure overview
6. Technologies used
7. Contributing guidelines
8. License section

Make it professional, well-formatted with proper markdown, and include relevant badges if appropriate. The README should be comprehensive but concise."""

    payload = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [
            {
                "role": "system", 
                "content": "You are a technical documentation expert. Create professional, well-structured README.md files with proper markdown formatting."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 2048
    }
    
    try:
        console.print("🤖 Generating README content...", style="green")
        response = requests.post(GROQ_API_URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        data = response.json()
        readme_content = data["choices"][0]["message"]["content"].strip()
        
        readme_path = os.path.join(path, "README.md")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)
        
        success_panel = Panel(
            f"✅ README.md generated successfully!\n📄 Saved to: {readme_path}",
            title="🎉 Success",
            border_style="green",
            padding=(1, 2)
        )
        console.print(success_panel)
        
        preview_panel = Panel(
            readme_content[:500] + "..." if len(readme_content) > 500 else readme_content,
            title="📖 README Preview",
            border_style="cyan",
            padding=(1, 2)
        )
        console.print(preview_panel)
        
        return readme_path
        
    except Exception as e:
        error_panel = Panel(
            f"❌ Failed to generate README: {str(e)}",
            title="⚠️ Error",
            border_style="red",
            padding=(1, 2)
        )
        console.print(error_panel)
        return None