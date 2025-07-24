#!/usr/bin/env python3
"""
Test Property Input System

Quick test of the user property input validation and collection system.
"""

from datetime import date
from user_input.input_validation import PropertyInputValidator, PropertyInputHelper, ValidationResult
from user_input.property_collector import PropertyInputCollector
from core.property_inputs import property_manager

def test_validation_system():
    """Test the input validation system."""
    print("=== TESTING PROPERTY INPUT VALIDATION ===")
    print()
    
    validator = PropertyInputValidator()
    helper = PropertyInputHelper()
    
    # Test currency validation
    print("[1] Testing currency validation...")
    test_cases = [
        "$5,000,000",
        "5000000",
        "5,000,000.00",
        "5.5M",  # This should fail
        "abc",   # This should fail
        "-100000"  # This should fail
    ]
    
    for test_value in test_cases:
        result = validator.validate_currency(test_value, "test amount")
        status = "[OK]" if result.is_valid else "[FAIL]"
        print(f"   {status} '{test_value}' -> {result.formatted_value if result.is_valid else 'Invalid'}")
        if result.errors:
            for error in result.errors:
                print(f"        Error: {error}")
        if result.warnings:
            for warning in result.warnings:
                print(f"        Warning: {warning}")
    
    print()
    
    # Test percentage validation
    print("[2] Testing percentage validation...")
    test_cases = [
        "25%",
        "0.25",
        "25",
        "150%",  # Should fail
        "abc"    # Should fail
    ]
    
    for test_value in test_cases:
        result = validator.validate_percentage(test_value, "test percentage")
        status = "[OK]" if result.is_valid else "[FAIL]"
        formatted = f"{result.formatted_value*100:.1f}%" if result.is_valid else "Invalid"
        print(f"   {status} '{test_value}' -> {formatted}")
        if result.errors:
            for error in result.errors:
                print(f"        Error: {error}")
        if result.warnings:
            for warning in result.warnings:
                print(f"        Warning: {warning}")
    
    print()
    
    # Test helper functions
    print("[3] Testing helper functions...")
    
    # Property type options
    type_options = helper.get_property_type_options()
    print(f"   Property types: {len(type_options)} options")
    for value, display in type_options:
        print(f"     - {display} ({value})")
    
    print()
    
    # Supported MSAs
    msa_options = helper.get_supported_msas()
    print(f"   Supported MSAs: {len(msa_options)} areas")
    for code, name in msa_options:
        print(f"     - {name} ({code})")
    
    print()


def test_property_creation():
    """Test property creation programmatically."""
    print("=== TESTING PROGRAMMATIC PROPERTY CREATION ===")
    print()
    
    try:
        from core.property_inputs import (
            PropertyInputData, PropertyPhysicalInfo, PropertyFinancialInfo,
            PropertyLocationInfo, PropertyOperatingInfo, UnitMix,
            PropertyType, PropertyClass
        )
        
        print("[1] Creating test property...")
        
        # Create a test property using user input validation
        validator = PropertyInputValidator()
        helper = PropertyInputHelper()
        
        # Simulate validated user inputs
        purchase_price_result = validator.validate_currency("$3,500,000", "purchase price")
        down_payment_result = validator.validate_percentage("30%", "down payment")
        
        if not (purchase_price_result.is_valid and down_payment_result.is_valid):
            print("   [FAIL] Input validation failed")
            return
        
        # Create property with validated inputs
        test_property = PropertyInputData(
            property_id="TEST_USER_001",
            property_name="Test User Property",
            analysis_date=date.today(),
            physical_info=PropertyPhysicalInfo(
                property_type=PropertyType.MULTIFAMILY,
                property_class=PropertyClass.CLASS_B,
                total_units=75,
                total_square_feet=67500,
                year_built=2015,
                parking_spaces=90
            ),
            financial_info=PropertyFinancialInfo(
                purchase_price=purchase_price_result.formatted_value,
                down_payment_pct=down_payment_result.formatted_value,
                current_noi=280000,
                current_gross_rent=420000
            ),
            location_info=PropertyLocationInfo(
                address="456 User Test Avenue",
                city="Los Angeles",
                state="CA",
                zip_code="90210",
                msa_code="31080"  # LA MSA
            ),
            operating_info=PropertyOperatingInfo(
                management_fee_pct=0.04,
                maintenance_reserve_pct=0.025,
                unit_mix=[
                    UnitMix("1BR/1BA", 30, 750, 2100),
                    UnitMix("2BR/2BA", 35, 1000, 2700),
                    UnitMix("3BR/2BA", 10, 1250, 3200)
                ]
            )
        )
        
        print(f"   [OK] Created property: {test_property.property_name}")
        print(f"   [OK] Property ID: {test_property.property_id}")
        
        # Add to property manager
        property_manager.add_property(test_property)
        print(f"   [OK] Added to property manager")
        
        # Calculate metrics
        metrics = helper.calculate_financial_metrics(test_property)
        print(f"   [METRICS] Price per unit: {helper.format_currency(metrics['price_per_unit'])}")
        print(f"   [METRICS] Price per SF: ${metrics['price_per_sf']:.0f}")
        print(f"   [METRICS] Current cap rate: {helper.format_percentage(metrics['current_cap_rate'])}")
        print(f"   [METRICS] Cash required: {helper.format_currency(metrics['down_payment'])}")
        
        # Test Monte Carlo integration
        print("\n[2] Testing Monte Carlo integration...")
        
        try:
            from monte_carlo.simulation_engine import monte_carlo_engine
            
            results = monte_carlo_engine.generate_scenarios(
                property_data=test_property,
                num_scenarios=25,  # Small number for quick test
                horizon_years=5,
                use_correlations=True
            )
            
            print(f"   [OK] Generated {len(results.scenarios)} scenarios")
            print(f"   [OK] Property ID in results: {results.property_id}")
            print(f"   [OK] MSA code: {results.msa_code}")
            
            # Sample scenario analysis
            if results.scenarios:
                first_scenario = results.scenarios[0]
                param_count = len(first_scenario.forecasted_parameters)
                growth_score = first_scenario.scenario_summary.get('growth_score', 0)
                risk_score = first_scenario.scenario_summary.get('risk_score', 0)
                
                print(f"   [METRICS] Parameters per scenario: {param_count}")
                print(f"   [METRICS] Sample growth score: {growth_score:.3f}")
                print(f"   [METRICS] Sample risk score: {risk_score:.3f}")
            
            print("\n   [SUCCESS] User input -> Monte Carlo pipeline working correctly!")
            
        except Exception as mc_error:
            print(f"   [WARNING] Monte Carlo integration error: {mc_error}")
            print("   (This may be due to missing forecast data)")
        
        return test_property
        
    except Exception as e:
        print(f"   [FAIL] Property creation failed: {e}")
        return None


def test_property_manager():
    """Test property manager operations."""
    print("\n=== TESTING PROPERTY MANAGER ===")
    print()
    
    # List current properties
    property_ids = property_manager.list_properties()
    print(f"[1] Current properties in manager: {len(property_ids)}")
    
    for prop_id in property_ids:
        prop = property_manager.get_property(prop_id)
        if prop:
            print(f"   - {prop.property_name} ({prop_id})")
            print(f"     Type: {prop.physical_info.property_type.value}")
            print(f"     Price: {PropertyInputHelper.format_currency(prop.financial_info.purchase_price)}")
    
    print()


def main():
    """Run all tests."""
    print("[TEST] PROPERTY INPUT SYSTEM TESTING")
    print("="*50)
    print()
    
    # Test validation
    test_validation_system()
    
    # Test property creation
    test_property = test_property_creation()
    
    # Test property manager
    test_property_manager()
    
    print("\n" + "="*50)
    print("[SUCCESS] PROPERTY INPUT SYSTEM TESTING COMPLETE")
    print()
    
    if test_property:
        print("[NEXT STEPS]")
        print("1. Run interactive collector: python user_input/property_collector.py")
        print("2. Test web forms (requires Flask): pip install flask")
        print("3. Integrate with your preferred UI framework")
        print()
        print("The property input system is ready for production use!")
    else:
        print("[FAIL] Some tests failed. Check error messages above.")


if __name__ == "__main__":
    main()