# Contributing Guide

Guidelines for contributing to the Pro-Forma Analytics Tool v1.3.

## Project Status

**Version**: 1.3 Production Ready
**Quality**: A+ (97/100) with enhanced code quality metrics
**Architecture**: Clean Architecture with domain-driven design
**Testing**: 96%+ coverage with 320+ test methods across comprehensive BDD/TDD framework
**CI/CD**: GitHub Actions pipeline with multi-Python version support (3.8-3.13)
**Data**: Production-grade validation with 2,174+ historical data points

**Core Achievement**: Complete 4-phase DCF workflow with NPV, IRR, and investment recommendations backed by rigorous automated quality gates.

## Priority Areas

**High Priority**: RESTful API development, web-based dashboard, advanced portfolio analysis
**Medium Priority**: Real-time data integration, enhanced reporting, multi-property optimization
**Low Priority**: Mobile applications, third-party integrations, advanced visualizations

## Development Workflow

### Setup
```bash
# Fork and clone the repository
git clone https://github.com/nglahani/pro-forma-analytics-tool.git
cd pro-forma-analytics-tool

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python demo_end_to_end_workflow.py
```

### Development Process
1. **Create feature branch**: `git checkout -b feature/your-feature`
2. **Write tests first**: Follow TDD/BDD practices with comprehensive edge case coverage
3. **Implement feature**: Maintain Clean Architecture principles with domain-driven design
4. **Run quality checks**: All CI/CD pipeline checks must pass locally
5. **Validate workflow**: `python demo_end_to_end_workflow.py` must succeed
6. **Submit PR**: Include test coverage, documentation updates, and performance validation

### Local Quality Validation
```bash
# Comprehensive test suite
pytest tests/ -v --cov=src --cov=core --cov=monte_carlo --cov-fail-under=96

# Code quality checks
black --check --diff src/ tests/
isort --check-only --diff src/ tests/
flake8 src/ tests/
mypy src/ --ignore-missing-imports

# Architecture validation
python scripts/validate_architecture.py

# Documentation validation
python scripts/validate_docs.py

# End-to-end workflow validation
python demo_end_to_end_workflow.py
```

## Architecture Standards

### Clean Architecture
- **Domain**: Business entities and rules (no external dependencies)
- **Application**: Use case orchestration and service layer
- **Infrastructure**: External concerns (databases, APIs)
- **Presentation**: User interfaces and visualization

### Code Quality
- **Test Coverage**: 96%+ enforced with 320+ test methods including comprehensive edge cases
- **Type Safety**: Full type hints with mypy validation across all modules
- **Documentation**: Google-style docstrings for all public interfaces with examples
- **Error Handling**: Consistent ValidationError usage with detailed error messages
- **Performance**: IRR calculations under 0.01ms, full DCF analysis sub-second
- **Security**: Automated vulnerability scanning with safety and bandit tools

## Testing Requirements

### Test Types
- **Unit Tests**: `tests/unit/` - Isolated component testing
- **Integration Tests**: `tests/integration/` - End-to-end workflow validation
- **Performance Tests**: `tests/performance/` - Load and performance validation

### Test Standards
```bash
# Run all tests with coverage enforcement
pytest tests/ -v --cov=src --cov=core --cov=monte_carlo --cov-fail-under=96

# Run specific test suites
pytest tests/unit/ -v          # 240+ unit tests
pytest tests/integration/ -v   # 50+ integration tests  
pytest tests/performance/ -v   # 30+ performance tests

# Generate comprehensive coverage report
pytest --cov=src --cov=core --cov=monte_carlo --cov-report=html --cov-report=term-missing

# Performance benchmarking
python tests/performance/test_irr_performance.py
python scripts/profile_memory.py
```

## Contribution Types

### Bug Fixes
1. Create issue describing the bug
2. Write failing test that reproduces the issue
3. Implement fix that makes test pass
4. Ensure no regression in existing tests

### New Features
1. Discuss feature in GitHub issue
2. Create design document for complex features
3. Implement following Clean Architecture
4. Add comprehensive test coverage
5. Update documentation

### Performance Improvements
1. Profile current implementation
2. Implement optimization
3. Add performance benchmarks
4. Validate no functional regression

## Code Style

### Python Standards
- **Black** for code formatting with line length 88
- **flake8** for linting with custom configuration
- **mypy** for type checking with strict mode
- **isort** for import organization with black compatibility
- **pylint** for additional code quality checks
- **radon** for complexity analysis
- **vulture** for dead code detection

### Naming Conventions
- **Classes**: PascalCase (e.g., `DCFAssumptionsService`)
- **Functions/Variables**: snake_case (e.g., `calculate_npv`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_DISCOUNT_RATE`)

## Documentation

### Required Documentation
- **Docstrings**: All public classes and methods
- **Type Hints**: All function signatures
- **README Updates**: For new features or workflow changes
- **API Documentation**: For new service methods

### Documentation Standards
- Use clear, concise language
- Include code examples
- Reference specific files and line numbers
- Follow existing documentation patterns

## CI/CD Pipeline Integration

### GitHub Actions Workflows

The project uses automated CI/CD with three main workflows:

#### 1. CI Pipeline (`.github/workflows/ci.yml`)
- **Multi-Python Testing**: Python 3.8, 3.9, 3.10, 3.11, 3.13
- **Code Quality**: Black, isort, flake8, mypy validation
- **Test Execution**: Unit, integration, and performance tests
- **Coverage Enforcement**: 96%+ threshold with detailed reporting
- **End-to-End Validation**: Complete DCF workflow verification

#### 2. Quality Assurance (`.github/workflows/quality.yml`) 
- **Advanced Linting**: pylint, radon complexity analysis
- **Security Scanning**: safety, bandit, pip-audit
- **Dependency Auditing**: Vulnerability and outdated package detection
- **Documentation Quality**: pydocstyle, link validation
- **Performance Monitoring**: Benchmark regression detection

#### 3. Release Pipeline (`.github/workflows/release.yml`)
- **Automated Versioning**: Semantic version tagging
- **Package Building**: Python wheel and source distribution
- **Release Notes**: Auto-generated from commit history
- **Artifact Storage**: Build artifacts and performance reports

### Quality Gates

All contributions must pass:
- ✅ **Multi-Python Compatibility**: Python 3.8-3.13
- ✅ **Test Coverage**: 96%+ with comprehensive edge cases
- ✅ **Architecture Compliance**: Clean Architecture validation
- ✅ **Security Checks**: No vulnerabilities or code smells
- ✅ **Performance Standards**: No regression in IRR calculations
- ✅ **Documentation Accuracy**: All examples execute correctly

### Automated Quality Enforcement

**Pre-commit Hooks** (`.pre-commit-config.yaml`):
- Code formatting (black, isort)
- Linting (flake8, mypy)
- Security scanning (bandit)
- Documentation validation

**CI/CD Quality Gates**:
- **Test Coverage**: Automatic failure if below 96%
- **Architecture Validation**: Clean Architecture compliance checking
- **Security Scanning**: Zero-tolerance for known vulnerabilities
- **Performance Regression**: IRR calculation speed monitoring
- **Documentation Accuracy**: All code examples must execute
- **Dependency Health**: Outdated and vulnerable package detection

**Local Development Requirements**:
```bash
# Install pre-commit hooks
pre-commit install

# Run all quality checks before commit
pre-commit run --all-files

# Validate full development workflow
python scripts/validate_architecture.py
python scripts/validate_docs.py
python demo_end_to_end_workflow.py
```

## Development Resources

### Technical Documentation
- **Architecture Guide**: `CLAUDE.md` - Complete technical specification and development standards
- **User Guide**: `docs/USER_GUIDE.md` - Comprehensive usage patterns and workflow examples
- **DCF Implementation**: `docs/DCF_IMPLEMENTATION.md` - Complete DCF engine architecture and design
- **Database Guide**: `docs/DATABASE.md` - Production-grade data implementation and schemas
- **Test Examples**: `tests/integration/` - 50+ integration test patterns and implementations
- **Demo Code**: `demo_end_to_end_workflow.py` - Complete workflow with realistic property analysis

### Development Tools
- **Validation Scripts**: `scripts/validate_*.py` - Architecture, documentation, and code validation
- **Performance Tools**: `scripts/profile_*.py` - Memory and performance profiling utilities
- **Quality Tools**: GitHub Actions workflows for comprehensive quality assurance
- **Database Tools**: `scripts/optimize_database_*.py` - Database performance optimization

### Development Workflow Support
1. **GitHub Issues**: Bug reports, feature requests, and technical discussions
2. **Pull Request Reviews**: Code review, architecture guidance, and implementation feedback
3. **CI/CD Pipeline**: Automated quality feedback and comprehensive validation
4. **Documentation**: Extensive technical documentation with working examples
5. **Test Suite**: 320+ tests demonstrating proper implementation patterns

## Review Process

### Pull Request Requirements
- **Descriptive Title**: Summarize the change clearly with scope
- **Detailed Description**: Explain what, why, and how with technical context
- **Test Coverage**: Include unit, integration, and performance tests
- **Documentation**: Update relevant documentation with examples
- **Quality Compliance**: Pass all CI/CD pipeline checks
- **Architecture Review**: Maintain Clean Architecture principles
- **Performance Impact**: Document any performance implications

### Review Criteria
- **Architecture Compliance**: Follows Clean Architecture principles with domain-driven design
- **Test Quality**: Comprehensive edge case coverage with meaningful assertions
- **Code Clarity**: Readable, maintainable implementation with clear abstractions
- **Performance**: No regression in DCF calculation speed or memory usage
- **Documentation**: Accurate documentation with working code examples
- **Security**: No introduction of vulnerabilities or security anti-patterns

## Release Process

### Version Management
- **Semantic Versioning**: MAJOR.MINOR.PATCH format
- **Feature Branches**: For new functionality
- **Hotfix Branches**: For critical bug fixes
- **Release Branches**: For version preparation

### Automated Release Pipeline

**Release Triggers**:
```bash
# Create and push version tag
git tag v1.3.1
git push origin v1.3.1
```

**Automated Steps**:
1. **Quality Validation**: Full CI/CD pipeline execution
2. **Multi-Python Testing**: Compatibility across Python 3.8-3.13
3. **Package Building**: Python wheel and source distribution creation
4. **Security Scanning**: Final vulnerability assessment
5. **Performance Validation**: Regression testing and benchmarking
6. **Documentation Generation**: Auto-generated release notes
7. **Artifact Publishing**: GitHub releases with build artifacts

### Release Quality Standards
- ✅ **Zero Test Failures**: 320+ tests passing across all Python versions
- ✅ **Coverage Maintenance**: 96%+ test coverage preserved
- ✅ **Performance Compliance**: No regression in DCF calculation speed
- ✅ **Security Clearance**: No known vulnerabilities in dependencies
- ✅ **Architecture Integrity**: Clean Architecture compliance validated
- ✅ **Documentation Accuracy**: All examples and workflows verified

### Post-Release Validation
```bash
# Validate release package
pip install pro-forma-analytics-tool==1.3.1
python -c "from demo_end_to_end_workflow import main; main()"

# Performance regression check
python tests/performance/test_irr_performance.py
```