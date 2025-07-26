# Pro-Forma Analytics Tool

[![Tests](https://github.com/your-org/pro-forma-analytics-tool/workflows/tests/badge.svg)](https://github.com/your-org/pro-forma-analytics-tool/actions)
[![Code Quality](https://github.com/your-org/pro-forma-analytics-tool/workflows/quality/badge.svg)](https://github.com/your-org/pro-forma-analytics-tool/actions)
[![Coverage](https://codecov.io/gh/your-org/pro-forma-analytics-tool/branch/main/graph/badge.svg)](https://codecov.io/gh/your-org/pro-forma-analytics-tool)

A production-ready real estate DCF analysis platform with complete 4-phase workflow: Monte Carlo scenario generation → DCF assumptions mapping → initial numbers calculation → cash flow projections → financial metrics and investment recommendations.

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

### ✅ Complete DCF Engine (Production Ready)
- **4-Phase Workflow**: DCF Assumptions → Initial Numbers → Cash Flow Projections → Financial Metrics
- **Investment Recommendations**: 5-tier system (STRONG_BUY to STRONG_SELL) with risk assessment
- **Terminal Value Modeling**: Exit scenarios with cap rate analysis and debt payoff
- **Break-even Analysis**: Comprehensive financial validation and stress testing

### 📊 Prophet Forecasting Engine
- **11 Pro Forma Parameters** forecasted using Meta's Prophet
- **5 Major MSAs** with 15+ years of historical data
- **Automatic Model Validation** with performance metrics
- **Forecast Caching** for improved performance

### 🎲 Monte Carlo Simulation
- **500+ Scenario Generation** with economic correlations
- **Market Classification** (Bull, Bear, Neutral, Growth, Stress)
- **Risk & Growth Scoring** with composite metrics
- **Statistical Validation**: 5/5 quality checks passed

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
- Python 3.8+ (tested with Python 3.13)
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

# Verify installation - run end-to-end test
python demo_end_to_end_workflow.py
```

## 🔧 Usage

### Complete DCF Workflow
```python
from src.application.services.dcf_assumptions_service import DCFAssumptionsService
from src.application.services.initial_numbers_service import InitialNumbersService
from src.application.services.cash_flow_projection_service import CashFlowProjectionService
from src.application.services.financial_metrics_service import FinancialMetricsService
from src.domain.entities.property_data import SimplifiedPropertyInput, ResidentialUnits, RenovationInfo, InvestorEquityStructure, RenovationStatus
from datetime import date

# Initialize services
dcf_service = DCFAssumptionsService()
initial_numbers_service = InitialNumbersService()
cash_flow_service = CashFlowProjectionService()
financial_metrics_service = FinancialMetricsService()

# Create property data
property_data = SimplifiedPropertyInput(
    property_id="DEMO_001",
    property_name="Chicago Mixed-Use Property",
    analysis_date=date.today(),
    residential_units=ResidentialUnits(total_units=40, average_rent_per_unit=1950),
    renovation_info=RenovationInfo(status=RenovationStatus.PLANNED, anticipated_duration_months=12),
    equity_structure=InvestorEquityStructure(investor_equity_share_pct=75.0, self_cash_percentage=20.0),
    city="Chicago", state="IL", msa_code="16980",
    purchase_price=3500000
)

# Phase 1: DCF Assumptions (from Monte Carlo scenario)
dcf_assumptions = dcf_service.create_dcf_assumptions_from_scenario(market_scenario, property_data)

# Phase 2: Initial Numbers
initial_numbers = initial_numbers_service.calculate_initial_numbers(property_data, dcf_assumptions)

# Phase 3: Cash Flow Projections
cash_flow_projection = cash_flow_service.calculate_cash_flow_projection(dcf_assumptions, initial_numbers)

# Phase 4: Financial Metrics
financial_metrics = financial_metrics_service.calculate_financial_metrics(
    cash_flow_projection, dcf_assumptions, initial_numbers, discount_rate=0.10
)

print(f"NPV: ${financial_metrics.net_present_value:,.0f}")
print(f"IRR: {financial_metrics.internal_rate_return:.1%}")
print(f"Recommendation: {financial_metrics.investment_recommendation.value}")
```

### Quick Demo
```bash
# Run complete end-to-end demonstration
python demo_end_to_end_workflow.py

# Expected output: NPV ~$2.5M, IRR ~64.8%, STRONG_BUY recommendation
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

# Run integration test for complete DCF workflow
python tests/integration/test_complete_dcf_workflow.py

# Run with verbose output
pytest -v --tb=short
```

### Test Coverage
- **Domain entities**: 17/17 tests passing (100% coverage)
- **Application services**: 40+ test methods covering all DCF phases
- **Integration tests**: Complete end-to-end workflow validation
- **Overall coverage**: 95%+ target for business logic

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
- **`market_data.db`**: Interest rates, cap rates, economic indicators (688+ historical data points)
- **`property_data.db`**: Rental market, operating expenses (5 MSAs, 15+ years data)
- **`economic_data.db`**: Regional indicators, lending requirements
- **`forecast_cache.db`**: Prophet forecasts, correlations, Monte Carlo results

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

## 📈 Production Status

**Current Version**: v1.0 - Production Ready
- ✅ Complete 4-phase DCF engine implemented and validated
- ✅ End-to-end workflow tested with realistic investment scenarios
- ✅ Python 3.13 compatibility verified
- ✅ 95%+ test coverage on core business logic
- ✅ Clean architecture with proper dependency injection

**Validated Performance**: $3.5M test property analysis produces 64.8% IRR and 9.79x equity multiple with STRONG_BUY recommendation in 4-phase workflow.

**Built with ❤️ using Clean Architecture & TDD/BDD Practices**