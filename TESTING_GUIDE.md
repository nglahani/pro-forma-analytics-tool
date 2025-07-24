# 🧪 COMPREHENSIVE TESTING GUIDE

## Overview

This guide provides complete instructions for testing the pro-forma analytics tool, including the new simplified property input system that captures your 7 required data fields.

---

## 🚀 QUICK START - Test Everything

### **Option 1: Complete System Test (Recommended)**

```bash
cd "C:\Users\nlaha\OneDrive\Documents\Personal\Real Estate\pro-forma-analytics-tool"

# Test the simplified property input system
python test_simplified_system.py
```

**Expected Output:**
```
=== TESTING SIMPLIFIED PROPERTY INPUT SYSTEM ===
[SUCCESS] All 7 data points captured!
[SUCCESS] Property saved to database
[SUCCESS] Generated 10 scenarios
SYSTEM STATUS: FULLY OPERATIONAL
```

### **Option 2: Interactive Test**

```bash
# Test the user input form
python simplified_input_form.py
```

Follow the prompts to enter your property data and see the complete workflow.

---

## 🎯 SPECIFIC TESTING SCENARIOS

### **Test 1: Your 7 Required Data Fields**

**File**: `test_simplified_system.py`
**Purpose**: Validates all 7 required data points are captured and stored

```bash
python test_simplified_system.py
```

**What it tests:**
- ✅ Number of residential units
- ✅ Anticipated renovation time  
- ✅ Number of commercial units
- ✅ Investor equity share
- ✅ Residential rent per unit
- ✅ Commercial rent per unit
- ✅ Self cash percentage

**Expected Results:**
```
[2] Verifying Your 7 Required Data Points...
   1. Residential units: 8
   2. Renovation time: 4 months
   3. Commercial units: 2
   4. Investor equity share: 80.0%
   5. Residential rent/unit: $2,800/month
   6. Commercial rent/unit: $4,200/month
   7. Self cash percentage: 25.0%
   [SUCCESS] All 7 data points captured!
```

### **Test 2: Database Backend Storage**

**File**: `test_simplified_system.py` (same file, different section)
**Purpose**: Tests backend database with building listings and pro forma analysis

```bash
python test_simplified_system.py
```

**What it tests:**
- ✅ Property storage in SQLite database
- ✅ Property retrieval and listing
- ✅ Pro forma analysis storage
- ✅ User listing tracking
- ✅ Database statistics and relationships

**Expected Results:**
```
[3] Testing Database Storage...
   [SUCCESS] Property saved to database
   [SUCCESS] Property loaded from database

[7] Testing Database Statistics...
   Total Properties: 1
   Total Analyses: 1
   Total Listings: 1
   Property Types: {'mixed_use': 1}
```

### **Test 3: Monte Carlo Integration**

**File**: `test_simplified_system.py` (same file, section 5)
**Purpose**: Tests integration with existing Monte Carlo analysis engine

**What it tests:**
- ✅ Conversion of simplified input to Monte Carlo format
- ✅ Scenario generation with property data
- ✅ Analysis results storage
- ✅ Investment recommendations

**Expected Results:**
```
[5] Testing Pro Forma Analysis Integration...
   [SUCCESS] Generated 10 scenarios
   [SUCCESS] Analysis results saved to database
```

### **Test 4: Mixed-Use Property Support**

**Purpose**: Tests properties with both residential and commercial units

```python
# Create a mixed-use property
from enhanced_property_inputs import *

mixed_property = SimplifiedPropertyInput(
    property_name="Mixed-Use Test",
    residential_units=ResidentialUnits(total_units=6, average_rent_per_unit=2500),
    commercial_units=CommercialUnits(total_units=2, average_rent_per_unit=4000),
    # ... other fields
)

print(f"Mixed-use: {mixed_property.is_mixed_use()}")  # Should be True
print(f"Property type: {mixed_property.get_property_type_classification()}")  # Should be 'mixed_use'
```

---

## 🔧 INDIVIDUAL COMPONENT TESTS

### **Test Core System Components**

```bash
# Test original Monte Carlo engine
python simple_monte_carlo_validation.py

# Test data infrastructure
python data_manager.py status
python data_manager.py verify

# Test property input validation
python demo_property_system.py
```

### **Test Database Operations**

```python
from database.property_database import property_db

# Test database statistics
stats = property_db.get_database_stats()
print(f"Properties: {stats['total_properties']}")

# Test property listing
properties = property_db.list_properties()
print(f"Listed {len(properties)} properties")

# Test user listings
user_listings = property_db.get_user_listings("test_user")
print(f"User has {len(user_listings)} listings")
```

### **Test Input Validation**

```python
from enhanced_property_inputs import SimplifiedPropertyInput, ResidentialUnits

try:
    # Test invalid input (should fail)
    invalid_property = SimplifiedPropertyInput(
        property_name="",  # Empty name should fail
        residential_units=ResidentialUnits(total_units=0, average_rent_per_unit=0)
    )
except Exception as e:
    print(f"Validation working: {e}")
```

---

## 🧪 UNIT TESTS

### **Run Existing Test Suite**

```bash
# Run all unit tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov=core --cov=enhanced_property_inputs
```

### **Test Specific Components**

```bash
# Test forecast entities
python -m pytest tests/unit/domain/test_forecast_entities.py -v

# Test application services
python -m pytest tests/unit/application/test_forecasting_service.py -v

# Test user workflow integration
python -m pytest tests/integration/test_user_workflow.py -v
```

---

## 📊 PERFORMANCE TESTS

### **Test Monte Carlo Performance**

```python
import time
from test_simplified_system import test_simplified_system

start_time = time.time()
test_simplified_system()
end_time = time.time()

print(f"Complete system test took: {end_time - start_time:.2f} seconds")
```

### **Test Database Performance**

```python
from database.property_database import property_db
import time

# Test bulk property creation
start_time = time.time()
for i in range(100):
    # Create and save properties
    pass
end_time = time.time()

print(f"100 property operations took: {end_time - start_time:.2f} seconds")
```

---

## 🔍 TROUBLESHOOTING TESTS

### **Common Issues and Solutions**

#### **Issue 1: Import Errors**
```bash
# If you get import errors, run from project root:
cd "C:\Users\nlaha\OneDrive\Documents\Personal\Real Estate\pro-forma-analytics-tool"
python test_simplified_system.py
```

#### **Issue 2: Database Errors**
```bash
# Check if database directory exists
ls data/databases/

# Reset database if needed
rm data/databases/property_listings.db
python test_simplified_system.py  # Will recreate database
```

#### **Issue 3: Monte Carlo Fails**
```bash
# Test with NYC MSA (has full data)
# In your test, use msa_code="35620"
```

#### **Issue 4: Unicode Display Issues**
```bash
# Use the simplified test instead
python demo_property_system.py
```

---

## 📋 TEST CHECKLIST

### **✅ Pre-Testing Setup**

- [ ] Navigate to project root directory
- [ ] Ensure Python 3.8+ is installed
- [ ] All required packages installed (`pip install -r requirements.txt`)
- [ ] No conflicting processes using database files

### **✅ Core Functionality Tests**

- [ ] **Simplified Input System**: `python test_simplified_system.py`
- [ ] **Interactive Form**: `python simplified_input_form.py`
- [ ] **Database Operations**: All CRUD operations working
- [ ] **Monte Carlo Integration**: Scenarios generated successfully
- [ ] **Data Validation**: Invalid inputs properly rejected

### **✅ Integration Tests**

- [ ] **Property → Database → Analysis**: Complete workflow
- [ ] **Mixed-Use Properties**: Residential + commercial support
- [ ] **User Listings**: Multi-user property tracking
- [ ] **Analysis Storage**: Results properly saved and retrieved

### **✅ Performance Tests**

- [ ] **Response Time**: System responds within reasonable time
- [ ] **Data Volume**: Handles multiple properties efficiently
- [ ] **Memory Usage**: No memory leaks during extended use

---

## 🎯 SUCCESS CRITERIA

### **All Tests Should Show:**

1. **✅ Data Collection**: All 7 required fields captured
2. **✅ Database Storage**: Properties saved and retrieved successfully
3. **✅ Analysis Integration**: Monte Carlo scenarios generated
4. **✅ User Experience**: Forms work smoothly with validation
5. **✅ Mixed-Use Support**: Both residential and commercial units handled
6. **✅ Performance**: Reasonable response times (< 10 seconds for analysis)

### **Final Validation Command**

```bash
# This should complete without errors and show all green checkmarks
python test_simplified_system.py
```

**Expected Final Output:**
```
TEST RESULTS SUMMARY
====================
[REQUIREMENTS COVERAGE]
✓ All 7 data points - CAPTURED
[BACKEND DATABASE]  
✓ All operations - WORKING
[INTEGRATION]
✓ Complete pipeline - WORKING

SYSTEM STATUS: FULLY OPERATIONAL
```

---

## 🚀 READY FOR PRODUCTION

If all tests pass, your property input system is ready for production use with:

- ✅ Your exact 7 required data fields
- ✅ Backend database storage
- ✅ Pro forma analysis integration
- ✅ Mixed-use property support
- ✅ Complete validation and error handling

**Start using immediately:** `python simplified_input_form.py`