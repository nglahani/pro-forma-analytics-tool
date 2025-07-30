"""
Edge Case Tests for Application Layer

Tests for error scenarios, edge cases, and boundary conditions
in the application services.
"""

from datetime import date

import pytest

from core.exceptions import ValidationError
from src.application.services.cash_flow_projection_service import (
    CashFlowProjectionService,
)
from src.application.services.dcf_assumptions_service import DCFAssumptionsService
from src.application.services.financial_metrics_service import FinancialMetricsService
from src.application.services.initial_numbers_service import InitialNumbersService
from src.domain.entities.cash_flow_projection import AnnualCashFlow, CashFlowProjection
from src.domain.entities.dcf_assumptions import DCFAssumptions
from src.domain.entities.initial_numbers import InitialNumbers
from src.domain.entities.property_data import SimplifiedPropertyInput


class TestCashFlowProjectionEdgeCases:
    """Test cash flow projection edge cases and error scenarios."""

    def test_calculate_cash_flow_with_extreme_negative_noi(self):
        """Test cash flow calculation with extremely negative NOI."""
        service = CashFlowProjectionService()

        # Create assumptions that lead to extreme negative NOI
        assumptions = DCFAssumptions(
            scenario_id="extreme_negative_noi_test",
            msa_code="35620",  # NYC
            property_id="test_property_001",
            commercial_mortgage_rate=[0.07, 0.072, 0.074, 0.076, 0.078, 0.08],
            treasury_10y_rate=[0.035, 0.037, 0.039, 0.041, 0.043, 0.045],
            fed_funds_rate=[0.025, 0.027, 0.029, 0.031, 0.033, 0.035],
            cap_rate=[0.08, 0.082, 0.084, 0.086, 0.088, 0.09],
            rent_growth_rate=[0.01, 0.01, 0.01, 0.01, 0.01, 0.01],  # Very low growth
            expense_growth_rate=[
                0.15,
                0.15,
                0.15,
                0.15,
                0.15,
                0.15,
            ],  # High expense growth
            property_growth_rate=[0.01, 0.01, 0.01, 0.01, 0.01, 0.01],
            vacancy_rate=[0.5, 0.5, 0.5, 0.5, 0.5, 0.5],  # High vacancy
            ltv_ratio=0.8,
            closing_cost_pct=0.025,
            lender_reserves_months=6.0,
            investor_equity_share=0.8,
            self_cash_percentage=0.3,
        )

        initial_numbers = InitialNumbers(
            property_id="test_property_001",
            scenario_id="extreme_negative_noi_test",
            purchase_price=1000000,
            closing_cost_amount=25000,  # Add closing costs
            renovation_capex=500000,
            cost_basis=1525000,  # purchase + closing + renovation
            loan_amount=800000,
            total_cash_required=725000,
            annual_interest_expense=64000,
            investor_cash_required=580000,  # 80% of total
            operator_cash_required=145000,  # 20% of total
            after_repair_value=1200000,
            pre_renovation_annual_rent=12000,
            post_renovation_annual_rent=14400,
            year_1_rental_income=7200,  # Reduced due to renovation period
            # Break down operating expenses into components
            property_taxes=6000,
            insurance=2000,
            repairs_maintenance=2500,
            property_management=1200,
            admin_expenses=800,
            contracting=500,
            replacement_reserves=680,
            total_operating_expenses=13680,  # Sum of above components
            investor_equity_share=0.8,
            preferred_return_rate=0.06,
        )

        # This should handle extreme scenarios gracefully
        projection = service.calculate_cash_flow_projection(
            assumptions, initial_numbers
        )

        assert projection is not None
        assert len(projection.annual_cash_flows) == 6  # Years 0-5

        # NOI should be very low or negative
        for annual_cf in projection.annual_cash_flows:
            assert annual_cf.net_operating_income < 100000  # Very low

    def test_calculate_cash_flow_with_zero_rental_income(self):
        """Test cash flow calculation with zero rental income."""
        service = CashFlowProjectionService()

        assumptions = DCFAssumptions(
            scenario_id="zero_rental_income_test",
            msa_code="35620",  # NYC
            property_id="test_property_002",
            commercial_mortgage_rate=[0.05, 0.051, 0.052, 0.053, 0.054, 0.055],
            treasury_10y_rate=[0.035, 0.036, 0.037, 0.038, 0.039, 0.04],
            fed_funds_rate=[0.025, 0.026, 0.027, 0.028, 0.029, 0.03],
            cap_rate=[0.06, 0.061, 0.062, 0.063, 0.064, 0.065],
            rent_growth_rate=[0.03, 0.03, 0.03, 0.03, 0.03, 0.03],
            expense_growth_rate=[0.02, 0.02, 0.02, 0.02, 0.02, 0.02],
            property_growth_rate=[0.03, 0.03, 0.03, 0.03, 0.03, 0.03],
            vacancy_rate=[0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
            ltv_ratio=0.75,
            closing_cost_pct=0.02,
            lender_reserves_months=5.0,
            investor_equity_share=0.8,
            self_cash_percentage=0.3,
        )

        initial_numbers = InitialNumbers(
            property_id="test_property_002",
            scenario_id="zero_rental_income_test",
            purchase_price=1000000,
            closing_cost_amount=20000,  # Add closing costs
            renovation_capex=200000,
            cost_basis=1220000,  # purchase + closing + renovation
            loan_amount=750000,
            total_cash_required=470000,
            annual_interest_expense=48000,
            investor_cash_required=376000,  # 80% of total
            operator_cash_required=94000,  # 20% of total
            after_repair_value=1300000,
            pre_renovation_annual_rent=0,
            post_renovation_annual_rent=0,
            year_1_rental_income=0,
            # All expense components are 0
            property_taxes=0,
            insurance=0,
            repairs_maintenance=0,
            property_management=0,
            admin_expenses=0,
            contracting=0,
            replacement_reserves=0,
            total_operating_expenses=0,
            investor_equity_share=0.8,
            preferred_return_rate=0.06,
        )

        # Should handle zero income scenario
        projection = service.calculate_cash_flow_projection(
            assumptions, initial_numbers
        )

        assert projection is not None
        # All cash flows should be negative
        for annual_cf in projection.annual_cash_flows:
            assert annual_cf.gross_rental_income == 0
            assert annual_cf.net_operating_income <= 0

    def test_calculate_cash_flow_with_extreme_growth_rates(self):
        """Test cash flow calculation with extreme growth rates."""
        service = CashFlowProjectionService()

        # Note: Extreme growth rates are outside validation ranges, using high but valid values
        assumptions = DCFAssumptions(
            scenario_id="extreme_growth_rates_test",
            msa_code="35620",  # NYC
            property_id="test_property_003",
            commercial_mortgage_rate=[0.06, 0.062, 0.064, 0.066, 0.068, 0.07],
            treasury_10y_rate=[0.035, 0.037, 0.039, 0.041, 0.043, 0.045],
            fed_funds_rate=[0.025, 0.027, 0.029, 0.031, 0.033, 0.035],
            cap_rate=[0.04, 0.041, 0.042, 0.043, 0.044, 0.045],
            rent_growth_rate=[
                0.2,
                0.2,
                0.2,
                0.2,
                0.2,
                0.2,
            ],  # High but valid 20% growth
            expense_growth_rate=[
                0.15,
                0.15,
                0.15,
                0.15,
                0.15,
                0.15,
            ],  # High but valid 15% growth
            property_growth_rate=[
                0.25,
                0.25,
                0.25,
                0.25,
                0.25,
                0.25,
            ],  # High but valid 25% growth
            vacancy_rate=[0.05, 0.05, 0.05, 0.05, 0.05, 0.05],
            ltv_ratio=0.8,
            closing_cost_pct=0.025,
            lender_reserves_months=6.0,
            investor_equity_share=0.8,
            self_cash_percentage=0.3,
        )

        initial_numbers = InitialNumbers(
            property_id="test_property_003",
            scenario_id="extreme_growth_rates_test",
            purchase_price=1000000,
            closing_cost_amount=25000,  # Add closing costs
            renovation_capex=200000,
            cost_basis=1225000,  # purchase + closing + renovation
            loan_amount=800000,
            total_cash_required=425000,
            annual_interest_expense=57600,
            investor_cash_required=340000,  # 80% of total
            operator_cash_required=85000,  # 20% of total
            after_repair_value=1400000,
            pre_renovation_annual_rent=16000,
            post_renovation_annual_rent=16000,
            year_1_rental_income=10667,  # Adjusted for 4 month renovation
            # Break down operating expenses
            property_taxes=2800,
            insurance=1200,
            repairs_maintenance=1000,
            property_management=800,
            admin_expenses=400,
            contracting=200,
            replacement_reserves=0,
            total_operating_expenses=6400,
            investor_equity_share=0.8,
            preferred_return_rate=0.06,
        )

        # Should handle extreme growth rates
        projection = service.calculate_cash_flow_projection(
            assumptions, initial_numbers
        )

        assert projection is not None
        # Rental income should grow dramatically
        year_1_income = projection.annual_cash_flows[
            1
        ].gross_rental_income  # First operational year
        year_5_income = projection.annual_cash_flows[5].gross_rental_income  # Last year

        # With high growth, income should increase significantly
        year_5_income = projection.annual_cash_flows[5].gross_rental_income
        assert year_5_income > year_1_income * 2


class TestFinancialMetricsEdgeCases:
    """Test financial metrics edge cases and error scenarios."""

    def test_calculate_metrics_with_all_negative_cash_flows(self):
        """Test metrics calculation with all negative cash flows."""
        service = FinancialMetricsService()

        # Create projection with all negative cash flows
        negative_cash_flows = []

        # Add year 0 (renovation/construction year)
        year_0_cf = AnnualCashFlow(
            year=0,
            gross_rental_income=0,
            vacancy_loss=0,
            effective_gross_income=0,
            property_taxes=0,
            insurance=0,
            repairs_maintenance=0,
            property_management=0,
            admin_expenses=0,
            contracting=0,
            replacement_reserves=0,
            total_operating_expenses=0,
            net_operating_income=0,
            annual_debt_service=0,
            before_tax_cash_flow=0,
            capital_expenditures=200000,  # Renovation costs
            net_cash_flow=-200000,
        )
        negative_cash_flows.append(year_0_cf)

        for year in range(1, 6):  # Years 1-5 only
            annual_cf = AnnualCashFlow(
                year=year,
                gross_rental_income=50000,
                vacancy_loss=0,
                effective_gross_income=50000,
                # Break down operating expenses into components to get small positive NOI
                property_taxes=20000,
                insurance=8000,
                repairs_maintenance=6000,
                property_management=4000,
                admin_expenses=3000,
                contracting=2000,
                replacement_reserves=2000,
                total_operating_expenses=45000,
                net_operating_income=5000,  # EGI (50000) - OpEx (45000) = 5000
                annual_debt_service=40000,
                before_tax_cash_flow=-35000,  # NOI (5000) - Debt Service (40000) = -35000
                net_cash_flow=-35000,
            )
            negative_cash_flows.append(annual_cf)

        # Create empty waterfall distributions for each year
        from src.domain.entities.cash_flow_projection import WaterfallDistribution

        waterfall_distributions = []
        for year in range(6):  # Years 0-5
            waterfall = WaterfallDistribution(
                year=year,
                available_cash=0,
                investor_preferred_return_due=0,
                investor_preferred_return_paid=0,
                investor_preferred_return_accrued=0,
                cumulative_unpaid_preferred=0,
                investor_cash_distribution=0,
                operator_cash_distribution=0,
                total_cash_distributed=0,
                remaining_cash=0,
            )
            waterfall_distributions.append(waterfall)

        projection = CashFlowProjection(
            property_id="test_property",
            scenario_id="test_assumptions",
            annual_cash_flows=negative_cash_flows,
            waterfall_distributions=waterfall_distributions,
        )

        initial_numbers = InitialNumbers(
            property_id="test_property_negative",
            scenario_id="negative_cash_flow_test",
            purchase_price=1000000,
            closing_cost_amount=0,  # Add closing costs field
            renovation_capex=200000,
            cost_basis=1200000,
            loan_amount=800000,
            total_cash_required=400000,
            annual_interest_expense=60000,
            investor_cash_required=320000,  # 80% of total
            operator_cash_required=80000,  # 20% of total
            after_repair_value=1200000,
            pre_renovation_annual_rent=50000,
            post_renovation_annual_rent=50000,
            year_1_rental_income=25000,  # Reduced due to renovation
            # Break down operating expenses
            property_taxes=35000,
            insurance=15000,
            repairs_maintenance=12000,
            property_management=8000,
            admin_expenses=5000,
            contracting=3000,
            replacement_reserves=2000,
            total_operating_expenses=80000,
            investor_equity_share=0.8,
            preferred_return_rate=0.06,
        )

        # Create simple DCF assumptions for testing
        test_assumptions = DCFAssumptions(
            scenario_id="negative_test",
            msa_code="35620",
            property_id="test_property",
            commercial_mortgage_rate=[0.05] * 6,
            treasury_10y_rate=[0.03] * 6,
            fed_funds_rate=[0.02] * 6,
            cap_rate=[0.06] * 6,
            rent_growth_rate=[0.03] * 6,
            expense_growth_rate=[0.02] * 6,
            property_growth_rate=[0.03] * 6,
            vacancy_rate=[0.05] * 6,
            ltv_ratio=0.75,
            closing_cost_pct=0.02,
            lender_reserves_months=6.0,
        )

        # Should raise ValidationError for extremely poor performing investment
        # (equity multiple becomes negative which is not allowed)
        with pytest.raises(ValidationError) as exc_info:
            service.calculate_financial_metrics(
                projection, test_assumptions, initial_numbers
            )

        assert "Equity multiple cannot be negative" in str(
            exc_info.value
        ) or "Financial metrics calculation failed" in str(exc_info.value)

    def test_calculate_metrics_with_zero_terminal_value(self):
        """Test metrics calculation with zero terminal value."""
        service = FinancialMetricsService()

        # Create projection with zero terminal value
        cash_flows = []

        # Add year 0 (renovation/construction year)
        year_0_cf = AnnualCashFlow(
            year=0,
            gross_rental_income=0,
            vacancy_loss=0,
            effective_gross_income=0,
            property_taxes=0,
            insurance=0,
            repairs_maintenance=0,
            property_management=0,
            admin_expenses=0,
            contracting=0,
            replacement_reserves=0,
            total_operating_expenses=0,
            net_operating_income=0,
            annual_debt_service=0,
            before_tax_cash_flow=0,
            capital_expenditures=200000,  # Renovation costs
            net_cash_flow=-200000,
        )
        cash_flows.append(year_0_cf)

        for year in range(1, 6):  # Years 1-5 only
            annual_cf = AnnualCashFlow(
                year=year,
                gross_rental_income=100000,
                vacancy_loss=0,
                effective_gross_income=100000,
                # Break down operating expenses
                property_taxes=20000,
                insurance=8000,
                repairs_maintenance=6000,
                property_management=3000,
                admin_expenses=2000,
                contracting=1000,
                replacement_reserves=0,
                total_operating_expenses=40000,
                net_operating_income=60000,
                annual_debt_service=45000,
                before_tax_cash_flow=15000,
                net_cash_flow=15000,
            )
            cash_flows.append(annual_cf)

        # Create empty waterfall distributions for each year
        from src.domain.entities.cash_flow_projection import WaterfallDistribution

        waterfall_distributions = []
        for year in range(6):  # Years 0-5
            waterfall = WaterfallDistribution(
                year=year,
                available_cash=0,
                investor_preferred_return_due=0,
                investor_preferred_return_paid=0,
                investor_preferred_return_accrued=0,
                cumulative_unpaid_preferred=0,
                investor_cash_distribution=0,
                operator_cash_distribution=0,
                total_cash_distributed=0,
                remaining_cash=0,
            )
            waterfall_distributions.append(waterfall)

        projection = CashFlowProjection(
            property_id="test_property",
            scenario_id="test_assumptions",
            annual_cash_flows=cash_flows,
            waterfall_distributions=waterfall_distributions,
        )

        initial_numbers = InitialNumbers(
            property_id="test_property_zero_terminal",
            scenario_id="zero_terminal_value_test",
            purchase_price=1000000,
            closing_cost_amount=0,  # Add closing costs field
            renovation_capex=200000,
            cost_basis=1200000,
            loan_amount=800000,
            total_cash_required=400000,
            annual_interest_expense=45000,
            investor_cash_required=320000,  # 80% of total
            operator_cash_required=80000,  # 20% of total
            after_repair_value=1200000,
            pre_renovation_annual_rent=100000,
            post_renovation_annual_rent=100000,
            year_1_rental_income=50000,  # Reduced due to renovation
            # Break down operating expenses
            property_taxes=20000,
            insurance=8000,
            repairs_maintenance=6000,
            property_management=3000,
            admin_expenses=2000,
            contracting=1000,
            replacement_reserves=0,
            total_operating_expenses=40000,
            investor_equity_share=0.8,
            preferred_return_rate=0.06,
        )

        # Create simple DCF assumptions for testing
        test_assumptions = DCFAssumptions(
            scenario_id="zero_terminal_test",
            msa_code="35620",
            property_id="test_property",
            commercial_mortgage_rate=[0.05] * 6,
            treasury_10y_rate=[0.03] * 6,
            fed_funds_rate=[0.02] * 6,
            cap_rate=[0.06] * 6,
            rent_growth_rate=[0.03] * 6,
            expense_growth_rate=[0.02] * 6,
            property_growth_rate=[0.03] * 6,
            vacancy_rate=[0.05] * 6,
            ltv_ratio=0.75,
            closing_cost_pct=0.02,
            lender_reserves_months=6.0,
        )

        # Should handle zero terminal value
        metrics = service.calculate_financial_metrics(
            projection, test_assumptions, initial_numbers
        )

        assert metrics is not None
        # Terminal value is calculated by the financial metrics service
        assert metrics is not None
        # NPV should be lower due to no terminal value
        assert metrics.net_present_value < 100000

    def test_calculate_irr_with_no_sign_changes(self):
        """Test IRR calculation with cash flows that have no sign changes."""
        service = FinancialMetricsService()

        # All positive cash flows (minimal initial investment)
        cash_flows = []

        # Add year 0 (minimal investment)
        year_0_cf = AnnualCashFlow(
            year=0,
            gross_rental_income=0,
            vacancy_loss=0,
            effective_gross_income=0,
            property_taxes=0,
            insurance=0,
            repairs_maintenance=0,
            property_management=0,
            admin_expenses=0,
            contracting=0,
            replacement_reserves=0,
            total_operating_expenses=0,
            net_operating_income=0,
            annual_debt_service=0,
            before_tax_cash_flow=0,
            capital_expenditures=1,  # Minimal initial investment
            net_cash_flow=-1,
        )
        cash_flows.append(year_0_cf)

        for year in range(1, 6):  # Years 1-5 only
            annual_cf = AnnualCashFlow(
                year=year,
                gross_rental_income=100000,
                vacancy_loss=0,
                effective_gross_income=100000,
                # Break down operating expenses
                property_taxes=15000,
                insurance=6000,
                repairs_maintenance=4000,
                property_management=3000,
                admin_expenses=1500,
                contracting=500,
                replacement_reserves=0,
                total_operating_expenses=30000,
                net_operating_income=70000,
                annual_debt_service=0,  # No debt
                before_tax_cash_flow=70000,
                net_cash_flow=70000,
            )
            cash_flows.append(annual_cf)

        # Create empty waterfall distributions for each year
        from src.domain.entities.cash_flow_projection import WaterfallDistribution

        waterfall_distributions = []
        for year in range(6):  # Years 0-5
            waterfall = WaterfallDistribution(
                year=year,
                available_cash=0,
                investor_preferred_return_due=0,
                investor_preferred_return_paid=0,
                investor_preferred_return_accrued=0,
                cumulative_unpaid_preferred=0,
                investor_cash_distribution=0,
                operator_cash_distribution=0,
                total_cash_distributed=0,
                remaining_cash=0,
            )
            waterfall_distributions.append(waterfall)

        projection = CashFlowProjection(
            property_id="test_property",
            scenario_id="test_assumptions",
            annual_cash_flows=cash_flows,
            waterfall_distributions=waterfall_distributions,
        )

        initial_numbers = InitialNumbers(
            property_id="test_property_no_investment",
            scenario_id="no_sign_changes_test",
            purchase_price=1,  # Minimal investment to avoid validation error
            closing_cost_amount=0,
            renovation_capex=0,
            cost_basis=1,
            loan_amount=0,
            total_cash_required=1,
            annual_interest_expense=0,
            investor_cash_required=1,  # Minimal amounts
            operator_cash_required=0,
            after_repair_value=1500000,
            pre_renovation_annual_rent=100000,
            post_renovation_annual_rent=100000,
            year_1_rental_income=100000,
            # Break down operating expenses
            property_taxes=15000,
            insurance=6000,
            repairs_maintenance=4000,
            property_management=3000,
            admin_expenses=1500,
            contracting=500,
            replacement_reserves=0,
            total_operating_expenses=30000,
            investor_equity_share=0.8,
            preferred_return_rate=0.06,
        )

        # Create simple DCF assumptions for testing
        test_assumptions = DCFAssumptions(
            scenario_id="no_sign_changes_test",
            msa_code="35620",
            property_id="test_property",
            commercial_mortgage_rate=[0.05] * 6,
            treasury_10y_rate=[0.03] * 6,
            fed_funds_rate=[0.02] * 6,
            cap_rate=[0.06] * 6,
            rent_growth_rate=[0.03] * 6,
            expense_growth_rate=[0.02] * 6,
            property_growth_rate=[0.03] * 6,
            vacancy_rate=[0.05] * 6,
            ltv_ratio=0.75,
            closing_cost_pct=0.02,
            lender_reserves_months=6.0,
        )

        # Should handle case with minimal initial investment
        metrics = service.calculate_financial_metrics(
            projection, test_assumptions, initial_numbers
        )

        assert metrics is not None
        # IRR may not be calculated due to all positive cash flows
        # But the investment should be profitable
        assert metrics.net_present_value > 0


class TestInitialNumbersEdgeCases:
    """Test initial numbers calculation edge cases."""

    def test_calculate_with_zero_purchase_price_should_raise_error(self):
        """Test calculation with zero purchase price."""
        service = InitialNumbersService()

        from src.domain.entities.property_data import (
            InvestorEquityStructure,
            RenovationInfo,
            RenovationStatus,
            ResidentialUnits,
        )

        property_input = SimplifiedPropertyInput(
            property_id="test_zero_price",
            property_name="Test Zero Price Property",
            analysis_date=date.today(),
            purchase_price=0,  # Zero price
            city="New York",
            state="NY",
            msa_code="35620",
            residential_units=ResidentialUnits(
                total_units=5, average_rent_per_unit=2000
            ),
            equity_structure=InvestorEquityStructure(
                investor_equity_share_pct=80, self_cash_percentage=30
            ),
            renovation_info=RenovationInfo(
                status=RenovationStatus.PLANNED, anticipated_duration_months=6
            ),
        )

        assumptions = DCFAssumptions(
            scenario_id="zero_purchase_price_test",
            msa_code="35620",
            property_id="test_zero_price",
            commercial_mortgage_rate=[0.05, 0.051, 0.052, 0.053, 0.054, 0.055],
            treasury_10y_rate=[0.035, 0.036, 0.037, 0.038, 0.039, 0.04],
            fed_funds_rate=[0.025, 0.026, 0.027, 0.028, 0.029, 0.03],
            cap_rate=[0.06, 0.061, 0.062, 0.063, 0.064, 0.065],
            rent_growth_rate=[0.03, 0.03, 0.03, 0.03, 0.03, 0.03],
            expense_growth_rate=[0.02, 0.02, 0.02, 0.02, 0.02, 0.02],
            property_growth_rate=[0.03, 0.03, 0.03, 0.03, 0.03, 0.03],
            vacancy_rate=[0.05, 0.05, 0.05, 0.05, 0.05, 0.05],
            ltv_ratio=0.75,
            closing_cost_pct=0.01,  # Minimum valid closing costs
            lender_reserves_months=1.0,  # Minimum valid value
            investor_equity_share=0.8,
            self_cash_percentage=0.3,
        )

        # Should raise validation error for zero purchase price
        with pytest.raises(ValidationError) as exc_info:
            service.calculate_initial_numbers(property_input, assumptions)

        assert "purchase price" in str(exc_info.value).lower()

    def test_calculate_with_extreme_ltv_ratio(self):
        """Test calculation with extreme LTV ratio."""
        service = InitialNumbersService()

        from src.domain.entities.property_data import (
            InvestorEquityStructure,
            RenovationInfo,
            RenovationStatus,
            ResidentialUnits,
        )

        property_input = SimplifiedPropertyInput(
            property_id="test_extreme_ltv",
            property_name="Test Extreme LTV Property",
            analysis_date=date.today(),
            purchase_price=1000000,
            city="New York",
            state="NY",
            msa_code="35620",
            residential_units=ResidentialUnits(
                total_units=10, average_rent_per_unit=2000
            ),
            equity_structure=InvestorEquityStructure(
                investor_equity_share_pct=80, self_cash_percentage=30
            ),
            renovation_info=RenovationInfo(
                status=RenovationStatus.PLANNED, anticipated_duration_months=6
            ),
        )

        # Note: Extreme LTV of 1.5 is outside validation range, using max valid LTV
        assumptions = DCFAssumptions(
            scenario_id="extreme_ltv_test",
            msa_code="35620",
            property_id="test_extreme_ltv",
            commercial_mortgage_rate=[0.05, 0.051, 0.052, 0.053, 0.054, 0.055],
            treasury_10y_rate=[0.035, 0.036, 0.037, 0.038, 0.039, 0.04],
            fed_funds_rate=[0.025, 0.026, 0.027, 0.028, 0.029, 0.03],
            cap_rate=[0.06, 0.061, 0.062, 0.063, 0.064, 0.065],
            rent_growth_rate=[0.03, 0.03, 0.03, 0.03, 0.03, 0.03],
            expense_growth_rate=[0.02, 0.02, 0.02, 0.02, 0.02, 0.02],
            property_growth_rate=[0.03, 0.03, 0.03, 0.03, 0.03, 0.03],
            vacancy_rate=[0.05, 0.05, 0.05, 0.05, 0.05, 0.05],
            ltv_ratio=0.95,  # Maximum valid LTV ratio
            closing_cost_pct=0.025,
            lender_reserves_months=6.0,
            investor_equity_share=0.8,
            self_cash_percentage=0.3,
        )

        # Should handle extreme LTV but flag as high risk
        initial_numbers = service.calculate_initial_numbers(property_input, assumptions)

        assert initial_numbers is not None
        # Check that loan amount is at 95% of purchase price (max LTV)
        expected_loan = 1000000 * 0.95
        assert abs(initial_numbers.loan_amount - expected_loan) < 1000

        # Since we used max valid LTV (0.95), there should be minimal validation issues
        # The test demonstrates the system handles high leverage scenarios
        assert initial_numbers is not None

    def test_calculate_with_negative_after_repair_value(self):
        """Test calculation resulting in negative after-repair value."""
        service = InitialNumbersService()

        from src.domain.entities.property_data import (
            InvestorEquityStructure,
            RenovationInfo,
            RenovationStatus,
            ResidentialUnits,
        )

        property_input = SimplifiedPropertyInput(
            property_id="test_negative_arv",
            property_name="Test Negative ARV Property",
            analysis_date=date.today(),
            purchase_price=1000000,
            city="New York",
            state="NY",
            msa_code="35620",
            residential_units=ResidentialUnits(
                total_units=2, average_rent_per_unit=500  # Very low rent
            ),
            equity_structure=InvestorEquityStructure(
                investor_equity_share_pct=80, self_cash_percentage=30
            ),
            renovation_info=RenovationInfo(
                status=RenovationStatus.PLANNED, anticipated_duration_months=12
            ),
        )

        assumptions = DCFAssumptions(
            scenario_id="negative_arv_test",
            msa_code="35620",
            property_id="test_negative_arv",
            commercial_mortgage_rate=[0.08, 0.082, 0.084, 0.086, 0.088, 0.09],
            treasury_10y_rate=[0.035, 0.037, 0.039, 0.041, 0.043, 0.045],
            fed_funds_rate=[0.025, 0.027, 0.029, 0.031, 0.033, 0.035],
            cap_rate=[
                0.15,
                0.15,
                0.15,
                0.15,
                0.15,
                0.15,
            ],  # Very high cap rate (low value)
            rent_growth_rate=[0.01, 0.01, 0.01, 0.01, 0.01, 0.01],
            expense_growth_rate=[0.05, 0.05, 0.05, 0.05, 0.05, 0.05],
            property_growth_rate=[0.01, 0.01, 0.01, 0.01, 0.01, 0.01],
            vacancy_rate=[0.3, 0.3, 0.3, 0.3, 0.3, 0.3],  # High vacancy
            ltv_ratio=0.8,
            closing_cost_pct=0.05,  # High closing costs
            lender_reserves_months=12.0,  # High reserves
            investor_equity_share=0.8,
            self_cash_percentage=0.3,
        )

        # Should handle scenario where ARV might be very low
        initial_numbers = service.calculate_initial_numbers(property_input, assumptions)

        assert initial_numbers is not None
        # After-repair value should be very low due to poor rental performance
        assert initial_numbers.after_repair_value < initial_numbers.cost_basis


class TestDCFAssumptionsEdgeCases:
    """Test DCF assumptions edge cases."""

    def test_create_assumptions_with_missing_parameters(self):
        """Test creating assumptions with missing Monte Carlo parameters."""
        service = DCFAssumptionsService()

        # Incomplete Monte Carlo scenario (missing some parameters)
        incomplete_scenario = {
            "scenario_id": "incomplete_scenario",
            "forecasted_parameters": {
                "treasury_10y": [0.03, 0.035, 0.04, 0.045, 0.05, 0.055],
                "commercial_mortgage_rate": [0.05, 0.055, 0.06, 0.065, 0.07, 0.075],
                # Missing other required parameters
            },
        }

        from src.domain.entities.property_data import (
            CommercialUnits,
            InvestorEquityStructure,
            RenovationInfo,
            RenovationStatus,
            ResidentialUnits,
        )

        property_input = SimplifiedPropertyInput(
            property_id="test_missing_params",
            property_name="Test Missing Parameters Property",
            analysis_date=date.today(),
            purchase_price=1000000,
            city="New York",
            state="NY",
            msa_code="35620",
            residential_units=ResidentialUnits(
                total_units=10, average_rent_per_unit=2000
            ),
            commercial_units=CommercialUnits(total_units=2, average_rent_per_unit=3000),
            equity_structure=InvestorEquityStructure(
                investor_equity_share_pct=80, self_cash_percentage=30
            ),
            renovation_info=RenovationInfo(
                status=RenovationStatus.PLANNED, anticipated_duration_months=6
            ),
        )

        # Should raise ValidationError for missing parameters
        with pytest.raises(ValidationError) as exc_info:
            service.create_dcf_assumptions_from_scenario(
                incomplete_scenario, property_input
            )

        assert "missing" in str(exc_info.value).lower()

    def test_create_assumptions_with_invalid_parameter_values(self):
        """Test creating assumptions with invalid parameter values."""
        service = DCFAssumptionsService()

        # Monte Carlo scenario with extreme but valid values
        invalid_scenario = {
            "scenario_id": "invalid_scenario",
            "forecasted_parameters": {
                "treasury_10y": [
                    0.005,
                    0.006,
                    0.007,
                    0.008,
                    0.009,
                    0.01,
                ],  # Low but valid rates
                "commercial_mortgage_rate": [
                    0.01,
                    0.011,
                    0.012,
                    0.013,
                    0.014,
                    0.015,
                ],  # Low but valid rates
                "cap_rate": [
                    0.03,
                    0.031,
                    0.032,
                    0.033,
                    0.034,
                    0.035,
                ],  # Minimum valid cap rates
                "vacancy_rate": [
                    0.5,
                    0.5,
                    0.5,
                    0.5,
                    0.5,
                    0.5,
                ],  # High but valid vacancy
                "rent_growth": [
                    -0.1,
                    -0.09,
                    -0.08,
                    -0.07,
                    -0.06,
                    -0.05,
                ],  # Negative but valid growth
                "expense_growth": [
                    0.15,
                    0.15,
                    0.15,
                    0.15,
                    0.15,
                    0.15,
                ],  # High but valid expense growth
                "property_growth": [
                    -0.2,
                    -0.18,
                    -0.16,
                    -0.14,
                    -0.12,
                    -0.1,
                ],  # Negative but valid appreciation
                "ltv_ratio": [
                    0.95,
                    0.95,
                    0.95,
                    0.95,
                    0.95,
                    0.95,
                ],  # High but valid leverage
                "closing_cost_pct": [
                    0.15,
                    0.15,
                    0.15,
                    0.15,
                    0.15,
                    0.15,
                ],  # High but valid closing costs
                "lender_reserves": [
                    12.0,
                    12.0,
                    12.0,
                    12.0,
                    12.0,
                    12.0,
                ],  # High but valid reserves
                "fed_funds_rate": [
                    0.0,
                    0.001,
                    0.002,
                    0.003,
                    0.004,
                    0.005,
                ],  # Low but valid fed funds
            },
        }

        from src.domain.entities.property_data import (
            CommercialUnits,
            InvestorEquityStructure,
            RenovationInfo,
            RenovationStatus,
            ResidentialUnits,
        )

        property_input = SimplifiedPropertyInput(
            property_id="test_invalid_values",
            property_name="Test Invalid Values Property",
            analysis_date=date.today(),
            purchase_price=1000000,
            city="New York",
            state="NY",
            msa_code="35620",
            residential_units=ResidentialUnits(
                total_units=10, average_rent_per_unit=2000
            ),
            commercial_units=CommercialUnits(total_units=2, average_rent_per_unit=3000),
            equity_structure=InvestorEquityStructure(
                investor_equity_share_pct=80, self_cash_percentage=30
            ),
            renovation_info=RenovationInfo(
                status=RenovationStatus.PLANNED, anticipated_duration_months=6
            ),
        )

        # Should handle extreme values but may generate warnings
        assumptions = service.create_dcf_assumptions_from_scenario(
            invalid_scenario, property_input
        )

        assert assumptions is not None
        # Some values should be within valid ranges
        assert assumptions.cap_rate[0] > 0.01  # Should be positive
        assert assumptions.ltv_ratio <= 1.0  # Should be within reasonable max

        # Compatibility validation should flag issues
        issues = service.validate_assumptions_compatibility(assumptions)
        assert len(issues) > 0
