import os
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/llama-4-scout-17b-16e-instruct")

TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json",
}

KEY_FILES = [
    "package.json",
    "setup.py",
    "pyproject.toml",
    "cargo.toml",
    "pom.xml",
    "build.gradle",          
    "build.gradle.kts",     
    "Makefile",              
    "CMakeLists.txt",        
    "requirements.in",       
    "composer.json",         
    "Gemfile",               
    "go.mod",                
    "go.sum",                
    "Rakefile",               
]

REQUIREMENTS_FILES = [
    "requirements.txt",
    "requirements-dev.txt",  
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",         
    "pipfile",
    "pipfile.lock",
    "poetry.lock",
    "environment.yml",       
    "composer.lock",         
    "Gemfile.lock",          
    "go.sum",                
]

CONFIG_FILES = [
    "config.py",
    "settings.py",
    ".env",
    ".env.local",
    "docker-compose.yml",
    "docker-compose.override.yml",
    "dockerfile",
    "Dockerfile",
    "Procfile",
    "app.yaml",
    "cloudbuild.yaml",
    "azure-pipelines.yml",
    ".gitlab-ci.yml",
    ".travis.yml",
    ".circleci/config.yml",
    ".github/workflows/",
    "tsconfig.json",
    "babel.config.js",
    "webpack.config.js",
    "vite.config.js",
]

MAX_TOKENS = 3000