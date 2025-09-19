import questionary
from questionary import Style
from devlens.utils.has_file import has_file
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

