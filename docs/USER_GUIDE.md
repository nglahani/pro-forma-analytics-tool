# User Guide: Pro Forma Analytics Tool v1.3

Complete guide to using the production-ready real estate investment analysis platform with comprehensive 4-phase DCF engine, Monte Carlo simulation, and 2,174+ historical data points.

## Quick Start

### Run Complete DCF Analysis
```bash
# Execute the end-to-end workflow demonstration
python demo_end_to_end_workflow.py
```

**Expected Output:**
```
[PHASE 1] Creating DCF assumptions from Monte Carlo scenario...
[PHASE 2] Calculating initial numbers and financing...
[PHASE 3] Generating 6-year cash flow projections...
[PHASE 4] Computing financial metrics and investment analysis...

FINANCIAL RESULTS:
NPV: $2,503,000 | IRR: 64.8% | Multiple: 9.79x
Recommendation: STRONG_BUY | Risk Level: MODERATE

SUCCESS: END-TO-END WORKFLOW TEST PASSED
✅ Production-grade validation with 2,174+ historical data points
✅ 96%+ test coverage with 320+ comprehensive test methods
✅ Sub-second analysis with optimized IRR calculations (<0.01ms)
```

This demonstration processes a $3.5M Chicago mixed-use property through all DCF phases using production-grade market data and statistical validation.

## Understanding the 4-Phase DCF Workflow

### Phase 1: DCF Assumptions
- Converts Monte Carlo market scenarios into DCF parameters using 2,174+ historical data points
- Maps 11 pro forma metrics to 6-year projections with statistical validation
- Applies economic correlations and market conditions across 5 major MSAs (NYC, LA, Chicago, DC, Miami)
- Leverages Prophet time-series forecasting for enhanced accuracy

### Phase 2: Initial Numbers  
- Calculates acquisition costs (purchase price, closing costs, renovation CapEx) with production-grade validation
- Determines financing terms (loan amounts, LTV ratios, lender reserves) using market-based parameters
- Projects initial rental income and operating expenses with MSA-specific adjustments
- Incorporates comprehensive edge case handling and validation

### Phase 3: Cash Flow Projections
- Generates annual cash flows for Years 0-5 with sophisticated waterfall modeling
- Models renovation periods with income interruption and phased unit delivery
- Calculates waterfall distributions between investors and operators with detailed equity structures
- Implements comprehensive business logic with 96%+ test coverage

### Phase 4: Financial Metrics
- Computes NPV, IRR, equity multiples, and payback periods with optimized algorithms (<0.01ms IRR calculations)
- Models terminal value and exit scenarios using cap rate projections
- Provides investment recommendations (STRONG_BUY to STRONG_SELL) with risk assessment
- Includes comprehensive performance validation and regression testing

## Property Input Requirements

The system requires 7 core data fields for property analysis, with comprehensive validation and production-grade error handling:

### Required Inputs

1. **Residential Units** - Total count of residential rental units
2. **Renovation Time** - Expected duration in months (0 = no renovation)  
3. **Commercial Units** - Count of commercial spaces (0 = residential only)
4. **Investor Equity Share** - Percentage ownership for investors (0-100%)
5. **Residential Rent** - Average monthly rent per residential unit
6. **Commercial Rent** - Average monthly rent per commercial space
7. **Self Cash Percentage** - Percentage of purchase price paid in cash

### Optional Inputs
- Purchase price (enables additional financial metrics and terminal value calculations)
- Location (city/state for MSA-specific market analysis using 2,174+ data points)
- Property name and analysis date (for tracking and reporting)

### Data Validation Features
- **Input Validation**: Comprehensive business rule checking with detailed error messages
- **Range Validation**: Realistic bounds for all numeric inputs with market-based constraints
- **MSA Integration**: Automatic MSA code lookup and validation for 5 major metropolitan areas
- **Edge Case Handling**: Robust handling of zero values, extreme scenarios, and boundary conditions

## Creating Property Analysis

### Method 1: Using Domain Entities (Recommended)

```python
from src.domain.entities.property_data import (
    SimplifiedPropertyInput, ResidentialUnits, CommercialUnits, 
    RenovationInfo, InvestorEquityStructure, RenovationStatus
)
from datetime import date

# Create property input
property_data = SimplifiedPropertyInput(
    property_id="ANALYSIS_001",
    property_name="Mixed-Use Investment",
    analysis_date=date.today(),
    residential_units=ResidentialUnits(
        total_units=24,
        average_rent_per_unit=2800
    ),
    commercial_units=CommercialUnits(
        total_units=3,
        average_rent_per_unit=4500
    ),
    renovation_info=RenovationInfo(
        status=RenovationStatus.PLANNED,
        anticipated_duration_months=8
    ),
    equity_structure=InvestorEquityStructure(
        investor_equity_share_pct=75.0,
        self_cash_percentage=30.0
    ),
    city="Chicago",
    state="IL", 
    msa_code="16980",
    purchase_price=3500000
)
```

### Method 2: Study the Demo Implementation

The `demo_end_to_end_workflow.py` file provides a complete working example:

1. **Property Creation** - Shows how to construct property data with all required fields
2. **Market Scenarios** - Demonstrates Monte Carlo scenario structure  
3. **Service Integration** - Examples of calling each DCF phase service
4. **Results Analysis** - How to interpret NPV, IRR, and investment recommendations

## Investment Analysis Results

### Financial Metrics Explained

**Net Present Value (NPV)**
- Dollar value added by the investment at specified discount rate
- Positive NPV indicates value creation
- Higher NPV suggests better investment opportunity

**Internal Rate of Return (IRR)**  
- Annualized return rate that makes NPV equal to zero
- Compare against target return rates and alternative investments
- Consider risk level when evaluating IRR attractiveness

**Equity Multiple**
- Total cash returned divided by total cash invested
- Shows how many times initial investment is recovered
- Accounts for both ongoing distributions and terminal sale proceeds

**Investment Recommendations**
- **STRONG_BUY**: Exceptional returns with acceptable risk
- **BUY**: Good returns with moderate risk
- **HOLD**: Marginal returns, consider alternatives  
- **SELL**: Poor returns or high risk
- **STRONG_SELL**: Significant value destruction likely

### Risk Assessment

**Risk Levels**
- **LOW**: Stable returns with minimal downside
- **MODERATE**: Balanced risk-return profile
- **HIGH**: Significant volatility with higher return potential
- **VERY_HIGH**: Speculative investment with extreme outcomes

## Advanced Usage

### Running Multiple Scenarios

To analyze different market conditions, the tool can process multiple Monte Carlo scenarios:

```python
# The integration tests demonstrate multi-scenario analysis
# See: tests/integration/test_complete_dcf_workflow.py
# Method: test_complete_dcf_workflow_multiple_scenarios()
```

### Custom Market Scenarios

Create custom market assumptions by modifying scenario parameters:

```python
custom_scenario = {
    'scenario_id': 'CUSTOM_CONSERVATIVE',
    'forecasted_parameters': {
        'commercial_mortgage_rate': [0.075, 0.077, 0.079, 0.081, 0.083, 0.085],
        'cap_rate': [0.070, 0.070, 0.070, 0.070, 0.070, 0.070],
        'rent_growth': [0.0, 0.025, 0.028, 0.022, 0.025, 0.020],
        # ... additional parameters
    }
}
```

### Performance Monitoring

Track analysis performance and validate results with comprehensive testing framework:

```bash
# Run comprehensive test suite with coverage enforcement
python -m pytest tests/ -v --cov=src --cov=core --cov=monte_carlo --cov-fail-under=96

# Performance benchmarking (IRR calculations <0.01ms)
python tests/performance/test_irr_performance.py

# Memory profiling and optimization validation
python scripts/profile_memory.py

# End-to-end workflow validation with production data
python demo_end_to_end_workflow.py

# Architecture compliance validation
python scripts/validate_architecture.py

# Database performance optimization check
python scripts/monitor_database_performance.py
```

### Quality Assurance Features
- **96%+ Test Coverage**: 320+ test methods including comprehensive edge cases
- **Performance Benchmarking**: Automated regression testing for calculation speed
- **Memory Optimization**: Efficient resource usage with cleanup validation
- **Architecture Validation**: Clean Architecture compliance checking
- **Data Integrity**: Production-grade validation with 2,174+ historical data points

## Troubleshooting

### Common Issues

**Import Errors**
- Ensure all dependencies installed: `pip install -r requirements.txt`
- Use Python 3.8-3.13 (multi-version CI/CD validation)
- Verify virtual environment activation and path configuration

**Database Errors**  
- Initialize databases: `python data_manager.py setup`
- Check database permissions and file paths
- Validate database schema with `python scripts/optimize_database_indexes.py`
- Monitor database performance with comprehensive profiling tools

**Calculation Errors**
- Verify all required property fields are provided with validation
- Check that numeric inputs are positive and realistic using business rules
- Ensure MSA codes are valid for market analysis (5 supported MSAs)
- Use comprehensive error messages and debugging information
- Validate edge cases with extensive test coverage (320+ test methods)

**Performance Issues**
- Check IRR calculation performance (should be <0.01ms)
- Monitor memory usage with profiling tools
- Validate database query optimization
- Use performance regression testing for validation

### Getting Help

1. **Review Examples**: Start with `demo_end_to_end_workflow.py` for comprehensive workflow
2. **Check Tests**: 320+ test methods in `tests/` demonstrate usage patterns and edge cases
3. **Read Documentation**: Extensive technical documentation in `/docs` with working examples
4. **Validate Installation**: Run comprehensive test suite to verify system functionality
5. **Performance Analysis**: Use profiling tools in `scripts/` for performance optimization
6. **Architecture Review**: Study Clean Architecture implementation with domain-driven design
7. **Quality Validation**: Use CI/CD pipeline tools for comprehensive quality assurance

## Next Steps

### For Real Estate Investors
1. Create property data using your actual investment parameters with comprehensive validation
2. Run analysis to get NPV, IRR, and investment recommendations using production-grade algorithms
3. Compare results across multiple properties for portfolio optimization with statistical backing
4. Use risk assessment to understand downside exposure with Monte Carlo simulation
5. Leverage 2,174+ historical data points for market-informed decision making
6. Utilize 5-MSA geographic coverage for location-specific analysis

### For Developers
1. Review Clean Architecture implementation in `/src` with domain-driven design
2. Study domain entities and application services with comprehensive business logic
3. Examine test patterns for new feature development (320+ test methods)
4. Read `CLAUDE.md` for development guidelines and standards
5. Use CI/CD pipeline with multi-Python version support (3.8-3.13)
6. Implement features with 96%+ test coverage requirement and automated quality gates
7. Follow performance standards with sub-second analysis and optimized calculations