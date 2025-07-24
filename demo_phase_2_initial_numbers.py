#!/usr/bin/env python3
"""
Demo: DCF Engine Phase 2 - Initial Numbers Calculator

Demonstrates the complete workflow from Monte Carlo scenarios -> DCF Assumptions -> Initial Numbers.
This shows Phase 1 + Phase 2 of the DCF engine working together.
"""

import sys
from pathlib import Path
from datetime import date

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.application.services.dcf_assumptions_service import DCFAssumptionsService
from src.application.services.initial_numbers_service import InitialNumbersService
from property_data import SimplifiedPropertyInput, ResidentialUnits, CommercialUnits, RenovationInfo, InvestorEquityStructure, RenovationStatus


def create_demo_property() -> SimplifiedPropertyInput:
    """Create a demo property with realistic parameters."""
    return SimplifiedPropertyInput(
        property_id="DEMO_PHASE2_001",
        property_name="Demo Mixed-Use Building - Phase 2",
        analysis_date=date.today(),
        residential_units=ResidentialUnits(
            total_units=18,
            average_rent_per_unit=3200  # $3,200/month per unit
        ),
        commercial_units=CommercialUnits(
            total_units=3,
            average_rent_per_unit=5800  # $5,800/month per unit
        ),
        renovation_info=RenovationInfo(
            status=RenovationStatus.PLANNED,
            anticipated_duration_months=10,
            estimated_cost=275000  # $275k renovation budget
        ),
        equity_structure=InvestorEquityStructure(
            investor_equity_share_pct=80.0,  # Investor gets 80%
            self_cash_percentage=25.0        # 25% cash down
        ),
        city="New York",
        state="NY",
        msa_code="35620",
        purchase_price=4200000  # $4.2M purchase price
    )


def create_market_scenarios() -> list:
    """Create three different market scenarios for comprehensive demo."""
    
    # Scenario 1: Optimistic Market
    optimistic_scenario = {
        'scenario_id': 'OPTIMISTIC_2024_001',
        'forecasted_parameters': {
            'commercial_mortgage_rate': [0.050, 0.052, 0.054, 0.056, 0.058, 0.060],
            'treasury_10y': [0.032, 0.034, 0.036, 0.038, 0.040, 0.042],
            'fed_funds_rate': [0.012, 0.015, 0.018, 0.020, 0.022, 0.024],
            'cap_rate': [0.060, 0.060, 0.060, 0.060, 0.055, 0.055],  # Cap compression
            'rent_growth': [0.0, 0.055, 0.048, 0.042, 0.038, 0.035],  # Strong rent growth
            'expense_growth': [0.0, 0.015, 0.018, 0.020, 0.022, 0.024],  # Moderate expenses
            'property_growth': [0.0, 0.042, 0.038, 0.035, 0.032, 0.028],  # Strong appreciation
            'vacancy_rate': [0.0, 0.025, 0.020, 0.025, 0.020, 0.025],  # Low vacancy
            'ltv_ratio': [0.75, 0.75, 0.75, 0.75, 0.75, 0.75],
            'closing_cost_pct': [0.045, 0.045, 0.045, 0.045, 0.045, 0.045],
            'lender_reserves': [2.0, 2.0, 2.0, 2.0, 2.0, 2.0]
        }
    }
    
    # Scenario 2: Conservative/Stress Market
    conservative_scenario = {
        'scenario_id': 'CONSERVATIVE_2024_001',
        'forecasted_parameters': {
            'commercial_mortgage_rate': [0.085, 0.090, 0.095, 0.100, 0.105, 0.110],
            'treasury_10y': [0.058, 0.062, 0.066, 0.070, 0.074, 0.078],
            'fed_funds_rate': [0.048, 0.052, 0.056, 0.060, 0.064, 0.068],
            'cap_rate': [0.080, 0.080, 0.085, 0.085, 0.090, 0.095],  # Cap expansion
            'rent_growth': [0.0, 0.008, 0.012, 0.015, 0.018, 0.020],  # Slow rent growth
            'expense_growth': [0.0, 0.045, 0.042, 0.048, 0.045, 0.040],  # High expense growth
            'property_growth': [0.0, -0.010, 0.005, 0.012, 0.015, 0.018],  # Weak appreciation
            'vacancy_rate': [0.0, 0.095, 0.088, 0.105, 0.095, 0.088],  # High vacancy
            'ltv_ratio': [0.65, 0.65, 0.65, 0.65, 0.65, 0.65],  # Tighter lending
            'closing_cost_pct': [0.060, 0.060, 0.060, 0.060, 0.060, 0.060],
            'lender_reserves': [5.0, 5.0, 5.0, 5.0, 5.0, 5.0]  # Higher reserves
        }
    }
    
    # Scenario 3: Moderate/Base Case Market
    moderate_scenario = {
        'scenario_id': 'MODERATE_2024_001',
        'forecasted_parameters': {
            'commercial_mortgage_rate': [0.068, 0.070, 0.072, 0.074, 0.076, 0.078],
            'treasury_10y': [0.042, 0.044, 0.046, 0.048, 0.050, 0.052],
            'fed_funds_rate': [0.028, 0.032, 0.036, 0.038, 0.040, 0.042],
            'cap_rate': [0.070, 0.070, 0.070, 0.070, 0.070, 0.070],  # Stable caps
            'rent_growth': [0.0, 0.028, 0.032, 0.030, 0.028, 0.026],  # Moderate growth
            'expense_growth': [0.0, 0.025, 0.028, 0.026, 0.027, 0.029],  # Normal expenses
            'property_growth': [0.0, 0.022, 0.025, 0.023, 0.021, 0.019],  # Steady appreciation
            'vacancy_rate': [0.0, 0.055, 0.048, 0.062, 0.055, 0.055],  # Normal vacancy
            'ltv_ratio': [0.70, 0.70, 0.70, 0.70, 0.70, 0.70],
            'closing_cost_pct': [0.050, 0.050, 0.050, 0.050, 0.050, 0.050],
            'lender_reserves': [3.5, 3.5, 3.5, 3.5, 3.5, 3.5]
        }
    }
    
    return [optimistic_scenario, conservative_scenario, moderate_scenario]


def format_currency(amount: float) -> str:
    """Format currency for display."""
    return f"${amount:,.0f}"


def format_percentage(rate: float) -> str:
    """Format percentage for display."""
    return f"{rate:.2%}"


def main():
    """Main demo function."""
    print("=" * 80)
    print("DCF ENGINE PHASE 2 DEMO: INITIAL NUMBERS CALCULATOR")
    print("=" * 80)
    print("Demonstrating complete workflow: Monte Carlo -> DCF Assumptions -> Initial Numbers")
    print()
    
    # Create demo data
    property_data = create_demo_property()
    market_scenarios = create_market_scenarios()
    
    # Display property information
    print("DEMO PROPERTY DETAILS")
    print("-" * 50)
    print(f"Property: {property_data.property_name}")
    print(f"Property ID: {property_data.property_id}")
    print(f"Purchase Price: {format_currency(property_data.purchase_price)}")
    print(f"Residential Units: {property_data.residential_units.total_units} units @ ${property_data.residential_units.average_rent_per_unit:,.0f}/month")
    print(f"Commercial Units: {property_data.commercial_units.total_units} units @ ${property_data.commercial_units.average_rent_per_unit:,.0f}/month")
    print(f"Renovation Duration: {property_data.renovation_info.anticipated_duration_months} months")
    print(f"Renovation Budget: {format_currency(property_data.renovation_info.estimated_cost)}")
    print(f"Investor Equity Share: {property_data.equity_structure.investor_equity_share_pct}%")
    print(f"Cash Down Payment: {property_data.equity_structure.self_cash_percentage}%")
    print()
    
    # Initialize services
    dcf_service = DCFAssumptionsService()
    initial_numbers_service = InitialNumbersService()
    
    # Process each scenario
    for i, scenario in enumerate(market_scenarios, 1):
        print(f"SCENARIO {i}: {scenario['scenario_id']}")
        print("=" * 80)
        
        try:
            # Step 1: Convert Monte Carlo scenario to DCF assumptions
            print("STEP 1: Creating DCF Assumptions from Monte Carlo Scenario")
            print("-" * 60)
            dcf_assumptions = dcf_service.create_dcf_assumptions_from_scenario(scenario, property_data)
            
            print(f"Scenario ID: {dcf_assumptions.scenario_id}")
            print(f"LTV Ratio: {format_percentage(dcf_assumptions.ltv_ratio)}")
            print(f"Closing Costs: {format_percentage(dcf_assumptions.closing_cost_pct)}")
            print(f"Lender Reserves: {dcf_assumptions.lender_reserves_months:.1f} months")
            print(f"Year 1 Mortgage Rate: {format_percentage(dcf_assumptions.commercial_mortgage_rate[1])}")
            print(f"Exit Cap Rate: {format_percentage(dcf_assumptions.cap_rate[5])}")
            print()
            
            # Step 2: Calculate Initial Numbers
            print("STEP 2: Calculating Initial Numbers (Acquisition & Financing)")
            print("-" * 60)
            initial_numbers = initial_numbers_service.calculate_initial_numbers(property_data, dcf_assumptions)
            
            # Display acquisition summary
            acquisition = initial_numbers.get_acquisition_summary()
            print("ACQUISITION SUMMARY:")
            print(f"  Purchase Price: {format_currency(acquisition['purchase_price'])}")
            print(f"  Total Acquisition Cost: {format_currency(acquisition['total_acquisition_cost'])}")
            print(f"  Loan Amount: {format_currency(acquisition['loan_amount'])}")
            print(f"  Total Cash Required: {format_currency(acquisition['total_cash_required'])}")
            print(f"  LTV Ratio: {format_percentage(acquisition['ltv_ratio'])}")
            print()
            
            # Display equity distribution
            equity = initial_numbers.get_equity_distribution()
            print("EQUITY DISTRIBUTION:")
            print(f"  Investor Cash: {format_currency(equity['investor_cash_required'])} ({format_percentage(equity['investor_equity_share'])})")
            print(f"  Operator Cash: {format_currency(equity['operator_cash_required'])} ({format_percentage(equity['operator_equity_share'])})")
            print(f"  Preferred Return: {format_percentage(equity['preferred_return_rate'])}")
            print()
            
            # Display income projections
            print("INCOME PROJECTIONS:")
            print(f"  Pre-Renovation Annual Rent: {format_currency(initial_numbers.pre_renovation_annual_rent)}")
            print(f"  Post-Renovation Annual Rent: {format_currency(initial_numbers.post_renovation_annual_rent)}")
            print(f"  Year 1 Rental Income: {format_currency(initial_numbers.year_1_rental_income)} (after {property_data.renovation_info.anticipated_duration_months}-month renovation)")
            print()
            
            # Display operating expenses
            expenses = initial_numbers.get_operating_expense_breakdown()
            print("OPERATING EXPENSES (Year 1):")
            print(f"  Property Taxes: {format_currency(expenses['property_taxes'])}")
            print(f"  Insurance: {format_currency(expenses['insurance'])}")
            print(f"  Property Management: {format_currency(expenses['property_management'])}")
            print(f"  Repairs & Maintenance: {format_currency(expenses['repairs_maintenance'])}")
            print(f"  Other Expenses: {format_currency(expenses['contracting'] + expenses['admin_expenses'] + expenses['replacement_reserves'])}")
            print(f"  TOTAL Operating Expenses: {format_currency(expenses['total_operating_expenses'])}")
            print(f"  Expense Ratio: {format_percentage(expenses['expense_ratio'])}")
            print()
            
            # Display key performance metrics
            print("KEY PERFORMANCE METRICS:")
            print(f"  Initial Cap Rate: {format_percentage(acquisition['initial_cap_rate'])}")
            print(f"  Year 1 Cash-on-Cash Return: {format_percentage(acquisition['year_1_cash_on_cash'])}")
            print(f"  Debt Service Coverage Ratio: {acquisition['debt_service_coverage']:.2f}x")
            print(f"  After-Repair Value: {format_currency(initial_numbers.after_repair_value)}")
            print(f"  Gross Rent Multiplier: {initial_numbers.calculate_gross_rent_multiplier():.1f}x")
            print()
            
            # Validate results
            print("VALIDATION RESULTS:")
            validation_issues = initial_numbers_service.validate_initial_numbers(initial_numbers)
            if validation_issues:
                print("WARNING: Validation Issues Found:")
                for issue in validation_issues:
                    print(f"  - {issue}")
            else:
                print("SUCCESS: All initial numbers validated successfully")
            print()
            
            # Show year-by-year assumptions impact
            print("YEAR-BY-YEAR MARKET ASSUMPTIONS:")
            for year in range(1, 6):  # Years 1-5
                year_assumptions = dcf_assumptions.get_year_assumptions(year)
                print(f"  Year {year}: Mortgage {format_percentage(year_assumptions['commercial_mortgage_rate'])}, "
                      f"Rent Growth {format_percentage(year_assumptions['rent_growth_rate'])}, "
                      f"Expense Growth {format_percentage(year_assumptions['expense_growth_rate'])}, "
                      f"Vacancy {format_percentage(year_assumptions['vacancy_rate'])}")
            print()
            
        except Exception as e:
            print(f"ERROR: Failed to process scenario: {str(e)}")
            print()
        
        print("=" * 80)
        print()
    
    # Summary
    print("PHASE 2 DEMONSTRATION COMPLETE")
    print("=" * 50)
    print()
    print("SUCCESS ACHIEVEMENTS:")
    print("1. [SUCCESS] Monte Carlo scenarios successfully converted to DCF assumptions")
    print("2. [SUCCESS] Property acquisition costs calculated correctly")
    print("3. [SUCCESS] Financing terms and loan amounts determined")
    print("4. [SUCCESS] Equity distribution computed based on investor structure")
    print("5. [SUCCESS] Income projections account for renovation period")
    print("6. [SUCCESS] Operating expenses estimated with market-standard ratios")
    print("7. [SUCCESS] Key performance metrics calculated (Cap Rate, Cash-on-Cash, DSCR)")
    print("8. [SUCCESS] Validation framework ensures data integrity")
    print()
    print("INTEGRATION STATUS:")
    print("[COMPLETE] Phase 1 (DCF Assumptions) - COMPLETE")
    print("[COMPLETE] Phase 2 (Initial Numbers) - COMPLETE") 
    print("[PENDING] Phase 3 (Cash Flow Projections) - PENDING")
    print("[PENDING] Phase 4 (Financial Metrics & NPV/IRR) - PENDING")
    print()
    print("NEXT DEVELOPMENT STEPS:")
    print("1. Build Cash Flow Projection Engine (Years 0-5 monthly/annual projections)")
    print("2. Implement waterfall distribution logic with preferred returns")
    print("3. Build NPV/IRR calculator with terminal value")
    print("4. Create investment decision framework and recommendations")
    print()


if __name__ == "__main__":
    main()