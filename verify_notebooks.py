import os
import glob
import nbformat
import ast
import sys
import importlib

class ImportVisitor(ast.NodeVisitor):
    def __init__(self):
        self.required_imports = set()
        self.optional_imports = set()
        self.in_try = False

    def visit_Try(self, node):
        prev_in_try = self.in_try
        self.in_try = True
        # Visit body
        for child in node.body:
            self.visit(child)
        self.in_try = prev_in_try
        # Handlers/Final/Else usually inherit the context or are separate.
        # For our purpose, imports in check blocks are also "protected" usually.
        for handler in node.handlers:
            self.visit(handler)
        for child in node.finalbody:
            self.visit(child)
        for child in node.orelse:
            self.visit(child)

    def visit_Import(self, node):
        for alias in node.names:
            name = alias.name.split('.')[0]
            if self.in_try:
                self.optional_imports.add(name)
            else:
                self.required_imports.add(name)

    def visit_ImportFrom(self, node):
        if node.module:
            name = node.module.split('.')[0]
            if self.in_try:
                self.optional_imports.add(name)
            else:
                self.required_imports.add(name)

def extract_imports_robust(code):
    """Parse python code and return sets of required and optional module names."""
    visitor = ImportVisitor()
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None, None
    
    visitor.visit(tree)
    return visitor.required_imports, visitor.optional_imports

def verify_notebooks(directory):
    notebooks = sorted(glob.glob(os.path.join(directory, "*.ipynb")))
    results = []

    print(f"Verifying {len(notebooks)} notebooks in {directory} (Static Analysis + Context)")
    print("-" * 80)
    print(f"{'Notebook':<50} | {'Syntax':<8} | {'Status':<15}")
    print("-" * 80)

    for nb_path in notebooks:
        nb_name = os.path.basename(nb_path)
        
        try:
            with open(nb_path, encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)
        except Exception as e:
            print(f"{nb_name:<50} | ERROR: Read Failed")
            results.append((nb_name, "ERROR", f"Read Failed: {e}"))
            continue

        syntax_ok = True
        required_imports = set()
        optional_imports = set()
        
        for cell in nb.cells:
            if cell.cell_type == 'code':
                source = cell.source
                clean_source = "\n".join([line for line in source.splitlines() if not line.strip().startswith('%') and not line.strip().startswith('!')])
                
                if not clean_source.strip():
                    continue

                req, opt = extract_imports_robust(clean_source)
                if req is None:
                    syntax_ok = False
                else:
                    required_imports.update(req)
                    optional_imports.update(opt)

        syntax_status = "PASS" if syntax_ok else "FAIL"
        
        # Check imports
        missing_imports = []
        for module in required_imports:
            if module in ['sys', 'os', 'warnings', 'getpass', 'typing', 'json', 'time', 'datetime']: continue
            
            try:
                importlib.import_module(module)
            except ImportError:
                missing_imports.append(module)
        
        # Check optional imports (just for info, or ignore?)
        # We ignore optional imports if they fail, because they are optional/guarded.
        
        if missing_imports:
            status = "FAIL"
            details = f"Missing: {', '.join(missing_imports)}"
        else:
            status = "PASS"
            details = "OK"

        if not syntax_ok:
            status = "FAIL"
            details = "Syntax Error"

        print(f"{nb_name[:50]:<50} | {syntax_status:<8} | {details}")
        results.append((nb_name, status, details))

    # Save report
    with open("notebook_verification_report.md", "w", encoding="utf-8") as f:
        f.write("# Notebook Verification Report (Static Analysis)\n\n")
        f.write("| Notebook | Status | Details |\n")
        f.write("| :--- | :--- | :--- |\n")
        for name, status, details in results:
            f.write(f"| {name} | {status} | {details} |\n")

if __name__ == "__main__":
    current_dir = os.getcwd()
    verify_notebooks(current_dir)
