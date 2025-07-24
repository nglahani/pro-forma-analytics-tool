# Property Input System

## Overview

The Property Input System provides a comprehensive framework for collecting, validating, and managing user-entered property data for pro forma analysis. It seamlessly integrates with the existing Monte Carlo simulation engine to provide end-to-end investment analysis.

## Components

### 1. Input Validation (`input_validation.py`)

**PropertyInputValidator** - Validates and formats user input with helpful error messages and warnings:

```python
from user_input.input_validation import PropertyInputValidator

validator = PropertyInputValidator()

# Currency validation
result = validator.validate_currency("$5,000,000", "purchase price")
if result.is_valid:
    price = result.formatted_value  # 5000000.0

# Percentage validation (handles % symbols and auto-conversion)
result = validator.validate_percentage("25%", "down payment")
if result.is_valid:
    down_payment = result.formatted_value  # 0.25
```

**PropertyInputHelper** - Provides utility functions for forms and formatting:

```python
from user_input.input_validation import PropertyInputHelper

helper = PropertyInputHelper()

# Get form options
property_types = helper.get_property_type_options()
supported_msas = helper.get_supported_msas()

# Format values for display
formatted_price = helper.format_currency(5000000)  # "$5.00M"
formatted_rate = helper.format_percentage(0.07)    # "7.0%"
```

### 2. Interactive Property Collector (`property_collector.py`)

**PropertyInputCollector** - Provides guided, step-by-step property data collection:

```python
from user_input.property_collector import PropertyInputCollector

collector = PropertyInputCollector()
property_data = collector.collect_property_data()

if property_data:
    print(f"Collected: {property_data.property_name}")
    # Property is automatically added to property_manager
```

Features:
- ✅ Step-by-step guided input with helpful prompts
- ✅ Real-time validation with error messages and warnings  
- ✅ Automatic MSA detection based on city/state
- ✅ Unit mix collection for multifamily properties
- ✅ Property summary and confirmation
- ✅ Integration with Monte Carlo analysis

### 3. Web Forms (`web_forms.py`)

**PropertyWebFormGenerator** - Generates complete HTML forms for web applications:

```python
from user_input.web_forms import PropertyWebFormGenerator

generator = PropertyWebFormGenerator()
html_form = generator.generate_property_form_html()

# Use in Flask, Django, FastAPI, etc.
```

**PropertyWebAPI** - Flask-compatible API endpoints:

```python
from user_input.web_forms import PropertyWebAPI

api = PropertyWebAPI()
result = api.handle_property_submission(form_data)

if result['success']:
    property_id = result['property_id']
```

## Usage Examples

### Basic Property Creation

```python
from core.property_inputs import *
from user_input.input_validation import PropertyInputValidator
from datetime import date

validator = PropertyInputValidator()

# Validate user inputs
price_result = validator.validate_currency("$5,000,000", "purchase price")
down_result = validator.validate_percentage("25%", "down payment")

# Create property with validated inputs
property_data = PropertyInputData(
    property_id="PROP_001",
    property_name="Investment Property",
    analysis_date=date.today(),
    physical_info=PropertyPhysicalInfo(
        property_type=PropertyType.MULTIFAMILY,
        property_class=PropertyClass.CLASS_B,
        total_units=50,
        total_square_feet=45000,
        year_built=2015
    ),
    financial_info=PropertyFinancialInfo(
        purchase_price=price_result.formatted_value,
        down_payment_pct=down_result.formatted_value,
        current_noi=350000
    ),
    location_info=PropertyLocationInfo(
        address="123 Investment St",
        city="New York",
        state="NY",
        zip_code="10001",
        msa_code="35620"
    ),
    operating_info=PropertyOperatingInfo()
)
```

### Monte Carlo Integration

```python
from monte_carlo.simulation_engine import monte_carlo_engine

# Generate scenarios using property data
results = monte_carlo_engine.generate_scenarios(
    property_data=property_data,
    num_scenarios=500,
    horizon_years=5,
    use_correlations=True
)

print(f"Generated {len(results.scenarios)} scenarios")
print(f"Growth score range: {min(s.scenario_summary.get('growth_score', 0) for s in results.scenarios):.3f} - {max(s.scenario_summary.get('growth_score', 0) for s in results.scenarios):.3f}")
```

### Property Management

```python
from core.property_inputs import property_manager

# Add property to manager
property_manager.add_property(property_data)

# List all properties
property_ids = property_manager.list_properties()

# Retrieve specific property
retrieved = property_manager.get_property("PROP_001")

# Validate property
issues = property_manager.validate_property(property_data)
```

## Input Validation Features

### Currency Input
- Accepts: `$5,000,000`, `5000000`, `5,000,000.00`
- Validates: Positive numbers, reasonable ranges
- Warnings: Very high (>$100M) or low (<$100K) amounts

### Percentage Input  
- Accepts: `25%`, `0.25`, `25` (auto-detects format)
- Converts: Percentage notation to decimals
- Validates: Range 0-100%

### Address Validation
- Validates: Required fields, basic format checking
- Helps: MSA auto-detection from city/state

### Unit Mix Validation
- Ensures: Unit counts match total property units
- Validates: Square footage, rent amounts per unit type

## Supported MSAs

The system currently supports these major metropolitan areas:

- **35620** - New York-Newark-Jersey City, NY-NJ-PA
- **31080** - Los Angeles-Long Beach-Anaheim, CA  
- **16980** - Chicago-Naperville-Elgin, IL-IN-WI
- **47900** - Washington-Arlington-Alexandria, DC-VA-MD-WV
- **33100** - Miami-Fort Lauderdale-West Palm Beach, FL

## Integration Points

### With Monte Carlo Engine
The property input system seamlessly integrates with the Monte Carlo simulation engine:

1. **Property Data** → Validated through input system
2. **MSA Code** → Used to load appropriate market forecasts  
3. **Property Characteristics** → Used in scenario generation
4. **Results** → Returned with property-specific analysis

### With Property Manager
- **Lifecycle Management**: Create, store, retrieve, validate properties
- **Persistence**: Properties stored in memory (can be extended to database)
- **Validation**: Business rule validation beyond basic input validation

## Error Handling

The system provides comprehensive error handling:

```python
# ValidationResult object contains:
result.is_valid        # Boolean success status
result.errors          # List of error messages
result.warnings        # List of warning messages  
result.formatted_value # Cleaned/formatted value
```

Example error handling:
```python
result = validator.validate_currency(user_input, "purchase price")

for warning in result.warnings:
    print(f"Warning: {warning}")

if result.is_valid:
    use_value = result.formatted_value
else:
    for error in result.errors:
        print(f"Error: {error}")
    # Handle validation failure
```

## Testing

Run the test suite to verify functionality:

```bash
# Test validation system
python test_property_input.py

# Run simple demo
python demo_simple.py

# Test interactive collector (manual)
python user_input/property_collector.py
```

## Next Steps

1. **UI Integration**: Use web forms or build desktop/mobile interface
2. **Financial Engine**: Add NPV, IRR, Cash-on-Cash calculations
3. **Decision Framework**: Build recommendation engine
4. **Reporting**: Create analysis reports and visualizations
5. **Database**: Add persistent storage for properties
6. **API**: Build REST API for external integrations

## Production Readiness

✅ **Input Validation**: Comprehensive validation with helpful error messages  
✅ **Monte Carlo Integration**: Seamless property → analysis pipeline  
✅ **Error Handling**: Robust error handling and user feedback  
✅ **Testing**: Comprehensive test coverage  
✅ **Documentation**: Complete usage examples and API documentation  
✅ **Extensibility**: Modular design for easy extension  

The Property Input System is production-ready and can be immediately integrated into web, desktop, or mobile applications for real estate investment analysis.