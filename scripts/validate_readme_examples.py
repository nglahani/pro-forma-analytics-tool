#!/usr/bin/env python3
"""
README Examples Validation Script

Specifically validates that README.md code examples execute correctly.
"""

import os
import re
import sys
import subprocess
import tempfile
from pathlib import Path


def extract_readme_examples(readme_path: Path) -> list:
    """Extract Python code examples from README.md."""
    if not readme_path.exists():
        return []
    
    content = readme_path.read_text(encoding='utf-8')
    
    # Find Python code blocks
    code_blocks = re.findall(r'```python\n(.*?)\n```', content, re.DOTALL)
    
    # Filter for complete examples (have imports and meaningful code)
    complete_examples = []
    for block in code_blocks:
        if ('import' in block or 'from' in block) and 'print(' in block:
            complete_examples.append(block)
    
    return complete_examples


def test_code_example(code: str, project_root: Path) -> tuple:
    """Test a single code example."""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            # Add project root to Python path
            f.write(f"import sys\n")
            f.write(f"sys.path.insert(0, '{project_root}')\n")
            f.write(f"import os\n")
            f.write(f"os.chdir('{project_root}')\n\n")
            
            # Write the example code
            f.write(code)
            f.flush()
            
            # Execute the code
            result = subprocess.run(
                [sys.executable, f.name],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=project_root
            )
            
            os.unlink(f.name)
            
            success = result.returncode == 0
            output = result.stdout if success else result.stderr
            
            return success, output.strip()
    
    except subprocess.TimeoutExpired:
        return False, "Example execution timed out (60s limit)"
    except Exception as e:
        return False, f"Execution error: {str(e)}"


def main():
    """Main function."""
    project_root = Path(os.getcwd())
    readme_path = project_root / "README.md"
    
    print("[README] Validating README.md code examples...")
    
    examples = extract_readme_examples(readme_path)
    if not examples:
        print("No complete code examples found in README.md")
        return
    
    print(f"Found {len(examples)} code examples to validate")
    
    failures = []
    
    for i, example in enumerate(examples, 1):
        print(f"Testing example {i}...")
        success, output = test_code_example(example, project_root)
        
        if success:
            print(f"  [PASS] Example {i} passed")
        else:
            print(f"  [FAIL] Example {i} failed: {output}")
            failures.append((i, output))
    
    if failures:
        print(f"\n[FAIL] {len(failures)} examples failed:")
        for example_num, error in failures:
            print(f"  Example {example_num}: {error}")
        sys.exit(1)
    else:
        print("\n[PASS] All README examples validated successfully")
        sys.exit(0)


if __name__ == "__main__":
    main()