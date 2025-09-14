def generate_readme_prompt(project_context: str) -> str:
    return f"""Create a professional README.md file for this project. Based on the project analysis:
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

def project_context(git_root_name: str, git_structure: list, key_files: list, requirements_files: list, config_files: list) -> str:
    return f"""
    Project Name: {git_root_name}
    Languages: {git_structure}
    Total Files: {len(git_structure)}
    Key Files: {key_files}
    Requirements Files: {requirements_files}
    Config Files: {config_files}
    """

def system_message() -> str:
    return "You are a technical documentation expert. Create professional, well-structured README.md files with proper markdown formatting."