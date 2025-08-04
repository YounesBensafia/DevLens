"""
DevLens - AI-Powered Code Analysis Tool

A comprehensive code analysis suite that provides:
- AI-powered code summaries using advanced language models
- Project statistics and insights with beautiful visualizations
- Automatic README generation for documentation
- Voice summaries for audio-based code reviews
- Dead code detection to clean up your codebase

Author: Younes Bensafia
Version: 1.0.0
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Younes Bensafia"
__email__ = "younes.bensafia@example.com"
__description__ = "AI-Powered Code Analysis Tool"
__url__ = "https://github.com/YounesBensafia/DevLens"

from devlens.cli import main

from devlens.analyzer.ai_summary import summarize_code
from devlens.analyzer.summary import display_code_summary, count_lines_by_language
from devlens.analyzer.deadcode import find_dead_files
from devlens.analyzer.readme_gen import generate_readme

__all__ = [
    "main",
    "summarize_code",
    "display_code_summary", 
    "count_lines_by_language",
    "find_dead_files",
    "generate_readme",
    "__version__",
    "__author__",
    "__description__"
]

PACKAGE_INFO = {
    "name": "devlens",
    "version": __version__,
    "author": __author__,
    "description": __description__,
    "url": __url__,
    "supported_languages": [
        "Python", "JavaScript", "TypeScript", "Java", 
        "C++", "C", "HTML", "CSS", "JSON", "Markdown"
    ],
    "features": [
        "AI Code Analysis",
        "Project Statistics", 
        "README Generation",
        "Voice Summaries",
        "Dead Code Detection"
    ]
}

def get_version():
    """Get the current version of DevLens."""
    return __version__

def get_info():
    """Get package information."""
    return PACKAGE_INFO
