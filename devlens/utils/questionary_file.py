import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
import questionary
from questionary import Style
from utils.has_file import has_file
from rich.console import Console

console = Console()

custom_style = Style([
    ("qmark", "fg:#ff9d00 bold"),     
    ("question", "bold"),              
    ("answer", "fg:#00ff00 bold"),     
    ("pointer", "fg:#00ff00 bold"),    
    ("highlighted", "fg:#00ff00 bold"),
    ("selected", "fg:#00ff00"),        
])

def confirm_readme_rewrite() -> bool:
    if has_file("README.md"):
        language = questionary.select(
            "README.md already exists. are you sure you want to overwrite it?\n",
            choices=[
                "Yes",
                "No"
            ],
        style=custom_style
        ).ask()
    else:
        language = questionary.select(
            "No README.md found. Do you want to generate one?\n",
            choices=[
                "Yes",
                "No"
            ],
        style=custom_style
        ).ask()

    language = str(language).lower()
    return language == "yes"

def confirm_env() -> bool:
    env = questionary.select(
        "Its seems you don't have a .env file which is required for ai summarization. Do you want to create one?",
        choices=[
            "Yes",
            "No"
        ],
        style=custom_style
    ).ask()

    env = str(env).lower()
    
    if env == "yes" and not has_file(".env"):
        with open(".env", "w") as f:
            f.write("GROQ_API_KEY=<your_api_key_here>\n")
        console.print("Created: .env file. Please add your GROQ_API_KEY.")
        return True
    else:
        console.print("[bold cyan] Already exists: .env file.")
    return False

print(confirm_env())