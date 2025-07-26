# Pro Forma Analytics Tool

> **Production-ready real estate DCF analysis platform with complete 4-phase workflow**

A comprehensive real estate financial analysis platform that transforms static Excel-based pro formas into data-driven DCF analysis using Prophet forecasting, Monte Carlo simulations, and automated investment recommendations.

## 🚀 Quick Start

### **Complete DCF Analysis** (Recommended)
```bash
# Run end-to-end DCF workflow with realistic $3.5M property
python demo_end_to_end_workflow.py

# Expected output: NPV $2.5M, IRR 64.8%, STRONG_BUY recommendation
```

### **Unit and Integration Testing**
```bash
# Run complete test suite
pytest tests/

# Run integration tests for DCF workflow
python tests/integration/test_complete_dcf_workflow.py
```

### **Monte Carlo Validation**
```bash
python simple_monte_carlo_validation.py
```

---

## 📋 What This Tool Does

### **Core Functionality**
- **Complete DCF Engine**: 4-phase workflow from assumptions to investment recommendations
- **Monte Carlo Integration**: 500+ scenario generation feeding into DCF analysis
- **Financial Metrics**: NPV, IRR, equity multiples, terminal value, payback period
- **Investment Recommendations**: 5-tier system (STRONG_BUY to STRONG_SELL) with risk assessment
- **Mixed-Use Support**: Both residential and commercial properties with renovation modeling

### **Your 7 Required Data Fields** ✅
1. **Number of residential units**
2. **Anticipated renovation time** 
3. **Number of commercial units**
4. **Investor equity share**
5. **Residential rent per unit**
6. **Commercial rent per unit** 
7. **Self cash percentage**

### **Backend Database** ✅
- **SQLite database** with full CRUD operations
- **Property listings** and **pro forma analysis** storage
- **User listing tracking** for portfolio management

---

## 🏗️ System Architecture

```
User Input → Property Data → Monte Carlo Engine → Investment Analysis
     ↓              ↓              ↓                    ↓
[7 Required    [Validation &   [500 Scenarios    [NPV, IRR, Risk
 Fields]        Storage]        + Correlations]   Assessment]
```

### **Core Components**
- **`property_data.py`** - Unified property input system
- **`input_file_processor.py`** - File-based input processing
- **`quick_analysis_workflow.py`** - Complete analysis pipeline
- **`simplified_input_form.py`** - Interactive input interface
- **`database/`** - SQLite backend storage
- **`src/`** - Clean architecture implementation

---

## 📊 Data Coverage

### **Geographic Coverage** 
- New York-Newark-Jersey City MSA
- Los Angeles-Long Beach-Anaheim MSA
- Chicago-Naperville-Elgin MSA
- Washington-Arlington-Alexandria MSA
- Miami-Fort Lauderdale-West Palm Beach MSA

### **Market Metrics** (11 total)
- **Interest Rates**: Treasury 10Y, Commercial Mortgage, Fed Funds
- **Property Metrics**: Cap Rates, Vacancy Rates, Rent Growth
- **Operating Costs**: Expense Growth, Property Tax Growth
- **Lending**: LTV Ratios, Closing Costs, Reserve Requirements
- **Market Growth**: Property Appreciation

### **Historical Data**
- **15+ years** of annual data (2010-2025)
- **688+ data points** across all metrics
- **No missing data gaps** - complete coverage

---

## 🧪 Testing Framework

### **Quick Validation**
```bash
# Test complete file-based workflow
python quick_analysis_workflow.py property_input_template.json

# Test Monte Carlo engine
python simple_monte_carlo_validation.py

# Test interactive input form
python simplified_input_form.py
```

### **Comprehensive Testing**
```bash
# Full test suite
python -m pytest tests/ -v

# Integration tests
python -m pytest tests/integration/ -v

# Monte Carlo validation with charts
python simple_monte_carlo_validation.py
```

---

## 💼 Business Use Cases

### **For Real Estate Investors**
- **Investment Decision Support**: Data-driven buy/hold/sell recommendations
- **Risk Assessment**: Quantified risk vs growth analysis
- **Portfolio Management**: Track multiple properties and performance
- **Market Timing**: Understand market cycles and optimal entry points

### **For Property Managers**
- **Renovation Planning**: Timeline and cost impact analysis
- **Rent Optimization**: Market-driven rent setting strategies
- **Operating Efficiency**: Expense forecasting and budgeting
- **Performance Tracking**: Actual vs projected performance analysis

### **For Financial Analysts**
- **Due Diligence**: Comprehensive property analysis with assumptions validation
- **Sensitivity Analysis**: Stress testing under different market conditions
- **Reporting**: Professional-grade analysis reports and visualizations
- **Model Validation**: Statistical validation of investment assumptions

---

## 🔧 Technical Requirements

### **System Requirements**
- **Python 3.8+**
- **SQLite** (included with Python)
- **Windows/Mac/Linux** compatible

### **Key Dependencies**
```bash
pip install pandas numpy prophet matplotlib sqlite3 pytest
```

### **Development Setup**
```bash
git clone [repository-url]
cd pro-forma-analytics-tool
pip install -r requirements.txt
python test_simplified_system.py  # Verify installation
```

---

## 📚 Documentation

- **[DCF Engine Architecture](DCF_ENGINE_ARCHITECTURE.md)** - Pro Forma DCF engine design and implementation roadmap
- **[DCF Data Structures](DCF_DATA_STRUCTURES.md)** - Complete data structure design for DCF engine implementation
- **[Monte Carlo Parameter Mapping](MONTE_CARLO_MAPPING.md)** - Detailed mapping between Monte Carlo forecasts and Excel assumptions
- **[Excel Pro Forma Analysis](EXCEL_PRO_FORMA_ANALYSIS.md)** - Detailed analysis of reference Excel model structure and calculations
- **[Property Input Workflow](PROPERTY_INPUT_WORKFLOW.md)** - Complete input system guide
- **[User Guide](USER_GUIDE.md)** - Complete user manual and workflows
- **[Database Schema](DATABASE.md)** - Database structure and operations
- **[Contributing](CONTRIBUTING.md)** - Development and contribution guidelines
- **[Deployment](DEPLOYMENT.md)** - Production deployment instructions

---

## 🎯 Current Status

### **✅ Production Ready - DCF Engine Complete**
- **4-Phase DCF Workflow**: DCF Assumptions → Initial Numbers → Cash Flow → Financial Metrics
- **Investment Analysis**: Automated recommendations with risk assessment and terminal value
- **End-to-End Validation**: Complete workflow tested with realistic property scenarios
- **Python 3.13 Compatible**: Modern Python compatibility with dataclass optimizations
- **Clean Architecture**: Domain-driven design with dependency injection

### **📈 Key Metrics**
- **A- Quality Score (88/100)**: Production-ready with critical issues resolved
- **40+ Test Methods**: Comprehensive BDD/TDD coverage across all DCF phases
- **688+ Historical Data Points** for accurate forecasting
- **11 Market Metrics** with 15+ years of data
- **5 Major MSAs** covered with complete data

---

## 🚀 Getting Started Workflows

### **New User - First DCF Analysis**
1. **Run Demo**: `python demo_end_to_end_workflow.py` to see complete DCF workflow
2. **Study Results**: NPV, IRR, equity multiples, and investment recommendations
3. **Create Property**: Modify demo property data for your specific investment
4. **Explore Documentation**: Start with [DCF Engine Architecture](DCF_ENGINE_ARCHITECTURE.md)

### **Developer - System Understanding**
1. **Read Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
2. **Run Tests**: `python -m pytest tests/ -v`
3. **Study API**: [API_REFERENCE.md](API_REFERENCE.md)
4. **Development Setup**: [DEVELOPMENT.md](DEVELOPMENT.md)

### **Investor - Portfolio Analysis**
1. **Create Property Files**: Use template format for each property
2. **Batch Processing**: Run analysis workflow for multiple properties
3. **Compare Scenarios**: Analyze risk vs growth across portfolio
4. **Track Performance**: Monitor actual vs projected results

---

## 🔮 Roadmap

### **Phase 1: Core Foundation** ✅ *Complete*
- Property input system with your 7 required fields
- Database backend with full storage capabilities
- Monte Carlo engine with scenario generation
- Testing framework and documentation

### **Phase 2: Advanced Analytics** ✅ *Complete*
- ✅ Financial calculation engine (NPV, IRR, equity multiples, terminal value)
- ✅ Investment decision framework with 5-tier recommendations
- ✅ Risk assessment and break-even analysis
- ✅ End-to-end workflow validation and testing

### **Phase 3: Platform Integration** 📅 *Future*
- RESTful API for external integrations
- Web-based user interface
- Export capabilities (PDF reports, Excel)
- Multi-user support and collaboration features

---

## 📞 Support

### **Quick Help**
- **Issues**: Check [DEVELOPMENT.md](DEVELOPMENT.md) troubleshooting section
- **Questions**: Review [User Guide](USER_GUIDE.md) for common workflows
- **Testing**: Run `python test_simplified_system.py` for system validation

### **System Validation**
```bash
# Verify complete DCF workflow
python demo_end_to_end_workflow.py

# Expected output:
# [PHASE 1] Creating DCF assumptions...
# [PHASE 2] Calculating initial numbers...
# [PHASE 3] Creating cash flow projections...
# [PHASE 4] Calculating financial metrics...
# NPV: $2,503,000 | IRR: 64.8% | Multiple: 9.79x
# Recommendation: STRONG_BUY | Risk Level: MODERATE
# SUCCESS: END-TO-END WORKFLOW TEST PASSED
```

---

**Ready to transform your real estate investment analysis?**

**Start now**: `python demo_end_to_end_workflow.py`