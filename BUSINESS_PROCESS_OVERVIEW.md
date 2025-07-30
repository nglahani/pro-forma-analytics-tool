# Real Estate DCF Analysis - Business Process Overview

## Quick Start for New Developers & Business SMEs

This document explains the **4-Phase DCF Workflow** in business terms that both developers and business process experts can quickly understand.

## The Big Picture

**Goal**: Analyze whether a real estate investment will be profitable using data-driven forecasting instead of static spreadsheet assumptions.

**Input**: Property details + Market forecasts  
**Output**: Investment recommendation (STRONG_BUY to STRONG_SELL) with financial metrics

---

## 4-Phase DCF Workflow

### 📊 **PHASE 1: DCF Assumptions** 
*File: `src/application/services/dcf_assumptions_service.py`*

**Business Purpose**: Convert market forecasts into specific financial parameters for this property.

**What Happens**:
- Takes Monte Carlo market scenarios (probabilistic forecasts)
- Maps them to property-specific assumptions (interest rates, cap rates, growth rates)
- Validates all assumptions against business rules

**Example**:
```
Monte Carlo Input: Interest rates 6.8-7.5%, Cap rates 5.9-6.3%
↓
DCF Assumptions: Use 7.2% interest rate, 6.1% cap rate for this property
```

---

### 💰 **PHASE 2: Initial Numbers**
*File: `src/application/services/initial_numbers_service.py`*

**Business Purpose**: Calculate all upfront costs and financing structure.

**What Happens**:
- Calculates total acquisition costs (purchase + closing + renovation)
- Determines financing (loan amount, LTV ratio, cash required)
- Sets up initial income and expense projections

**Example**:
```
$3.5M Property + $400K Renovation + $175K Closing Costs
↓
Total: $4.075M → 75% LTV = $3.06M Loan, $1.015M Cash Required
```

---

### 📈 **PHASE 3: Cash Flow Projections**
*File: `src/application/services/cash_flow_projection_service.py`*

**Business Purpose**: Model the property's financial performance over 6 years.

**What Happens**:
- Projects rental income growth year by year
- Calculates operating expenses (management, maintenance, taxes)
- Models debt service payments
- Computes investor distributions (waterfall structure)

**Example**:
```
Year 1: $936K Income - $279K Expenses - $206K Debt Service = $451K NOI
Year 2: $988K Income - $286K Expenses - $204K Debt Service = $498K NOI
...continuing through Year 5
```

---

### 🎯 **PHASE 4: Financial Metrics**
*File: `src/application/services/financial_metrics_service.py`*

**Business Purpose**: Calculate investment returns and provide buy/sell recommendation.

**What Happens**:
- Computes Net Present Value (NPV) - dollar value created
- Calculates Internal Rate of Return (IRR) - annualized return percentage  
- Determines equity multiple - how many times investment is returned
- Models property sale at Year 5 (terminal value)
- Provides investment recommendation with risk assessment

**Example**:
```
6-Year Cash Flows + Terminal Sale
↓  
NPV: $2.5M | IRR: 64.8% | Multiple: 9.79x | STRONG_BUY
```

---

## Key Business Concepts

### **Monte Carlo Simulation**
Instead of using single "best guess" numbers, the system runs 500+ scenarios with different market conditions to understand the range of possible outcomes.

### **Waterfall Distribution**
Models how profits are shared between investors and operators based on preferred returns and profit-sharing agreements.

### **Terminal Value**
Assumes the property is sold at Year 5 and calculates the proceeds based on projected NOI and exit cap rates.

### **Investment Recommendations**
- **STRONG_BUY**: Exceptional returns with acceptable risk
- **BUY**: Good returns with moderate risk  
- **HOLD**: Marginal returns, consider alternatives
- **SELL**: Poor returns or high risk
- **STRONG_SELL**: Likely to lose money

---

## For Developers: Code Organization

```
src/application/services/
├── dcf_assumptions_service.py     # PHASE 1: Market data → Assumptions
├── initial_numbers_service.py     # PHASE 2: Costs & Financing  
├── cash_flow_projection_service.py # PHASE 3: 6-year cash flows
└── financial_metrics_service.py   # PHASE 4: NPV, IRR, Recommendations
```

**Entry Point**: `demo_end_to_end_workflow.py` shows the complete process.

**Domain Entities**: `src/domain/entities/` contains the business objects (Property, CashFlow, etc.)

**Data**: `data/databases/` contains 2,174+ historical data points for market analysis.

---

## For Business SMEs: Key Validation Points

1. **Phase 1**: Are the market assumptions realistic for this location and property type?
2. **Phase 2**: Do the acquisition costs and financing terms match market conditions?  
3. **Phase 3**: Are the income growth and expense projections reasonable?
4. **Phase 4**: Does the investment recommendation align with risk tolerance and return expectations?

---

## Quick Demo

Run the complete workflow:
```bash
python demo_end_to_end_workflow.py
```

Expected output: NPV ~$2.5M, IRR ~64.8%, STRONG_BUY recommendation for a $3.5M Chicago property.