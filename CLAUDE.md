# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

This document serves as a technical specification and development guide for AI assistants working on the pro-forma-analytics-tool. It provides context about the current implementation state, architectural decisions, and development standards to ensure consistent and informed code contributions.

## Repository Overview

**pro-forma-analytics-tool** - A production-ready real estate DCF analysis platform that transforms static Excel-based pro formas into sophisticated financial models using Prophet time series forecasting and Monte Carlo simulations.

## Current Implementation Status

**Status**: API-Ready (v1.4) - Pre-production with comprehensive environment configuration
**Quality**: A+ (98/100) - Enhanced configuration management and FastAPI preparation
**Architecture**: Clean Architecture with domain-driven design + environment configuration system
**Testing**: 96%+ coverage with 320+ test methods across BDD/TDD framework including comprehensive edge case testing
**Data Coverage**: 100% parameter completion with production-grade validation
**CI/CD**: Fully debugged GitHub Actions pipeline with multi-Python version support (3.9-3.11) and CLI integration
**Configuration**: Multi-environment support (dev/test/prod) with security best practices

### Core Capabilities
- **Complete 4-Phase DCF Engine**: Assumptions → Initial Numbers → Cash Flow → Financial Metrics
- **Prophet Forecasting**: 11 pro forma parameters with 6-year projections
- **Monte Carlo Simulation**: 500+ scenarios with economic correlations
- **Investment Analysis**: NPV, IRR, equity multiples, risk assessment, terminal value
- **Data Infrastructure**: 4 SQLite databases with 2,174+ production-grade historical data points
- **Environment Configuration**: Multi-environment support with security best practices and FastAPI preparation

## Technical Architecture

### Clean Architecture Implementation
```
src/
├── domain/              # Core business logic (no external dependencies)
│   ├── entities/        # Immutable business entities
│   └── repositories/    # Abstract repository interfaces
├── application/         # Use case orchestration
│   └── services/        # 6 DCF service classes
├── infrastructure/      # External concerns
│   ├── repositories/    # SQLite repository implementations
│   └── container.py     # Dependency injection
└── presentation/        # Visualization components
```

### Key Services
1. **DCFAssumptionsService** - Monte Carlo to DCF parameter mapping
2. **InitialNumbersService** - Acquisition costs and financing calculations  
3. **CashFlowProjectionService** - 6-year cash flow modeling with waterfall distributions
4. **FinancialMetricsService** - NPV, IRR, terminal value, investment recommendations
5. **ForecastingService** - Prophet-based time series forecasting
6. **MonteCarloService** - Probabilistic scenario generation

### Database Schema
- **market_data.db**: National economic indicators (interest rates, treasury yields)
- **property_data.db**: MSA-specific rental market data and operating expenses
- **economic_data.db**: Regional growth metrics and lending requirements  
- **forecast_cache.db**: Prophet forecasts and Monte Carlo simulation results

### Data Coverage
- **5 Major MSAs**: NYC, LA, Chicago, DC, Miami
- **11 Pro Forma Metrics**: Interest rates, cap rates, vacancy, rent growth, expense growth, property growth, LTV ratios, closing costs, lender reserves
- **Historical Depth**: 15+ years (2010-2025) with 2,174+ data points
- **Parameter Completion**: 100% coverage across all 11 parameters
- **Data Quality**: Production-grade validation with comprehensive test coverage
- **Geographic Coverage**: 5+ MSAs for all location-dependent parameters
- **Validation Status**: Complete data coverage, statistical validation passed

## Development Standards

### Code Quality Requirements
- **Test Coverage**: 95%+ target for business logic with comprehensive BDD/TDD framework
- **Architecture**: Strict adherence to Clean Architecture principles
- **Type Safety**: Comprehensive type hints with mypy validation
- **Error Handling**: Consistent ValidationError usage with detailed messages
- **Documentation**: Docstrings for all public interfaces

#### Linux Compatibility Validation
```bash
# Validate Linux compatibility before pushing
scripts\validate-linux.bat    # Windows
./scripts/validate-linux.sh   # Unix/Mac

# Manual Docker validation
docker build -f Dockerfile.test -t proforma-test .
```

## Recent Enhancements (v1.3)

### Code Quality Improvements
- **Comprehensive Linting Cleanup**: Fixed 100+ flake8 violations including unused imports, trailing whitespace, and undefined names
- **Type Safety Enhancements**: Improved TYPE_CHECKING imports and forward references for better type checking
- **Error Handling**: Replaced bare except clauses with specific exception handling
- **Code Consolidation**: Removed redundant imports and variables across 20+ files

### CI/CD Pipeline Enhancements
- **GitHub Actions Debugging**: Implemented CLI-based debugging with `gh` tool integration
- **Python Version Compatibility**: Resolved pandas compatibility issues for Python 3.8+ support
- **Automated Quality Gates**: Enhanced pipeline with comprehensive validation steps
- **Configuration Optimization**: Fixed flake8 configuration parsing and simplified workflow commands

### Testing Infrastructure
- **Edge Case Coverage**: Added 40+ new test cases for error scenarios and boundary conditions
- **Infrastructure Testing**: Comprehensive database error handling and configuration edge cases
- **Application Testing**: Extreme scenario testing for financial calculations and business logic
- **Performance Validation**: IRR calculation performance testing with batch processing

### Development Experience
- **Documentation Accuracy**: Improved inline documentation and code comments
- **Windows Compatibility**: Fixed file handling issues in validation scripts
- **Debugging Tools**: Enhanced error tracking and resolution capabilities
- **Automated Formatting**: Consistent code formatting across entire codebase

## Key Implementation Details

### DCF Engine Workflow
1. **Phase 1**: Convert Monte Carlo scenarios to DCF assumptions using economic parameter mapping
2. **Phase 2**: Calculate acquisition costs, financing terms, and initial investment requirements
3. **Phase 3**: Generate 6-year cash flow projections with waterfall distributions and growth modeling
4. **Phase 4**: Compute financial metrics (NPV, IRR, terminal value) and investment recommendations

### Monte Carlo Integration
- **Correlation Modeling**: 23 economic relationships (e.g., interest rates → cap rates)
- **Scenario Classification**: Bull/Bear/Neutral/Growth/Stress market identification
- **Risk Metrics**: Growth scores (0.376-0.557), Risk scores (0.385-0.593)
- **Quality Assurance**: 5/5 statistical validation checks passed

### Property Input System
- **Current**: `SimplifiedPropertyInput` in `src/domain/entities/property_data.py`
- **Legacy**: `PropertyInputData` has been removed and replaced with modern implementation
- **Required Fields**: 7 core inputs (residential units, renovation time, commercial units, equity share, rent rates, cash percentage)

### Environment Configuration System
- **Configuration File**: Enhanced `config/settings.py` with multi-environment support
- **Environment Types**: Development, Testing, Production with automatic detection
- **Environment Variable**: `PRO_FORMA_ENV` controls environment (defaults to development)
- **Security**: Environment variable-based secrets management (no hardcoded API keys)
- **API Preparation**: FastAPI-ready configuration with CORS, rate limiting, authentication settings
- **Validation**: Automatic configuration validation prevents production misconfigurations
- **External APIs**: Secure FRED API key management via `FRED_API_KEY` environment variable

## CI/CD Pipeline and Development Workflow

### Streamlined Linux-Focused CI/CD

**Pipeline Design**: Optimized for Linux deployment with simplified validation workflow
- **Platform**: Ubuntu Linux only (eliminates cross-platform complexity)
- **Python Versions**: 3.9, 3.10, 3.11 (focused on production-relevant versions)
- **Execution Time**: ~3-5 minutes (reduced from 10+ minutes)
- **Jobs**: 2 parallel jobs (test + production-validation)

### Development Workflow

#### 1. Local Development (Windows)
```bash
# Normal development cycle
python -m pytest tests/ -v           # Quick local testing
python demo_end_to_end_workflow.py   # Validate DCF engine
black src/ tests/                    # Code formatting
```

#### 2. Linux Compatibility Check (Pre-Push)
```bash
# Validate Linux compatibility
scripts\validate-linux.bat           # Full Linux validation
git push origin main                 # Push with confidence
```

#### 3. CI/CD Pipeline (Automatic)
- **Test Job**: Code quality, type checking, comprehensive tests across Python versions
- **Production Validation**: Security, architecture, build validation, 95% coverage enforcement

### Docker Integration

**Purpose**: Local Linux compatibility validation without workflow disruption
- **File**: `Dockerfile.test` - Lightweight Linux testing container
- **Usage**: On-demand validation before pushing changes
- **Benefits**: Catch platform-specific issues early, maintain Windows development workflow

## Development Guidelines

### When Working with This Codebase

1. **Always read existing code** before making changes to understand patterns and conventions
2. **Follow Clean Architecture** - maintain dependency flow (presentation/infrastructure → application → domain)
3. **Write tests first** for new functionality using BDD/TDD patterns
4. **Use domain entities** from `src/domain/entities/` rather than legacy classes
5. **Maintain backwards compatibility** when modifying public interfaces

### **MANDATORY POST-FEATURE WORKFLOW**

**After ANY major feature addition or codebase change, you MUST complete the following steps in order:**

#### 1. **Update Technical Documentation**
- Update relevant documentation files (CLAUDE.md, README.md, etc.)
- Document new configuration options, environment variables, or settings
- Update architecture diagrams or API specifications if applicable
- Ensure all code examples and references remain accurate

#### 2. **Add/Update Test Cases** 
- Write comprehensive unit tests for new functionality
- Add integration tests for cross-component features
- Update edge case tests for new error scenarios
- Ensure test coverage remains ≥95% for business logic

#### 3. **Run Complete Local Testing Workflow**
- Execute full test suite: `python -m pytest tests/ -v`
- Validate end-to-end functionality: `python demo_end_to_end_workflow.py`
- Run code quality checks: `black`, `isort`, `flake8`, `mypy`
- Verify performance tests pass without regression

#### 4. **Push to GitHub with CI/CD Validation**
- Commit with descriptive message explaining the change
- Push to GitHub: `git push origin main`
- **Monitor CI/CD pipeline results closely**
- Debug and fix any pipeline failures immediately
- **Never ignore or bypass failing CI/CD checks**

#### 5. **Pipeline Debugging Protocol**
- Review GitHub Actions logs for specific failure points
- Fix issues locally and re-test before pushing again
- Update CI/CD configuration if environment changes require it
- Ensure all automated quality gates pass

**This workflow ensures:**
- ✅ Documentation stays current and accurate
- ✅ Test coverage remains comprehensive
- ✅ CI/CD pipeline continues to function
- ✅ Code quality standards are maintained
- ✅ Production deployments remain stable

**Failure to follow this workflow may result in:**
- ❌ Broken CI/CD pipelines
- ❌ Outdated documentation
- ❌ Production deployment failures
- ❌ Reduced code quality and reliability

### Common Development Tasks

**Adding New Pro Forma Metrics**:
1. Update parameter definitions in `config/parameters.py`
2. Add database schema changes in `data/databases/`
3. Update forecasting logic in `forecasting/prophet_engine.py`
4. Modify Monte Carlo correlations in `monte_carlo/simulation_engine.py`
5. Update DCF mapping in `src/application/services/dcf_assumptions_service.py`

**Adding New DCF Calculations**:
1. Create new domain entities in `src/domain/entities/`
2. Implement business logic in application services
3. Add comprehensive unit tests in `tests/unit/application/`
4. Update integration tests in `tests/integration/`

### Reference Materials

- **Excel Analysis**: `Reference_ Docs/MultiFamily_RE_Pro_Forma.xlsx` - Original pro forma structure
- **Validation Charts**: `validation_charts/` - Monte Carlo statistical validation results
- **Demo Workflow**: `demo_end_to_end_workflow.py` - Complete implementation example

## Production Deployment Notes

**Ready for Production**: The DCF engine is fully implemented and validated
**Dependencies**: Python 3.8+, SQLite (no external database required)
**Performance**: Handles 500+ Monte Carlo scenarios with sub-second response times
**Scalability**: Clean architecture supports horizontal scaling and microservice decomposition

## Testing and Quality Assurance

**CRITICAL**: All code changes require comprehensive testing and CI/CD compliance.

### Essential Testing Commands

**Quick Validation (5 minutes)**:
```bash
# Core business logic and end-to-end validation
python -m pytest tests/unit/application/ tests/integration/ -q
python demo_end_to_end_workflow.py
# Expected: 91/91 tests passing, NPV $7.8M, IRR 64.8%, STRONG_BUY
```

**Complete Testing Suite**:
```bash
# 1. All test categories (91 tests total)
python -m pytest tests/unit/application/ -v           # 74 tests
python -m pytest tests/unit/infrastructure/test_edge_cases.py -v  # 12 tests  
python -m pytest tests/integration/test_complete_dcf_workflow.py -v  # 1 test
python -m pytest tests/performance/ -v                # 4 tests

# 2. Code quality and formatting
black --check src/ tests/
isort --check-only --profile black src/ tests/
flake8 src/ tests/
mypy src/

# 3. Architecture and coverage validation
python scripts/validate_architecture.py
pytest --cov=src --cov=core --cov=monte_carlo --cov-fail-under=95

# 4. End-to-end workflow validation
python demo_end_to_end_workflow.py
```

### Test Development Requirements

**TDD/BDD Pattern** - Always write tests first:
1. Create failing test describing desired behavior
2. Implement minimum code to make test pass
3. Refactor while keeping tests green
4. Maintain ≥95% test coverage for business logic

**Test Categories by Component**:
- **Unit Tests** (`tests/unit/`): Isolated component testing
- **Integration Tests** (`tests/integration/`): End-to-end workflow validation  
- **Performance Tests** (`tests/performance/`): Load and regression testing
- **Edge Case Tests** (`tests/unit/*/test_edge_cases.py`): Error scenarios and boundary conditions

### CI/CD Pipeline

**Automated Quality Gates**:
- Python 3.9-3.11 compatibility testing
- 95% test coverage enforcement
- Clean Architecture compliance validation
- Security vulnerability scanning
- Performance regression detection

**Pipeline Status Check**:
```bash
gh run list --limit 3  # Check recent CI/CD runs
```

**Failure Response**: Never ignore pipeline failures - debug locally, fix issues, and re-run validation before pushing.

## Next Development Priorities

**Current Status**: Infrastructure and code quality improvements completed ✅

1. **RESTful API Layer** - Ready to begin development of external integrations layer
2. **Web-based Dashboard** - Property input and analysis user interface 
3. **Investment Reporting** - PDF export and Excel integration capabilities
4. **Portfolio Optimization** - Enhanced IRR calculations for larger property sets
5. **Advanced Analytics** - Machine learning features for investment recommendations

**Remember**: Every code change must include corresponding test updates and pass all CI/CD quality gates before merging.

---

## Development Workflow - Kiro-Style Spec-Driven Development

### How Kiro Works

Kiro is an AI assistant that helps build features systematically through a structured spec-driven development process.

### Core Philosophy

Instead of jumping straight into code, Kiro guides development through three phases:

1. **Requirements** - What needs to be built
2. **Design** - How it will be built  
3. **Tasks** - Step-by-step implementation plan

This ensures every feature is well-planned before implementation begins.

### The Spec Structure

Each feature gets its own folder in `.kiro/specs/{feature-name}/` containing:

- **`requirements.md`** - User stories and acceptance criteria
- **`design.md`** - Technical architecture and implementation approach
- **`tasks.md`** - Actionable coding checklist

### Workflow Process

#### Phase 1: Requirements Gathering

1. Create initial requirements based on feature idea
2. Use user stories format: *"As a [role], I want [feature], so that [benefit]"*
3. Include acceptance criteria in EARS format (Easy Approach to Requirements Syntax)
   - Example: *"WHEN user clicks submit THEN system SHALL validate all fields"*
4. Iterate until requirements are approved

#### Phase 2: Design Documentation

1. Research and create comprehensive `design.md`
2. Cover architecture, components, data models, error handling, testing strategy
3. May include Mermaid diagrams for visual representation
4. Address all requirements from the previous phase
5. Iterate until design is approved

#### Phase 3: Task Planning

1. Break down design into actionable coding tasks in `tasks.md`
2. Create numbered checklist items (1.1, 1.2, etc.)
3. Each task references specific requirements
4. Focus only on code implementation activities
5. Prioritize incremental, testable progress
6. Iterate until task list is approved

### Key Features

- **Iterative Approval** - Explicit approval required for each document before moving to next phase
- **Requirement Traceability** - Tasks link back to specific requirements
- **Incremental Development** - Tasks build on each other progressively
- **Code-Focused** - Tasks only include activities a coding agent can execute

### Task Execution

Once spec is complete, execute tasks by:

1. Opening the `tasks.md` file
2. Clicking "Start task" next to individual task items
3. Implement one task at a time, stopping for review between tasks

### Getting Started

To begin a new feature spec:
1. Describe your feature idea
2. I'll guide you through the three-phase process
3. For existing specs, I can help review, update any phase, or execute implementation tasks

### Pro-Forma Analytics Specific Guidelines

#### Business Domain Context
- **Real Estate Investment Analysis** - Focus on investor decision-making workflows
- **Financial Modeling** - Emphasis on accuracy, validation, and risk assessment
- **Data-Driven Decisions** - Replace manual assumptions with statistical forecasting

#### Architecture Constraints
- **Clean Architecture** - Maintain domain/application/infrastructure separation
- **TDD/BDD Testing** - All features must include comprehensive test coverage
- **Prophet + Monte Carlo** - Leverage existing forecasting and simulation infrastructure

#### Feature Prioritization
1. **Financial Calculation Engine** (highest priority - missing core business logic)
2. **Investment Decision Framework** (high priority - complete user workflow)
3. **Visualization & Reporting** (medium priority - user experience)
4. **API & Integration** (lower priority - external access)

---

## Documentation Standards

### Writing Guidelines

When creating or updating documentation in this repository, adhere to the following standards:

#### Professional Tone Requirements
- Maintain professional, technical language throughout all documentation
- Avoid emojis, exclamation marks, or overly casual expressions
- Use declarative statements rather than conversational tone
- Write for technical audiences with appropriate domain expertise

#### MECE Principle (Mutually Exclusive, Completely Exhaustive)
- Structure documentation to eliminate overlap between sections
- Ensure each topic is covered in exactly one authoritative location
- Organize content hierarchically with clear boundaries between topics
- Verify that all relevant aspects of a topic are addressed comprehensively

#### Centralized Documentation Structure
- All documentation must reside in the `/docs` folder
- Use clear, descriptive filenames following the pattern: `TOPIC_NAME.md`
- Maintain a master index in `/docs/README.md` linking to all documentation
- Reference external documentation through standardized linking conventions

#### Redundancy Elimination
- Consolidate duplicate information into single authoritative sources
- Use cross-references rather than repeating content across documents
- Maintain a single source of truth for each technical concept
- Review existing documentation before creating new files to prevent duplication

#### Implementation Requirements
- Update documentation concurrently with code changes
- Include technical specifications, API references, and architectural decisions
- Provide clear examples and usage patterns where applicable
- Maintain version compatibility information and migration guides

### Comprehensive Documentation Analysis Protocol

When analyzing or updating documentation, Claude Code MUST perform comprehensive analysis across ALL markdown files in the repository:

#### Required Documentation Analysis Steps
1. **Repository-Wide Search**: Use `Glob` tool to find all `**/*.md` files across the entire repository
2. **Comprehensive Review**: Read ALL relevant documentation files, not just root-level files
3. **Cross-Reference Analysis**: Check for consistency across all documentation sources
4. **Gap Identification**: Identify missing or outdated information across all docs
5. **Redundancy Detection**: Find duplicate or conflicting information across files

#### Documentation File Categories to Analyze
- **Root Level**: README.md, CLAUDE.md, CONTRIBUTING.md
- **Primary Docs**: `/docs/*.md` - All technical documentation
- **Module Docs**: `/src/README.md`, `/tests/README.md`, `/core/README.md`, etc.
- **Database Docs**: `/data/databases/README.md`, `/data/databases/schemas/README.md`
- **Specialized Docs**: `/scripts/README.md`, `/validation_charts/*.md`
- **Configuration Docs**: Any workflow or config documentation

#### Documentation Consistency Requirements
- **Testing Commands**: Ensure all documentation shows consistent, current testing procedures
- **CI/CD References**: Validate all pipeline documentation matches actual workflows
- **Installation Procedures**: Verify setup instructions are consistent across all docs
- **Architecture References**: Ensure all architectural documentation aligns
- **Development Workflows**: Validate development process documentation consistency

#### Analysis Output Requirements
- **Status Assessment**: Current vs. required documentation state
- **Gap Analysis**: Missing or outdated information identification
- **Consistency Review**: Cross-document alignment validation
- **Update Recommendations**: Specific files and sections requiring updates
- **Priority Classification**: Critical vs. minor documentation issues

---

## Collaborative Development Workflow

### Clarifying Questions Protocol

When working with domain experts and stakeholders, Claude Code should actively engage in iterative clarification to ensure accurate implementation. This collaborative approach prevents costly rework and ensures technical solutions align with business requirements.

#### Best Practices for Clarifying Questions

**When to Ask Questions:**
- Complex business logic requires implementation
- Technical specifications have ambiguities or gaps
- Multiple interpretation paths exist for requirements
- Domain-specific knowledge is required
- Integration points between systems are unclear

**How to Structure Questions:**
- Be specific and technical rather than generic
- Reference concrete examples from the codebase or documentation
- Provide your current understanding for validation
- Ask multiple related questions in logical sequence
- Include technical implications of different approaches

**Documentation-First Approach:**
- Document answers immediately in appropriate codebase locations
- Update architectural decisions and specifications
- Maintain traceability between questions and implementation
- Create searchable knowledge base for future reference

#### Example Workflow Pattern

```
1. Identify Ambiguity
   └── "I see parameter X, but need clarification on calculation Y"

2. Form Specific Questions  
   └── "Is the calculation: A × B ÷ C, or (A × B) ÷ (C + D)?"

3. Provide Current Understanding
   └── "My understanding is X, but this conflicts with Y"

4. Ask for Validation/Correction
   └── "Should I implement approach A or B?"

5. Document Answers Immediately
   └── Update relevant .md files in /docs folder

6. Confirm Understanding
   └── "Let me summarize to ensure alignment..."
```

#### Documentation Update Workflow

**Immediate Documentation:**
- Technical clarifications → Architecture documentation
- Business logic clarifications → Process flow documentation
- Integration clarifications → API and interface documentation
- Implementation decisions → Technical decision logs

**Documentation Standards:**
- Use clear, technical language appropriate for developers
- Include code examples and implementation patterns
- Reference specific files, functions, and line numbers when applicable
- Maintain MECE structure with cross-references
- Update table of contents and indexes

#### Iterative Refinement Process

**Clarification Loop:**
1. Ask specific technical questions
2. Receive domain expert answers
3. Document answers in codebase immediately
4. Confirm understanding with summary
5. Identify follow-up questions if needed
6. Repeat until complete clarity achieved

**Knowledge Capture:**
- Each clarification session should result in permanent documentation
- Technical decisions should be traceable to business requirements
- Implementation patterns should be documented for consistency
- Edge cases and special conditions should be explicitly documented

#### Communication Guidelines

**Effective Question Patterns:**
- "My understanding is X, but I need clarification on Y"
- "Should the system handle scenario A by doing X or Y?"
- "When condition Z occurs, what is the expected behavior?"
- "Are there any edge cases for calculation X that I should consider?"

**Avoid:**
- Generic questions without technical context
- Yes/no questions that don't advance understanding
- Questions that could be answered by reading existing documentation
- Multiple unrelated topics in single question set

#### Success Indicators

**Quality Metrics:**
- Technical implementation matches business requirements
- Edge cases are identified and handled appropriately
- Documentation accurately reflects implemented behavior
- Future developers can understand design decisions
- Domain experts can validate technical specifications

**Process Metrics:**
- Reduced rework due to misunderstood requirements
- Faster onboarding for new team members
- Consistent implementation patterns across features
- Comprehensive knowledge base for maintenance