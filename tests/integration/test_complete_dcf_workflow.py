"""
Integration Tests for Complete DCF Workflow

Tests the end-to-end DCF workflow with real data processing,
ensuring all 4 phases work together correctly.
"""

from datetime import date
from typing import Any, Dict, List

from src.application.services.cash_flow_projection_service import (
    CashFlowProjectionService,
)
from src.application.services.dcf_assumptions_service import DCFAssumptionsService
from src.application.services.financial_metrics_service import FinancialMetricsService
from src.application.services.initial_numbers_service import InitialNumbersService
from src.domain.entities.financial_metrics import InvestmentRecommendation, RiskLevel
from src.domain.entities.property_data import (
    InvestorEquityStructure,
    RenovationInfo,
    RenovationStatus,
    ResidentialUnits,
    SimplifiedPropertyInput,
)


class TestCompleteDCFWorkflow:
    """Integration tests for complete DCF workflow."""

    def setup_method(self):
        """Set up test data and services."""
        # Initialize services
        self.dcf_service = DCFAssumptionsService()
        self.initial_numbers_service = InitialNumbersService()
        self.cash_flow_service = CashFlowProjectionService()
        self.financial_metrics_service = FinancialMetricsService()

        # Create test property data
        self.test_property = SimplifiedPropertyInput(
            property_id="INTEGRATION_TEST_001",
            property_name="Integration Test Property",
            analysis_date=date(2024, 1, 15),
            residential_units=ResidentialUnits(
                total_units=50, average_rent_per_unit=2000.0
            ),
            renovation_info=RenovationInfo(
                status=RenovationStatus.PLANNED,
                anticipated_duration_months=6,
                estimated_cost=500000,
            ),
            equity_structure=InvestorEquityStructure(
                investor_equity_share_pct=75.0, self_cash_percentage=25.0
            ),
            commercial_units=None,
            city="New York",
            state="NY",
            msa_code="35620",
            purchase_price=4500000,
            property_address="123 Test Street, New York, NY 10001",
        )

        # Create test market scenarios
        self.market_scenarios = self._create_test_market_scenarios()

    def _create_test_market_scenarios(self) -> List[Dict[str, Any]]:
        """Create test market scenarios for integration testing."""
        conservative_scenario = {
            "scenario_id": "CONSERVATIVE_TEST_2024",
            "forecasted_parameters": {
                "commercial_mortgage_rate": [0.07, 0.072, 0.075, 0.078, 0.08, 0.082],
                "treasury_10y": [0.045, 0.047, 0.05, 0.052, 0.055, 0.057],
                "fed_funds_rate": [0.05, 0.052, 0.055, 0.057, 0.06, 0.062],
                "cap_rate": [0.055, 0.056, 0.057, 0.058, 0.059, 0.06],
                "vacancy_rate": [0.06, 0.06, 0.06, 0.06, 0.06, 0.06],
                "rent_growth": [0.03, 0.03, 0.03, 0.03, 0.03, 0.03],
                "expense_growth": [0.035, 0.035, 0.035, 0.035, 0.035, 0.035],
                "property_growth": [0.025, 0.025, 0.025, 0.025, 0.025, 0.025],
                "ltv_ratio": [0.75, 0.75, 0.75, 0.75, 0.75, 0.75],
                "closing_cost_pct": [0.025, 0.025, 0.025, 0.025, 0.025, 0.025],
                "lender_reserves": [2.5, 2.5, 2.5, 2.5, 2.5, 2.5],
            },
        }

        optimistic_scenario = {
            "scenario_id": "OPTIMISTIC_TEST_2024",
            "forecasted_parameters": {
                "commercial_mortgage_rate": [0.065, 0.067, 0.07, 0.072, 0.075, 0.077],
                "treasury_10y": [0.04, 0.042, 0.045, 0.047, 0.05, 0.052],
                "fed_funds_rate": [0.045, 0.047, 0.05, 0.052, 0.055, 0.057],
                "cap_rate": [0.05, 0.051, 0.052, 0.053, 0.054, 0.055],
                "vacancy_rate": [0.04, 0.04, 0.04, 0.04, 0.04, 0.04],
                "rent_growth": [0.04, 0.04, 0.04, 0.04, 0.04, 0.04],
                "expense_growth": [0.03, 0.03, 0.03, 0.03, 0.03, 0.03],
                "property_growth": [0.035, 0.035, 0.035, 0.035, 0.035, 0.035],
                "ltv_ratio": [0.75, 0.75, 0.75, 0.75, 0.75, 0.75],
                "closing_cost_pct": [0.025, 0.025, 0.025, 0.025, 0.025, 0.025],
                "lender_reserves": [2.5, 2.5, 2.5, 2.5, 2.5, 2.5],
            },
        }

        return [conservative_scenario, optimistic_scenario]

    def test_complete_dcf_workflow_single_scenario(self):
        """Test complete DCF workflow for a single market scenario."""
        scenario = self.market_scenarios[0]  # Conservative scenario

        # Phase 1: DCF Assumptions
        dcf_assumptions = self.dcf_service.create_dcf_assumptions_from_scenario(
            scenario, self.test_property
        )

        # Validate DCF assumptions
        assert dcf_assumptions.property_id == "INTEGRATION_TEST_001"
        assert dcf_assumptions.scenario_id == "CONSERVATIVE_TEST_2024"
        assert len(dcf_assumptions.commercial_mortgage_rate) == 6  # Years 0-5
        assert all(
            0.05 < rate < 0.15 for rate in dcf_assumptions.commercial_mortgage_rate
        )
        assert dcf_assumptions.investor_equity_share == 0.75

        # Phase 2: Initial Numbers
        initial_numbers = self.initial_numbers_service.calculate_initial_numbers(
            self.test_property, dcf_assumptions
        )

        # Validate initial numbers
        assert initial_numbers.property_id == "INTEGRATION_TEST_001"
        assert initial_numbers.purchase_price == 4500000
        assert initial_numbers.total_cash_required > 0
        assert 0.5 < initial_numbers.calculate_ltv_ratio() < 0.8  # Reasonable LTV
        assert (
            initial_numbers.year_1_rental_income >= 0
        )  # Partial income after 6-month renovation
        assert (
            initial_numbers.post_renovation_annual_rent
            > initial_numbers.pre_renovation_annual_rent
        )

        # Phase 3: Cash Flow Projections
        cash_flow_projection = self.cash_flow_service.calculate_cash_flow_projection(
            dcf_assumptions, initial_numbers
        )

        # Validate cash flow projections
        assert cash_flow_projection.property_id == "INTEGRATION_TEST_001"
        assert len(cash_flow_projection.annual_cash_flows) == 6  # Years 0-5
        assert len(cash_flow_projection.waterfall_distributions) == 6

        # Validate Year 0 (renovation year)
        year_0_cf = cash_flow_projection.get_cash_flow_by_year(0)
        assert year_0_cf.gross_rental_income == 0  # No income during renovation
        assert year_0_cf.capital_expenditures > 0  # Renovation costs

        # Validate operational years (1-5)
        for year in range(1, 6):
            year_cf = cash_flow_projection.get_cash_flow_by_year(year)
            if year == 1:
                assert year_cf.gross_rental_income >= 0  # May be partial in Year 1
            else:
                assert year_cf.gross_rental_income > 0
            assert year_cf.net_operating_income > 0
            assert year_cf.annual_debt_service > 0

            # Waterfall distribution validation
            distribution = cash_flow_projection.get_distribution_by_year(year)
            assert distribution.available_cash >= 0
            assert (
                distribution.total_cash_distributed
                <= distribution.available_cash + 0.01
            )  # Allow small rounding

        # Phase 4: Financial Metrics
        financial_metrics = self.financial_metrics_service.calculate_financial_metrics(
            cash_flow_projection, dcf_assumptions, initial_numbers, discount_rate=0.10
        )

        # Validate financial metrics
        assert financial_metrics.property_id == "INTEGRATION_TEST_001"
        assert financial_metrics.scenario_id == "CONSERVATIVE_TEST_2024"
        assert financial_metrics.initial_investment > 0
        assert isinstance(financial_metrics.net_present_value, float)
        assert (
            -1.0 < financial_metrics.internal_rate_return < 5.0
        )  # Reasonable IRR range
        assert financial_metrics.equity_multiple > 0
        assert financial_metrics.payback_period_years > 0
        assert isinstance(
            financial_metrics.investment_recommendation, InvestmentRecommendation
        )
        assert isinstance(financial_metrics.risk_level, RiskLevel)
        assert financial_metrics.terminal_value is not None
        assert financial_metrics.terminal_value.net_sale_proceeds > 0

        print("\n✅ Single Scenario Integration Test Results:")
        print(f"   NPV: ${financial_metrics.net_present_value:,.0f}")
        print(f"   IRR: {financial_metrics.internal_rate_return:.1%}")
        print(f"   Multiple: {financial_metrics.equity_multiple:.2f}x")
        print(f"   Recommendation: {financial_metrics.investment_recommendation.value}")
        print(f"   Risk Level: {financial_metrics.risk_level.value}")


if __name__ == "__main__":
    # Run integration tests directly for development
    import logging

    logging.basicConfig(level=logging.INFO)

    test_suite = TestCompleteDCFWorkflow()
    test_suite.setup_method()

    print("\n" + "=" * 80)
    print("COMPLETE DCF WORKFLOW INTEGRATION TESTS")
    print("=" * 80)

    try:
        test_suite.test_complete_dcf_workflow_single_scenario()

        print("\n" + "=" * 80)
        print("[SUCCESS] INTEGRATION TEST PASSED")
        print("The complete DCF workflow is functioning correctly!")
        print("=" * 80)

    except Exception as e:
        print(f"\n[ERROR] Integration test failed: {str(e)}")
        raise
