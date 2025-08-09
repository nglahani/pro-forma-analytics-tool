# Complete User Guide: Pro Forma Analytics Tool v2.0

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Frontend Web Application](#frontend-web-application)
4. [Property Analysis Workflow](#property-analysis-workflow)
5. [DCF Analysis Features](#dcf-analysis-features)
6. [Monte Carlo Simulation](#monte-carlo-simulation)
7. [Market Data Explorer](#market-data-explorer)
8. [Results and Visualization](#results-and-visualization)
9. [Advanced Features](#advanced-features)
10. [API Integration](#api-integration)
11. [Testing and Quality Assurance](#testing-and-quality-assurance)
12. [Troubleshooting](#troubleshooting)

## Overview

The Pro Forma Analytics Tool is a production-ready real estate investment analysis platform that transforms traditional Excel-based pro formas into sophisticated financial models. The platform provides both a modern web interface and robust backend infrastructure for comprehensive investment analysis.

### Key Features

**🏢 Property Input System**
- Interactive web forms with step-by-step guidance
- Template-based property configuration
- Real-time validation and error handling
- Multi-property comparison capabilities

**📊 DCF Analysis Engine**
- Complete 4-phase DCF workflow (Assumptions → Initial Numbers → Cash Flow → Financial Metrics)
- Prophet time series forecasting for 11 pro forma parameters
- 6-year cash flow projections with waterfall distributions
- NPV, IRR, equity multiples, and investment recommendations

**🎲 Monte Carlo Simulation**
- 500+ scenario analysis with economic correlations
- Risk assessment with growth and risk scoring
- Probabilistic investment outcome modeling
- Comprehensive statistical validation

**📈 Market Data Integration**
- 2,174+ historical data points across 5 major MSAs
- Real-time market data visualization
- Economic indicator tracking and analysis
- MSA-specific property market insights

**🔧 Production Infrastructure**
- Comprehensive testing suite (82% coverage, 320+ tests)
- Performance benchmarking and load testing
- Visual regression testing for UI components
- End-to-end workflow validation

## Getting Started

### Prerequisites

- **Python 3.10 or higher** (3.10-3.11 tested)
- **Node.js 18+** for frontend development
- **4GB RAM minimum** for optimal performance
- **Modern web browser** (Chrome, Firefox, Safari, Edge)

### Installation

#### 1. Clone and Setup Backend
```bash
# Clone repository
git clone <repository-url>
cd pro-forma-analytics-tool

# Install Python dependencies
pip install -r requirements.txt

# Initialize databases
python data_manager.py setup

# Verify installation
python demo_end_to_end_workflow.py
```

#### 2. Setup Frontend Web Application
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

#### 3. Access the Application
- **Web Interface**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs (when backend is running)

### Quick Start Example

```bash
# Run complete end-to-end analysis
python demo_end_to_end_workflow.py

# Expected output:
# NPV: $7,847,901 | IRR: 64.8% | Multiple: 9.79x
# Recommendation: STRONG_BUY | Risk Level: MODERATE
```

## Frontend Web Application

### Main Dashboard

The web application provides an intuitive interface for real estate investment analysis:

**Navigation Components:**
- **Property Analysis** - Main analysis workflow
- **Market Data Explorer** - Market trends and economic indicators  
- **Portfolio Comparison** - Multi-property analysis
- **Results Dashboard** - Analysis results and visualizations

### Property Input Interface

#### Step-by-Step Property Form

The property input form guides users through data collection:

1. **Basic Information**
   - Property name and description
   - Location (address, city, state, ZIP)
   - Property type and class

2. **Unit Configuration**
   - Residential units and average rent
   - Commercial units and lease rates
   - Square footage and unit mix

3. **Renovation Planning** 
   - Renovation duration and budget
   - Phased delivery schedule
   - Construction timeline

4. **Investment Structure**
   - Investor equity percentage
   - Self-cash requirements
   - Financing parameters

#### Template System

Pre-configured templates accelerate property input:

**Available Templates:**
- **Multifamily Basic** - Standard apartment buildings
- **Mixed-Use Commercial** - Retail + residential properties
- **Value-Add Renovation** - Properties requiring renovation
- **Ground-Up Development** - New construction projects

**Using Templates:**
```typescript
// Select template in web interface
const template = PropertyTemplates.MULTIFAMILY_BASIC;

// Customize parameters
const propertyData = {
  ...template,
  residential_units: 24,
  average_rent: 2800,
  location: "Chicago, IL"
};
```

### Real-Time Validation

The interface provides immediate feedback:

**Validation Features:**
- Field-level validation with error messages
- Business rule enforcement (e.g., realistic rent ranges)
- MSA code verification for market data integration
- Cross-field dependency validation

**Example Validation Messages:**
```
✅ Valid rent range for Chicago MSA ($2,200 - $3,500)
❌ Renovation duration exceeds typical range (max 24 months)
⚠️ Consider property insurance for commercial units
```

## Property Analysis Workflow

### Complete Analysis Process

#### 1. Property Data Entry

**Basic Property Information:**
```typescript
interface PropertyInput {
  property_name: string;
  residential_units: number;
  renovation_time_months: number;
  commercial_units: number;
  investor_equity_share_pct: number;
  residential_rent_per_unit: number;
  commercial_rent_per_unit: number;
  self_cash_percentage: number;
  city: string;
  state: string;
  purchase_price?: number;
}
```

**Required Fields:**
- Residential units (1-500 units)
- Renovation time (0-24 months)
- Commercial units (0-50 units)  
- Investor equity share (0-100%)
- Rent rates (market-validated ranges)
- Cash percentage (10-100%)

#### 2. Market Data Integration

The system automatically integrates market data:

**Data Sources:**
- **Property Market Data** - Rent growth, vacancy rates, market comparables
- **Economic Indicators** - Interest rates, cap rates, lending requirements
- **Regional Metrics** - MSA-specific growth patterns and economic conditions

**MSA Coverage:**
- New York City (MSA: 35620)
- Los Angeles (MSA: 31080) 
- Chicago (MSA: 16980)
- Washington DC (MSA: 47900)
- Miami (MSA: 33100)

#### 3. Analysis Execution

**Phase 1: DCF Assumptions**
- Monte Carlo scenario to DCF parameter mapping
- Economic correlation modeling (23 relationships)
- Market condition classification (Bull/Bear/Neutral/Growth/Stress)

**Phase 2: Initial Numbers**
- Acquisition cost calculations (purchase, closing, renovation)
- Financing term determination (LTV, rates, reserves)
- Initial income and expense projections

**Phase 3: Cash Flow Projections** 
- 6-year annual cash flow modeling
- Renovation period income interruption
- Waterfall distribution calculations

**Phase 4: Financial Metrics**
- NPV calculations with terminal value
- IRR optimization (sub-0.01ms performance)
- Equity multiple and payback period analysis
- Investment recommendation generation

### Batch Analysis

For multiple properties or scenario testing:

```bash
# Process multiple properties
python batch_analysis.py --input-dir properties/ --output results/

# Compare scenarios
python scenario_comparison.py --base-case property1.json --scenarios scenarios/
```

## DCF Analysis Features

### Financial Calculations

#### Net Present Value (NPV)
```python
# NPV calculation includes:
# - Initial investment (purchase + renovation + costs)
# - Annual cash flows (rental income - expenses - debt service)
# - Terminal value (sale proceeds at year 6)
# - Discount rate (weighted average cost of capital)

npv = sum(annual_cash_flows / (1 + discount_rate) ** year) - initial_investment
```

#### Internal Rate of Return (IRR)
```python
# Optimized IRR calculation using Newton-Raphson method
# Performance: <0.01ms for standard 6-year cash flow
# Handles edge cases: negative cash flows, multiple IRRs, no solution

irr = optimize_irr(cash_flows, initial_guess=0.15, max_iterations=100)
```

#### Equity Multiple
```python
# Total distributions divided by invested equity
equity_multiple = (total_distributions + terminal_proceeds) / equity_invested

# Example calculation:
# Equity Investment: $1,050,000
# 6-Year Distributions: $2,450,000  
# Terminal Proceeds: $7,875,000
# Equity Multiple: 9.79x
```

### Cash Flow Modeling

#### Waterfall Distribution Structure

**Priority Levels:**
1. **Operating Expenses** - Property taxes, insurance, management
2. **Debt Service** - Principal and interest payments
3. **Capital Reserves** - Maintenance and replacement reserves
4. **Investor Distributions** - Based on equity percentage
5. **Operator Promote** - Performance-based distributions

#### Renovation Period Modeling

**Income Interruption:**
- Phased unit delivery during renovation
- Partial income recognition based on completion percentage
- Construction loan interest capitalization

**Example Renovation Impact:**
```
Month 1-3: 0% rental income (full renovation)
Month 4-6: 60% rental income (partial occupancy)
Month 7-8: 85% rental income (substantial completion)
Month 9+: 100% stabilized income
```

### Market-Based Parameters

#### Prophet Forecasting Integration

**Forecasted Parameters:**
1. Commercial mortgage rates (6-year projection)
2. Cap rates by property type and MSA
3. Rent growth rates (residential and commercial)
4. Operating expense growth
5. Property value appreciation
6. Vacancy rates and market conditions

**Forecasting Process:**
```python
# Prophet model generates 6-year forecasts for each parameter
forecast = prophet_model.predict(future_periods=6)

# Example output:
forecast_data = {
    'commercial_mortgage_rate': [0.075, 0.077, 0.079, 0.081, 0.083, 0.085],
    'rent_growth': [0.025, 0.028, 0.032, 0.029, 0.025, 0.022],
    'cap_rate': [0.065, 0.065, 0.066, 0.067, 0.068, 0.069]
}
```

## Monte Carlo Simulation

### Scenario Generation

The Monte Carlo engine generates 500+ realistic market scenarios:

**Economic Modeling:**
- 23 correlation relationships between economic parameters
- Historical volatility patterns from 15+ years of data
- Market regime modeling (recession, growth, stable periods)

**Scenario Classification:**
- **Bull Market**: High growth, low rates, strong fundamentals
- **Bear Market**: Economic contraction, high rates, weak demand
- **Neutral**: Stable economic conditions, moderate growth
- **Growth**: Strong economic expansion, increasing rates
- **Stress**: Economic stress testing with adverse conditions

### Risk Assessment

#### Growth Score Calculation
```python
# Growth score based on parameter favorability
growth_factors = {
    'rent_growth': weight * normalize(rent_growth_rate),
    'property_appreciation': weight * normalize(appreciation_rate),
    'market_conditions': weight * normalize(market_score)
}

growth_score = sum(growth_factors.values())  # Range: 0.0 - 1.0
```

#### Risk Score Calculation  
```python
# Risk score based on parameter volatility and uncertainty
risk_factors = {
    'interest_rate_volatility': weight * volatility_measure,
    'market_uncertainty': weight * uncertainty_index,
    'concentration_risk': weight * geographic_concentration
}

risk_score = sum(risk_factors.values())  # Range: 0.0 - 1.0
```

### Simulation Results

**Statistical Outputs:**
- **Percentile Analysis**: P10, P25, P50, P75, P90 outcomes
- **Risk Metrics**: Value at Risk (VaR), Expected Shortfall
- **Scenario Distribution**: Outcome probability distributions
- **Stress Testing**: Worst-case scenario analysis

**Example Results:**
```
Monte Carlo Analysis (1,000 scenarios):
├── NPV Distribution
│   ├── P10: $1,250,000
│   ├── P50: $7,847,901  
│   └── P90: $15,420,000
├── IRR Distribution
│   ├── P10: 18.5%
│   ├── P50: 64.8%
│   └── P90: 127.3%
└── Risk Assessment
    ├── Probability of Loss: 2.1%
    ├── Expected Return: 68.4%
    └── Risk-Adjusted Return: 4.2x
```

## Market Data Explorer

### Economic Indicators

The Market Data Explorer provides comprehensive market analysis:

**National Economic Data:**
- Federal funds rate and treasury yields
- Inflation rates and economic growth indicators
- Employment statistics and consumer confidence
- Real estate market indices and trends

**MSA-Specific Metrics:**
- Population growth and demographic trends
- Employment growth and income levels
- Housing supply and demand dynamics
- Commercial real estate fundamentals

### Interactive Visualizations

**Chart Types:**
- **Time Series**: Historical trends and forecasted projections
- **Correlation Heatmaps**: Economic parameter relationships
- **Distribution Charts**: Monte Carlo scenario outcomes
- **Comparative Analysis**: Multi-MSA performance comparison

**Available Views:**
```typescript
interface MarketDataViews {
  timeSeries: {
    parameter: string;
    timeRange: 'historical' | 'forecast' | 'combined';
    msas: string[];
  };
  
  correlation: {
    parameters: string[];
    timeWindow: number;
    method: 'pearson' | 'spearman';
  };
  
  distribution: {
    scenarios: number;
    metric: 'npv' | 'irr' | 'multiple';
    confidenceLevel: number;
  };
}
```

### Data Export and Integration

**Export Formats:**
- CSV for spreadsheet analysis
- JSON for programmatic access
- PDF reports with visualizations
- Excel workbooks with multiple sheets

**API Integration:**
```bash
# Fetch market data via API
curl -X GET "http://localhost:8000/api/market-data/msa/16980" \
  -H "accept: application/json"

# Response format:
{
  "msa_code": "16980",
  "msa_name": "Chicago-Naperville-Elgin, IL-IN-WI",
  "data": {
    "rent_growth": [0.025, 0.028, 0.032],
    "cap_rates": [0.065, 0.066, 0.067],
    "vacancy_rates": [0.08, 0.075, 0.07]
  }
}
```

## Results and Visualization

### DCF Results Dashboard

The results dashboard provides comprehensive investment analysis:

**Key Metrics Display:**
- **Financial Performance**: NPV, IRR, Equity Multiple
- **Cash Flow Analysis**: Annual distributions and terminal value
- **Investment Timeline**: Cash-on-cash returns by year
- **Risk Assessment**: Scenario analysis and stress testing

**Interactive Features:**
- **Scenario Comparison**: Side-by-side analysis of different assumptions
- **Sensitivity Analysis**: Parameter impact on key metrics
- **Waterfall Charts**: Cash flow distribution visualization
- **Timeline Views**: Investment performance over time

### Chart Components

#### Financial Metrics Visualization
```typescript
// Example chart configuration
const MetricsChart: React.FC = () => {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart data={metricsData}>
        <XAxis dataKey="metric" />
        <YAxis />
        <Tooltip formatter={formatCurrency} />
        <Bar dataKey="value" fill="#8884d8" />
      </BarChart>
    </ResponsiveContainer>
  );
};
```

#### Cash Flow Projections
```typescript
// Cash flow timeline visualization
const CashFlowChart: React.FC = () => {
  return (
    <LineChart data={cashFlowData}>
      <XAxis dataKey="year" />
      <YAxis />
      <Line type="monotone" dataKey="operating_cash_flow" stroke="#82ca9d" />
      <Line type="monotone" dataKey="distributions" stroke="#8884d8" />
    </LineChart>
  );
};
```

#### Monte Carlo Distribution
```typescript
// Probability distribution visualization
const DistributionChart: React.FC = () => {
  return (
    <AreaChart data={distributionData}>
      <XAxis dataKey="outcome" />
      <YAxis />
      <Area type="monotone" dataKey="probability" fill="#8884d8" />
    </AreaChart>
  );
};
```

### Report Generation

**Automated Reports:**
- **Investment Summary**: Executive overview with key metrics
- **Detailed Analysis**: Complete financial model and assumptions
- **Risk Assessment**: Monte Carlo results and scenario analysis
- **Market Context**: Economic conditions and market data

**Report Formats:**
- **PDF**: Professional presentation-ready reports
- **Excel**: Detailed spreadsheets with formulas and data
- **Web View**: Interactive dashboard with drill-down capabilities
- **API Response**: JSON format for programmatic access

## Advanced Features

### Scenario Analysis

#### Custom Scenario Creation
```typescript
// Define custom market scenarios
const customScenario: MarketScenario = {
  scenario_id: 'CONSERVATIVE_2024',
  description: 'Conservative growth with rising rates',
  parameters: {
    commercial_mortgage_rate: [0.080, 0.085, 0.090, 0.095, 0.100, 0.105],
    rent_growth: [0.015, 0.020, 0.022, 0.018, 0.015, 0.012],
    cap_rate: [0.070, 0.072, 0.074, 0.076, 0.078, 0.080],
    vacancy_rate: [0.08, 0.09, 0.08, 0.07, 0.07, 0.06]
  }
};
```

#### Stress Testing
```python
# Define stress test scenarios
stress_scenarios = {
    'recession': {
        'rent_growth': [-0.05, -0.03, 0.00, 0.01, 0.02, 0.025],
        'vacancy_rate': [0.15, 0.18, 0.15, 0.12, 0.10, 0.08],
        'cap_rate': [0.085, 0.090, 0.095, 0.090, 0.085, 0.080]
    },
    'high_inflation': {
        'mortgage_rate': [0.090, 0.100, 0.110, 0.105, 0.095, 0.090],
        'operating_expense_growth': [0.08, 0.10, 0.12, 0.08, 0.06, 0.05]
    }
}
```

### Portfolio Analysis

#### Multi-Property Comparison
```typescript
// Compare multiple properties
interface PortfolioComparison {
  properties: PropertyAnalysis[];
  metrics: {
    weighted_avg_irr: number;
    portfolio_npv: number;
    diversification_score: number;
    concentration_risk: number;
  };
}

// Example usage
const portfolio = await analyzePortfolio([
  'chicago_multifamily.json',
  'miami_mixed_use.json', 
  'nyc_value_add.json'
]);
```

#### Risk Diversification Analysis
```python
# Calculate portfolio-level metrics
def analyze_portfolio_risk(properties):
    # Geographic diversification
    msa_concentration = calculate_msa_concentration(properties)
    
    # Property type diversification  
    type_concentration = calculate_type_concentration(properties)
    
    # Correlation analysis
    correlation_matrix = calculate_cross_correlations(properties)
    
    return {
        'diversification_score': (100 - msa_concentration - type_concentration) / 100,
        'correlation_risk': max(correlation_matrix.values()),
        'portfolio_var': calculate_portfolio_var(properties)
    }
```

### Performance Optimization

#### Calculation Performance
```python
# Optimized IRR calculation
class OptimizedIRR:
    def __init__(self):
        self.cache = {}
        
    def calculate(self, cash_flows):
        cache_key = hash(tuple(cash_flows))
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        # Newton-Raphson optimization
        irr = self.newton_raphson(cash_flows)
        self.cache[cache_key] = irr
        return irr
        
    def newton_raphson(self, cash_flows):
        # Implementation achieves <0.01ms performance
        pass
```

#### Memory Management
```python
# Efficient memory usage for large Monte Carlo simulations
class MemoryOptimizedSimulation:
    def __init__(self, batch_size=100):
        self.batch_size = batch_size
        
    def run_simulation(self, scenarios=1000):
        results = []
        for batch_start in range(0, scenarios, self.batch_size):
            batch = self.process_batch(batch_start)
            results.extend(batch)
            # Clear intermediate calculations
            gc.collect()
        return results
```

## API Integration

### RESTful API Endpoints

#### Property Analysis
```bash
# Submit property for analysis
POST /api/properties/analyze
Content-Type: application/json

{
  "property_name": "Test Property",
  "residential_units": 24,
  "renovation_time_months": 6,
  "commercial_units": 0,
  "investor_equity_share_pct": 75.0,
  "residential_rent_per_unit": 2800,
  "commercial_rent_per_unit": 0,
  "self_cash_percentage": 30.0,
  "city": "Chicago",
  "state": "IL",
  "purchase_price": 3500000
}
```

#### Monte Carlo Simulation
```bash
# Run Monte Carlo analysis
POST /api/monte-carlo/simulate
Content-Type: application/json

{
  "property_id": "prop_123",
  "scenarios": 1000,
  "confidence_level": 0.95,
  "custom_parameters": {
    "mortgage_rate_volatility": 0.15,
    "rent_growth_variance": 0.02
  }
}
```

#### Market Data Access
```bash
# Get market data for MSA
GET /api/market-data/msa/{msa_code}?parameters=rent_growth,cap_rate&years=6

# Response:
{
  "msa_code": "16980",
  "msa_name": "Chicago-Naperville-Elgin, IL-IN-WI",
  "forecast": {
    "rent_growth": [0.025, 0.028, 0.032, 0.029, 0.025, 0.022],
    "cap_rate": [0.065, 0.065, 0.066, 0.067, 0.068, 0.069]
  },
  "confidence_intervals": {
    "rent_growth": {
      "lower": [0.015, 0.018, 0.022, 0.019, 0.015, 0.012],
      "upper": [0.035, 0.038, 0.042, 0.039, 0.035, 0.032]
    }
  }
}
```

### Authentication and Rate Limiting

```bash
# API authentication (when enabled)
POST /api/auth/login
{
  "username": "user@example.com",
  "password": "password"
}

# Use JWT token for subsequent requests
Authorization: Bearer <jwt_token>

# Rate limiting headers
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

### SDK Integration

#### Python SDK
```python
from proforma_client import ProFormaClient

# Initialize client
client = ProFormaClient(base_url="http://localhost:8000")

# Analyze property
result = client.analyze_property({
    "property_name": "Investment Property",
    "residential_units": 20,
    "city": "Chicago",
    "state": "IL"
    # ... other parameters
})

# Access results
print(f"NPV: ${result.npv:,.0f}")
print(f"IRR: {result.irr:.1%}")
print(f"Recommendation: {result.recommendation}")
```

#### JavaScript/TypeScript SDK
```typescript
import { ProFormaClient } from '@proforma/client';

// Initialize client
const client = new ProFormaClient({
  baseURL: 'http://localhost:8000',
  apiKey: process.env.PROFORMA_API_KEY
});

// Analyze property
const result = await client.analyzeProperty({
  propertyName: 'Investment Property',
  residentialUnits: 20,
  city: 'Chicago',
  state: 'IL'
  // ... other parameters
});

// Process results
console.log(`NPV: $${result.npv.toLocaleString()}`);
console.log(`IRR: ${(result.irr * 100).toFixed(1)}%`);
```

## Testing and Quality Assurance

### Comprehensive Testing Suite

The platform includes extensive testing infrastructure:

**Test Coverage:**
- **Unit Tests**: 82% coverage, 320+ test methods
- **Integration Tests**: Complete workflow validation
- **Performance Tests**: Load and benchmark testing
- **End-to-End Tests**: Full user workflow automation
- **Visual Regression**: UI component consistency testing

### Running Tests

#### Backend Testing
```bash
# Run all tests with coverage
python -m pytest tests/ -v --cov=src --cov=core --cov=monte_carlo --cov-fail-under=82

# Performance testing
python tests/performance/test_irr_performance.py

# Architecture validation
python scripts/validate_architecture.py

# End-to-end workflow
python demo_end_to_end_workflow.py
```

#### Frontend Testing
```bash
# Unit and integration tests
npm test

# Performance testing
npm run test:performance

# End-to-end testing
npm run test:e2e

# Visual regression testing
npm run test:visual

# Load testing
npm run test:load
```

### Quality Assurance Metrics

**Performance Benchmarks:**
- IRR calculation: <0.01ms per calculation
- Monte Carlo simulation: <10 seconds for 1000 scenarios
- API response time: <3 seconds for DCF analysis
- Memory usage: <500MB for typical analysis

**Reliability Metrics:**
- Test pass rate: >98% across all test suites
- Error rate: <1% in production scenarios
- Uptime target: >99.9% availability
- Data accuracy: Validated against Excel benchmarks

### Automated Quality Gates

**CI/CD Pipeline:**
- Multi-Python version testing (3.10-3.11)
- Code quality validation (black, isort, flake8)
- Type checking with mypy
- Security scanning with bandit
- Performance regression detection

**Code Quality Standards:**
```bash
# Format code
black src/ tests/
isort src/ tests/

# Lint code  
flake8 src/ tests/

# Type checking
mypy src/

# Security scan
bandit -r src/
```

## Troubleshooting

### Common Issues

#### Installation Problems

**Python Dependencies:**
```bash
# Clear pip cache
pip cache purge

# Reinstall dependencies
pip install --no-cache-dir -r requirements.txt

# Check Python version
python --version  # Should be 3.10+
```

**Database Issues:**
```bash
# Reset databases
python data_manager.py reset

# Validate database integrity
python scripts/validate_database.py

# Check database permissions
ls -la data/databases/
```

**Frontend Build Issues:**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check Node.js version
node --version  # Should be 18+
```

#### Runtime Errors

**Memory Issues:**
```bash
# Monitor memory usage
python scripts/profile_memory.py

# Increase Python heap size
export PYTHONHASHSEED=0
python -c "import sys; print(sys.version)"
```

**Performance Issues:**
```bash
# Profile performance
python scripts/profile_performance.py

# Check database indexes
python scripts/optimize_database_indexes.py

# Monitor system resources
htop  # Linux/Mac
taskmgr  # Windows
```

**API Connection Issues:**
```bash
# Check API status
curl -X GET "http://localhost:8000/health"

# Validate API configuration
python -c "import src.presentation.api.main; print('API imports OK')"

# Check port availability
netstat -tuln | grep 8000
```

### Error Messages and Solutions

**Common Error Patterns:**

**ValidationError: Invalid property parameters**
- Solution: Check required fields and value ranges
- Validation: Use property input form for guided entry
- Reference: See property input validation rules in docs

**DatabaseError: Cannot connect to database**
- Solution: Initialize databases with `python data_manager.py setup`
- Check: Database file permissions and disk space
- Reset: Use `python data_manager.py reset` if corrupted

**CalculationError: IRR calculation failed**
- Solution: Verify cash flow inputs are realistic
- Check: Ensure positive initial investment
- Debug: Use `python scripts/debug_irr.py` for detailed analysis

**MemoryError: Insufficient memory for Monte Carlo**
- Solution: Reduce scenario count or use batch processing
- Optimize: Set batch size with `BATCH_SIZE=100` environment variable
- Monitor: Use memory profiling tools to identify bottlenecks

### Debug Mode

**Enable Verbose Logging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run analysis with detailed logging
python demo_end_to_end_workflow.py --debug
```

**Performance Profiling:**
```bash
# Profile specific operations
python -m cProfile -o profile.stats scripts/analyze_property.py

# View profiling results
python -c "import pstats; pstats.Stats('profile.stats').sort_stats('tottime').print_stats(10)"
```

### Getting Help

**Documentation Resources:**
1. **Technical Documentation**: `/docs` folder with comprehensive guides
2. **Code Examples**: `demo_end_to_end_workflow.py` and test files
3. **API Documentation**: OpenAPI spec at `/docs` when backend is running

**Validation Tools:**
1. **System Check**: `python scripts/validate_system.py`
2. **Database Validation**: `python scripts/validate_database.py`
3. **Architecture Check**: `python scripts/validate_architecture.py`

**Support Channels:**
- Check existing issues in project repository
- Review comprehensive test suite for usage patterns
- Examine validation scripts for system health checks

### Performance Optimization

**System Optimization:**
```bash
# Optimize database indexes
python scripts/optimize_database_indexes.py

# Clear analysis cache
rm -rf cache/

# Monitor resource usage
python scripts/monitor_resources.py
```

**Memory Management:**
```python
# Enable garbage collection optimization
import gc
gc.set_threshold(700, 10, 10)

# Monitor memory usage
import tracemalloc
tracemalloc.start()
# ... run analysis ...
current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
```

---

## Next Steps

### For Real Estate Investors

1. **Start with Demo Analysis**
   - Run `python demo_end_to_end_workflow.py` to see complete workflow
   - Review sample property analysis results and methodology

2. **Input Your Properties**
   - Use web interface at http://localhost:3000 for guided property input
   - Start with template-based configurations for common property types

3. **Compare Investment Options**
   - Analyze multiple properties using batch processing or web interface
   - Use Monte Carlo simulation for risk assessment and scenario analysis

4. **Integrate with Your Workflow**
   - Export results to Excel for further analysis
   - Use API integration for portfolio management systems

### For Developers

1. **Understand the Architecture**
   - Review Clean Architecture implementation in `/src`
   - Study domain entities and application services structure

2. **Explore Testing Infrastructure**
   - Examine comprehensive test suite (320+ tests, 82% coverage)
   - Run performance benchmarks and load testing suites

3. **Extend Functionality**
   - Add new property types or analysis features
   - Implement additional market data sources or forecasting models

4. **Deploy to Production**
   - Follow deployment guide in `/docs/DEPLOYMENT.md`
   - Configure monitoring and performance optimization

---

*This guide covers the complete feature set of the Pro Forma Analytics Tool v2.0. For specific technical implementation details, refer to the technical documentation in the `/docs` folder.*