# Scripts

Automation scripts for CI/CD pipeline, validation, and development workflows.

## CI/CD Pipeline Scripts

- **`validate_architecture.py`** - Validates Clean Architecture compliance and dependency rules
- **`validate_docs.py`** - Validates documentation examples and internal links
- **`validate_readme_examples.py`** - Tests that README code examples execute correctly
- **`profile_memory.py`** - Memory profiling for performance monitoring
- **`generate_release_notes.py`** - Automated release notes generation from git commits

## Usage

These scripts are primarily executed by the CI/CD pipeline but can be run manually:

```bash
# Architecture validation
python scripts/validate_architecture.py

# Documentation validation  
python scripts/validate_docs.py

# Memory profiling
python scripts/profile_memory.py

# Generate release notes
python scripts/generate_release_notes.py v1.0.0
```