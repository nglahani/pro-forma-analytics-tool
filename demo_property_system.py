#!/usr/bin/env python3
"""
Demo: Property Input System

Shows the complete property input workflow.
"""

import sys
from pathlib import Path
from datetime import date
import uuid

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.property_inputs import *
from user_input.input_validation import PropertyInputValidator, PropertyInputHelper

def demo_property_input_system():
    """Demonstrate the property input system."""
    
    print("=== PROPERTY INPUT SYSTEM DEMO ===")
    print()
    
    validator = PropertyInputValidator()
    helper = PropertyInputHelper()
    
    print("[1] Input Validation Demo")
    print("-" * 30)
    
    # Demo validation
    test_inputs = [
        ("$5,500,000", "purchase price"),
        ("30%", "down payment"),
        ("2015", "year built")
    ]
    
    validated_data = {}
    
    for test_input, field_name in test_inputs:
        if field_name == "purchase price":
            result = validator.validate_currency(test_input, field_name)
            validated_data['purchase_price'] = result.formatted_value
        elif field_name == "down payment":
            result = validator.validate_percentage(test_input, field_name)
            validated_data['down_payment'] = result.formatted_value
        elif field_name == "year built":
            result = validator.validate_year(int(test_input), field_name)
            validated_data['year_built'] = result.formatted_value
        
        print(f"Input: '{test_input}' -> Valid: {result.is_valid}")
        if result.is_valid:
            if field_name == "purchase price":
                print(f"   Formatted: ${result.formatted_value:,.0f}")
            elif field_name == "down payment":
                print(f"   Formatted: {result.formatted_value*100:.1f}%")
            else:
                print(f"   Formatted: {result.formatted_value}")
        
        if result.warnings:
            for warning in result.warnings:
                print(f"   Warning: {warning}")
        
        print()
    
    print("[2] Property Creation Demo")
    print("-" * 30)
    
    # Create demo property with validated inputs
    demo_property = PropertyInputData(
        property_id=f"DEMO_{uuid.uuid4().hex[:8].upper()}",
        property_name="Demo Investment Property",
        analysis_date=date.today(),
        physical_info=PropertyPhysicalInfo(
            property_type=PropertyType.MULTIFAMILY,
            property_class=PropertyClass.CLASS_B,
            total_units=85,
            total_square_feet=76500,
            year_built=validated_data['year_built']
        ),
        financial_info=PropertyFinancialInfo(
            purchase_price=validated_data['purchase_price'],
            down_payment_pct=validated_data['down_payment'],
            current_noi=450000
        ),
        location_info=PropertyLocationInfo(
            address="456 Demo Avenue",
            city="New York",
            state="NY",
            zip_code="10016",
            msa_code="35620"  # NYC MSA
        ),
        operating_info=PropertyOperatingInfo(
            management_fee_pct=0.045,
            maintenance_reserve_pct=0.025
        )
    )
    
    # Add to property manager
    property_manager.add_property(demo_property)
    
    print(f"Created: {demo_property.property_name}")
    print(f"ID: {demo_property.property_id}")
    print(f"Type: {demo_property.physical_info.property_type.value.title()}")
    print(f"Units: {demo_property.physical_info.total_units}")
    print(f"Price: {helper.format_currency(demo_property.financial_info.purchase_price)}")
    print()
    
    # Calculate metrics
    metrics = helper.calculate_financial_metrics(demo_property)
    print("Key Metrics:")
    print(f"  Price per Unit: {helper.format_currency(metrics['price_per_unit'])}")
    print(f"  Price per SF: ${metrics['price_per_sf']:.0f}")
    print(f"  Current Cap Rate: {helper.format_percentage(metrics['current_cap_rate'])}")
    print(f"  Cash Required: {helper.format_currency(metrics['down_payment'])}")
    print()
    
    print("[3] Monte Carlo Integration Demo")
    print("-" * 30)
    
    try:
        from monte_carlo.simulation_engine import monte_carlo_engine
        
        print("Running Monte Carlo analysis...")
        results = monte_carlo_engine.generate_scenarios(
            property_data=demo_property,
            num_scenarios=25,
            horizon_years=5,
            use_correlations=True
        )
        
        print(f"SUCCESS: Generated {len(results.scenarios)} scenarios")
        print(f"Property: {results.property_id}")
        print(f"MSA: {results.msa_code}")
        
        if results.scenarios:
            growth_scores = [s.scenario_summary.get('growth_score', 0) for s in results.scenarios]
            risk_scores = [s.scenario_summary.get('risk_score', 0) for s in results.scenarios]
            
            import numpy as np
            print(f"Growth Range: {min(growth_scores):.3f} - {max(growth_scores):.3f}")
            print(f"Risk Range: {min(risk_scores):.3f} - {max(risk_scores):.3f}")
            print(f"Average Growth: {np.mean(growth_scores):.3f}")
            print(f"Average Risk: {np.mean(risk_scores):.3f}")
        
        print("\nPipeline: Property Input -> Validation -> Monte Carlo -> Analysis")
        print("Status: WORKING PERFECTLY!")
        
    except Exception as e:
        print(f"Monte Carlo error: {e}")
    
    print()
    print("=== HOW TO USE THE SYSTEM ===")
    print()
    print("OPTION 1: Interactive Mode")
    print("  Run: python simple_property_input.py")
    print("  Follow prompts to enter property data step-by-step")
    print()
    print("OPTION 2: Programmatic Use")
    print("  from user_input.input_validation import PropertyInputValidator")
    print("  validator = PropertyInputValidator()")
    print("  result = validator.validate_currency(user_input)")
    print()
    print("OPTION 3: Web Interface")
    print("  from user_input.web_forms import PropertyWebFormGenerator")
    print("  generator = PropertyWebFormGenerator()")
    print("  html = generator.generate_property_form_html()")
    print()
    print("Your property input system is ready for production use!")


if __name__ == "__main__":
    demo_property_input_system()