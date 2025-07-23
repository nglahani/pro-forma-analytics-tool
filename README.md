# Pro-Forma Analytics Tool

[![Tests](https://github.com/your-org/pro-forma-analytics-tool/workflows/tests/badge.svg)](https://github.com/your-org/pro-forma-analytics-tool/actions)
[![Code Quality](https://github.com/your-org/pro-forma-analytics-tool/workflows/quality/badge.svg)](https://github.com/your-org/pro-forma-analytics-tool/actions)
[![Coverage](https://codecov.io/gh/your-org/pro-forma-analytics-tool/branch/main/graph/badge.svg)](https://codecov.io/gh/your-org/pro-forma-analytics-tool)

A production-grade real estate financial analysis platform that transforms static Excel-based pro formas into data-driven forecasting using Prophet time series analysis and Monte Carlo simulations.

## 🏗️ Architecture

This project follows **Clean Architecture** principles with clear separation of concerns:

```
src/
├── domain/              # Business Logic & Entities (Core)
│   ├── entities/        # Domain entities (immutable)
│   └── repositories/    # Repository interfaces (abstract)
├── application/         # Use Cases & Application Services
│   └── services/        # Application workflow orchestration
├── infrastructure/      # External Concerns (Databases, APIs)
│   ├── repositories/    # Concrete repository implementations
│   └── container.py     # Dependency injection container
└── presentation/        # CLI, Web Interface (Future)
```

### Key Architectural Benefits
- ✅ **Testable**: Full dependency injection with mocked interfaces
- ✅ **Maintainable**: Clear separation of business logic from infrastructure
- ✅ **Scalable**: Domain-driven design with well-defined boundaries
- ✅ **Production-Ready**: Comprehensive error handling and logging

## 🚀 Features

### 📊 Prophet Forecasting Engine
- **11 Pro Forma Parameters** forecasted using Meta's Prophet
- **5 Major MSAs** with 15+ years of historical data
- **Automatic Model Validation** with performance metrics
- **Forecast Caching** for improved performance

### 🎲 Monte Carlo Simulation
- **Advanced Scenario Generation** with economic correlations
- **Market Classification** (Bull, Bear, Neutral, Growth, Stress)
- **Risk & Growth Scoring** with composite metrics
- **Extreme Scenario Analysis** for stress testing

### 🏢 Pro Forma Parameters
1. **Interest Rates**: Treasury 10Y, Commercial Mortgage, Fed Funds
2. **Market Metrics**: Cap Rate, Vacancy Rate
3. **Growth Metrics**: Rent Growth, Expense Growth, Property Growth
4. **Lending Requirements**: LTV Ratio, Closing Costs, Lender Reserves

### 🌍 Geographic Coverage
- New York-Newark-Jersey City MSA (35620)
- Los Angeles-Long Beach-Anaheim MSA (31080)
- Chicago-Naperville-Elgin MSA (16980)
- Washington-Arlington-Alexandria MSA (47900)
- Miami-Fort Lauderdale-West Palm Beach MSA (33100)

## 📦 Installation

### Prerequisites
- Python 3.8+
- SQLite 3.x

### Setup
```bash
# Clone the repository
git clone https://github.com/your-org/pro-forma-analytics-tool.git
cd pro-forma-analytics-tool

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Initialize databases
python data_manager.py setup

# Verify installation
python test_integration.py
```

## 🔧 Usage

### Basic Forecasting
```python
from src.application.services.forecasting_service import ForecastingApplicationService
from src.domain.entities.forecast import ParameterId, ParameterType, ForecastRequest
from src.infrastructure.container import get_container

# Get configured container
container = get_container()
forecasting_service = container.resolve(ForecastingApplicationService)

# Create forecast request
parameter_id = ParameterId(
    name="cap_rate",
    geographic_code="35620",  # New York MSA
    parameter_type=ParameterType.MARKET_METRIC
)

request = ForecastRequest(
    parameter_id=parameter_id,
    horizon_years=5,
    model_type="prophet",
    confidence_level=0.95
)

# Generate forecast
forecast_result = forecasting_service.generate_forecast(request)
print(f"Forecast generated: {len(forecast_result.forecast_points)} points")
```

### Monte Carlo Simulation
```python
from src.application.services.monte_carlo_service import MonteCarloApplicationService
from src.domain.entities.monte_carlo import SimulationRequest

# Get configured container
container = get_container()
monte_carlo_service = container.resolve(MonteCarloApplicationService)

# Create simulation request
request = SimulationRequest(
    property_id="SAMPLE_PROPERTY_001",
    msa_code="35620",  # New York MSA
    num_scenarios=1000,
    horizon_years=5,
    use_correlations=True,
    confidence_level=0.95
)

# Run simulation
simulation_result = monte_carlo_service.run_simulation(request)

# Analyze results
print(f"Generated {len(simulation_result.scenarios)} scenarios")
print(f"Market scenarios: {simulation_result.summary.scenario_distribution}")
```

## 🧪 Testing

This project follows **Test-Driven Development (TDD)** and **Behavior-Driven Development (BDD)** practices.

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test types
pytest tests/unit/                    # Unit tests only
pytest tests/integration/             # Integration tests only

# Run with verbose output
pytest -v --tb=short
```

### Test Structure
```
tests/
├── unit/                # Fast, isolated unit tests
│   ├── domain/          # Domain entity tests
│   ├── application/     # Application service tests
│   └── infrastructure/  # Repository implementation tests
├── integration/         # End-to-end integration tests
└── conftest.py         # Shared test fixtures
```

## 🛠️ Development

### Code Quality Standards
```bash
# Format code
black src/ tests/
isort src/ tests/

# Lint code
flake8 src/ tests/
mypy src/

# Pre-commit hooks (recommended)
pre-commit install
pre-commit run --all-files
```

## 📊 Database Schema

### Core Tables
- **`historical_data`**: Parameter historical values
- **`forecasts`**: Cached forecast results
- **`simulations`**: Monte Carlo simulation results
- **`correlations`**: Parameter correlation matrices

### Database Files
- **`market_data.db`**: Interest rates, cap rates, economic indicators
- **`property_data.db`**: Rental market, operating expenses
- **`economic_data.db`**: Regional indicators, lending requirements
- **`forecast_cache.db`**: Prophet forecasts, correlations, simulation results

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow TDD: Write tests first
4. Implement feature following clean architecture
5. Ensure all tests pass and coverage is maintained
6. Run code quality checks (`pre-commit run --all-files`)
7. Commit changes (`git commit -m 'Add amazing feature'`)
8. Push to branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ using Clean Architecture & TDD/BDD Practices**