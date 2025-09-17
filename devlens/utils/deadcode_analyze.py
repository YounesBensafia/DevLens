import ast

def analyze_imports(issues, tree, has_functions, has_classes, has_imports):
    if has_imports and not has_functions and not has_classes:
        non_import_code = []
        for node in tree.body:
            if not isinstance(node, (ast.Import, ast.ImportFrom)):
                non_import_code.append(node)
        if not non_import_code:
            issues.append(("imports_only", "File contains only imports"))

def read_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    return content

def check_code_structure(content, tree):
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
    return has_functions,has_classes,has_imports,unused_imports

def extract_code_lines(content):
    lines = content.split('\n')
    code_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('#'):
            code_lines.append(stripped)
    return code_lines

def analyze_python_file(file_path: str):
    """Analyze a Python file for dead code patterns"""
    issues = []
    try:
        content = read_file_content(file_path)
        
        if not content.strip():
            issues.append(("empty", "File is completely empty"))
            return issues
        
        code_lines = extract_code_lines(content)
        
        if not code_lines:
            issues.append(("comments_only", "File contains only comments"))
            return issues
    
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            issues.append(("syntax_error", f"Syntax error: {str(e)}"))
            return issues
        
        has_functions, has_classes, has_imports, unused_imports = check_code_structure(content, tree)
        
        if unused_imports:
            issues.append(("unused_imports", f"Potentially unused imports: {', '.join(unused_imports)}"))
        

        analyze_imports(issues, tree, has_functions, has_classes, has_imports)
    
    except Exception as e:
        issues.append(("read_error", f"Error reading file: {str(e)}"))
    
    return issues



