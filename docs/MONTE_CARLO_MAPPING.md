# Monte Carlo to Excel Pro Forma Parameter Mapping

## Overview

This document defines the exact mapping between our 11 forecasted Monte Carlo parameters and the Excel pro forma assumptions. Each Monte Carlo scenario provides 5-year forecasts that feed directly into the DCF engine calculations.

## Parameter Mapping Table

| Excel Assumption | Monte Carlo Parameter | Data Type | Usage in DCF | Years Used |
|-----------------|----------------------|-----------|--------------|------------|
| Interest Rate | `commercial_mortgage_rate` | List[float] | Debt service calculations | 1-5 |
| Market Cap Rate | `cap_rate` | List[float] | Terminal value calculation | 5 only |
| Rent Growth | `rent_growth` | List[float] | Annual income projections | 2-5 |
| Expense Growth | `expense_growth` | List[float] | Annual expense projections | 2-5 |
| Property Growth | `property_growth` | List[float] | Terminal value appreciation | 1-5 |
| Vacancy Rate | `vacancy_rate` | List[float] | Income adjustments | 1-5 |
| LTV Ratio | `ltv_ratio` | List[float] | Loan amount calculation | 0 only |
| Closing Cost % | `closing_cost_pct` | List[float] | Acquisition costs | 0 only |
| Lender Reserves | `lender_reserves` | List[float] | Reserve requirements | 0 only |
| Treasury 10Y | `treasury_10y` | List[float] | Discount rate reference | 1-5 |
| Fed Funds Rate | `fed_funds_rate` | List[float] | Economic context | 1-5 |

## Detailed Parameter Usage

### 1. Commercial Mortgage Rate
**Monte Carlo Parameter:** `commercial_mortgage_rate`
**Excel Location:** Cell C3 (Interest rate)
**DCF Usage:** 
- Year 1-5: Annual interest expense calculation
- Formula: `Loan Amount × Commercial Mortgage Rate[Year]`
**Data Structure:**
```python
commercial_mortgage_rate: List[float]  # [Year0, Year1, Year2, Year3, Year4, Year5]
# Example: [0.065, 0.067, 0.069, 0.071, 0.073, 0.075]
```

### 2. Cap Rate
**Monte Carlo Parameter:** `cap_rate`
**Excel Location:** Cell G5 (Market Cap Rate)
**DCF Usage:**
- Year 5 only: Terminal value calculation
- Formula: `Terminal Value = Year 5 NOI ÷ Cap Rate[5]`
**Data Structure:**
```python
cap_rate: List[float]  # Only Year 5 value used for exit
# Example: [0.07, 0.07, 0.07, 0.07, 0.07, 0.065]  # Exit cap rate = 6.5%
```

### 3. Rent Growth
**Monte Carlo Parameter:** `rent_growth`
**Excel Location:** Cell E5 (Rent Growth)
**DCF Usage:**
- Years 2-5: Annual rent increases
- Year 1: Uses base rent (no growth applied)
- Formula: `Year N Rent = Year N-1 Rent × (1 + Rent Growth[N])`
**Data Structure:**
```python
rent_growth: List[float]  # Annual growth rates
# Example: [0.0, 0.03, 0.032, 0.029, 0.031, 0.028]  # 3% average growth
```

### 4. Expense Growth
**Monte Carlo Parameter:** `expense_growth`
**Excel Location:** Cell E7 (Expense Growth)
**DCF Usage:**
- Years 2-5: Annual expense increases
- Year 1: Uses base expenses (no growth applied)
- Formula: `Year N Expenses = Year N-1 Expenses × (1 + Expense Growth[N])`
**Data Structure:**
```python
expense_growth: List[float]  # Annual growth rates
# Example: [0.0, 0.02, 0.025, 0.022, 0.024, 0.021]  # 2.3% average growth
```

### 5. Property Growth
**Monte Carlo Parameter:** `property_growth`
**Excel Location:** Cell E6 (Property Growth)
**DCF Usage:**
- Years 1-5: Property value appreciation for terminal value
- Combined with cap rate for exit valuation
- Formula: `Appreciated Value = Initial Value × Π(1 + Property Growth[i])`
**Data Structure:**
```python
property_growth: List[float]  # Annual appreciation rates
# Example: [0.0, 0.02, 0.025, 0.018, 0.022, 0.019]  # 2.1% average appreciation
```

### 6. Vacancy Rate
**Monte Carlo Parameter:** `vacancy_rate`
**Excel Location:** Cell G3 (Vacancy Rate)
**DCF Usage:**
- Years 1-5: Income reduction from vacant units
- Formula: `Effective Gross Income = Gross Rent × (1 - Vacancy Rate[Year])`
**Data Structure:**
```python
vacancy_rate: List[float]  # Annual vacancy percentages
# Example: [0.0, 0.05, 0.04, 0.06, 0.045, 0.05]  # 5% average vacancy
```

### 7. LTV Ratio
**Monte Carlo Parameter:** `ltv_ratio`
**Excel Location:** Cell C4 (LTV)
**DCF Usage:**
- Year 0 only: Initial loan amount calculation
- Formula: `Loan Amount = Purchase Price × LTV Ratio[0]`
**Data Structure:**
```python
ltv_ratio: List[float]  # Only first value used
# Example: [0.75, 0.75, 0.75, 0.75, 0.75, 0.75]  # 75% LTV
```

### 8. Closing Cost Percentage
**Monte Carlo Parameter:** `closing_cost_pct`
**Excel Location:** Cell G4 (Closing Cost %)
**DCF Usage:**
- Year 0 only: Acquisition cost calculation
- Formula: `Closing Costs = Purchase Price × Closing Cost %[0]`
**Data Structure:**
```python
closing_cost_pct: List[float]  # Only first value used
# Example: [0.05, 0.05, 0.05, 0.05, 0.05, 0.05]  # 5% closing costs
```

### 9. Lender Reserves
**Monte Carlo Parameter:** `lender_reserves`
**Excel Location:** Row 19 (Lender Reserves calculation)
**DCF Usage:**
- Year 0 only: Required reserve calculation
- Formula: `Reserves = Annual Debt Service × (Lender Reserves[0] / 12)`
**Data Structure:**
```python
lender_reserves: List[float]  # Months of reserves required
# Example: [3.0, 3.0, 3.0, 3.0, 3.0, 3.0]  # 3 months reserves
```

### 10. Treasury 10Y Rate
**Monte Carlo Parameter:** `treasury_10y`
**Excel Location:** Not directly used in Excel
**DCF Usage:**
- Reference for discount rate calculations
- Could be used for NPV discount rate (currently 5% hardcoded)
- Economic context for scenario classification
**Data Structure:**
```python
treasury_10y: List[float]  # Reference rates
# Example: [0.04, 0.042, 0.045, 0.043, 0.046, 0.044]
```

### 11. Fed Funds Rate
**Monte Carlo Parameter:** `fed_funds_rate`
**Excel Location:** Not directly used in Excel
**DCF Usage:**
- Economic context and scenario classification
- Potential input for financing cost calculations
- Market environment assessment
**Data Structure:**
```python
fed_funds_rate: List[float]  # Federal funds rates
# Example: [0.02, 0.025, 0.03, 0.028, 0.032, 0.029]
```

## Implementation Code Example

### DCF Assumptions Creation
```python
def create_dcf_assumptions(monte_carlo_scenario: MonteCarloScenario, 
                          property_data: PropertyInputData) -> DCFAssumptions:
    """Create DCF assumptions from Monte Carlo scenario."""
    
    # Extract forecasted parameters (5-year arrays)
    forecasts = monte_carlo_scenario.forecasted_parameters
    
    return DCFAssumptions(
        scenario_id=monte_carlo_scenario.scenario_id,
        msa_code=property_data.get_msa_code(),
        
        # Primary DCF Parameters (directly used in calculations)
        commercial_mortgage_rate=forecasts['commercial_mortgage_rate'],
        cap_rate=forecasts['cap_rate'],
        rent_growth_rate=forecasts['rent_growth'],
        expense_growth_rate=forecasts['expense_growth'],
        property_growth_rate=forecasts['property_growth'],
        vacancy_rate=forecasts['vacancy_rate'],
        
        # Acquisition Parameters (Year 0 only)
        ltv_ratio=forecasts['ltv_ratio'][0],
        closing_cost_pct=forecasts['closing_cost_pct'][0],
        lender_reserves_months=forecasts['lender_reserves'][0],
        
        # Reference Parameters (economic context)
        treasury_10y_rate=forecasts['treasury_10y'],
        fed_funds_rate=forecasts['fed_funds_rate'],
        
        # Property-specific parameters from user input
        investor_equity_share=property_data.equity_structure.investor_equity_share_pct / 100,
        preferred_return_rate=0.06,  # 6% from Excel Cell C7
        self_cash_percentage=property_data.equity_structure.self_cash_percentage / 100
    )
```

### Year-by-Year Calculation Example
```python
def calculate_year_cash_flow(year: int, assumptions: DCFAssumptions, 
                           previous_income: float, previous_expenses: float) -> AnnualCashFlow:
    """Calculate cash flow for a specific year."""
    
    # Get year-specific parameters
    rent_growth = assumptions.rent_growth_rate[year] if year > 0 else 0
    expense_growth = assumptions.expense_growth_rate[year] if year > 0 else 0
    vacancy_rate = assumptions.vacancy_rate[year]
    interest_rate = assumptions.commercial_mortgage_rate[year]
    
    # Calculate gross income with growth
    gross_income = previous_income * (1 + rent_growth) if year > 0 else previous_income
    
    # Apply vacancy loss
    vacancy_loss = gross_income * vacancy_rate
    effective_income = gross_income - vacancy_loss
    
    # Calculate expenses with growth
    operating_expenses = previous_expenses * (1 + expense_growth) if year > 0 else previous_expenses
    
    # Net Operating Income
    noi = effective_income - operating_expenses
    
    # Debt service (interest-only)
    debt_service = assumptions.loan_amount * interest_rate
    
    # Cash Flow After Financing
    cfaf = noi - debt_service
    
    return AnnualCashFlow(
        year=year,
        gross_rental_income=gross_income,
        vacancy_loss=vacancy_loss,
        effective_gross_income=effective_income,
        operating_expenses=operating_expenses,
        net_operating_income=noi,
        interest_expense=debt_service,
        principal_payment=0.0,  # Interest-only
        debt_service=debt_service,
        cash_flow_after_financing=cfaf
        # ... waterfall distribution calculations
    )
```

## Validation and Testing

### Parameter Validation
```python
def validate_monte_carlo_parameters(scenario: MonteCarloScenario) -> List[str]:
    """Validate Monte Carlo scenario has all required parameters."""
    required_params = [
        'commercial_mortgage_rate', 'cap_rate', 'rent_growth', 'expense_growth',
        'property_growth', 'vacancy_rate', 'ltv_ratio', 'closing_cost_pct',
        'lender_reserves', 'treasury_10y', 'fed_funds_rate'
    ]
    
    issues = []
    for param in required_params:
        if param not in scenario.forecasted_parameters:
            issues.append(f"Missing parameter: {param}")
        elif len(scenario.forecasted_parameters[param]) != 6:
            issues.append(f"Parameter {param} should have 6 years of data")
    
    return issues
```

### Mapping Verification
```python
def verify_excel_mapping(dcf_assumptions: DCFAssumptions) -> bool:
    """Verify DCF assumptions match Excel model expectations."""
    
    # Check data ranges are reasonable
    checks = [
        (0.01 <= dcf_assumptions.commercial_mortgage_rate[1] <= 0.15, "Interest rate range"),
        (0.03 <= dcf_assumptions.cap_rate[5] <= 0.12, "Cap rate range"),
        (-0.05 <= dcf_assumptions.rent_growth_rate[1] <= 0.10, "Rent growth range"),
        (0.005 <= dcf_assumptions.expense_growth_rate[1] <= 0.08, "Expense growth range"),
        (0.50 <= dcf_assumptions.ltv_ratio <= 0.90, "LTV ratio range"),
        (0.01 <= dcf_assumptions.closing_cost_pct <= 0.10, "Closing cost range")
    ]
    
    for check, description in checks:
        if not check:
            print(f"Validation failed: {description}")
            return False
    
    return True
```

This mapping ensures that every Monte Carlo parameter has a clear purpose in the DCF calculations and matches the Excel pro forma model structure exactly.