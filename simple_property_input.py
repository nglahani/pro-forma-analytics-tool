#!/usr/bin/env python3
"""
Simple Property Input System

Windows-compatible interactive property data collection.
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

def collect_property_interactively():
    """Collect property data with interactive prompts."""
    
    print("=" * 60)
    print("PROPERTY DATA COLLECTION")
    print("=" * 60)
    print("Please provide information about your investment property.")
    print("You can enter amounts with $ and commas (e.g., $5,000,000)")
    print("Percentages can be entered as 25% or 0.25")
    print()
    
    validator = PropertyInputValidator()
    helper = PropertyInputHelper()
    
    try:
        # Generate property ID
        property_id = f"PROP_{uuid.uuid4().hex[:8].upper()}"
        
        # Basic Information
        print("[1] BASIC INFORMATION")
        print("-" * 30)
        
        property_name = input("Property name: ").strip()
        if not property_name:
            property_name = "Investment Property"
        
        print()
        
        # Physical Information
        print("[2] PHYSICAL CHARACTERISTICS")
        print("-" * 30)
        
        print("Property type options:")
        print("1. Multifamily")
        print("2. Office") 
        print("3. Retail")
        print("4. Industrial")
        print("5. Mixed Use")
        
        while True:
            try:
                type_choice = int(input("Select property type (1-5): "))
                if 1 <= type_choice <= 5:
                    property_types = [PropertyType.MULTIFAMILY, PropertyType.OFFICE, 
                                    PropertyType.RETAIL, PropertyType.INDUSTRIAL, PropertyType.MIXED_USE]
                    property_type = property_types[type_choice - 1]
                    break
                else:
                    print("Please enter a number between 1 and 5.")
            except ValueError:
                print("Please enter a valid number.")
        
        print("\nProperty class options:")
        print("1. Class A")
        print("2. Class B")
        print("3. Class C")
        
        while True:
            try:
                class_choice = int(input("Select property class (1-3): "))
                if 1 <= class_choice <= 3:
                    property_classes = [PropertyClass.CLASS_A, PropertyClass.CLASS_B, PropertyClass.CLASS_C]
                    property_class = property_classes[class_choice - 1]
                    break
                else:
                    print("Please enter 1, 2, or 3.")
            except ValueError:
                print("Please enter a valid number.")
        
        # Get validated integer inputs
        total_units = get_validated_integer("Total number of units: ", 1)
        total_square_feet = get_validated_integer("Total square feet: ", 1000)
        year_built = get_validated_integer("Year built: ", 1900, 2025)
        
        print()
        
        # Financial Information
        print("[3] FINANCIAL INFORMATION")
        print("-" * 30)
        
        purchase_price = get_validated_currency("Purchase price: ", validator)
        down_payment_pct = get_validated_percentage("Down payment (% or decimal): ", validator)
        
        # Optional financial data
        current_noi_input = input("Current annual NOI (optional, press Enter to skip): ").strip()
        current_noi = None
        if current_noi_input:
            noi_result = validator.validate_currency(current_noi_input, "NOI")
            if noi_result.is_valid:
                current_noi = noi_result.formatted_value
        
        print()
        
        # Location Information
        print("[4] LOCATION INFORMATION")
        print("-" * 30)
        
        address = input("Street address: ").strip()
        if not address:
            address = "123 Investment Street"
        
        city = input("City: ").strip()
        if not city:
            city = "New York"
        
        state = input("State (2 letters, e.g., NY): ").strip().upper()
        if not state or len(state) != 2:
            state = "NY"
        
        zip_code = input("ZIP code: ").strip()
        if not zip_code:
            zip_code = "10001"
        
        # MSA Selection
        print("\nSupported metropolitan areas:")
        msa_options = helper.get_supported_msas()
        for i, (code, name) in enumerate(msa_options, 1):
            print(f"{i}. {name}")
        
        while True:
            try:
                msa_choice = int(input(f"Select MSA (1-{len(msa_options)}): "))
                if 1 <= msa_choice <= len(msa_options):
                    msa_code = msa_options[msa_choice - 1][0]
                    break
                else:
                    print(f"Please enter a number between 1 and {len(msa_options)}.")
            except ValueError:
                print("Please enter a valid number.")
        
        print()
        
        # Operating Information
        print("[5] OPERATING INFORMATION")
        print("-" * 30)
        
        mgmt_fee_input = input("Management fee % (default 5%, press Enter): ").strip()
        if mgmt_fee_input:
            mgmt_result = validator.validate_percentage(mgmt_fee_input, "management fee")
            mgmt_fee = mgmt_result.formatted_value if mgmt_result.is_valid else 0.05
        else:
            mgmt_fee = 0.05
        
        maint_reserve_input = input("Maintenance reserve % (default 2%, press Enter): ").strip()
        if maint_reserve_input:
            maint_result = validator.validate_percentage(maint_reserve_input, "maintenance reserve")
            maint_reserve = maint_result.formatted_value if maint_result.is_valid else 0.02
        else:
            maint_reserve = 0.02
        
        print()
        
        # Create Property Data
        print("[6] CREATING PROPERTY...")
        print("-" * 30)
        
        property_data = PropertyInputData(
            property_id=property_id,
            property_name=property_name,
            analysis_date=date.today(),
            physical_info=PropertyPhysicalInfo(
                property_type=property_type,
                property_class=property_class,
                total_units=total_units,
                total_square_feet=total_square_feet,
                year_built=year_built
            ),
            financial_info=PropertyFinancialInfo(
                purchase_price=purchase_price,
                down_payment_pct=down_payment_pct,
                current_noi=current_noi
            ),
            location_info=PropertyLocationInfo(
                address=address,
                city=city,
                state=state,
                zip_code=zip_code,
                msa_code=msa_code
            ),
            operating_info=PropertyOperatingInfo(
                management_fee_pct=mgmt_fee,
                maintenance_reserve_pct=maint_reserve
            )
        )
        
        # Display Summary
        print("\n" + "=" * 60)
        print("PROPERTY SUMMARY")
        print("=" * 60)
        
        print(f"Property: {property_data.property_name}")
        print(f"ID: {property_data.property_id}")
        print(f"Type: {property_data.physical_info.property_type.value.title()}")
        print(f"Class: {property_data.physical_info.property_class.value.replace('_', ' ').title()}")
        print(f"Units: {property_data.physical_info.total_units:,}")
        print(f"Square Feet: {property_data.physical_info.total_square_feet:,}")
        print(f"Year Built: {property_data.physical_info.year_built}")
        print(f"Purchase Price: {helper.format_currency(property_data.financial_info.purchase_price)}")
        print(f"Down Payment: {helper.format_percentage(property_data.financial_info.down_payment_pct)}")
        print(f"Location: {property_data.location_info.city}, {property_data.location_info.state}")
        print(f"MSA: {property_data.location_info.msa_code}")
        
        # Calculate metrics
        metrics = helper.calculate_financial_metrics(property_data)
        print(f"\nKey Metrics:")
        print(f"Price per Unit: {helper.format_currency(metrics['price_per_unit'])}")
        print(f"Price per SF: ${metrics['price_per_sf']:.0f}")
        if 'current_cap_rate' in metrics:
            print(f"Current Cap Rate: {helper.format_percentage(metrics['current_cap_rate'])}")
        print(f"Cash Required: {helper.format_currency(metrics['down_payment'])}")
        
        # Confirm save
        save_confirm = input("\nSave this property? (y/n): ").strip().lower()
        if save_confirm in ['y', 'yes']:
            property_manager.add_property(property_data)
            print(f"\n[SUCCESS] Property '{property_data.property_name}' saved!")
            
            # Monte Carlo Analysis
            mc_confirm = input("\nRun Monte Carlo analysis? (y/n): ").strip().lower()
            if mc_confirm in ['y', 'yes']:
                print("\n[RUNNING] Monte Carlo analysis...")
                
                try:
                    from monte_carlo.simulation_engine import monte_carlo_engine
                    
                    results = monte_carlo_engine.generate_scenarios(
                        property_data=property_data,
                        num_scenarios=50,  # Smaller number for faster demo
                        horizon_years=5,
                        use_correlations=True
                    )
                    
                    print(f"\n[SUCCESS] Generated {len(results.scenarios)} scenarios!")
                    print(f"Property: {results.property_id}")
                    print(f"MSA: {results.msa_code}")
                    
                    if results.scenarios:
                        growth_scores = [s.scenario_summary.get('growth_score', 0) for s in results.scenarios]
                        risk_scores = [s.scenario_summary.get('risk_score', 0) for s in results.scenarios]
                        
                        import numpy as np
                        print(f"\nScenario Analysis:")
                        print(f"Growth Range: {min(growth_scores):.3f} - {max(growth_scores):.3f}")
                        print(f"Risk Range: {min(risk_scores):.3f} - {max(risk_scores):.3f}")
                        print(f"Average Growth: {np.mean(growth_scores):.3f}")
                        print(f"Average Risk: {np.mean(risk_scores):.3f}")
                    
                    print("\n[COMPLETE] Analysis finished!")
                    
                except Exception as e:
                    print(f"\n[ERROR] Monte Carlo failed: {e}")
                    print("This may be due to missing forecast data for the MSA.")
            
            return property_data
        else:
            print("\n[CANCELLED] Property not saved.")
            return None
            
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Input cancelled by user.")
        return None
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return None


def get_validated_integer(prompt, min_val=1, max_val=None):
    """Get validated integer input."""
    while True:
        try:
            value = int(input(prompt))
            if value >= min_val and (max_val is None or value <= max_val):
                return value
            else:
                range_str = f"at least {min_val}" if max_val is None else f"between {min_val} and {max_val}"
                print(f"Please enter a value {range_str}.")
        except ValueError:
            print("Please enter a valid number.")


def get_validated_currency(prompt, validator):
    """Get validated currency input."""
    while True:
        value = input(prompt).strip()
        result = validator.validate_currency(value, "amount")
        
        if result.warnings:
            for warning in result.warnings:
                print(f"Warning: {warning}")
        
        if result.is_valid:
            return result.formatted_value
        else:
            for error in result.errors:
                print(f"Error: {error}")
            print("Please try again.")


def get_validated_percentage(prompt, validator):
    """Get validated percentage input."""
    while True:
        value = input(prompt).strip()
        result = validator.validate_percentage(value, "percentage")
        
        if result.warnings:
            for warning in result.warnings:
                print(f"Warning: {warning}")
        
        if result.is_valid:
            return result.formatted_value
        else:
            for error in result.errors:
                print(f"Error: {error}")
            print("Please try again.")


def main():
    """Main function."""
    print("Welcome to the Property Input System!")
    print("This will guide you through entering property data for analysis.")
    print()
    
    property_data = collect_property_interactively()
    
    if property_data:
        print("\n" + "=" * 60)
        print("COLLECTION COMPLETE")
        print("=" * 60)
        print("Your property is ready for investment analysis!")
        
        # Show current properties
        all_properties = property_manager.list_properties()
        if len(all_properties) > 1:
            print(f"\nYou now have {len(all_properties)} properties in the system:")
            for prop_id in all_properties:
                prop = property_manager.get_property(prop_id)
                if prop:
                    helper = PropertyInputHelper()
                    price = helper.format_currency(prop.financial_info.purchase_price)
                    print(f"- {prop.property_name} ({prop_id}): {price}")
    else:
        print("\nNo property data was collected.")


if __name__ == "__main__":
    main()