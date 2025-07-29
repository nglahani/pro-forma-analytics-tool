# Scripts - v1.3

Comprehensive automation scripts for GitHub Actions CI/CD pipeline, validation frameworks, and development workflows supporting production-grade real estate DCF analysis with multi-Python version compatibility and extensive quality assurance.

## CI/CD Pipeline Integration (v1.3)

### GitHub Actions Automation
- **Multi-Python Version Support**: Automated testing across Python 3.8-3.11
- **Quality Gate Enforcement**: Comprehensive linting, type checking, and architecture validation
- **Performance Regression Detection**: Automated performance threshold monitoring
- **Documentation Validation**: Ensure code examples and documentation accuracy
- **Release Automation**: Automated release notes and version management

## Core Validation Scripts

### Architecture and Code Quality

#### `validate_architecture.py`
**Purpose**: Validates Clean Architecture compliance and dependency rules
```bash
# Full architecture validation
python scripts/validate_architecture.py --strict

# Check specific layer dependencies
python scripts/validate_architecture.py --layer domain --check-dependencies

# Generate architecture compliance report
python scripts/validate_architecture.py --report architecture_compliance.html
```

**Validation Checks**:
- **Dependency Direction**: Ensures proper dependency flow (presentation → application → domain)
- **Layer Isolation**: Validates that domain layer has no external dependencies
- **Interface Compliance**: Checks that infrastructure implements domain abstractions
- **Import Analysis**: Detects forbidden imports between architectural layers
- **Service Registration**: Validates dependency injection container configuration

#### `validate_docs.py`
**Purpose**: Validates documentation accuracy, internal links, and code examples
```bash
# Comprehensive documentation validation
python scripts/validate_docs.py --comprehensive

# Check internal links only
python scripts/validate_docs.py --links-only

# Validate specific documentation file
python scripts/validate_docs.py --file docs/README.md
```

**Validation Features**:
- **Link Validation**: Verify all internal and external links are accessible
- **Code Example Testing**: Execute all code examples to ensure they work correctly
- **Documentation Consistency**: Check consistency between README files and codebase
- **API Documentation**: Validate API documentation matches actual implementation
- **Version Consistency**: Ensure version references are consistent across all documentation

#### `validate_readme_examples.py`
**Purpose**: Tests that README code examples execute correctly and produce expected results
```bash
# Test all README code examples
python scripts/validate_readme_examples.py --all

# Test specific README file
python scripts/validate_readme_examples.py --file src/README.md

# Generate example test report
python scripts/validate_readme_examples.py --report examples_test_report.html
```

**Testing Capabilities**:
- **Code Extraction**: Automatically extract code blocks from markdown files
- **Execution Testing**: Execute code examples in isolated environments
- **Output Validation**: Verify code examples produce expected outputs
- **Error Detection**: Identify and report code examples that fail to execute
- **Documentation Updates**: Suggest fixes for broken code examples

### Performance and Profiling

#### `profile_memory.py`
**Purpose**: Memory profiling and performance monitoring for DCF calculations
```bash
# Profile complete DCF workflow
python scripts/profile_memory.py --workflow complete

# Profile specific service
python scripts/profile_memory.py --service MonteCarloService --scenarios 1000

# Generate memory usage report
python scripts/profile_memory.py --report memory_profile.html --detailed
```

**Profiling Features**:
- **Memory Usage Tracking**: Monitor memory consumption during DCF calculations
- **Performance Benchmarking**: Track execution times for critical operations
- **Memory Leak Detection**: Identify potential memory leaks in long-running operations
- **Resource Utilization**: Monitor CPU and I/O usage during intensive calculations
- **Regression Detection**: Compare performance against historical benchmarks

#### `profile_performance.py` (New in v1.3)
**Purpose**: Comprehensive performance profiling and regression detection
```bash
# Performance regression testing
python scripts/profile_performance.py --regression-test

# Benchmark specific calculations
python scripts/profile_performance.py --benchmark IRR --scenarios 500

# Generate performance report
python scripts/profile_performance.py --report performance_analysis.html
```

### Release and Version Management

#### `generate_release_notes.py`
**Purpose**: Automated release notes generation from git commits with semantic versioning
```bash
# Generate release notes for specific version
python scripts/generate_release_notes.py v1.3.0

# Generate release notes since last tag
python scripts/generate_release_notes.py --since-last-tag

# Generate comprehensive changelog
python scripts/generate_release_notes.py --changelog --output CHANGELOG.md
```

**Release Features**:
- **Semantic Versioning**: Automatically categorize changes by type (feat, fix, docs, etc.)
- **Commit Analysis**: Parse commit messages for feature descriptions and breaking changes  
- **Issue Integration**: Link commits to GitHub issues and pull requests
- **Contributor Recognition**: Automatic contributor attribution and statistics
- **Format Options**: Generate release notes in markdown, HTML, or JSON formats

#### `bump_version.py` (New in v1.3)
**Purpose**: Automated version bumping with validation and tagging
```bash
# Bump patch version
python scripts/bump_version.py patch

# Bump minor version with release notes
python scripts/bump_version.py minor --release-notes

# Bump major version with breaking changes documentation
python scripts/bump_version.py major --breaking-changes
```

## Data Management and Validation Scripts

### Database Management

#### `validate_data_quality.py`
**Purpose**: Comprehensive data quality validation for production databases
```bash
# Validate all databases
python scripts/validate_data_quality.py --all-databases

# Validate specific parameter data
python scripts/validate_data_quality.py --parameter rent_growth --msa 35620

# Generate data quality report
python scripts/validate_data_quality.py --report data_quality.html
```

**Data Quality Checks**:
- **Statistical Validation**: Outlier detection and range validation
- **Historical Consistency**: Trend validation and discontinuity detection
- **Source Attribution**: Verify data lineage and source information
- **Completeness Analysis**: Check for missing data points and coverage gaps
- **Cross-Parameter Validation**: Validate relationships between parameters

#### `export_data.py`
**Purpose**: Data export utilities for analysis and reporting
```bash
# Export all parameter data to Excel
python scripts/export_data.py --all --format excel --output market_data.xlsx

# Export specific parameter data
python scripts/export_data.py --parameter cap_rate --msa 31080 --format csv

# Export for specific date range
python scripts/export_data.py --start-date 2020-01-01 --end-date 2025-01-01
```

### Configuration and Environment Management

#### `validate_configuration.py`
**Purpose**: Configuration validation and environment setup verification
```bash
# Validate production configuration
python scripts/validate_configuration.py --env production

# Check parameter definitions
python scripts/validate_configuration.py --parameters

# Validate database connections
python scripts/validate_configuration.py --database-connectivity
```

**Configuration Validation**:
- **Parameter Definitions**: Validate parameter schemas and constraints
- **Environment Settings**: Check environment-specific configuration
- **Database Connectivity**: Verify database connections and permissions
- **API Endpoints**: Validate external API configurations and credentials
- **Feature Flags**: Check feature flag consistency and dependencies

## GitHub Actions CI/CD Scripts

### Pipeline Integration Scripts

#### `.github/workflows/ci.yml` Support Scripts
```bash
# Pre-commit hooks
python scripts/pre_commit_checks.py

# Post-deployment validation
python scripts/post_deploy_validation.py --environment staging

# Integration test orchestration
python scripts/run_integration_tests.py --parallel --coverage
```

#### Multi-Python Version Testing
```bash
# Test matrix execution
python scripts/test_matrix.py --python-versions 3.8,3.9,3.10,3.11

# Compatibility validation
python scripts/validate_compatibility.py --python-version 3.11

# Dependency analysis
python scripts/analyze_dependencies.py --security-check
```

### Quality Assurance Automation

#### `lint_and_format.py`
**Purpose**: Comprehensive code quality enforcement
```bash
# Run all linting and formatting
python scripts/lint_and_format.py --fix

# Check specific file patterns
python scripts/lint_and_format.py --pattern "src/**/*.py"

# Generate code quality report
python scripts/lint_and_format.py --report code_quality.html
```

**Quality Checks**:
- **Code Formatting**: Black formatting with consistent style
- **Import Sorting**: isort with Clean Architecture-aware configuration
- **Linting**: flake8 with custom rules for real estate domain
- **Type Checking**: mypy with comprehensive type validation
- **Security Analysis**: bandit security scanning for vulnerabilities

## Development Workflow Scripts

### Local Development Support

#### `setup_dev_environment.py`
**Purpose**: Automated development environment setup
```bash
# Complete development setup
python scripts/setup_dev_environment.py --full

# Install only required dependencies
python scripts/setup_dev_environment.py --minimal

# Setup with sample data
python scripts/setup_dev_environment.py --with-sample-data
```

#### `run_development_server.py`
**Purpose**: Development server with hot reloading and debugging
```bash
# Start development server
python scripts/run_development_server.py --debug

# Run with specific configuration
python scripts/run_development_server.py --config development.yml

# Enable performance monitoring
python scripts/run_development_server.py --profile
```

### Testing and Validation Utilities

#### `run_comprehensive_tests.py`
**Purpose**: Orchestrated test execution with comprehensive reporting
```bash
# Run all test suites
python scripts/run_comprehensive_tests.py --all

# Run specific test categories
python scripts/run_comprehensive_tests.py --unit --integration --performance

# Generate test coverage report
python scripts/run_comprehensive_tests.py --coverage-html
```

**Test Orchestration Features**:
- **Parallel Execution**: Multi-threaded test execution for speed
- **Coverage Analysis**: Comprehensive coverage reporting with thresholds
- **Performance Testing**: Automated performance regression detection
- **Flaky Test Detection**: Identify and report unstable tests
- **Test Result Analysis**: Detailed test failure analysis and reporting

## Usage Patterns and Integration

### CI/CD Pipeline Execution
```yaml
# Example GitHub Actions workflow step
- name: Validate Architecture and Quality
  run: |
    python scripts/validate_architecture.py --strict --report
    python scripts/validate_docs.py --comprehensive
    python scripts/lint_and_format.py --check
    python scripts/profile_performance.py --regression-test
```

### Local Development Workflow
```bash
# Pre-commit validation (recommended workflow)
python scripts/validate_architecture.py --quick
python scripts/lint_and_format.py --fix
python scripts/validate_readme_examples.py --changed-files
python scripts/run_comprehensive_tests.py --changed-only

# Pre-release validation
python scripts/validate_docs.py --comprehensive
python scripts/validate_data_quality.py --all-databases
python scripts/profile_performance.py --benchmark-all
python scripts/generate_release_notes.py --preview
```

### Performance Monitoring
```bash
# Continuous performance monitoring
python scripts/profile_memory.py --continuous --alert-threshold 500MB
python scripts/profile_performance.py --monitor --baseline-file benchmarks.json
```

## Script Dependencies and Requirements

### Core Dependencies
- **Python 3.8+**: Minimum Python version for all scripts
- **Git Integration**: Automated git operations for version management
- **GitHub CLI**: Integration with GitHub Actions and repository management
- **Performance Libraries**: Memory profiling and performance analysis tools
- **Validation Libraries**: Comprehensive validation and testing frameworks

### Environment Configuration
- **Environment Variables**: Support for environment-specific configuration
- **Configuration Files**: YAML and JSON configuration support
- **Credential Management**: Secure handling of API keys and database credentials
- **Logging Integration**: Comprehensive logging for all script operations

## Maintenance and Updates

### Script Versioning
- **Version Tracking**: All scripts tagged with version information
- **Backward Compatibility**: Maintain compatibility with previous script versions
- **Migration Support**: Automated migration for script configuration changes
- **Documentation Updates**: Automatic documentation updates for script changes

### Monitoring and Alerts
- **Script Health Monitoring**: Monitor script execution and performance
- **Failure Alerts**: Automated alerts for script failures or performance degradation
- **Usage Analytics**: Track script usage patterns and optimization opportunities
- **Maintenance Scheduling**: Automated maintenance and update scheduling