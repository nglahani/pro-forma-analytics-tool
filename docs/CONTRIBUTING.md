# Contributing Guide

Guidelines for contributing to the Pro-Forma Analytics Tool.

## Project Status

**Production-Ready DCF Engine**: Complete 4-phase workflow with NPV, IRR, and investment recommendations.

## Priority Areas

**High Priority**: Performance optimization, API development, additional test coverage
**Medium Priority**: Web UI, export functionality, portfolio analysis

## Development Workflow

### Setup
```bash
# Fork and clone the repository
git clone https://github.com/your-username/pro-forma-analytics-tool.git
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
2. **Write tests first**: Follow TDD/BDD practices
3. **Implement feature**: Maintain Clean Architecture principles
4. **Run tests**: `pytest tests/ -v`
5. **Code quality**: `black src/ tests/` and `flake8 src/ tests/`
6. **Submit PR**: Include test coverage and documentation

## Architecture Standards

### Clean Architecture
- **Domain**: Business entities and rules (no external dependencies)
- **Application**: Use case orchestration and service layer
- **Infrastructure**: External concerns (databases, APIs)
- **Presentation**: User interfaces and visualization

### Code Quality
- **Test Coverage**: 95%+ target for business logic
- **Type Safety**: Comprehensive type hints
- **Documentation**: Docstrings for all public interfaces
- **Error Handling**: Consistent ValidationError usage

## Testing Requirements

### Test Types
- **Unit Tests**: `tests/unit/` - Isolated component testing
- **Integration Tests**: `tests/integration/` - End-to-end workflow validation
- **Performance Tests**: `tests/performance/` - Load and performance validation

### Test Standards
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=src --cov-report=html

# Performance validation
python tests/performance/test_irr_performance.py
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
- **Black** for code formatting
- **flake8** for linting
- **mypy** for type checking
- **isort** for import organization

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

## Getting Help

### Resources
- **Architecture Guide**: Read `CLAUDE.md` for technical context
- **User Guide**: `docs/USER_GUIDE.md` for usage patterns
- **Test Examples**: `tests/integration/` for implementation patterns
- **Demo Code**: `demo_end_to_end_workflow.py` for complete workflow

### Support Channels
1. **GitHub Issues**: Bug reports and feature requests
2. **Discussions**: Architecture questions and design discussions
3. **Documentation**: Check existing docs before asking questions

## Review Process

### Pull Request Requirements
- **Descriptive Title**: Summarize the change clearly
- **Detailed Description**: Explain what, why, and how
- **Test Coverage**: Include appropriate tests
- **Documentation**: Update relevant documentation
- **Code Quality**: Pass all quality checks

### Review Criteria
- **Architecture Compliance**: Follows Clean Architecture principles
- **Test Quality**: Comprehensive and meaningful tests
- **Code Clarity**: Readable and maintainable implementation
- **Performance**: No significant performance regression
- **Documentation**: Adequate documentation for changes

## Release Process

### Version Management
- **Semantic Versioning**: MAJOR.MINOR.PATCH format
- **Feature Branches**: For new functionality
- **Hotfix Branches**: For critical bug fixes
- **Release Branches**: For version preparation

### Quality Gates
- All tests passing
- Code coverage maintained
- Performance benchmarks met
- Documentation updated
- Architecture review completed