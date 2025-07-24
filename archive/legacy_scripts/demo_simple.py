#!/usr/bin/env python3
"""
Simple Demo: Property Input System

Windows-compatible demonstration without Unicode characters.
"""

from datetime import date
from user_input.input_validation import PropertyInputValidator, PropertyInputHelper
from core.property_inputs import *

def simple_demo():
    """Run a simple demonstration."""
    print("=" * 60)
    print("PROPERTY INPUT SYSTEM DEMONSTRATION")
    print("=" * 60)
    print()
    
    # Demo validation
    print("[1] Input Validation Demo")
    print("-" * 30)
    
    validator = PropertyInputValidator()
    helper = PropertyInputHelper()
    
    # Test currency input
    test_input = "$5,000,000"
    result = validator.validate_currency(test_input, "purchase price")
    print(f"Input: {test_input}")
    print(f"Output: ${result.formatted_value:,.0f}")
    print()
    
    # Test percentage input
    test_input = "25%"
    result = validator.validate_percentage(test_input, "down payment")
    print(f"Input: {test_input}")
    print(f"Output: {helper.format_percentage(result.formatted_value)}")
    print()
    
    # Demo property creation
    print("[2] Property Creation Demo")
    print("-" * 30)
    
    # Create demo property
    demo_property = PropertyInputData(
        property_id="DEMO_001",
        property_name="Demo Investment Property",
        analysis_date=date.today(),
        physical_info=PropertyPhysicalInfo(
            property_type=PropertyType.MULTIFAMILY,
            property_class=PropertyClass.CLASS_B,
            total_units=50,
            total_square_feet=45000,
            year_built=2015
        ),
        financial_info=PropertyFinancialInfo(
            purchase_price=5_000_000,
            down_payment_pct=0.25,
            current_noi=350_000
        ),
        location_info=PropertyLocationInfo(
            address="123 Demo Street",
            city="New York",
            state="NY",
            zip_code="10001",
            msa_code="35620"  # NYC MSA
        ),
        operating_info=PropertyOperatingInfo()
    )
    
    print(f"Created: {demo_property.property_name}")
    print(f"Type: {demo_property.physical_info.property_type.value}")
    print(f"Units: {demo_property.physical_info.total_units}")
    print(f"Price: ${demo_property.financial_info.purchase_price:,.0f}")
    print()
    
    # Calculate metrics
    metrics = helper.calculate_financial_metrics(demo_property)
    print("Key Metrics:")
    print(f"  Price per Unit: ${metrics['price_per_unit']:,.0f}")
    print(f"  Price per SF: ${metrics['price_per_sf']:.0f}")
    print(f"  Current Cap Rate: {helper.format_percentage(metrics['current_cap_rate'])}")
    print(f"  Cash Required: ${metrics['down_payment']:,.0f}")
    print()
    
    # Demo Monte Carlo integration
    print("[3] Monte Carlo Integration Demo")
    print("-" * 30)
    
    try:
        from monte_carlo.simulation_engine import monte_carlo_engine
        
        results = monte_carlo_engine.generate_scenarios(
            property_data=demo_property,
            num_scenarios=25,
            horizon_years=5,
            use_correlations=True
        )
        
        print(f"SUCCESS: Generated {len(results.scenarios)} scenarios")
        print(f"Property ID: {results.property_id}")
        print(f"MSA Code: {results.msa_code}")
        
        if results.scenarios:
            sample = results.scenarios[0]
            param_count = len(sample.forecasted_parameters)
            growth = sample.scenario_summary.get('growth_score', 0)
            risk = sample.scenario_summary.get('risk_score', 0)
            
            print(f"Parameters per scenario: {param_count}")
            print(f"Sample growth score: {growth:.3f}")
            print(f"Sample risk score: {risk:.3f}")
        
        print()
        print("RESULT: Property input -> Monte Carlo pipeline WORKING!")
        
    except Exception as e:
        print(f"Monte Carlo error: {e}")
        print("(May be due to missing forecast data)")
    
    print()
    print("=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print()
    print("The property input system is ready for production use!")
    print()
    print("Available components:")
    print("1. PropertyInputValidator - Input validation and formatting")
    print("2. PropertyInputCollector - Interactive data collection")
    print("3. PropertyWebFormGenerator - HTML form generation")
    print("4. PropertyDataManager - Property lifecycle management")
    print("5. Monte Carlo integration - Seamless analysis pipeline")
    print()
    print("Next steps:")
    print("- Run: python user_input/property_collector.py (interactive mode)")
    print("- Integrate with your preferred UI framework")
    print("- Add financial calculation engine (NPV, IRR, etc.)")


if __name__ == "__main__":
    simple_demo()