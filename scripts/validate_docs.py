#!/usr/bin/env python3
"""
Documentation Validation Script

Validates that documentation examples work correctly and links are valid.
"""

import os
import re
import sys
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Tuple


class DocumentationValidator:
    """Validates documentation for accuracy and completeness."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.violations = []
    
    def validate(self) -> bool:
        """Run complete documentation validation."""
        print("[DOCS] Validating documentation...")
        
        self._validate_readme_examples()
        self._validate_user_guide_examples()
        self._validate_internal_links()
        self._validate_code_references()
        
        if self.violations:
            print(f"\n[FAIL] Documentation validation failed with {len(self.violations)} issues:")
            for violation in self.violations:
                print(f"   - {violation}")
            return False
        else:
            print("[PASS] Documentation validation passed")
            return True
    
    def _validate_readme_examples(self):
        """Validate code examples in README.md."""
        readme_path = self.project_root / "README.md"
        if not readme_path.exists():
            self.violations.append("README.md file not found")
            return
        
        content = readme_path.read_text(encoding='utf-8')
        
        # Extract Python code blocks
        code_blocks = re.findall(r'```python\n(.*?)\n```', content, re.DOTALL)
        
        for i, code_block in enumerate(code_blocks):
            if self._is_runnable_example(code_block):
                success, error = self._test_code_block(code_block)
                if not success:
                    self.violations.append(f"README.md code block {i+1} failed: {error}")
    
    def _validate_user_guide_examples(self):
        """Validate code examples in user guide."""
        user_guide_path = self.project_root / "docs" / "USER_GUIDE.md"
        if not user_guide_path.exists():
            return
        
        content = user_guide_path.read_text(encoding='utf-8')
        code_blocks = re.findall(r'```python\n(.*?)\n```', content, re.DOTALL)
        
        for i, code_block in enumerate(code_blocks):
            if self._is_runnable_example(code_block):
                success, error = self._test_code_block(code_block)
                if not success:
                    self.violations.append(f"USER_GUIDE.md code block {i+1} failed: {error}")
    
    def _validate_internal_links(self):
        """Validate internal links in documentation."""
        doc_files = list(self.project_root.glob("*.md")) + list((self.project_root / "docs").glob("*.md"))
        
        for doc_file in doc_files:
            content = doc_file.read_text(encoding='utf-8')
            
            # Find markdown links [text](link)
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
            
            for link_text, link_url in links:
                if self._is_internal_link(link_url):
                    if not self._link_exists(link_url, doc_file):
                        self.violations.append(f"{doc_file.name}: Broken link '{link_url}'")
    
    def _validate_code_references(self):
        """Validate that code references in documentation are accurate."""
        doc_files = list(self.project_root.glob("*.md")) + list((self.project_root / "docs").glob("*.md"))
        
        for doc_file in doc_files:
            content = doc_file.read_text(encoding='utf-8')
            
            # Find file references like `src/domain/entities/property_data.py`
            file_refs = re.findall(r'`([^`]+\.py)`', content)
            
            for file_ref in file_refs:
                if "/" in file_ref:  # It's a file path
                    file_path = self.project_root / file_ref
                    if not file_path.exists():
                        self.violations.append(f"{doc_file.name}: Referenced file '{file_ref}' does not exist")
            
            # Find class/function references
            class_refs = re.findall(r'`([A-Z][a-zA-Z]*Service|[A-Z][a-zA-Z]*)`', content)
            for class_ref in class_refs:
                if not self._class_exists(class_ref):
                    self.violations.append(f"{doc_file.name}: Referenced class '{class_ref}' may not exist")
    
    def _is_runnable_example(self, code_block: str) -> bool:
        """Check if a code block is meant to be runnable."""
        # Skip examples that are clearly just snippets
        skip_patterns = [
            "# ...",
            "# ... additional parameters",
            "# Expected output:",
            "print(f\"",
            "assert ",
        ]
        
        for pattern in skip_patterns:
            if pattern in code_block:
                return False
        
        # Must have imports to be runnable
        return "import" in code_block or "from" in code_block
    
    def _test_code_block(self, code_block: str) -> Tuple[bool, str]:
        """Test if a code block executes without errors."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                # Add project root to path
                f.write(f"import sys\nsys.path.insert(0, '{self.project_root}')\n")
                f.write(code_block)
                f.flush()
                
                # Run the code
                result = subprocess.run(
                    [sys.executable, f.name],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.project_root
                )
                
                os.unlink(f.name)
                
                if result.returncode != 0:
                    return False, result.stderr.strip()
                
                return True, ""
        
        except subprocess.TimeoutExpired:
            return False, "Code execution timed out"
        except Exception as e:
            return False, str(e)
    
    def _is_internal_link(self, url: str) -> bool:
        """Check if a link is internal to the project."""
        return not url.startswith(("http://", "https://", "mailto:"))
    
    def _link_exists(self, url: str, current_file: Path) -> bool:
        """Check if an internal link exists."""
        if url.startswith("#"):
            # Anchor link - would need to parse headers
            return True
        
        # Relative file link
        if url.startswith("./"):
            url = url[2:]
        
        # Resolve relative to current file
        target_path = current_file.parent / url
        
        return target_path.exists()
    
    def _class_exists(self, class_name: str) -> bool:
        """Check if a class exists in the codebase."""
        # Simple check - look for class definitions
        for py_file in self.project_root.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                if f"class {class_name}" in content:
                    return True
            except UnicodeDecodeError:
                continue
        
        return False


def main():
    """Main function."""
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = os.getcwd()
    
    validator = DocumentationValidator(project_root)
    success = validator.validate()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()