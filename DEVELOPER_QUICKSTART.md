# Developer Quick-Start Guide

## 🚀 Get Running in 5 Minutes

### 1. Setup & Installation
```bash
# Clone and setup
git clone https://github.com/nglahani/pro-forma-analytics-tool.git
cd pro-forma-analytics-tool

# Create virtual environment (Python 3.10-3.11)  
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Initialize databases (2,174+ data points)
python data_manager.py setup

# Verify everything works
python demo_end_to_end_workflow.py
```

### 2. Understanding the Code Structure

```
📁 Key Folders for New Developers:
├── src/application/services/          # 🔥 START HERE - 4 DCF Phase Services
├── src/domain/entities/              # Business objects (Property, CashFlow, etc.)  
├── demo_end_to_end_workflow.py       # 👀 WORKING EXAMPLE - Shows complete flow
├── tests/integration/                # End-to-end test examples
└── BUSINESS_PROCESS_OVERVIEW.md      # Business context
```

### 3. The 4-Phase DCF Workflow (Your First Code Review)

**🎯 Start Here**: Open `demo_end_to_end_workflow.py` and follow along:

```python
# PHASE 1: Market scenarios → Financial assumptions
dcf_assumptions = dcf_service.create_dcf_assumptions_from_scenario(scenario, property)

# PHASE 2: Calculate acquisition costs & financing  
initial_numbers = initial_service.calculate_initial_numbers(property, dcf_assumptions)

# PHASE 3: Project 6-year cash flows
cash_flows = cash_flow_service.calculate_cash_flow_projection(dcf_assumptions, initial_numbers)

# PHASE 4: Calculate NPV, IRR, investment recommendation
metrics = financial_service.calculate_financial_metrics(cash_flows, dcf_assumptions, initial_numbers)
```

### 4. Making Your First Change

**Easy Win**: Add a new property type to the analysis.

1. **Find the code**: `src/domain/entities/property_data.py`  
2. **Look for**: `SimplifiedPropertyInput` class
3. **Add field**: Maybe `property_subtype` (e.g., "luxury", "affordable", "mixed-income")
4. **Test it**: Update `demo_end_to_end_workflow.py` to use your new field
5. **Run tests**: `python -m pytest tests/ -v`

### 5. Key Business Concepts (for Code Context)

- **DCF** = Discounted Cash Flow (NPV calculation using projected cash flows)
- **IRR** = Internal Rate of Return (what % return does this investment generate?)  
- **LTV** = Loan-to-Value ratio (how much is financed vs. cash down)
- **NOI** = Net Operating Income (rental income minus expenses)
- **Cap Rate** = NOI ÷ Property Value (market valuation metric)
- **Waterfall** = How profits are split between investors and operators

### 6. Testing Your Changes

```bash
# Quick validation (< 1 minute)
python demo_end_to_end_workflow.py

# Core business logic tests (2-3 minutes)  
pytest tests/unit/application/ tests/integration/ -v

# Full test suite if needed
pytest tests/ -v --cov=src --cov=core --cov=monte_carlo
```

### 7. Common Developer Tasks

#### **Add a New Financial Metric**
1. Update `src/domain/entities/financial_metrics.py`
2. Add calculation logic in `src/application/services/financial_metrics_service.py` 
3. Add tests in `tests/unit/application/test_financial_metrics_service.py`
4. Update demo to show new metric

#### **Modify Cash Flow Calculations**
1. Look at `src/application/services/cash_flow_projection_service.py`
2. Find the specific calculation method (rent growth, expenses, etc.)
3. Modify business logic 
4. Run `python demo_end_to_end_workflow.py` to see impact

#### **Add New Property Data Fields**
1. Update `src/domain/entities/property_data.py`
2. Update any services that use property data
3. Update demo with example data
4. Add validation tests

### 8. Debugging Tips

**🔍 When something breaks:**

1. **Start with the demo**: `python demo_end_to_end_workflow.py`
2. **Check logs**: Services log their operations to console
3. **Use tests**: `pytest tests/integration/ -v -s` (shows print statements)
4. **Trace the flow**: Follow data through each phase

**🐛 Common issues:**
- **Import errors**: Check virtual environment is activated
- **Database errors**: Run `python data_manager.py setup` 
- **Test failures**: Make sure all dependencies installed

### 9. Architecture Overview (Advanced)

```
🏗️ Clean Architecture Layers:
├── Domain Layer (src/domain/)         # Pure business logic, no dependencies
├── Application Layer (src/application/) # Use cases, orchestrates domain logic  
├── Infrastructure Layer (src/infrastructure/) # Databases, external services
└── External Engines (monte_carlo/, forecasting/) # Specialized calculation engines
```

**Dependencies flow inward**: Infrastructure → Application → Domain

### 10. Next Steps After Your First Change

1. **Read business docs**: `BUSINESS_PROCESS_OVERVIEW.md`
2. **Explore tests**: `tests/integration/test_complete_dcf_workflow.py` 
3. **Check CI/CD**: `.github/workflows/ci.yml` shows the build pipeline
4. **Add features**: Look at GitHub issues for feature requests
5. **Optimize performance**: `tests/performance/` shows current benchmarks

---

## 🎯 Success Metrics

You'll know you're productive when you can:
- ✅ Run the demo and understand the output  
- ✅ Make a small change and see it reflected in results
- ✅ Run tests and understand what they're validating
- ✅ Explain the 4-phase DCF workflow to a business stakeholder
- ✅ Debug a failing test or broken demo

**Welcome to the team! The codebase is designed to be approachable - don't hesitate to experiment and ask questions.**