"""
Quick End-to-End DCF Workflow Demo

Tests the complete 4-phase DCF workflow to verify system readiness.
"""

from src.application.services.dcf_assumptions_service import DCFAssumptionsService
from src.application.services.initial_numbers_service import InitialNumbersService
from src.application.services.cash_flow_projection_service import CashFlowProjectionService
from src.application.services.financial_metrics_service import FinancialMetricsService
from src.domain.entities.property_data import SimplifiedPropertyInput, InvestorEquityStructure, ResidentialUnits, RenovationStatus, RenovationInfo
from datetime import date


def main():
    """Run complete DCF workflow end-to-end test."""
    
    print("\n" + "="*80)
    print("COMPLETE DCF WORKFLOW - END-TO-END TEST")
    print("="*80)
    
    # Initialize services
    dcf_service = DCFAssumptionsService()
    initial_numbers_service = InitialNumbersService()
    cash_flow_service = CashFlowProjectionService()
    financial_metrics_service = FinancialMetricsService()
    
    print("[OK] Services initialized successfully")
    
    # Create test property
    test_property = SimplifiedPropertyInput(
        property_id="E2E_TEST_001",
        property_name="End-to-End Test Property",
        analysis_date=date.today(),
        residential_units=ResidentialUnits(
            total_units=40,
            average_rent_per_unit=1950,
            unit_types="Mixed: 15x1BR, 20x2BR, 5x3BR"
        ),
        renovation_info=RenovationInfo(
            status=RenovationStatus.PLANNED,
            anticipated_duration_months=12
        ),
        equity_structure=InvestorEquityStructure(
            investor_equity_share_pct=75.0,
            self_cash_percentage=20.0,
            number_of_investors=1
        ),
        city="Chicago",
        state="IL",
        msa_code="16980",
        purchase_price=3500000  # $3.5M property
    )
    
    print(f"[OK] Test property created: {test_property.property_name}")
    print(f"   Purchase Price: ${test_property.purchase_price:,}")
    print(f"   Total Units: {test_property.residential_units.total_units}")
    
    # Create market scenario
    test_scenario = {
        'scenario_id': 'E2E_MARKET_SCENARIO',
        'forecasted_parameters': {
            'commercial_mortgage_rate': [0.070, 0.072, 0.074, 0.076, 0.078, 0.080],
            'treasury_10y': [0.042, 0.044, 0.046, 0.048, 0.050, 0.052],
            'fed_funds_rate': [0.025, 0.027, 0.029, 0.031, 0.033, 0.035],
            'cap_rate': [0.065, 0.065, 0.063, 0.061, 0.059, 0.057],
            'rent_growth': [0.0, 0.035, 0.032, 0.030, 0.028, 0.025],
            'expense_growth': [0.0, 0.025, 0.023, 0.025, 0.022, 0.024],
            'property_growth': [0.0, 0.030, 0.028, 0.025, 0.022, 0.020],
            'vacancy_rate': [0.0, 0.045, 0.040, 0.045, 0.042, 0.045],
            'ltv_ratio': [0.75, 0.75, 0.75, 0.75, 0.75, 0.75],
            'closing_cost_pct': [0.050, 0.050, 0.050, 0.050, 0.050, 0.050],
            'lender_reserves': [3.0, 3.0, 3.0, 3.0, 3.0, 3.0]
        }
    }
    
    print("[OK] Market scenario created")
    
    try:
        # Phase 1: DCF Assumptions
        print("\n[PHASE 1] Creating DCF assumptions...")
        dcf_assumptions = dcf_service.create_dcf_assumptions_from_scenario(
            test_scenario, test_property
        )
        print(f"   [OK] DCF assumptions created for scenario: {dcf_assumptions.scenario_id}")
        print(f"   Mortgage Rate Range: {min(dcf_assumptions.commercial_mortgage_rate):.1%} - {max(dcf_assumptions.commercial_mortgage_rate):.1%}")
        
        # Phase 2: Initial Numbers
        print("\n[PHASE 2] Calculating initial numbers...")
        initial_numbers = initial_numbers_service.calculate_initial_numbers(
            test_property, dcf_assumptions
        )
        print(f"   [OK] Initial numbers calculated")
        print(f"   Total Cash Required: ${initial_numbers.total_cash_required:,.0f}")
        print(f"   LTV Ratio: {initial_numbers.calculate_ltv_ratio():.1%}")
        print(f"   Year 1 NOI: ${initial_numbers.year_1_rental_income - initial_numbers.total_operating_expenses:,.0f}")
        
        # Phase 3: Cash Flow Projections
        print("\n[PHASE 3] Creating cash flow projections...")
        cash_flow_projection = cash_flow_service.calculate_cash_flow_projection(
            dcf_assumptions, initial_numbers
        )
        print(f"   [OK] Cash flow projections created")
        print(f"   Years Projected: {len(cash_flow_projection.annual_cash_flows)}")
        
        # Calculate total distributions for summary
        total_distributions = sum(d.total_cash_distributed 
                                for d in cash_flow_projection.waterfall_distributions 
                                if d.year > 0)
        print(f"   Total Distributions (5 years): ${total_distributions:,.0f}")
        
        # Phase 4: Financial Metrics
        print("\n[PHASE 4] Calculating financial metrics...")
        financial_metrics = financial_metrics_service.calculate_financial_metrics(
            cash_flow_projection, dcf_assumptions, initial_numbers, discount_rate=0.10
        )
        print(f"   [OK] Financial metrics calculated")
        
        # Display Results
        print("\n" + "="*80)
        print("INVESTMENT ANALYSIS RESULTS")
        print("="*80)
        print(f"Property: {test_property.property_name}")
        print(f"Purchase Price: ${test_property.purchase_price:,}")
        print(f"Total Investment: ${financial_metrics.initial_investment:,.0f}")
        print()
        print("FINANCIAL PERFORMANCE:")
        print(f"  Net Present Value: ${financial_metrics.net_present_value:,.0f}")
        print(f"  Internal Rate of Return: {financial_metrics.internal_rate_return:.1%}")
        print(f"  Equity Multiple: {financial_metrics.equity_multiple:.2f}x")
        print(f"  Payback Period: {financial_metrics.payback_period_years:.1f} years")
        print()
        print("INVESTMENT RECOMMENDATION:")
        print(f"  Recommendation: {financial_metrics.investment_recommendation.value}")
        print(f"  Risk Level: {financial_metrics.risk_level.value}")
        print(f"  Rationale: {financial_metrics.recommendation_rationale}")
        print()
        print("TERMINAL VALUE:")
        print(f"  Gross Property Value: ${financial_metrics.terminal_value.gross_property_value:,.0f}")
        print(f"  Net Sale Proceeds: ${financial_metrics.terminal_value.net_sale_proceeds:,.0f}")
        print(f"  Exit Cap Rate: {financial_metrics.terminal_value.exit_cap_rate:.1%}")
        
        # Validation checks
        print("\n" + "="*80)
        print("SYSTEM VALIDATION CHECKS")
        print("="*80)
        
        validation_passed = True
        
        # Check 1: Data consistency
        if (dcf_assumptions.property_id == test_property.property_id and
            initial_numbers.property_id == test_property.property_id and
            cash_flow_projection.property_id == test_property.property_id and
            financial_metrics.property_id == test_property.property_id):
            print("[PASS] Property ID consistency across all phases")
        else:
            print("[FAIL] Property ID inconsistency detected")
            validation_passed = False
        
        # Check 2: Financial calculations
        if (financial_metrics.initial_investment == initial_numbers.total_cash_required and
            abs(financial_metrics.total_distributions - total_distributions) < 10.0):
            print("[PASS] Financial calculations consistent across phases")
        else:
            print("[FAIL] Financial calculation inconsistency detected")
            validation_passed = False
        
        # Check 3: Business logic validation
        if (initial_numbers.after_repair_value > initial_numbers.purchase_price and
            0.4 < initial_numbers.calculate_ltv_ratio() < 0.9 and
            financial_metrics.debt_service_coverage_avg > 1.0):
            print("[PASS] Business logic validation passed")
        else:
            print("[FAIL] Business logic validation failed")
            validation_passed = False
        
        # Check 4: Reasonable returns
        if (0.02 < financial_metrics.internal_rate_return < 1.0 and
            financial_metrics.equity_multiple > 1.0 and
            financial_metrics.net_present_value > -1000000):
            print("[PASS] Investment returns are reasonable")
        else:
            print("[FAIL] Investment returns are unrealistic")
            validation_passed = False
        
        # Final status
        if validation_passed:
            print("\n" + "="*80)
            print("SUCCESS: END-TO-END WORKFLOW TEST PASSED")
            print("The complete DCF workflow is functioning correctly!")
            print("System is ready for production use.")
            print("="*80)
            return True
        else:
            print("\n" + "="*80)
            print("WARNING: END-TO-END WORKFLOW TEST HAS ISSUES")
            print("The DCF workflow completed but has validation concerns.")
            print("Review the issues above before production use.")
            print("="*80)
            return False
            
    except Exception as e:
        print(f"\nERROR: End-to-end workflow failed")
        print(f"   Error: {str(e)}")
        print(f"   Type: {type(e).__name__}")
        print("\n" + "="*80)
        print("FAILED: END-TO-END WORKFLOW TEST")
        print("System requires fixes before production use.")
        print("="*80)
        raise


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    success = main()
    exit(0 if success else 1)