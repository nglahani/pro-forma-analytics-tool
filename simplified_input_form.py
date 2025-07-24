#!/usr/bin/env python3
"""
Simplified Property Input Form

Matches your exact requirements:
1. Number of residential units
2. Anticipated renovation time
3. Number of commercial units  
4. Investor equity share
5. Residential rent/unit
6. Commercial rent/unit
7. Self cash percentage
"""

import sys
from pathlib import Path
from datetime import date
import uuid

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from property_data import (
    SimplifiedPropertyInput, ResidentialUnits, CommercialUnits, 
    RenovationInfo, InvestorEquityStructure, RenovationStatus,
    property_manager as simplified_property_manager
)
from database.property_database import property_db


def collect_simplified_property_data():
    """Collect property data using your exact requirements."""
    
    print("=" * 60)
    print("SIMPLIFIED PROPERTY INPUT FORM")
    print("=" * 60)
    print("Please enter the following information about your property:")
    print()
    
    try:
        # Basic information
        property_name = input("Property name: ").strip()
        if not property_name:
            property_name = f"Property_{date.today().strftime('%Y%m%d')}"
        
        print()
        print("CORE PROPERTY DATA")
        print("-" * 30)
        
        # 1. Number of residential units
        residential_units_count = get_positive_integer("1. Number of residential units: ")
        
        # 2. Anticipated renovation time (months)
        print("\n2. Anticipated renovation time:")
        print("   0 = No renovation needed")
        print("   1-60 = Months of renovation")
        renovation_months = get_integer_in_range("   Renovation time (months): ", 0, 60)
        
        renovation_status = RenovationStatus.NOT_NEEDED if renovation_months == 0 else RenovationStatus.PLANNED
        
        # 3. Number of commercial units
        commercial_units_count = get_non_negative_integer("3. Number of commercial units (0 if none): ")
        
        # 4. Investor equity share (percentage)
        investor_equity_share = get_percentage("4. Investor equity share (%): ")
        
        # 5. Residential rent per unit
        residential_rent = 0
        if residential_units_count > 0:
            residential_rent = get_positive_float("5. Residential rent per unit ($/month): ")
        
        # 6. Commercial rent per unit  
        commercial_rent = 0
        if commercial_units_count > 0:
            commercial_rent = get_positive_float("6. Commercial rent per unit ($/month): ")
        
        # 7. Self cash percentage
        self_cash_percentage = get_percentage("7. Self cash percentage (%): ")
        
        print()
        print("OPTIONAL INFORMATION")
        print("-" * 30)
        
        # Optional location info for market analysis
        city = input("City (optional, for market analysis): ").strip()
        state = input("State (optional, 2 letters like NY): ").strip().upper()
        
        # Optional purchase price for metrics calculation
        purchase_price_input = input("Purchase price (optional, for calculations): $").strip()
        purchase_price = None
        if purchase_price_input:
            try:
                # Remove commas and convert
                purchase_price = float(purchase_price_input.replace(',', ''))
            except ValueError:
                print("Invalid purchase price format, skipping...")
        
        # Auto-detect MSA for known cities
        msa_code = ""
        if city and state:
            msa_mappings = {
                ("NEW YORK", "NY"): "35620",
                ("LOS ANGELES", "CA"): "31080", 
                ("CHICAGO", "IL"): "16980",
                ("WASHINGTON", "DC"): "47900",
                ("MIAMI", "FL"): "33100"
            }
            msa_code = msa_mappings.get((city.upper(), state.upper()), "")
        
        print()
        print("CREATING PROPERTY...")
        print("-" * 30)
        
        # Create property data structure
        property_data = SimplifiedPropertyInput(
            property_id=f"USER_{uuid.uuid4().hex[:8].upper()}",
            property_name=property_name,
            analysis_date=date.today(),
            residential_units=ResidentialUnits(
                total_units=residential_units_count,
                average_rent_per_unit=residential_rent
            ),
            commercial_units=CommercialUnits(
                total_units=commercial_units_count,
                average_rent_per_unit=commercial_rent
            ) if commercial_units_count > 0 else None,
            renovation_info=RenovationInfo(
                status=renovation_status,
                anticipated_duration_months=renovation_months if renovation_months > 0 else None
            ),
            equity_structure=InvestorEquityStructure(
                investor_equity_share_pct=investor_equity_share,
                self_cash_percentage=self_cash_percentage
            ),
            city=city,
            state=state,
            msa_code=msa_code,
            purchase_price=purchase_price
        )
        
        # Display summary
        print_property_summary(property_data)
        
        # Confirm save
        save_confirm = input("\nSave this property to database? (y/n): ").strip().lower()
        if save_confirm in ['y', 'yes']:
            
            # Save to in-memory manager
            simplified_property_manager.add_property(property_data)
            
            # Save to database
            if property_db.save_property(property_data):
                print(f"\n[SUCCESS] Property saved to database!")
                print(f"Property ID: {property_data.property_id}")
                
                # Create user listing entry
                user_id = "default_user"  # In production, this would come from authentication
                listing_id = property_db.create_user_listing(user_id, property_data.property_id)
                if listing_id:
                    print(f"Listing ID: {listing_id}")
                
                # Offer Monte Carlo analysis
                run_analysis = input("\nRun pro forma analysis? (y/n): ").strip().lower()
                if run_analysis in ['y', 'yes']:
                    run_monte_carlo_analysis(property_data)
                
                return property_data
            else:
                print("\n[ERROR] Failed to save to database")
                return None
        else:
            print("\n[CANCELLED] Property not saved")
            return None
            
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Input cancelled by user")
        return None
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return None


def print_property_summary(property_data: SimplifiedPropertyInput):
    """Print a summary of the collected property data."""
    print("\n" + "=" * 60)
    print("PROPERTY SUMMARY")
    print("=" * 60)
    
    print(f"Property Name: {property_data.property_name}")
    print(f"Property ID: {property_data.property_id}")
    print(f"Analysis Date: {property_data.analysis_date}")
    
    print(f"\nYour Input Data:")
    print(f"1. Residential Units: {property_data.residential_units.total_units}")
    print(f"2. Renovation Time: {property_data.renovation_info.anticipated_duration_months or 0} months")
    print(f"3. Commercial Units: {property_data.commercial_units.total_units if property_data.commercial_units else 0}")
    print(f"4. Investor Equity Share: {property_data.equity_structure.investor_equity_share_pct}%")
    print(f"5. Residential Rent/Unit: ${property_data.residential_units.average_rent_per_unit:,.0f}/month")
    print(f"6. Commercial Rent/Unit: ${property_data.commercial_units.average_rent_per_unit if property_data.commercial_units else 0:,.0f}/month")
    print(f"7. Self Cash Percentage: {property_data.equity_structure.self_cash_percentage}%")
    
    # Show calculated metrics
    metrics = property_data.calculate_key_metrics()
    print(f"\nCalculated Metrics:")
    print(f"Total Units: {metrics['total_units']}")
    print(f"Monthly Gross Rent: ${metrics['monthly_gross_rent']:,.0f}")
    print(f"Annual Gross Rent: ${metrics['annual_gross_rent']:,.0f}")
    print(f"Property Type: {metrics['property_type'].replace('_', ' ').title()}")
    print(f"Mixed Use: {'Yes' if metrics['is_mixed_use'] else 'No'}")
    
    if property_data.purchase_price:
        print(f"Purchase Price: ${property_data.purchase_price:,.0f}")
        print(f"Price per Unit: ${metrics['price_per_unit']:,.0f}")
        print(f"Cash Required: ${metrics['total_cash_required']:,.0f}")
        print(f"Gross Cap Rate: {metrics['gross_cap_rate']*100:.1f}%")
    
    if property_data.city and property_data.state:
        print(f"Location: {property_data.city}, {property_data.state}")
        if property_data.msa_code:
            print(f"MSA Code: {property_data.msa_code} (for market analysis)")


def run_monte_carlo_analysis(property_data: SimplifiedPropertyInput):
    """Run Monte Carlo analysis if possible."""
    print("\n" + "=" * 60)
    print("PRO FORMA ANALYSIS")
    print("=" * 60)
    
    if not property_data.msa_code:
        print("[WARNING] No MSA code available - analysis may be limited")
        print("For full analysis, specify a supported city (NYC, LA, Chicago, DC, Miami)")
        return
    
    try:
        # Convert to legacy PropertyInputData format for Monte Carlo engine
        from datetime import date
        
        # Create legacy format property using conversion method
        legacy_property = property_data.to_legacy_format()
        
        print(f"Running analysis for {property_data.msa_code}...")
        
        from monte_carlo.simulation_engine import monte_carlo_engine
        
        results = monte_carlo_engine.generate_scenarios(
            property_data=legacy_property,
            num_scenarios=50,
            horizon_years=5,
            use_correlations=True
        )
        
        print(f"\n[SUCCESS] Generated {len(results.scenarios)} scenarios")
        
        # Save results to database
        if property_db.save_analysis_results(property_data.property_id, results):
            print(f"Analysis results saved to database")
        
        # Display summary
        if results.scenarios:
            growth_scores = [s.scenario_summary.get('growth_score', 0) for s in results.scenarios]
            risk_scores = [s.scenario_summary.get('risk_score', 0) for s in results.scenarios]
            
            import numpy as np
            
            print(f"\nAnalysis Results:")
            print(f"Growth Potential: {min(growth_scores):.3f} - {max(growth_scores):.3f}")
            print(f"Risk Assessment: {min(risk_scores):.3f} - {max(risk_scores):.3f}")
            print(f"Average Growth: {np.mean(growth_scores):.3f}")
            print(f"Average Risk: {np.mean(risk_scores):.3f}")
            
            # Investment recommendation
            avg_growth = np.mean(growth_scores)
            avg_risk = np.mean(risk_scores)
            
            print(f"\nInvestment Assessment:")
            if avg_growth > 0.5 and avg_risk < 0.5:
                print("STRONG BUY - High growth potential with moderate risk")
            elif avg_growth > 0.4 and avg_risk < 0.6:
                print("BUY - Good growth potential with acceptable risk")
            elif avg_growth > 0.3:
                print("CONSIDER - Moderate growth potential, review risk tolerance")
            else:
                print("CAUTION - Lower growth potential, consider alternatives")
        
    except Exception as e:
        print(f"\n[ERROR] Analysis failed: {e}")
        print("This may be due to missing market data for the selected location")


# Helper functions for input validation
def get_positive_integer(prompt: str) -> int:
    """Get positive integer input."""
    while True:
        try:
            value = int(input(prompt))
            if value > 0:
                return value
            print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")


def get_non_negative_integer(prompt: str) -> int:
    """Get non-negative integer input."""
    while True:
        try:
            value = int(input(prompt))
            if value >= 0:
                return value
            print("Please enter a non-negative number.")
        except ValueError:
            print("Please enter a valid number.")


def get_integer_in_range(prompt: str, min_val: int, max_val: int) -> int:
    """Get integer input within a range."""
    while True:
        try:
            value = int(input(prompt))
            if min_val <= value <= max_val:
                return value
            print(f"Please enter a number between {min_val} and {max_val}.")
        except ValueError:
            print("Please enter a valid number.")


def get_positive_float(prompt: str) -> float:
    """Get positive float input."""
    while True:
        try:
            value_str = input(prompt).replace('$', '').replace(',', '').strip()
            value = float(value_str)
            if value > 0:
                return value
            print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")


def get_percentage(prompt: str) -> float:
    """Get percentage input (0-100)."""
    while True:
        try:
            value_str = input(prompt).replace('%', '').strip()
            value = float(value_str)
            if 0 <= value <= 100:
                return value
            print("Please enter a percentage between 0 and 100.")
        except ValueError:
            print("Please enter a valid percentage.")


def main():
    """Main function."""
    print("SIMPLIFIED PROPERTY INPUT SYSTEM")
    print("Designed for your exact requirements")
    print()
    
    property_data = collect_simplified_property_data()
    
    if property_data:
        print(f"\n" + "=" * 60)
        print("INPUT COMPLETE")
        print("=" * 60)
        print("Your property data has been saved and is ready for analysis!")
        
        # Show database stats
        stats = property_db.get_database_stats()
        print(f"\nDatabase Status:")
        print(f"Total Properties: {stats.get('total_properties', 0)}")
        print(f"Total Analyses: {stats.get('total_analyses', 0)}")
        
        # Show next steps
        print(f"\nNext Steps:")
        print("1. Review the analysis results above")
        print("2. Add more properties for comparison")
        print("3. Access your saved properties anytime")
        print("4. Use the data for investment decisions")
        
    else:
        print("\nNo property data was collected.")


if __name__ == "__main__":
    main()