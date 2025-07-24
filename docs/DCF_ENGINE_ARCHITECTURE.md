# Pro Forma DCF Engine Architecture

## Executive Summary

This document defines the architectural approach for implementing the Pro Forma Discounted Cash Flow (DCF) engine that bridges the gap between Monte Carlo scenario generation and investment decision analysis. The DCF engine represents the critical missing component in the current analytics pipeline.

## Current State Analysis

### Existing Infrastructure Assets

The system provides a robust foundation for DCF engine implementation:

**Data Collection Infrastructure:**
- Comprehensive property data structures (`PropertyInputData`, `SimplifiedPropertyInput`)
- Property financial inputs including NOI, purchase price, down payment percentages
- Operating assumptions with vacancy rates, management fees, expense ratios
- Geographic specificity via MSA codes for market-specific analysis

**Market Forecasting Infrastructure:**
- Prophet-based forecasting for 11 pro forma parameters
- Monte Carlo simulation generating 500+ correlated economic scenarios
- Five-year parameter forecasts with statistical validation
- Market scenario classification (bull/bear/neutral/growth/stress markets)

**Technical Infrastructure:**
- Clean architecture with domain/application/infrastructure separation
- SQLite database system with optimized schemas
- Comprehensive testing framework with 95%+ coverage targets
- Excel analysis tools for reference pro forma integration

### Forecasted Parameters Available for DCF Calculations

The Monte Carlo engine provides forecasts for all standard pro forma metrics:

**Interest Rate Parameters:**
- Treasury 10Y Rate (discount rate basis)
- Commercial Mortgage Rate (financing calculations)
- Fed Funds Rate (macroeconomic context)

**Property Market Parameters:**
- Cap Rate (terminal value calculations)
- Vacancy Rate (operating income projections)
- Rent Growth (revenue projections)
- Expense Growth (operating cost projections)

**Financing Parameters:**
- LTV Ratio (loan sizing)
- Closing Cost Percentage (acquisition costs)
- Lender Reserve Requirements (cash flow impact)

**Investment Parameters:**
- Property Growth (appreciation projections)

### Critical Gap Identification

**Missing Component: Financial Calculation Engine**

The system terminates at scenario generation without performing the fundamental financial calculations required for investment analysis:

- No cash flow projection functionality
- No Net Present Value (NPV) calculations
- No Internal Rate of Return (IRR) calculations
- No Cash-on-Cash return analysis
- No terminal value computations
- No investment decision framework

## DCF Engine Architecture Design

### Phase 1: Data Structure Foundation

**Objective:** Establish the data architecture before implementing calculations

**Required Activities:**

1. **Excel Pro Forma Structure Analysis**
   - Reverse engineer calculation logic from `MultiFamily_RE_Pro_Forma.xlsx`
   - Map Excel formulas to programming logic
   - Document cash flow line item relationships
   - Identify multi-year projection patterns

2. **Cash Flow Data Structure Design**
   - Operating cash flow components (rent, expenses, NOI)
   - Financing cash flow components (debt service, principal/interest)
   - Terminal value components (exit scenarios, residual values)
   - Multi-year projection data models

3. **Integration Interface Specification**
   - Monte Carlo Results to DCF Input transformation
   - DCF Output to Investment Decision logic
   - Database persistence for DCF results

### Phase 2: Integration Architecture

**Objective:** Design the data flow from existing components into DCF calculations

**Architecture Decisions Required:**

1. **Scenario Processing Strategy**
   - Computational approach for 500+ Monte Carlo scenarios
   - Vectorized calculations versus iterative processing
   - Memory management for large scenario sets

2. **Results Aggregation Methodology**
   - Distribution analysis for NPV/IRR across scenarios
   - Statistical summary generation (mean, median, percentiles)
   - Risk-adjusted return calculations

3. **Performance Optimization**
   - Caching strategies for repeated calculations
   - Database query optimization
   - Parallel processing considerations

### Phase 3: Implementation

**Objective:** Build the DCF calculation engine

**Core Components Required:**

```python
class ProFormaDCFEngine:
    def project_operating_cash_flows(
        property: PropertyInputData, 
        scenarios: MonteCarloResults
    ) -> List[CashFlow]
    
    def calculate_financing_cash_flows(
        property: PropertyInputData, 
        scenarios: MonteCarloResults
    ) -> List[CashFlow]
    
    def calculate_terminal_value(
        property: PropertyInputData, 
        scenarios: MonteCarloResults
    ) -> float
    
    def calculate_npv(
        cash_flows: List[CashFlow], 
        discount_rate: float
    ) -> float
    
    def calculate_irr(
        cash_flows: List[CashFlow]
    ) -> float
```

## Technical Architecture Considerations

### Data Flow Architecture

**Current Pipeline:**
```
PropertyInputData → Monte Carlo Scenarios → [MISSING DCF ENGINE] → Investment Analysis
```

**Target Pipeline:**
```
PropertyInputData → Monte Carlo Scenarios → DCF Engine → Financial Metrics → Investment Decisions
```

### Integration Points

**Input Sources:**
- Property data from `PropertyInputData` objects
- Market forecasts from `MonteCarloResults` scenarios
- Operating assumptions from property management parameters

**Output Destinations:**
- Financial metrics database storage
- Investment decision framework
- Reporting and visualization systems

### Performance Requirements

**Computational Scalability:**
- Process 500+ Monte Carlo scenarios per property analysis
- Support multiple property comparisons
- Maintain sub-60 second analysis completion times

**Data Management:**
- Efficient storage of multi-year cash flow projections
- Version control for assumption changes
- Historical analysis result preservation

## Business Logic Specifications

### Investment Decision Framework

**Financial Metrics Integration:**
- NPV distribution analysis across Monte Carlo scenarios
- IRR sensitivity to market condition variations
- Cash-on-Cash return projections with risk adjustments
- Payback period calculations with scenario modeling

**Decision Thresholds:**
- Risk-adjusted return requirements
- Market-specific hurdle rates
- Portfolio diversification considerations
- Liquidity and holding period constraints

### Discount Rate Methodology

**Approach Options:**
- Weighted Average Cost of Capital (WACC) calculations
- Required return based on risk premiums
- Market-derived discount rates from comparable transactions
- Risk-free rate plus property-specific risk premiums

### Terminal Value Calculations

**Methodology:**
- Exit cap rate approach using forecasted market cap rates
- Going concern value based on stabilized cash flows
- Comparable sales analysis integration
- Market cycle timing considerations

## Implementation Roadmap

### Immediate Phase (Solutions Architecture)

**Priority 1: Excel Pro Forma Analysis**
- Deep analysis of reference Excel calculations
- Documentation of formula relationships
- Mapping to existing forecasted parameters

**Priority 2: Data Architecture Design**
- Cash flow data structure specifications
- Integration interface definitions
- Database schema extensions

**Priority 3: Integration Point Specification**
- Monte Carlo to DCF transformation logic
- DCF to investment decision workflows
- Result storage and retrieval patterns

### Development Phase

**Priority 1: Core DCF Engine**
- Cash flow projection algorithms
- NPV and IRR calculation functions
- Terminal value computation methods

**Priority 2: Monte Carlo Integration**
- Scenario-based calculation processing
- Results aggregation and statistical analysis
- Performance optimization implementation

**Priority 3: Investment Decision Framework**
- Decision logic based on financial metrics
- Risk assessment integration
- Recommendation engine development

## Risk Mitigation Strategies

### Technical Risks

**Computational Performance:**
- Prototype scenario processing approaches
- Benchmark calculation performance
- Implement caching and optimization strategies

**Data Integration Complexity:**
- Validate Monte Carlo to DCF data transformation
- Test edge cases and data quality scenarios
- Implement comprehensive error handling

### Business Logic Risks

**Assumption Validation:**
- Cross-reference Excel pro forma calculations
- Validate against industry standard methodologies
- Implement sensitivity analysis for key assumptions

**Market Data Accuracy:**
- Ensure forecast parameter alignment with DCF inputs
- Validate geographic and temporal data consistency
- Implement data quality monitoring

## Success Criteria

### Technical Success Metrics

- DCF calculations complete within 60 seconds for 500 scenarios
- Financial metrics match Excel pro forma results within 1% tolerance
- System handles multiple property analyses concurrently
- Database performance maintains sub-second query response times

### Business Success Metrics

- Investment recommendations align with Excel-based analysis
- Risk assessment accurately reflects market scenario variations
- Financial projections demonstrate statistical validity
- User workflow provides comprehensive investment decision support

## Next Steps

1. **Excel Pro Forma Structure Analysis** - Extract exact calculation methodology from reference file
2. **DCF Data Architecture Design** - Define cash flow structures and integration interfaces
3. **Integration Point Specification** - Design Monte Carlo to DCF to Investment Decision workflow

This architectural foundation ensures the DCF engine integrates seamlessly with existing infrastructure while providing the financial calculation capabilities required for comprehensive real estate investment analysis.