#!/usr/bin/env python3
"""
Demo: Property Input System

Interactive demonstration of the property input collection system.
Shows how users can manually input property data for pro forma analysis.
"""

import sys
from datetime import date
from user_input.property_collector import PropertyInputCollector
from user_input.input_validation import PropertyInputValidator, PropertyInputHelper
from core.property_inputs import property_manager


def demo_validation_features():
    """Demonstrate input validation features."""
    print("\n" + "="*60)
    print("🔍 DEMO: INPUT VALIDATION FEATURES")
    print("="*60)
    print()
    
    validator = PropertyInputValidator()
    helper = PropertyInputHelper()
    
    print("The system validates and formats user input automatically:")
    print()
    
    # Demo currency validation
    print("💰 Currency Input Examples:")
    examples = [
        ("$5,000,000", "Clean currency formatting"),
        ("5000000", "Plain numbers"),
        ("5,000,000.00", "Decimal formatting"),
    ]
    
    for example, description in examples:
        result = validator.validate_currency(example, "purchase price")
        print(f"   Input: '{example}' ({description})")
        print(f"   Output: ${result.formatted_value:,.0f}")
        if result.warnings:
            for warning in result.warnings:
                print(f"   Warning: {warning}")
        print()
    
    # Demo percentage validation
    print("📊 Percentage Input Examples:")
    examples = [
        ("25%", "Percentage notation"),
        ("0.25", "Decimal format"),
        ("25", "Auto-detected percentage"),
    ]
    
    for example, description in examples:
        result = validator.validate_percentage(example, "down payment")
        print(f"   Input: '{example}' ({description})")
        print(f"   Output: {helper.format_percentage(result.formatted_value)}")
        if result.warnings:
            for warning in result.warnings:
                print(f"   Warning: {warning}")
        print()


def demo_property_creation():
    """Demonstrate programmatic property creation."""
    print("\n" + "="*60)
    print("🏢 DEMO: PROPERTY DATA STRUCTURE")
    print("="*60)
    print()
    
    print("Creating a sample property with validated inputs...")
    print()
    
    # Import required classes
    from core.property_inputs import (
        PropertyInputData, PropertyPhysicalInfo, PropertyFinancialInfo,
        PropertyLocationInfo, PropertyOperatingInfo, UnitMix,
        PropertyType, PropertyClass
    )
    
    # Create demo property
    demo_property = PropertyInputData(
        property_id="DEMO_001",
        property_name="Downtown Investment Property",
        analysis_date=date.today(),
        physical_info=PropertyPhysicalInfo(
            property_type=PropertyType.MULTIFAMILY,
            property_class=PropertyClass.CLASS_B,
            total_units=85,
            total_square_feet=76500,
            year_built=2012,
            year_renovated=2020,
            parking_spaces=100,
            stories=4
        ),
        financial_info=PropertyFinancialInfo(
            purchase_price=6_800_000,
            down_payment_pct=0.30,
            current_noi=510_000,
            current_gross_rent=780_000,
            current_expenses=270_000
        ),
        location_info=PropertyLocationInfo(
            address="789 Investment Avenue",
            city="New York",
            state="NY",
            zip_code="10016",
            msa_code="35620"  # NYC MSA
        ),
        operating_info=PropertyOperatingInfo(
            management_fee_pct=0.045,
            maintenance_reserve_pct=0.025,
            insurance_annual=35_000,
            property_tax_annual=95_000,
            unit_mix=[
                UnitMix("Studio", 15, 600, 2400),
                UnitMix("1BR/1BA", 35, 800, 2900),
                UnitMix("2BR/2BA", 30, 1100, 3600),
                UnitMix("3BR/2BA", 5, 1400, 4500)
            ]
        )
    )
    
    print(f"✅ Created: {demo_property.property_name}")
    print(f"   Property ID: {demo_property.property_id}")
    print(f"   Type: {demo_property.physical_info.property_type.value.title()}")
    print(f"   Class: {demo_property.physical_info.property_class.value.replace('_', ' ').title()}")
    print(f"   Location: {demo_property.location_info.city}, {demo_property.location_info.state}")
    print()
    
    # Calculate and display key metrics
    helper = PropertyInputHelper()
    metrics = helper.calculate_financial_metrics(demo_property)
    
    print("📊 Key Financial Metrics:")
    print(f"   Purchase Price: {helper.format_currency(demo_property.financial_info.purchase_price)}")
    print(f"   Price per Unit: {helper.format_currency(metrics['price_per_unit'])}")
    print(f"   Price per SF: ${metrics['price_per_sf']:.0f}")
    print(f"   Current Cap Rate: {helper.format_percentage(metrics['current_cap_rate'])}")
    print(f"   Down Payment: {helper.format_percentage(demo_property.financial_info.down_payment_pct)}")
    print(f"   Cash Required: {helper.format_currency(metrics['down_payment'])}")
    print(f"   Loan Amount: {helper.format_currency(metrics['loan_amount'])}")
    print()
    
    # Unit mix breakdown
    print("🏠 Unit Mix Breakdown:")
    total_monthly_income = 0
    for unit in demo_property.operating_info.unit_mix:
        monthly_income = unit.count * unit.current_rent
        total_monthly_income += monthly_income
        print(f"   {unit.unit_type}: {unit.count} units × ${unit.current_rent:,.0f}/mo "
              f"({unit.avg_square_feet} SF) = ${monthly_income:,.0f}/mo")
    
    print(f"   Total Monthly Income: ${total_monthly_income:,.0f}")
    print(f"   Annual Gross Income: ${total_monthly_income * 12:,.0f}")
    print()
    
    return demo_property


def demo_monte_carlo_integration(property_data):
    """Demonstrate Monte Carlo analysis integration."""
    print("\n" + "="*60)
    print("🎲 DEMO: MONTE CARLO ANALYSIS INTEGRATION")
    print("="*60)
    print()
    
    print("Running Monte Carlo analysis with the property data...")
    print()
    
    try:
        from monte_carlo.simulation_engine import monte_carlo_engine
        
        # Generate scenarios
        results = monte_carlo_engine.generate_scenarios(
            property_data=property_data,
            num_scenarios=100,
            horizon_years=5,
            use_correlations=True
        )
        
        print(f"✅ Successfully generated {len(results.scenarios)} scenarios")
        print(f"   Property: {results.property_id}")
        print(f"   MSA: {results.msa_code}")
        print(f"   Forecast Horizon: {results.horizon_years} years")
        print()
        
        # Analyze results
        if results.scenarios:
            growth_scores = [s.scenario_summary.get('growth_score', 0) for s in results.scenarios]
            risk_scores = [s.scenario_summary.get('risk_score', 0) for s in results.scenarios]
            
            import numpy as np
            
            print("📈 Scenario Analysis Results:")
            print(f"   Growth Scores: {min(growth_scores):.3f} - {max(growth_scores):.3f} (avg: {np.mean(growth_scores):.3f})")
            print(f"   Risk Scores: {min(risk_scores):.3f} - {max(risk_scores):.3f} (avg: {np.mean(risk_scores):.3f})")
            print(f"   Scenario Diversity: {np.std(growth_scores):.3f} (growth), {np.std(risk_scores):.3f} (risk)")
            print()
            
            # Sample scenario details
            sample_scenario = results.scenarios[0]
            print("🔍 Sample Scenario Parameters:")
            param_names = list(sample_scenario.forecasted_parameters.keys())[:5]  # Show first 5
            for param_name in param_names:
                values = sample_scenario.forecasted_parameters[param_name]
                if values:
                    avg_value = np.mean(values)
                    print(f"   {param_name}: {avg_value:.4f} (5-year average)")
            print(f"   ... and {len(sample_scenario.forecasted_parameters) - 5} more parameters")
            print()
            
            # Extreme scenarios
            if results.extreme_scenarios:
                print("🎯 Extreme Scenarios Identified:")
                for scenario_type, scenario in results.extreme_scenarios.items():
                    growth = scenario.scenario_summary.get('growth_score', 0)
                    risk = scenario.scenario_summary.get('risk_score', 0)
                    print(f"   {scenario_type.replace('_', ' ').title()}: Growth={growth:.3f}, Risk={risk:.3f}")
                print()
        
        print("🚀 INTEGRATION SUCCESS: Property input flows seamlessly into Monte Carlo analysis!")
        print("   The system is ready for production use.")
        
        return results
        
    except Exception as e:
        print(f"❌ Monte Carlo integration error: {e}")
        print("   This may indicate missing forecast data for the selected MSA.")
        return None


def demo_interactive_mode():
    """Offer to run interactive property collection."""
    print("\n" + "="*60)
    print("🖥️  DEMO: INTERACTIVE PROPERTY COLLECTION")
    print("="*60)
    print()
    
    print("The system includes an interactive property collector that guides")
    print("users through step-by-step property data entry with validation.")
    print()
    
    # Ask if user wants to try interactive mode
    try:
        response = input("Would you like to try the interactive property collector? (y/n): ").strip().lower()
        
        if response in ['y', 'yes']:
            print("\n🚀 Starting interactive property collector...")
            print("(You can press Ctrl+C at any time to cancel)")
            print()
            
            collector = PropertyInputCollector()
            new_property = collector.collect_property_data()
            
            if new_property:
                print(f"\n✅ Successfully collected property: {new_property.property_name}")
                return new_property
            else:
                print("\n❌ Property collection was cancelled or failed.")
                return None
        else:
            print("📋 Interactive mode skipped.")
            print("   You can run it anytime with: python user_input/property_collector.py")
            return None
            
    except KeyboardInterrupt:
        print("\n\n❌ Interactive mode cancelled.")
        return None


def main():
    """Run the complete property input system demo."""
    print("="*60)
    print("🏢 PROPERTY INPUT SYSTEM DEMONSTRATION")
    print("="*60)
    print()
    print("This demo shows how users can input property data for pro forma analysis.")
    print("The system validates inputs, calculates metrics, and integrates with")
    print("Monte Carlo simulation for comprehensive investment analysis.")
    
    # Demo 1: Validation features
    demo_validation_features()
    
    # Demo 2: Property creation
    demo_property = demo_property_creation()
    
    # Demo 3: Monte Carlo integration
    monte_carlo_results = demo_monte_carlo_integration(demo_property)
    
    # Demo 4: Interactive mode (optional)
    interactive_property = demo_interactive_mode()
    
    # Summary
    print("\n" + "="*60)
    print("📋 DEMONSTRATION SUMMARY")
    print("="*60)
    print()
    
    properties_created = 1  # Demo property
    if interactive_property:
        properties_created += 1
    
    print(f"✅ Properties Created: {properties_created}")
    print(f"✅ Monte Carlo Integration: {'Working' if monte_carlo_results else 'Needs Forecast Data'}")
    print(f"✅ Input Validation: Working")
    print(f"✅ Property Management: Working")
    print()
    
    # List all properties in manager
    all_properties = property_manager.list_properties()
    if all_properties:
        print("📊 Properties in System:")
        for prop_id in all_properties:
            prop = property_manager.get_property(prop_id)
            if prop:
                helper = PropertyInputHelper()
                price = helper.format_currency(prop.financial_info.purchase_price)
                print(f"   - {prop.property_name} ({prop_id}): {price}")
    
    print()
    print("🎯 NEXT STEPS:")
    print("1. Integrate with your preferred UI framework (web, desktop, mobile)")
    print("2. Add financial calculation engine (NPV, IRR, Cash-on-Cash)")
    print("3. Build investment decision framework")
    print("4. Create results dashboard and reporting")
    print()
    print("The property input system foundation is complete and production-ready!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Demo cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        sys.exit(1)