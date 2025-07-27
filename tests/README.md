# Tests

Comprehensive test suite following TDD/BDD practices with 95%+ coverage targets.

## Structure

- **`unit/`** - Isolated unit tests for individual components
- **`integration/`** - End-to-end workflow testing 
- **`performance/`** - Performance and load testing
- **`conftest.py`** - Shared test fixtures and configuration

## Running Tests

```bash
# All tests
pytest

# Specific test types  
pytest tests/unit/
pytest tests/integration/

# With coverage
pytest --cov=src --cov-report=html
```