# DCF Engine Data Structures Design

## Overview

This document defines the data structures for the Pro Forma DCF engine that integrate with existing Monte Carlo scenarios and property input systems. The design follows established patterns from the current architecture while extending capabilities for financial analysis.

## Integration Architecture

```
PropertyInputData → DCFEngine → DCFResults → InvestmentAnalysis
       ↑                ↑           ↑              ↑
MonteCarloResults → Assumptions → CashFlows → KPIs
```

## Core Data Structures

### 1. DCF Assumptions

```python
@dataclass
class DCFAssumptions:
    """
    Market assumptions extracted from Monte Carlo scenarios.
    Maps Monte Carlo forecasted parameters to Excel pro forma assumptions.
    """
    scenario_id: str
    msa_code: str
    
    # Interest and Financing Parameters
    commercial_mortgage_rate: List[float]  # 6-year forecast (Years 0-5)
    treasury_10y_rate: List[float]         # For discount rate calculations
    fed_funds_rate: List[float]            # Macroeconomic context
    
    # Property Market Parameters  
    cap_rate: List[float]                  # Terminal value calculations
    rent_growth_rate: List[float]          # Annual rent increases
    expense_growth_rate: List[float]       # Annual expense increases
    property_growth_rate: List[float]      # Property appreciation
    vacancy_rate: List[float]              # Income adjustments
    
    # Financing and Transaction Parameters
    ltv_ratio: float                       # Loan-to-value ratio
    closing_cost_pct: float                # Acquisition costs
    lender_reserves_months: float          # Reserve requirements
    
    # Investment Structure (from property inputs)
    investor_equity_share: float           # Investor ownership %
    preferred_return_rate: float           # Annual preferred return
    self_cash_percentage: float            # Cash vs financing split
    
    def get_year_assumptions(self, year: int) -> Dict[str, float]:
        """Get all assumptions for a specific year."""
        return {
            'commercial_mortgage_rate': self.commercial_mortgage_rate[year],
            'cap_rate': self.cap_rate[year],
            'rent_growth_rate': self.rent_growth_rate[year],
            'expense_growth_rate': self.expense_growth_rate[year],
            'property_growth_rate': self.property_growth_rate[year],
            'vacancy_rate': self.vacancy_rate[year]
        }
    
    @classmethod
    def from_monte_carlo_scenario(cls, scenario: MonteCarloScenario, 
                                  property_data: PropertyInputData) -> 'DCFAssumptions':
        """Create DCF assumptions from Monte Carlo scenario and property data."""
        return cls(
            scenario_id=scenario.scenario_id,
            msa_code=property_data.get_msa_code(),
            commercial_mortgage_rate=scenario.forecasted_parameters['commercial_mortgage_rate'],
            treasury_10y_rate=scenario.forecasted_parameters['treasury_10y'],
            fed_funds_rate=scenario.forecasted_parameters['fed_funds_rate'],
            cap_rate=scenario.forecasted_parameters['cap_rate'],
            rent_growth_rate=scenario.forecasted_parameters['rent_growth'],
            expense_growth_rate=scenario.forecasted_parameters['expense_growth'],
            property_growth_rate=scenario.forecasted_parameters['property_growth'],
            vacancy_rate=scenario.forecasted_parameters['vacancy_rate'],
            ltv_ratio=scenario.forecasted_parameters['ltv_ratio'][0],  # Static value
            closing_cost_pct=scenario.forecasted_parameters['closing_cost_pct'][0],
            lender_reserves_months=scenario.forecasted_parameters['lender_reserves'][0],
            investor_equity_share=property_data.equity_structure.investor_equity_share_pct / 100,
            preferred_return_rate=0.06,  # Default 6%, could be parameterized
            self_cash_percentage=property_data.equity_structure.self_cash_percentage / 100
        )
```

### 2. Initial Numbers Calculator

```python
@dataclass
class InitialNumbers:
    """
    Property acquisition and initial investment calculations.
    Corresponds to "Initial Numbers" section in Excel pro forma.
    """
    property_id: str
    scenario_id: str
    
    # Purchase Details
    purchase_price: float
    closing_cost_amount: float
    renovation_capex: float
    cost_basis: float
    
    # Financing Calculations
    loan_amount: float
    annual_interest_expense: float
    lender_reserves_amount: float
    
    # Equity Requirements
    investor_cash_required: float
    operator_cash_required: float
    total_cash_required: float
    
    # Valuation Metrics
    after_repair_value: float
    initial_cap_rate: float
    
    # Income Structure
    pre_renovation_annual_rent: float
    post_renovation_annual_rent: float
    year_1_rental_income: float  # Adjusted for renovation period
    
    # Operating Expenses (Year 1 baseline)
    property_taxes: float
    insurance: float
    repairs_maintenance: float
    property_management: float
    admin_expenses: float
    contracting: float
    replacement_reserves: float
    total_operating_expenses: float
    
    @classmethod
    def calculate(cls, property_data: PropertyInputData, 
                  assumptions: DCFAssumptions) -> 'InitialNumbers':
        """Calculate initial numbers from property data and assumptions."""
        
        # Purchase calculations
        purchase_price = property_data.purchase_price
        closing_cost_amount = purchase_price * assumptions.closing_cost_pct
        renovation_capex = property_data.renovation_info.estimated_cost or 0
        cost_basis = purchase_price + closing_cost_amount + renovation_capex
        
        # Financing calculations
        loan_amount = purchase_price * assumptions.ltv_ratio
        annual_interest = loan_amount * assumptions.commercial_mortgage_rate[1]  # Year 1 rate
        lender_reserves = annual_interest * (assumptions.lender_reserves_months / 12)
        
        # Equity calculations
        total_cash = purchase_price - loan_amount + closing_cost_amount + renovation_capex + lender_reserves
        investor_cash = total_cash * assumptions.investor_equity_share
        operator_cash = total_cash * (1 - assumptions.investor_equity_share)
        
        # Income calculations
        monthly_rent = (property_data.residential_units.monthly_gross_rent + 
                       (property_data.commercial_units.monthly_gross_rent if property_data.commercial_units else 0))
        
        pre_renovation_rent = monthly_rent * 12
        # Assuming 12.5% rent increase post-renovation (configurable)
        post_renovation_rent = pre_renovation_rent * 1.125
        
        # Year 1 rent adjusted for renovation period
        renovation_months = property_data.renovation_info.anticipated_duration_months or 0
        year_1_rent = post_renovation_rent * (12 - renovation_months) / 12
        
        # Operating expenses (placeholder - would be calculated from property data)
        annual_rent = post_renovation_rent
        total_expenses = annual_rent * 0.25  # Placeholder: 25% expense ratio
        
        return cls(
            property_id=property_data.property_id,
            scenario_id=assumptions.scenario_id,
            purchase_price=purchase_price,
            closing_cost_amount=closing_cost_amount,
            renovation_capex=renovation_capex,
            cost_basis=cost_basis,
            loan_amount=loan_amount,
            annual_interest_expense=annual_interest,
            lender_reserves_amount=lender_reserves,
            investor_cash_required=investor_cash,
            operator_cash_required=operator_cash,
            total_cash_required=total_cash,
            after_repair_value=cost_basis * 1.25,  # Placeholder calculation
            initial_cap_rate=year_1_rent / purchase_price,
            pre_renovation_annual_rent=pre_renovation_rent,
            post_renovation_annual_rent=post_renovation_rent,
            year_1_rental_income=year_1_rent,
            property_taxes=total_expenses * 0.4,
            insurance=total_expenses * 0.1,
            repairs_maintenance=total_expenses * 0.15,
            property_management=total_expenses * 0.2,
            admin_expenses=total_expenses * 0.05,
            contracting=total_expenses * 0.05,
            replacement_reserves=total_expenses * 0.05,
            total_operating_expenses=total_expenses
        )
```

### 3. Cash Flow Projections

```python
@dataclass
class AnnualCashFlow:
    """Single year cash flow calculation."""
    year: int
    
    # Operating Cash Flows
    gross_rental_income: float
    vacancy_loss: float
    effective_gross_income: float
    operating_expenses: float
    net_operating_income: float
    
    # Financing Cash Flows
    interest_expense: float
    principal_payment: float  # Will be 0 for interest-only
    debt_service: float
    
    # After-Financing Cash Flow
    cash_flow_after_financing: float
    
    # Waterfall Distribution
    preferred_return_amount: float
    preferred_return_shortfall: float
    remaining_cash_flow: float
    investor_distribution: float
    operator_distribution: float
    
    # Terminal Value (Year 5 only)
    terminal_value: Optional[float] = None
    loan_payoff: Optional[float] = None
    net_sale_proceeds: Optional[float] = None
    terminal_investor_share: Optional[float] = None
    terminal_operator_share: Optional[float] = None

@dataclass 
class CashFlowProjection:
    """
    Complete 6-year cash flow projection (Years 0-5).
    Corresponds to "Cash Flow Projections" section in Excel.
    """
    property_id: str
    scenario_id: str
    projection_date: date
    
    # Initial Investment (Year 0)
    initial_investor_investment: float
    initial_operator_investment: float
    
    # Annual Cash Flows (Years 1-5)
    annual_cash_flows: List[AnnualCashFlow]
    
    # Cumulative Preferred Return Tracking
    cumulative_preferred_shortfall: List[float]  # By year
    
    # Summary Metrics
    total_investor_distributions: float
    total_operator_distributions: float
    property_terminal_value: float
    
    def get_investor_cash_flow_series(self) -> List[float]:
        """Get investor cash flow series for IRR calculation."""
        cash_flows = [-self.initial_investor_investment]  # Year 0
        
        for cf in self.annual_cash_flows:
            annual_total = cf.investor_distribution
            if cf.terminal_investor_share:  # Year 5
                annual_total += cf.terminal_investor_share
            cash_flows.append(annual_total)
            
        return cash_flows
    
    def get_operator_cash_flow_series(self) -> List[float]:
        """Get operator cash flow series for IRR calculation."""
        cash_flows = [-self.initial_operator_investment]  # Year 0
        
        for cf in self.annual_cash_flows:
            annual_total = cf.operator_distribution
            if cf.terminal_operator_share:  # Year 5
                annual_total += cf.terminal_operator_share
            cash_flows.append(annual_total)
            
        return cash_flows
```

### 4. Financial Metrics

```python
@dataclass
class FinancialMetrics:
    """
    Investment performance metrics.
    Corresponds to "KPIs" section in Excel.
    """
    property_id: str
    scenario_id: str
    calculation_date: date
    
    # IRR Calculations
    investor_irr: float
    operator_irr: float
    
    # NPV Calculations (5% discount rate)
    investor_npv: float
    operator_npv: float
    
    # Cash-on-Cash Returns
    investor_cash_on_cash_year_1: float
    operator_cash_on_cash_year_1: float
    
    # Valuation Metrics
    exit_cap_rate: float
    total_return_multiple: float
    
    # Risk Metrics
    payback_period_years: float
    break_even_occupancy: float
    
    @classmethod
    def calculate(cls, cash_flow_projection: CashFlowProjection) -> 'FinancialMetrics':
        """Calculate financial metrics from cash flow projection."""
        
        # IRR calculations using numpy_financial
        investor_cash_flows = cash_flow_projection.get_investor_cash_flow_series()
        operator_cash_flows = cash_flow_projection.get_operator_cash_flow_series()
        
        investor_irr = np.irr(investor_cash_flows)
        operator_irr = np.irr(operator_cash_flows)
        
        # NPV calculations (5% discount rate)
        discount_rate = 0.05
        investor_npv = np.npv(discount_rate, investor_cash_flows)
        operator_npv = np.npv(discount_rate, operator_cash_flows)
        
        # Cash-on-Cash returns (Year 1 cash flow / initial investment)
        year_1_investor_cf = cash_flow_projection.annual_cash_flows[0].investor_distribution
        year_1_operator_cf = cash_flow_projection.annual_cash_flows[0].operator_distribution
        
        investor_coc = year_1_investor_cf / cash_flow_projection.initial_investor_investment
        operator_coc = year_1_operator_cf / cash_flow_projection.initial_operator_investment
        
        return cls(
            property_id=cash_flow_projection.property_id,
            scenario_id=cash_flow_projection.scenario_id,
            calculation_date=date.today(),
            investor_irr=investor_irr,
            operator_irr=operator_irr,
            investor_npv=investor_npv,
            operator_npv=operator_npv,
            investor_cash_on_cash_year_1=investor_coc,
            operator_cash_on_cash_year_1=operator_coc,
            exit_cap_rate=0.0,  # To be calculated from terminal value
            total_return_multiple=0.0,  # To be calculated
            payback_period_years=0.0,  # To be calculated
            break_even_occupancy=0.0  # To be calculated
        )
```

### 5. DCF Results Container

```python
@dataclass
class DCFResults:
    """
    Complete DCF analysis results for a single property across all Monte Carlo scenarios.
    """
    property_id: str
    analysis_date: date
    monte_carlo_run_id: str
    
    # Scenario-Level Results
    scenario_results: List[Tuple[str, InitialNumbers, CashFlowProjection, FinancialMetrics]]
    
    # Aggregated Statistics
    investor_irr_statistics: Dict[str, float]  # mean, std, percentiles
    operator_irr_statistics: Dict[str, float]
    investor_npv_statistics: Dict[str, float]
    operator_npv_statistics: Dict[str, float]
    
    # Investment Decision Metrics
    probability_positive_npv: float
    risk_adjusted_return: float
    investment_recommendation: str  # "STRONG BUY", "BUY", "CONSIDER", "CAUTION"
    
    def get_scenario_count(self) -> int:
        """Get number of Monte Carlo scenarios analyzed."""
        return len(self.scenario_results)
    
    def get_investment_summary(self) -> Dict[str, Any]:
        """Get summary for investment decision making."""
        return {
            'property_id': self.property_id,
            'scenarios_analyzed': self.get_scenario_count(),
            'investor_irr_mean': self.investor_irr_statistics['mean'],
            'investor_irr_std': self.investor_irr_statistics['std'],
            'investor_npv_mean': self.investor_npv_statistics['mean'],
            'probability_positive_npv': self.probability_positive_npv,
            'investment_recommendation': self.investment_recommendation,
            'risk_adjusted_return': self.risk_adjusted_return
        }
```

## Monte Carlo Parameter Mapping

### Direct Mappings (Excel ← Monte Carlo)

```python
MONTE_CARLO_PARAMETER_MAPPING = {
    # Excel Assumption ← Monte Carlo Parameter
    'commercial_mortgage_rate': 'commercial_mortgage_rate',  # Interest rate
    'cap_rate': 'cap_rate',                                  # Market cap rate
    'rent_growth_rate': 'rent_growth',                       # Rent growth
    'expense_growth_rate': 'expense_growth',                 # Expense growth  
    'property_growth_rate': 'property_growth',               # Property appreciation
    'vacancy_rate': 'vacancy_rate',                          # Vacancy adjustments
    'ltv_ratio': 'ltv_ratio',                               # Loan-to-value
    'closing_cost_pct': 'closing_cost_pct',                 # Closing costs
    'lender_reserves': 'lender_reserves',                    # Reserve requirements
    
    # Reference but not directly used in DCF
    'treasury_10y': 'treasury_10y',                         # Discount rate reference
    'fed_funds_rate': 'fed_funds_rate'                      # Economic context
}
```

## Database Schema Extensions

### New Tables Required

```sql
-- DCF Results Storage
CREATE TABLE dcf_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id TEXT NOT NULL,
    monte_carlo_run_id TEXT NOT NULL,
    analysis_date TEXT NOT NULL,
    scenario_count INTEGER NOT NULL,
    results_json TEXT NOT NULL,  -- JSON serialized DCFResults
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties(property_id)
);

-- Individual Scenario Cash Flows (optional detailed storage)
CREATE TABLE scenario_cash_flows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id TEXT NOT NULL,
    scenario_id TEXT NOT NULL,
    year INTEGER NOT NULL,
    cash_flow_json TEXT NOT NULL,  -- JSON serialized AnnualCashFlow
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Financial Metrics Summary
CREATE TABLE financial_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id TEXT NOT NULL,
    scenario_id TEXT NOT NULL,
    investor_irr REAL,
    operator_irr REAL,
    investor_npv REAL,
    operator_npv REAL,
    investment_recommendation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Integration Points

### 1. Input Integration
```python
# From existing property input workflow
property_data = simplified_property_manager.get_property(property_id)
monte_carlo_results = monte_carlo_engine.get_results_for_property(property_id)

# Convert to DCF format
dcf_assumptions_list = [
    DCFAssumptions.from_monte_carlo_scenario(scenario, property_data)
    for scenario in monte_carlo_results.scenarios
]
```

### 2. Calculation Workflow
```python
# For each Monte Carlo scenario
for assumptions in dcf_assumptions_list:
    initial_numbers = InitialNumbers.calculate(property_data, assumptions)
    cash_flows = CashFlowProjection.calculate(initial_numbers, assumptions)
    metrics = FinancialMetrics.calculate(cash_flows)
    
    scenario_results.append((assumptions.scenario_id, initial_numbers, cash_flows, metrics))

# Aggregate results
dcf_results = DCFResults(
    property_id=property_data.property_id,
    scenario_results=scenario_results,
    # ... statistical analysis
)
```

### 3. Output Integration
```python
# Store in database
dcf_database.save_dcf_results(dcf_results)

# Generate investment recommendation
investment_analyzer.generate_recommendation(dcf_results)

# Create visualizations
visualization_engine.create_dcf_charts(dcf_results)
```

This data structure design provides the foundation for implementing the DCF engine while maintaining compatibility with existing systems and following established architectural patterns.