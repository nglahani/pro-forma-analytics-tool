# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

This document serves as a technical specification and development guide for AI assistants working on the pro-forma-analytics-tool. It provides context about the current implementation state, architectural decisions, and development standards to ensure consistent and informed code contributions.

## Repository Overview

**pro-forma-analytics-tool** - A production-ready real estate DCF analysis platform that transforms static Excel-based pro formas into sophisticated financial models using Prophet time series forecasting and Monte Carlo simulations.

## Current Implementation Status

**Status**: Production Ready (v1.0)
**Quality**: A- (88/100) 
**Architecture**: Clean Architecture with domain-driven design
**Testing**: 95%+ coverage with 40+ test methods across BDD/TDD framework

### Core Capabilities
- **Complete 4-Phase DCF Engine**: Assumptions → Initial Numbers → Cash Flow → Financial Metrics
- **Prophet Forecasting**: 11 pro forma parameters with 6-year projections
- **Monte Carlo Simulation**: 500+ scenarios with economic correlations
- **Investment Analysis**: NPV, IRR, equity multiples, risk assessment, terminal value
- **Data Infrastructure**: 4 SQLite databases with 688+ historical data points

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
- **Historical Depth**: 15+ years (2010-2025) with 688+ data points
- **Validation Status**: No missing data gaps, statistical validation passed

## Development Standards

### Code Quality Requirements
- **Test Coverage**: 95%+ target for business logic
- **Architecture**: Strict adherence to Clean Architecture principles
- **Type Safety**: Comprehensive type hints with mypy validation
- **Error Handling**: Consistent ValidationError usage with detailed messages
- **Documentation**: Docstrings for all public interfaces

### Testing Framework
- **Unit Tests**: `tests/unit/` - Isolated component testing
- **Integration Tests**: `tests/integration/` - End-to-end workflow validation
- **Performance Tests**: `tests/performance/` - Load and performance validation
- **BDD/TDD**: Behavior-driven development with given/when/then patterns

### Build Commands
```bash
# Test execution
python -m pytest tests/ -v
python demo_end_to_end_workflow.py

# Code quality
black src/ tests/
flake8 src/ tests/
mypy src/

# Coverage analysis
pytest --cov=src --cov=core --cov=monte_carlo
```

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
- **Legacy**: `PropertyInputData` in `core/property_inputs.py` (compatibility only)
- **Required Fields**: 7 core inputs (residential units, renovation time, commercial units, equity share, rent rates, cash percentage)

## Development Guidelines

### When Working with This Codebase

1. **Always read existing code** before making changes to understand patterns and conventions
2. **Follow Clean Architecture** - maintain dependency flow (presentation/infrastructure → application → domain)
3. **Write tests first** for new functionality using BDD/TDD patterns
4. **Use domain entities** from `src/domain/entities/` rather than legacy classes
5. **Maintain backwards compatibility** when modifying public interfaces

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

## CI/CD Pipeline and Testing Requirements

### Mandatory Testing and Quality Assurance

**CRITICAL**: When making any code changes, you MUST update tests and maintain CI/CD pipeline compliance:

### 1. Test-Driven Development Requirements

**For ANY code changes, you MUST:**

1. **Write Tests First** (TDD/BDD Pattern):
   ```bash
   # Create failing test that describes desired behavior
   pytest tests/unit/[relevant_test_file].py::test_new_functionality -v
   
   # Implement feature to make test pass
   # Refactor while keeping tests green
   ```

2. **Update All Relevant Test Types**:
   - **Unit Tests**: `tests/unit/` - Test individual components in isolation
   - **Integration Tests**: `tests/integration/` - Test end-to-end workflows  
   - **Performance Tests**: `tests/performance/` - Validate performance requirements
   - **Architecture Tests**: Validated automatically by `scripts/validate_architecture.py`

3. **Maintain Test Coverage**:
   ```bash
   # Coverage must remain ≥95% for business logic
   pytest --cov=src --cov=core --cov=monte_carlo --cov-fail-under=95
   ```

### 2. CI/CD Pipeline Compliance

**Before any code commit, ensure:**

1. **All Quality Checks Pass**:
   ```bash
   # Code formatting
   black --check src/ tests/
   isort --check-only src/ tests/
   
   # Linting
   flake8 src/ tests/
   
   # Type checking  
   mypy src/
   
   # Architecture validation
   python scripts/validate_architecture.py
   
   # Documentation validation
   python scripts/validate_docs.py
   ```

2. **End-to-End Workflow Validation**:
   ```bash
   # MUST pass before any commit
   python demo_end_to_end_workflow.py
   ```

3. **Performance Regression Check**:
   ```bash
   # Ensure no performance degradation
   python tests/performance/test_irr_performance.py
   ```

### 3. Specific Testing Requirements by Change Type

**When Adding New Services**:
1. Create comprehensive unit tests in `tests/unit/application/test_[service_name].py`
2. Add integration tests in `tests/integration/test_complete_dcf_workflow.py`
3. Update performance tests if the service affects calculation speed
4. Validate Clean Architecture compliance

**When Modifying Domain Entities**:
1. Update entity tests in `tests/unit/test_[entity_name].py`
2. Ensure immutability and validation rules are tested
3. Update integration tests that use the entity
4. Verify serialization/deserialization works correctly

**When Changing DCF Calculations**:
1. Add specific test cases for edge cases and boundary conditions
2. Include realistic property scenarios in integration tests
3. Validate financial calculations against known benchmarks
4. Test error handling for invalid inputs

**When Adding New Pro Forma Parameters**:
1. Update `tests/unit/test_forecast_entities.py`
2. Add Monte Carlo correlation tests
3. Update end-to-end workflow validation
4. Test database schema changes

### 4. CI/CD Pipeline Files

**Pipeline Configuration** (`.github/workflows/`):
- `ci.yml` - Main CI pipeline with multi-Python version testing
- `quality.yml` - Code quality and security checks
- `release.yml` - Automated release and deployment

**Validation Scripts** (`scripts/`):
- `validate_architecture.py` - Clean Architecture compliance checking
- `validate_docs.py` - Documentation accuracy validation
- `profile_memory.py` - Memory usage profiling
- `generate_release_notes.py` - Automated release documentation

### 5. Automated Quality Gates

**The CI/CD pipeline enforces**:
- **Python 3.8-3.13 compatibility** across all code changes
- **95% test coverage** threshold for business logic
- **Zero architecture violations** in Clean Architecture patterns
- **No security vulnerabilities** in dependencies
- **Performance regression detection** for DCF calculations
- **Documentation accuracy** for all code examples

### 6. Release Process

**For version releases**:
1. Tag with semantic versioning: `git tag v1.1.0`
2. Push tag: `git push origin v1.1.0`
3. CI/CD automatically runs full validation suite
4. Generates release notes from commit history
5. Creates GitHub release with build artifacts
6. Optionally deploys to PyPI (if configured)

### 7. Failure Response Protocol

**If CI/CD pipeline fails**:
1. **Never ignore pipeline failures** - fix immediately
2. **Review specific failure logs** in GitHub Actions
3. **Run failing checks locally** to reproduce and debug
4. **Update tests** if business requirements changed
5. **Maintain architectural compliance** - no shortcuts

**Common Failure Resolutions**:
- **Test failures**: Update test expectations or fix implementation
- **Coverage drops**: Add tests for uncovered code paths
- **Architecture violations**: Refactor to maintain Clean Architecture
- **Performance regression**: Optimize or update performance thresholds
- **Documentation outdated**: Update examples and references

## Next Development Priorities

1. **API Development** - RESTful endpoints for external integrations
2. **UI Enhancement** - Web-based property input and analysis dashboard  
3. **Reporting** - PDF export and Excel integration for investment reports
4. **Performance** - Optimize IRR calculations for larger property portfolios

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