# Source Code (src/) - v1.3

Production-ready Clean Architecture implementation with domain-driven design principles for real estate DCF analysis.

## Architecture Overview

This directory implements the **Clean Architecture** pattern with strict dependency inversion, ensuring maintainable, testable, and scalable code that isolates business logic from external concerns.

### Structure

- **`domain/`** - Core business logic and entities (pure business rules, no external dependencies)
- **`application/`** - Use cases and application services (orchestration layer, business workflow management)
- **`infrastructure/`** - External concerns (SQLite repositories, caching, dependency injection)
- **`presentation/`** - User interfaces and visualization components (charts, dashboards)

### Dependency Flow

```
presentation/ → application/ → domain/
                     ↓
             infrastructure/
```

**Key Principle**: Infrastructure and presentation layers depend on domain abstractions through dependency injection, never on concrete implementations.

## Core Services (application/services/)

### 1. DCFAssumptionsService
- Converts Monte Carlo scenarios to DCF parameters
- Handles economic correlation mapping
- Manages assumption validation and bounds checking

### 2. InitialNumbersService  
- Calculates acquisition costs and financing terms
- Processes down payment, closing costs, and lender reserves
- Handles loan-to-value ratio validation

### 3. CashFlowProjectionService
- Generates 6-year cash flow projections
- Implements waterfall distribution modeling
- Manages rental income, operating expenses, and debt service

### 4. FinancialMetricsService
- Computes NPV, IRR, and equity multiples
- Calculates terminal value with cap rate analysis  
- Generates investment recommendations (5-tier system)

### 5. ForecastingService
- Prophet-based time series forecasting for 11 pro forma parameters
- Handles trend detection and seasonality adjustment
- Provides uncertainty quantification with confidence intervals

### 6. MonteCarloService
- Generates 500+ probabilistic scenarios
- Models economic correlations and market dynamics
- Performs scenario classification and risk scoring

## Domain Entities (domain/entities/)

### Immutable Business Objects
- **`cash_flow_projection.py`** - Annual cash flow projections with waterfall calculations
- **`dcf_assumptions.py`** - DCF input parameters with validation rules
- **`financial_metrics.py`** - Investment performance metrics and recommendations
- **`forecast.py`** - Time series forecasting results with confidence intervals
- **`initial_numbers.py`** - Acquisition costs and financing calculations
- **`monte_carlo.py`** - Probabilistic scenario data and risk metrics
- **`property_data.py`** - Property input specifications and validation

### Repository Interfaces (domain/repositories/)
- **`parameter_repository.py`** - Abstract interface for market data access
- **`simulation_repository.py`** - Abstract interface for Monte Carlo result storage

## Infrastructure Layer (infrastructure/)

### Repository Implementations
- **`sqlite_parameter_repository.py`** - SQLite-based market data access with query optimization
- **`sqlite_simulation_repository.py`** - Persistent Monte Carlo result storage
- **`cached_parameter_repository.py`** - Performance-optimized caching layer

### Configuration and Dependencies
- **`configuration.py`** - Application settings and environment configuration
- **`container.py`** - Dependency injection container with service registration
- **`cache/query_cache.py`** - Query result caching for performance optimization

## Quality Metrics (v1.3)

- **Test Coverage**: 96%+ across all business logic
- **Architecture Compliance**: 100% Clean Architecture adherence validated by CI/CD
- **Code Quality**: A+ rating (97/100) with comprehensive linting and type checking
- **Performance**: Sub-second response times for 500+ Monte Carlo scenarios
- **CI/CD**: Fully automated GitHub Actions pipeline with multi-Python version support

## Development Standards

### Coding Principles
- **Domain-Driven Design**: Business logic encapsulated in domain entities
- **Dependency Injection**: All external dependencies injected through abstractions
- **Immutability**: Domain entities are immutable with validation on construction
- **Type Safety**: Comprehensive type hints with mypy validation
- **Error Handling**: Consistent ValidationError usage with detailed messages

### Testing Requirements
- **Unit Tests**: Isolated testing of individual components with mocking
- **Integration Tests**: End-to-end workflow validation
- **Edge Case Testing**: Comprehensive boundary condition validation
- **Performance Tests**: Load testing and memory profiling

## Getting Started

### Running the Complete DCF Engine
```python
from src.infrastructure.container import Container

# Initialize dependency container
container = Container()

# Execute complete DCF workflow
property_input = SimplifiedPropertyInput(...)
dcf_result = container.financial_metrics_service().calculate_metrics(property_input)

# Access results
print(f"NPV: ${dcf_result.npv:,.2f}")
print(f"IRR: {dcf_result.irr:.2%}")
print(f"Recommendation: {dcf_result.investment_recommendation}")
```

### Architecture Validation
```bash
# Validate Clean Architecture compliance
python scripts/validate_architecture.py

# Run comprehensive test suite
pytest src/ tests/ --cov=src --cov-report=html

# Type checking
mypy src/
```