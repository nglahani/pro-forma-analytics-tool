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

## Next Development Priorities

1. **API Development** - RESTful endpoints for external integrations
2. **UI Enhancement** - Web-based property input and analysis dashboard  
3. **Reporting** - PDF export and Excel integration for investment reports
4. **Performance** - Optimize IRR calculations for larger property portfolios