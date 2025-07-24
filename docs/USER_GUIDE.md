# User Guide: Pro Forma Analytics Tool

> **Complete guide to using the real estate investment analysis platform**

This guide covers everything you need to know to use the pro forma analytics tool for real estate investment analysis.

---

## 🎯 Quick Start

### **1. File-Based Input (Recommended)**
```bash
# Edit property_input_template.json first, then run:
python quick_analysis_workflow.py property_input_template.json
```
**Expected Output:**
```
[SUCCESS] Property loaded to database
[SUCCESS] Generated 100 investment scenarios
[BUY] - Good growth potential with moderate risk
WORKFLOW COMPLETE - ANALYSIS SUCCESSFUL
```

### **2. Interactive Console Input**
```bash
# Interactive property input form
python simplified_input_form.py
```

### **3. Validate Monte Carlo Engine**
```bash
# Quick validation with charts
python simple_monte_carlo_validation.py
```

---

## 📋 Your 7 Required Data Fields

The system is designed around your specific requirements. Here's how to input each field:

### **1. Number of Residential Units**
- **What it is**: Total count of residential rental units
- **Example**: 12 units in a multifamily building
- **Validation**: Must be positive integer

### **2. Anticipated Renovation Time**
- **What it is**: Expected duration of renovations in months
- **Options**: 
  - `0` = No renovation needed
  - `1-60` = Months of renovation work
- **Example**: 6 months for major renovations

### **3. Number of Commercial Units**
- **What it is**: Count of commercial/retail spaces
- **Example**: 2 ground-floor retail units
- **Note**: Enter `0` if purely residential

### **4. Investor Equity Share**
- **What it is**: Percentage of ownership for investors
- **Range**: 0-100%
- **Example**: 75% (investors own 75%, you own 25%)

### **5. Residential Rent per Unit**
- **What it is**: Average monthly rent per residential unit
- **Format**: Dollar amount (e.g., $2,800)
- **Example**: $2,500/month average across all units

### **6. Commercial Rent per Unit**
- **What it is**: Average monthly rent per commercial space
- **Format**: Dollar amount (e.g., $4,200)
- **Note**: Enter $0 if no commercial units

### **7. Self Cash Percentage**
- **What it is**: Percentage of purchase price paid in cash
- **Range**: 0-100%
- **Example**: 25% (25% cash, 75% financing)

---

## 🏠 Property Input Workflows

### **Residential-Only Property**
```bash
python simplified_input_form.py
```
**Input Example:**
```
Property name: Downtown Apartments
1. Residential units: 20
2. Renovation time: 0 (no renovation)
3. Commercial units: 0
4. Investor equity: 100%
5. Residential rent: $1,800
6. Commercial rent: $0
7. Self cash: 20%
```

### **Mixed-Use Property**
```bash
python simplified_input_form.py
```
**Input Example:**
```
Property name: Main Street Mixed-Use
1. Residential units: 8
2. Renovation time: 4 months
3. Commercial units: 2
4. Investor equity: 80%
5. Residential rent: $2,800
6. Commercial rent: $4,200
7. Self cash: 30%
```

### **Property with Renovation**
```bash
python simplified_input_form.py
```
**Input Example:**
```
Property name: Renovation Project
1. Residential units: 15
2. Renovation time: 8 months
3. Commercial units: 0
4. Investor equity: 70%
5. Residential rent: $2,200
6. Commercial rent: $0
7. Self cash: 35%
```

---

## 📊 Understanding Your Results

### **Property Metrics Calculated**
After input, the system automatically calculates:

- **Total Units**: Residential + Commercial
- **Monthly Gross Rent**: Combined rent from all units
- **Annual Gross Rent**: Monthly rent × 12
- **Property Type**: Mixed-use vs. Multifamily classification
- **Price per Unit**: If purchase price provided
- **Cash Required**: Purchase price × Self cash percentage
- **Gross Cap Rate**: Annual rent ÷ Purchase price

### **Monte Carlo Analysis**
The system generates investment scenarios with:

- **Growth Scores**: 0.0 (low growth) to 1.0 (high growth)
- **Risk Scores**: 0.0 (low risk) to 1.0 (high risk)
- **Market Scenarios**: Bull, Bear, Neutral, Growth, Stress
- **Investment Recommendations**: Based on score combinations

### **Investment Recommendations**
- **STRONG BUY**: High growth (>0.5) + Low risk (<0.5)
- **BUY**: Good growth (>0.4) + Acceptable risk (<0.6)  
- **CONSIDER**: Moderate growth (>0.3) + Review risk tolerance
- **CAUTION**: Lower growth potential, consider alternatives

---

## 🗄️ Database Operations

### **View Your Properties**
```python
from database.property_database import property_db

# List all properties
properties = property_db.list_properties()
print(f"You have {len(properties)} properties")

# Get database statistics
stats = property_db.get_database_stats()
print(f"Total properties: {stats['total_properties']}")
print(f"Property types: {stats['property_types']}")
```

### **Retrieve Specific Property**
```python
# Load a property by ID
property_data = property_db.load_property("YOUR_PROPERTY_ID")
if property_data:
    print(f"Loaded: {property_data.property_name}")
    metrics = property_data.calculate_key_metrics()
    print(f"Annual rent: ${metrics['annual_gross_rent']:,.0f}")
```

### **User Listings Management**
```python
# Create user listing
listing_id = property_db.create_user_listing("your_username", property_id)

# Get all your listings
my_listings = property_db.get_user_listings("your_username")
print(f"You have {len(my_listings)} property listings")
```

---

## 📈 Monte Carlo Validation

### **Simple Validation**
```bash
python monte_carlo_validator.py --mode=simple --scenarios=100
```
**Use Cases:**
- Quick system validation
- Basic scenario analysis
- Development testing

### **Comprehensive Validation** 
```bash
python monte_carlo_validator.py --mode=comprehensive --scenarios=500
```
**Use Cases:**
- Full market analysis
- Investment decision making
- Portfolio risk assessment

### **Custom Analysis**
```bash
python monte_carlo_validator.py --mode=custom --scenarios=200 --years=10
```
**Use Cases:**
- Specific investment horizons
- Custom scenario counts
- Specialized analysis needs

### **Understanding Validation Charts**

1. **Growth Score Distribution**: Shows range of growth potential
2. **Risk Score Distribution**: Shows range of risk levels
3. **Risk vs Growth Scatter**: Relationship between risk and return
4. **Market Scenario Distribution**: Breakdown of market conditions
5. **Statistical Summary**: Mean, standard deviation, correlations
6. **Quality Checks**: Validation of scenario diversity and realism

---

## 🔧 Advanced Usage

### **Programmatic Property Creation**
```python
from property_data import SimplifiedPropertyInput, ResidentialUnits, CommercialUnits, RenovationInfo, InvestorEquityStructure, RenovationStatus
from datetime import date

# Create property programmatically
property_data = SimplifiedPropertyInput(
    property_id="PROG_001",
    property_name="Programmatic Property",
    analysis_date=date.today(),
    residential_units=ResidentialUnits(
        total_units=12,
        average_rent_per_unit=2500
    ),
    commercial_units=CommercialUnits(
        total_units=2,
        average_rent_per_unit=4000
    ),
    renovation_info=RenovationInfo(
        status=RenovationStatus.PLANNED,
        anticipated_duration_months=6
    ),
    equity_structure=InvestorEquityStructure(
        investor_equity_share_pct=80.0,
        self_cash_percentage=25.0
    ),
    city="New York",
    state="NY",
    msa_code="35620",
    purchase_price=2000000
)

# Calculate metrics
metrics = property_data.calculate_key_metrics()
print(f"ROI Potential: {metrics['gross_cap_rate']*100:.1f}%")
```

### **Batch Property Analysis**
```python
# Analyze multiple properties
properties = [property1, property2, property3]

for prop in properties:
    print(f"\n=== {prop.property_name} ===")
    metrics = prop.calculate_key_metrics()
    print(f"Units: {metrics['total_units']}")
    print(f"Annual Rent: ${metrics['annual_gross_rent']:,.0f}")
    print(f"Mixed Use: {metrics['is_mixed_use']}")
```

### **Export Property Data**
```python
# Convert to dictionary for export
property_dict = property_data.to_dict()

# Save to JSON
import json
with open('my_property.json', 'w') as f:
    json.dump(property_dict, f, indent=2)

# Load from JSON
with open('my_property.json', 'r') as f:
    loaded_dict = json.load(f)
    restored_property = SimplifiedPropertyInput.from_dict(loaded_dict)
```

---

## 🚨 Troubleshooting

### **Common Issues**

#### **"Property not saved to database"**
**Solution:**
```bash
# Check if database directory exists
ls data/databases/

# Reset database if needed
rm data/databases/property_listings.db
python test_simplified_system.py  # Recreates database
```

#### **"Monte Carlo analysis failed"**
**Solution:**
```bash
# Use NYC MSA (has full data coverage)
# In your property input, specify:
# City: New York
# State: NY
# This auto-assigns MSA code 35620
```

#### **"Import errors"**
**Solution:**
```bash
# Run from project root directory
cd "C:\Users\nlaha\OneDrive\Documents\Personal\Real Estate\pro-forma-analytics-tool"
python simplified_input_form.py
```

#### **"Unicode display issues"**
**Solution:**
```bash
# Use the non-Unicode test version
python test_simplified_system.py
```

### **Validation Commands**
```bash
# Test each component individually
python property_data.py                        # Test property data structures
python simple_monte_carlo_validation.py        # Test Monte Carlo engine
python simplified_input_form.py                # Test interactive input system
python quick_analysis_workflow.py              # Test complete file-based workflow
```

---

## 🎯 Best Practices

### **Property Input**
- **Be Realistic**: Use current market rates for rent estimates
- **Consider Location**: Specify city/state for accurate market analysis
- **Document Assumptions**: Use the notes field for key assumptions
- **Regular Updates**: Re-analyze properties quarterly with updated data

### **Monte Carlo Analysis**
- **Start Simple**: Use simple mode for initial validation
- **Scale Up**: Use comprehensive mode for investment decisions
- **Multiple Runs**: Run analysis multiple times to verify consistency
- **Save Results**: Export analysis results for documentation

### **Database Management**
- **Backup Regularly**: Copy `data/databases/` folder for backups
- **Organize Properties**: Use clear, descriptive property names
- **Track Changes**: Document major property updates and assumptions
- **User Separation**: Use different user IDs for different investors/projects

### **Investment Analysis**
- **Conservative Assumptions**: Use conservative rent and growth estimates
- **Stress Testing**: Test properties under different market scenarios
- **Portfolio Perspective**: Analyze properties as part of broader portfolio
- **Professional Review**: Have complex analyses reviewed by real estate professionals

---

## 📚 Additional Resources

### **System Architecture**
- See [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- Review [API_REFERENCE.md](API_REFERENCE.md) for developer information

### **Development and Testing**
- See [DEVELOPMENT.md](DEVELOPMENT.md) for development setup
- See [DATABASE.md](DATABASE.md) for database schema details

### **Market Data Sources**
- Federal Reserve Economic Data (FRED)
- U.S. Census Bureau
- Bureau of Labor Statistics
- Local MSA economic indicators

---

## 💬 Support

### **Quick Help**
1. **Run system validation**: `python quick_analysis_workflow.py property_input_template.json`
2. **Check documentation**: This user guide covers most scenarios
3. **Review error messages**: Most errors include helpful guidance
4. **Test with NYC**: Use New York properties for testing (full data coverage)

### **Expected System Performance**
- **Property Input**: < 5 minutes for manual entry
- **Database Operations**: < 1 second for save/load
- **Monte Carlo Analysis**: 30-60 seconds for 100 scenarios
- **Chart Generation**: 10-30 seconds depending on complexity

---

**Ready to analyze your real estate investments?**

**Start with**: `python quick_analysis_workflow.py property_input_template.json`