#!/usr/bin/env python3
"""
Architecture Validation Script

Validates Clean Architecture compliance by checking dependency rules:
- Domain layer has no external dependencies
- Application layer only depends on domain
- Infrastructure layer depends on domain abstractions
- Presentation layer depends on application and domain
"""

import ast
import os
import sys
from pathlib import Path
from typing import List, Dict, Set, Tuple


class ArchitectureValidator:
    """Validates Clean Architecture dependency rules."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.src_path = self.project_root / "src"
        self.violations = []
        
        # Define allowed dependencies for each layer
        self.dependency_rules = {
            "domain": {
                "allowed_internal": ["domain"],
                "allowed_external": ["typing", "datetime", "enum", "dataclasses", "abc"],
                "forbidden": ["src.application", "src.infrastructure", "src.presentation"]
            },
            "application": {
                "allowed_internal": ["domain", "application"],
                "allowed_external": ["typing", "datetime", "enum", "dataclasses", "abc"],
                "forbidden": ["src.infrastructure", "src.presentation"]
            },
            "infrastructure": {
                "allowed_internal": ["domain", "infrastructure"],
                "allowed_external": ["typing", "datetime", "sqlite3", "pathlib", "json"],
                "forbidden": ["src.application", "src.presentation"]
            },
            "presentation": {
                "allowed_internal": ["domain", "application", "presentation"],
                "allowed_external": ["typing", "datetime", "matplotlib", "numpy", "pandas"],
                "forbidden": []
            }
        }
    
    def validate(self) -> bool:
        """Run complete architecture validation."""
        print("[ARCH] Validating Clean Architecture compliance...")
        
        self._check_layer_dependencies()
        self._check_circular_dependencies()
        self._check_domain_purity()
        self._check_interface_segregation()
        
        if self.violations:
            print(f"\n[FAIL] Architecture validation failed with {len(self.violations)} violations:")
            for violation in self.violations:
                print(f"   - {violation}")
            return False
        else:
            print("[PASS] Architecture validation passed - Clean Architecture compliance verified")
            return True
    
    def _check_layer_dependencies(self):
        """Check that each layer only imports from allowed layers."""
        for layer in ["domain", "application", "infrastructure", "presentation"]:
            layer_path = self.src_path / layer
            if not layer_path.exists():
                continue
            
            for py_file in layer_path.rglob("*.py"):
                if py_file.name == "__init__.py":
                    continue
                
                imports = self._extract_imports(py_file)
                for import_stmt in imports:
                    if not self._is_import_allowed(layer, import_stmt):
                        self.violations.append(
                            f"{layer}/{py_file.name}: Forbidden import '{import_stmt}'"
                        )
    
    def _check_circular_dependencies(self):
        """Check for circular dependencies between modules."""
        dependency_graph = self._build_dependency_graph()
        cycles = self._find_cycles(dependency_graph)
        
        for cycle in cycles:
            self.violations.append(f"Circular dependency detected: {' -> '.join(cycle)}")
    
    def _check_domain_purity(self):
        """Ensure domain layer contains no infrastructure concerns."""
        domain_path = self.src_path / "domain"
        if not domain_path.exists():
            return
        
        forbidden_patterns = [
            "import sqlite3",
            "import requests",
            "import pandas",
            "import numpy",
            "from pathlib import Path",
            "import json"
        ]
        
        for py_file in domain_path.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
            
            content = py_file.read_text(encoding='utf-8')
            for pattern in forbidden_patterns:
                if pattern in content:
                    self.violations.append(
                        f"domain/{py_file.name}: Infrastructure concern detected - '{pattern}'"
                    )
    
    def _check_interface_segregation(self):
        """Check that interfaces are properly segregated."""
        repositories_path = self.src_path / "domain" / "repositories"
        if not repositories_path.exists():
            return
        
        for py_file in repositories_path.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
            
            tree = ast.parse(py_file.read_text(encoding='utf-8'))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                    if len(methods) > 10:  # Interface too large
                        self.violations.append(
                            f"domain/repositories/{py_file.name}: Interface '{node.name}' "
                            f"has {len(methods)} methods - consider segregation"
                        )
    
    def _extract_imports(self, file_path: Path) -> List[str]:
        """Extract all import statements from a Python file."""
        try:
            tree = ast.parse(file_path.read_text(encoding='utf-8'))
        except (SyntaxError, UnicodeDecodeError):
            return []
        
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        return imports
    
    def _is_import_allowed(self, layer: str, import_stmt: str) -> bool:
        """Check if an import is allowed for the given layer."""
        rules = self.dependency_rules.get(layer, {})
        
        # Check forbidden imports
        for forbidden in rules.get("forbidden", []):
            if import_stmt.startswith(forbidden):
                return False
        
        # Check if it's an allowed external import
        for allowed_external in rules.get("allowed_external", []):
            if import_stmt.startswith(allowed_external):
                return True
        
        # Check if it's an allowed internal import
        for allowed_internal in rules.get("allowed_internal", []):
            if import_stmt.startswith(f"src.{allowed_internal}"):
                return True
        
        # Allow relative imports within the same layer
        if not import_stmt.startswith("src."):
            return True
        
        return False
    
    def _build_dependency_graph(self) -> Dict[str, Set[str]]:
        """Build a dependency graph of all modules."""
        graph = {}
        
        for py_file in self.src_path.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
            
            module_name = str(py_file.relative_to(self.project_root)).replace(os.sep, ".").replace(".py", "")
            imports = self._extract_imports(py_file)
            
            # Filter to only internal imports
            internal_imports = {imp for imp in imports if imp.startswith("src.")}
            graph[module_name] = internal_imports
        
        return graph
    
    def _find_cycles(self, graph: Dict[str, Set[str]]) -> List[List[str]]:
        """Find circular dependencies in the dependency graph."""
        def dfs(node: str, path: List[str], visited: Set[str], rec_stack: Set[str]) -> List[List[str]]:
            visited.add(node)
            rec_stack.add(node)
            cycles = []
            
            for neighbor in graph.get(node, set()):
                if neighbor not in visited:
                    cycles.extend(dfs(neighbor, path + [neighbor], visited, rec_stack))
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])
            
            rec_stack.remove(node)
            return cycles
        
        visited = set()
        all_cycles = []
        
        for node in graph:
            if node not in visited:
                all_cycles.extend(dfs(node, [node], visited, set()))
        
        return all_cycles


def main():
    """Main function."""
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = os.getcwd()
    
    validator = ArchitectureValidator(project_root)
    success = validator.validate()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()