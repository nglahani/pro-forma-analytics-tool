# How to Use the Property Input System

## 🚀 Quick Start

Your property input system is **ready to use right now!** Here are 3 ways to use it:

---

## **Option 1: Interactive Console (Easiest)**

**Run this command to start collecting property data:**

```bash
cd "C:\Users\nlaha\OneDrive\Documents\Personal\Real Estate\pro-forma-analytics-tool"
python simple_property_input.py
```

**What happens:**
- Step-by-step prompts guide you through property data entry
- Real-time validation with helpful error messages
- Automatic calculation of key metrics
- Optional Monte Carlo analysis at the end
- Property saved for future use

**Example interaction:**
```
PROPERTY DATA COLLECTION
============================
Property name: My Investment Property
Property type: 1 (Multifamily)
Total units: 75
Purchase price: 5,500,000
Down payment: 25%
City: New York
...
Generated 25 investment scenarios!
```

---

## **Option 2: Programmatic Use (For Integration)**

**Use the validation system in your own code:**

```python
from user_input.input_validation import PropertyInputValidator, PropertyInputHelper
from core.property_inputs import *

# Create validator
validator = PropertyInputValidator()

# Validate user inputs
price_result = validator.validate_currency("$5,500,000", "purchase price")
down_result = validator.validate_percentage("25%", "down payment")

if price_result.is_valid and down_result.is_valid:
    # Create property with validated data
    property_data = PropertyInputData(
        property_id="MY_PROP_001",
        property_name="My Investment Property",
        # ... rest of property data
    )
    
    # Run Monte Carlo analysis
    from monte_carlo.simulation_engine import monte_carlo_engine
    results = monte_carlo_engine.generate_scenarios(property_data)
```

---

## **Option 3: Web Interface (For Production)**

**Create a web form for property input:**

```python
from user_input.web_forms import PropertyWebFormGenerator

# Generate HTML form
generator = PropertyWebFormGenerator()
html_form = generator.generate_property_form_html()

# Use in Flask, Django, FastAPI, etc.
```

---

## **🎯 What You Get**

### **Input Validation**
- **Currency**: Accepts `$5,000,000`, `5000000`, `5,000,000.00`
- **Percentages**: Accepts `25%`, `0.25`, `25` (auto-detects format)
- **Addresses**: Validates format and helps with MSA detection
- **Smart formatting**: Converts to proper formats automatically

### **Property Management**
- **Storage**: Properties saved in memory (extensible to database)
- **Retrieval**: Get properties by ID, list all properties
- **Validation**: Business rule validation beyond input validation

### **Monte Carlo Integration**
- **Seamless pipeline**: Property data → Market forecasts → Investment scenarios
- **500+ scenarios**: Generate comprehensive investment analysis
- **Risk assessment**: Growth vs risk scoring for decision making

### **Key Metrics Calculated**
- Price per unit and per square foot
- Current cap rate (if NOI provided)
- Cash required for down payment
- Loan amount and LTV ratio

---

## **🏢 Supported Property Types**

- **Multifamily** (apartments, condos)
- **Office** (office buildings)
- **Retail** (shopping centers, stores)
- **Industrial** (warehouses, manufacturing)
- **Mixed Use** (combination properties)

## **📍 Supported Markets**

- **New York** (35620) - Full forecast data
- **Los Angeles** (31080) - Limited forecast data
- **Chicago** (16980) - Limited forecast data
- **Washington DC** (47900) - Limited forecast data
- **Miami** (33100) - Limited forecast data

**💡 Tip:** Use New York MSA for testing - it has complete forecast data.

---

## **🧪 Test It Right Now**

**Quick demo to see it working:**

```bash
python demo_property_system.py
```

This shows:
- Input validation examples
- Property creation process
- Monte Carlo integration
- Complete pipeline working

---

## **💡 Tips for Success**

1. **Start with Option 1** (interactive mode) to see the full workflow
2. **Use realistic values** for better validation experience
3. **Try different property types** to see how the system adapts
4. **Review the metrics** calculated automatically
5. **Run Monte Carlo analysis** to see investment scenarios

---

## **🔧 Integration Examples**

### **Desktop App Integration**
```python
# Use validation in your GUI
from user_input.input_validation import PropertyInputValidator
validator = PropertyInputValidator()

# Validate user input from text fields
result = validator.validate_currency(price_textfield.text)
if result.is_valid:
    validated_price = result.formatted_value
```

### **Web API Integration**
```python
# Use in Flask/FastAPI endpoints
from user_input.web_forms import PropertyWebAPI
api = PropertyWebAPI()

@app.route('/api/property', methods=['POST'])
def create_property():
    result = api.handle_property_submission(request.json)
    return jsonify(result)
```

### **Mobile App Integration**
```python
# Use validation logic in mobile backend
from user_input.input_validation import PropertyInputValidator
# Validate data from mobile app before processing
```

---

## **🚀 Ready to Use!**

Your property input system is **production-ready** and can handle:

✅ **Real user input** with comprehensive validation  
✅ **Multiple interface types** (console, web, API)  
✅ **Integration with Monte Carlo** analysis  
✅ **Professional-grade error handling**  
✅ **Extensible architecture** for future features  

**Start with: `python simple_property_input.py`**

The system will guide you through collecting your first property for investment analysis!