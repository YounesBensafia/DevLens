import os
import ast
import fnmatch
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

console = Console()

def load_gitignore_patterns(path: str):
    """Load patterns from .gitignore file"""
    gitignore_path = os.path.join(path, '.gitignore')
    patterns = []
    
    default_patterns = ['__pycache__/', '*.pyc', '*.pyo', '*.pyd', '.Python', 'build/', 'develop-eggs/', 'dist/', 'downloads/', 'eggs/', '.eggs/', 'lib/',
        'lib64/', 'parts/', 'sdist/', 'var/', 'wheels/', '*.egg-info/', '.installed.cfg', '*.egg', 'venv/', 'env/', 'ENV/', '.venv/', '.env', '.idea/', '.vscode/',
        '*.swp', '*.swo', '.DS_Store', 'Thumbs.db', 'node_modules/', '.git/', '.pytest_cache/', '.coverage', '.tox/', 'htmlcov/', '*.log', 'temp/', 'tmp/',
        'cache/', 'output/'
    ]
    
    patterns.extend(default_patterns)
    
    if os.path.exists(gitignore_path):
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(line)
        except Exception:
            pass
    
    return patterns

def should_ignore_path(file_path: str, base_path: str, patterns: list):
    """Check if a file path should be ignored based on gitignore patterns"""
    relative_path = os.path.relpath(file_path, base_path)
    
    relative_path = relative_path.replace('\\', '/')
    
    for pattern in patterns:
        if not pattern.strip():
            continue
            
        if pattern.endswith('/'):
            path_parts = relative_path.split('/')
            for i in range(len(path_parts)):
                partial_path = '/'.join(path_parts[:i+1]) + '/'
                if fnmatch.fnmatch(partial_path, pattern):
                    return True
        else:
            if fnmatch.fnmatch(relative_path, pattern):
                return True
            filename = os.path.basename(relative_path)
            if fnmatch.fnmatch(filename, pattern):
                return True
    
    return False

def analyze_python_file(file_path: str):
    """Analyze a Python file for dead code patterns"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        if not content.strip():
            issues.append(("empty", "File is completely empty"))
            return issues
        
        lines = content.split('\n')
        code_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                code_lines.append(stripped)
        
        if not code_lines:
            issues.append(("comments_only", "File contains only comments"))
            return issues
        
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            issues.append(("syntax_error", f"Syntax error: {str(e)}"))
            return issues
        
        has_functions = False
        has_classes = False
        has_imports = False
        unused_imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                has_functions = True
            elif isinstance(node, ast.ClassDef):
                has_classes = True
            elif isinstance(node, ast.Import):
                has_imports = True
                for alias in node.names:
                    import_name = alias.name
                    if content.count(import_name) == 1:
                        unused_imports.append(import_name)
            elif isinstance(node, ast.ImportFrom):
                has_imports = True
                for alias in node.names:
                    import_name = alias.name
                    if import_name != '*' and content.count(import_name) == 1:
                        unused_imports.append(import_name)
        
        if unused_imports:
            issues.append(("unused_imports", f"Potentially unused imports: {', '.join(unused_imports)}"))
        
        if has_imports and not has_functions and not has_classes:
            non_import_code = []
            for node in tree.body:
                if not isinstance(node, (ast.Import, ast.ImportFrom)):
                    non_import_code.append(node)
            
            if not non_import_code:
                issues.append(("imports_only", "File contains only imports"))
    
    except Exception as e:
        issues.append(("read_error", f"Error reading file: {str(e)}"))
    
    return issues

def find_dead_files(path: str):
    """Enhanced dead code analysis with comprehensive detection and gitignore support"""
    
    console.print()
    header_text = Text("DevLens - Dead Code Analyzer", style="bold red")
    header_panel = Panel(
        Align.center(header_text),
        border_style="red",
        padding=(1, 2)
    )
    console.print(header_panel)
    console.print()
    
    ignore_patterns = load_gitignore_patterns(path)
    console.print(f"📋 Loaded {len(ignore_patterns)} ignore patterns (including defaults)", style="dim")
    
    python_files = []
    ignored_files = 0
    
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if not should_ignore_path(os.path.join(root, d), path, ignore_patterns)]
        
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                if not should_ignore_path(file_path, path, ignore_patterns):
                    python_files.append(file_path)
                else:
                    ignored_files += 1
    
    if not python_files:
        error_panel = Panel(
            f"❌ No Python files found in the specified path.\n📋 Ignored {ignored_files} files based on patterns.",
            title="⚠️  Warning",
            border_style="yellow",
            padding=(1, 2)
        )
        console.print(error_panel)
        return
    
    info_table = Table(show_header=False, box=None, padding=(0, 1))
    info_table.add_row("📂 Scan Path:", f"[cyan]{path}[/cyan]")
    info_table.add_row("📄 Python Files Found:", f"[green]{len(python_files)}[/green]")
    info_table.add_row("🚫 Files Ignored:", f"[yellow]{ignored_files}[/yellow]")
    info_table.add_row("🔍 Analysis Type:", "[blue]Dead Code Detection[/blue]")
    
    info_panel = Panel(
        info_table,
        title="📊 Scan Information",
        border_style="blue",
        padding=(1, 2)
    )
    console.print(info_panel)
    console.print()
    
    dead_files = {}
    total_issues = 0
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
        expand=True
    ) as progress:
        task = progress.add_task("🔍 Analyzing files...", total=len(python_files))
        
        for file_path in python_files:
            file_name = os.path.basename(file_path)
            relative_path = os.path.relpath(file_path, path)
            progress.update(task, description=f"🔍 Checking: {file_name}")
            
            issues = analyze_python_file(file_path)
            if issues:
                dead_files[relative_path] = issues
                total_issues += len(issues)
            
            progress.advance(task)
    
    console.print()
    
    if not dead_files:
        success_panel = Panel(
            "✅ No dead code detected! All Python files appear to be in use.",
            title="🎉 Clean Code",
            border_style="green",
            padding=(1, 2)
        )
        console.print(success_panel)
    else:
        results_table = Table(title="🔍 Dead Code Analysis Results", show_header=True, header_style="bold red")
        results_table.add_column("File", style="cyan", min_width=30)
        results_table.add_column("Issue Type", style="yellow", min_width=15)
        results_table.add_column("Description", style="white", min_width=40)
        
        for file_path, issues in dead_files.items():
            for issue_type, description in issues:
                emoji_map = {
                    "empty": "🗑️",
                    "comments_only": "💬",
                    "imports_only": "📦",
                    "unused_imports": "🚫",
                    "syntax_error": "❌",
                    "read_error": "⚠️"
                }
                emoji = emoji_map.get(issue_type, "🔍")
                
                results_table.add_row(
                    f"{emoji} {file_path}",
                    issue_type.replace("_", " ").title(),
                    description
                )
        
        console.print(results_table)
        console.print()
        
        summary_table = Table(show_header=False, box=None, padding=(0, 1))
        summary_table.add_row("📊 Total Files Scanned:", f"[blue]{len(python_files)}[/blue]")
        summary_table.add_row("🔍 Files with Issues:", f"[yellow]{len(dead_files)}[/yellow]")
        summary_table.add_row("⚠️  Total Issues Found:", f"[red]{total_issues}[/red]")
        summary_table.add_row("✅ Clean Files:", f"[green]{len(python_files) - len(dead_files)}[/green]")
        
        issue_counts = {}
        for issues in dead_files.values():
            for issue_type, _ in issues:
                issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        console.print()
        summary_panel = Panel(
            summary_table,
            title="📈 Analysis Summary",
            border_style="magenta",
            padding=(1, 2)
        )
        console.print(summary_panel)
        
        if issue_counts:
            console.print()
            breakdown_table = Table(title="📋 Issue Breakdown", show_header=True, header_style="bold cyan")
            breakdown_table.add_column("Issue Type", style="yellow")
            breakdown_table.add_column("Count", style="red", justify="right")
            breakdown_table.add_column("Description", style="white")
            
            descriptions = {
                "empty": "Completely empty files",
                "comments_only": "Files with only comments",
                "imports_only": "Files with only imports",
                "unused_imports": "Potentially unused imports",
                "syntax_error": "Files with syntax errors",
                "read_error": "Files that couldn't be read"
            }
            
            for issue_type, count in sorted(issue_counts.items()):
                breakdown_table.add_row(
                    issue_type.replace("_", " ").title(),
                    str(count),
                    descriptions.get(issue_type, "Unknown issue")
                )
            
            console.print(breakdown_table)
    
    console.print()
    console.print("[bold green]✅ Dead code analysis complete![/bold green]")
