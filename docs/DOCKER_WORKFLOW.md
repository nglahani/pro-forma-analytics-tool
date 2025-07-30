# Docker Workflow Guide

This document explains how to use Docker for Linux compatibility validation in the pro-forma-analytics-tool project.

## Overview

Our development workflow supports:
- **Primary Development**: Windows native environment (fast iteration)
- **Linux Validation**: Docker-based testing (compatibility assurance)
- **CI/CD Pipeline**: Linux-only GitHub Actions (production alignment)

## Docker Setup

### Prerequisites
- Docker Desktop installed and running
- Git repository cloned locally

### Files Overview
- `Dockerfile.test` - Linux testing container definition
- `scripts/validate-linux.bat` - Windows validation script
- `scripts/validate-linux.sh` - Unix validation script
- `.dockerignore` - Optimized build context

## Usage

### Quick Validation (Recommended)
```bash
# Windows
scripts\validate-linux.bat

# Unix/Mac  
./scripts/validate-linux.sh
```

### Manual Docker Commands
```bash
# Build test container
docker build -f Dockerfile.test -t proforma-linux-test .

# Run interactive container (for debugging)
docker run -it --rm proforma-linux-test bash
```

## What Gets Validated

The Docker validation runs the complete Linux compatibility check:

1. **Code Quality**
   - Black code formatting
   - isort import sorting
   - flake8 linting

2. **Type Safety**
   - mypy type checking

3. **Test Suite**
   - Unit tests (95%+ coverage)
   - Integration tests
   - Performance tests

4. **Business Logic**
   - End-to-end DCF workflow validation

## Development Workflow

### Daily Development
```bash
# 1. Normal Windows development
python -m pytest tests/ -v
python demo_end_to_end_workflow.py

# 2. Code quality checks
black src/ tests/
isort src/ tests/
flake8 src/ tests/
```

### Pre-Push Validation
```bash
# 3. Validate Linux compatibility
scripts\validate-linux.bat

# 4. Push with confidence
git add .
git commit -m "Your changes"
git push origin main
```

## Troubleshooting

### Docker Build Issues

**Problem**: Build fails with dependency errors
```bash
# Solution: Clear Docker cache and rebuild
docker system prune -f
docker build --no-cache -f Dockerfile.test -t proforma-linux-test .
```

**Problem**: Out of disk space
```bash
# Solution: Clean unused Docker resources
docker system prune -a
```

### Platform-Specific Issues

**Problem**: Tests pass on Windows but fail in Docker
- Check file path separators (use `os.path.join()` or `pathlib.Path`)
- Verify environment variable handling
- Review dependency versions

**Problem**: Import errors in Docker
- Ensure `PYTHONPATH` is set correctly in container
- Check that all dependencies are in `requirements.txt`

## Best Practices

### When to Use Docker Validation
- ✅ Before pushing to main branch
- ✅ Before creating pull requests
- ✅ When adding new dependencies
- ✅ When modifying file handling code

### When NOT to Use Docker Validation
- ❌ During rapid local development cycles
- ❌ For quick unit test iterations
- ❌ When only changing documentation
- ❌ For small code formatting fixes

### Performance Tips
- **Use Docker validation selectively** - not for every small change
- **Leverage Docker layer caching** - dependencies cached between builds
- **Run in parallel with other tasks** - Docker validation while writing documentation

## CI/CD Integration

The Docker validation complements our CI/CD pipeline:

1. **Local Docker**: Pre-push validation
2. **GitHub Actions**: Post-push comprehensive testing
3. **Both run on Linux**: Consistent environment validation

This approach ensures:
- Fast local development feedback
- Early platform compatibility detection
- Confident production deployments

## Next Steps

After Docker validation passes:
1. Push changes to GitHub
2. Monitor CI/CD pipeline results
3. Proceed with RESTful API development

The combination of Windows development + Docker validation + Linux CI/CD provides the optimal balance of speed and reliability for our RESTful API development goals.