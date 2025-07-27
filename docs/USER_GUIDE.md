# User Guide: Pro Forma Analytics Tool

Complete guide to using the real estate investment analysis platform with 4-phase DCF engine and Monte Carlo simulation.

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
```

This demonstration processes a $3.5M Chicago mixed-use property through all DCF phases using realistic market scenarios.

## Understanding the 4-Phase DCF Workflow

### Phase 1: DCF Assumptions
- Converts Monte Carlo market scenarios into DCF parameters
- Maps 11 pro forma metrics to 6-year projections
- Applies economic correlations and market conditions

### Phase 2: Initial Numbers  
- Calculates acquisition costs (purchase price, closing costs, renovation CapEx)
- Determines financing terms (loan amounts, LTV ratios, lender reserves)
- Projects initial rental income and operating expenses

### Phase 3: Cash Flow Projections
- Generates annual cash flows for Years 0-5
- Models renovation periods with income interruption
- Calculates waterfall distributions between investors and operators

### Phase 4: Financial Metrics
- Computes NPV, IRR, equity multiples, and payback periods
- Models terminal value and exit scenarios
- Provides investment recommendations (STRONG_BUY to STRONG_SELL)

## Property Input Requirements

The system requires 7 core data fields for property analysis:

### Required Inputs

1. **Residential Units** - Total count of residential rental units
2. **Renovation Time** - Expected duration in months (0 = no renovation)  
3. **Commercial Units** - Count of commercial spaces (0 = residential only)
4. **Investor Equity Share** - Percentage ownership for investors (0-100%)
5. **Residential Rent** - Average monthly rent per residential unit
6. **Commercial Rent** - Average monthly rent per commercial space
7. **Self Cash Percentage** - Percentage of purchase price paid in cash

### Optional Inputs
- Purchase price (enables additional financial metrics)
- Location (city/state for MSA-specific market analysis)
- Property name and analysis date

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

Track analysis performance and validate results:

```bash
# Run comprehensive test suite
python -m pytest tests/ -v

# Performance testing
python tests/performance/test_irr_performance.py

# System validation
python -c "from demo_end_to_end_workflow import main; main()"
```

## Troubleshooting

### Common Issues

**Import Errors**
- Ensure all dependencies installed: `pip install -r requirements.txt`
- Use Python 3.8+ (tested with Python 3.13)

**Database Errors**  
- Initialize databases: `python data_manager.py setup`
- Check database permissions and file paths

**Calculation Errors**
- Verify all required property fields are provided
- Check that numeric inputs are positive and realistic
- Ensure MSA codes are valid for market analysis

### Getting Help

1. **Review Examples**: Start with `demo_end_to_end_workflow.py`
2. **Check Tests**: Integration tests show various usage patterns
3. **Read Documentation**: Architecture and technical docs in `/docs`
4. **Validate Installation**: Run test suite to verify system functionality

## Next Steps

### For Real Estate Investors
1. Create property data using your actual investment parameters
2. Run analysis to get NPV, IRR, and investment recommendations  
3. Compare results across multiple properties for portfolio optimization
4. Use risk assessment to understand downside exposure

### For Developers
1. Review Clean Architecture implementation in `/src`
2. Study domain entities and application services
3. Examine test patterns for new feature development
4. Read `CLAUDE.md` for development guidelines and standards