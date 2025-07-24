# Excel Pro Forma Structure Analysis

## Executive Summary

This document provides a comprehensive analysis of the reference Excel pro forma model (`MultiFamily_RE_Pro_Forma.xlsx`) that serves as the foundation for our DCF engine implementation. The Excel model represents a sophisticated 6-year real estate investment analysis with investor waterfall distributions.

## Excel Model Overview

**File Structure:**
- Single sheet: "Pro Forma"
- Dimensions: 46 rows x 12 columns
- Time horizon: 6 years (Year 0 through Year 5)
- Year 0: Initial investment period
- Years 1-5: Operating cash flow projections
- Year 5: Terminal value/exit year

## Four Main Sections

### Section A: ASSUMPTIONS (Rows 1-8)
**Purpose:** Market characteristics that affect the DCF model but are not property-specific

**Key Parameters:**
- Interest Rate: 7% (Cell C3)
- LTV (Loan-to-Value): 75% (Cell C4) 
- Self Cash: 25% (Cell E3)
- Equity Share (Investor): 80% (Cell C6)
- Preferred Return: 6% (Cell C7)
- Rent Growth: 3% (Cell E5)
- Property Growth: 2% (Cell E6)
- Expense Growth: 2% (Cell E7)
- Vacancy Rate: (Cell G3)
- Closing Cost %: (Cell G4)
- Market Cap Rate: (Cell G5)

**Monte Carlo Integration:** These parameters will be sourced from our forecasted Monte Carlo scenarios rather than hard-coded values.

### Section B: INITIAL NUMBERS (Rows 9-25)
**Purpose:** User input property specifics combined with derived calculations

**Property Details:**
- Purchase Price: $895,000 (Cell C12)
- Closing Cost: $44,750 (Cell C13)
- Renovation CapEx: $45,000 (Cell C14)
- Cost Basis: $984,750 (Cell C15)

**Financing Calculations:**
- Loan Amount: $738,562 (Cell C17)
- Annual Interest: $51,699 (Cell C18)
- Lender Reserves: $17,509 (Cell C19)

**Equity Requirements:**
- Investor Cash: $197,773 (Cell C22)
- Our Cash: $65,924 (Cell C23)
- Total Cash: $263,697 (Cell C24)

**Valuation:**
- ARV (After Repair Value): $1,244,010 (Cell C26)

**Income Structure:**
- Pre-Renovation Residential Rent/Unit: $2,000 (Cell C30)
- Pre-Renovation Commercial Rent/Unit: $2,000 (Cell C31)
- Pre-Renovation Gross Rent: $64,800 (Cell C32)
- Post-Renovation Residential Rent/Unit: $2,250 (Cell C34)
- Post-Renovation Commercial Rent/Unit: $2,250 (Cell C35)
- Post-Renovation Gross Rent: $72,900 (Cell C36)

**Operating Expenses (Year 1):**
- Property Taxes: $9,848 (Cell C39)
- Insurance: $1,500 (Cell C40)
- Repairs & Maintenance: $1,500 (Cell C41)
- Property Management: $3,240 (Cell C42)
- Admin: $500 (Cell C43)
- Contracting: $1,000 (Cell C44)
- Replacement Reserves: $750 (Cell C45)
- Total Expenses: $18,338 (Cell C46)

### Section C: CASH FLOW PROJECTIONS (Columns F-K, Years 0-5)
**Purpose:** Combines assumptions and initial numbers into year-by-year DCF analysis

**Column Structure:**
- Column F: Year 0 (Initial investment)
- Column G: Year 1
- Column H: Year 2
- Column I: Year 3
- Column J: Year 4
- Column K: Year 5 (Exit year)

**Cash Flow Components:**
- Income (with renovation period adjustments)
- Operating Expenses (with annual growth)
- Net Operating Income (NOI)
- Interest Payments (interest-only debt service)
- Cash Flow After Financing (CFAF)
- Preferred Return Distribution
- Remaining Cash Flow
- Investor Share
- Operator Share

**Terminal Value Calculation:**
- Formula: Final Year NOI ÷ Market Cap Rate
- Location: Cell K30 (exit proceeds distribution)

### Section D: KPIs (Columns K-L, Rows 36-40)
**Purpose:** Final investment performance metrics

**Financial Metrics:**
- Investor IRR
- Operator IRR  
- Exit Cap Rate
- Investor NPV (5% discount rate)
- Operator NPV (5% discount rate)

## Key Model Logic

### Renovation Period Handling
**Method:** Proportional income reduction in Year 1
**Example:** 6-month renovation = 50% reduction in Year 1 rental income
**Implementation:** Year 1 Income = Post-Renovation Rent × (12 - Renovation Months) ÷ 12

### Growth Rate Application
**Rent Growth:** Applied annually to gross rental income starting Year 2
**Expense Growth:** Applied annually to all operating expenses starting Year 2
**Property Growth:** Applied to property value for terminal value calculation

### Debt Service Structure
**Type:** Interest-only payments
**Calculation:** Loan Amount × Interest Rate
**Principal Paydown:** Occurs only at exit/sale

### Cash Flow Distribution (Waterfall)
**Step 1:** Preferred Return (6% cumulative) to investor
**Step 2:** Remaining cash flows split per equity share (80% investor, 20% operator)
**Exit Distribution:** Same equity split applied to sale proceeds after loan payoff

### Terminal Value Methodology
**Calculation:** Year 5 NOI ÷ Market Cap Rate
**Market Cap Rate:** Sourced from assumptions section
**Distribution:** Exit proceeds distributed per equity share after debt payoff

## DCF Engine Implementation Roadmap

### Phase 1: Assumption Data Integration
**Objective:** Replace hard-coded assumptions with Monte Carlo forecasts

**Required Mappings:**
- Interest Rate → Commercial Mortgage Rate forecast ✓
- Cap Rate → Cap Rate forecast ✓
- Rent Growth → Rent Growth forecast ✓
- Expense Growth → Expense Growth forecast ✓
- Property Growth → Property Growth forecast ✓
- Vacancy Rate → Vacancy Rate forecast (unused in original Excel)
- LTV Ratio → LTV Ratio forecast (unused in original Excel)
- Closing Cost % → Closing Cost forecast (unused in original Excel)

**Note:** All 11 forecasted parameters should be available for DCF engine use

### Phase 2: Initial Numbers Calculator
**Objective:** Build property-specific calculations using user inputs + assumptions

**Required Components:**
- Purchase price and acquisition cost calculations
- Financing calculations (loan amount, interest, reserves)
- Equity requirement calculations (investor/operator split)
- Income projections (pre/post renovation, unit counts)
- Operating expense calculations

### Phase 3: Cash Flow Projection Engine
**Objective:** Year-by-year DCF calculations (Years 0-5)

**Required Components:**
- Annual income calculations with growth rates
- Annual expense calculations with growth rates
- NOI calculations (income - expenses - vacancy)
- Debt service calculations (interest-only)
- Cash flow after financing calculations
- Waterfall distribution calculations (preferred return + equity splits)
- Terminal value calculations (exit year)

### Phase 4: KPI Calculator
**Objective:** Investment performance metrics

**Required Components:**
- IRR calculations (investor and operator cash flows)
- NPV calculations (5% discount rate, investor and operator)
- Exit cap rate validation
- Investment recommendation logic

## Technical Implementation Considerations

### Data Flow Architecture
```
Monte Carlo Scenarios → Assumption Parameters
User Property Input → Initial Numbers Calculations
Combined → Cash Flow Projections (Years 0-5)
Cash Flows → Financial Metrics (IRR, NPV)
Financial Metrics → Investment Recommendations
```

### Key Calculations for Replication

**Annual Income Calculation:**
```
Year 1: Post-Renovation Annual Rent × (12 - Renovation Months) ÷ 12
Year 2+: Previous Year Income × (1 + Rent Growth Rate) × (1 - Vacancy Rate)
```

**Annual Expense Calculation:**
```
Year 1: Full Annual Operating Expenses (no renovation reduction)
Year 2+: Previous Year Expenses × (1 + Expense Growth Rate)
```

**Preferred Return Distribution (Cumulative):**
```
Accumulated Shortfall = Previous shortfall + (Preferred Return - Current Year CFAF)
If CFAF >= (Preferred Return + Accumulated Shortfall): 
    Investor gets Preferred Return + Accumulated Shortfall
    Remaining CFAF: Split per equity share
    Reset Accumulated Shortfall = 0
If CFAF < (Preferred Return + Accumulated Shortfall):
    Investor gets all CFAF
    Update Accumulated Shortfall for next year
```

**Terminal Value:**
```
Terminal Value = Year 5 NOI ÷ Exit Cap Rate
Net Proceeds = Terminal Value - Outstanding Loan Balance
Distribution = Net Proceeds × Equity Share %
```

**IRR Calculation:**
```
Cash Flow Series: [Year 0 Investment, Year 1 CF, Year 2 CF, ..., Year 5 CF + Terminal Distribution]
IRR = Internal Rate of Return of cash flow series
```

**NPV Calculation:**
```
NPV = Sum of [Cash Flow ÷ (1 + 5%)^Year] for all years
```

## Critical Implementation Notes

### Preferred Return Handling
**Implementation:** True cumulative preferred return logic required
**Logic:** If Year N CFAF < preferred return, shortfall carries forward to Year N+1
**Calculation:** Investor receives preferred return + accumulated shortfall before equity splits
**Priority:** Implement correct cumulative logic (improve upon Excel model)

### Monte Carlo Integration Points
**Scenario Processing:** Each Monte Carlo scenario provides different assumption parameters
**Bulk Calculation:** DCF engine must process 500+ scenarios efficiently
**Result Aggregation:** NPV/IRR distributions across scenarios for risk analysis

### Database Schema Requirements
**Cash Flow Storage:** Year-by-year projections for each scenario
**Metrics Storage:** IRR, NPV, and derived metrics for each scenario
**Parameter Tracking:** Which Monte Carlo parameters influenced each calculation

## Validation Strategy

### Excel Model Verification
**Test Cases:** Replicate exact Excel calculations with known inputs
**Tolerance:** Financial metrics within 1% of Excel results
**Comprehensive Testing:** Multiple property types and renovation scenarios

### Monte Carlo Integration Testing
**Parameter Sensitivity:** Verify calculations respond correctly to forecast variations
**Scenario Volume:** Ensure performance with 500+ scenario calculations
**Statistical Validation:** Distribution analysis of NPV/IRR results

## Success Criteria

**Technical Performance:**
- DCF calculations complete within 60 seconds for 500 scenarios
- Financial metrics match Excel model within 1% tolerance
- System handles concurrent property analyses

**Business Validation:**
- Investment recommendations align with Excel-based analysis
- Risk assessment reflects Monte Carlo scenario variations
- Cash flow projections demonstrate statistical validity

This analysis provides the foundation for implementing a DCF engine that accurately replicates the Excel model logic while integrating with our Monte Carlo forecasting infrastructure.