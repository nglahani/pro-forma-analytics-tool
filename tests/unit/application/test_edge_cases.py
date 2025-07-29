"""
Edge Case Tests for Application Layer

Tests for error scenarios, edge cases, and boundary conditions
in the application services.
"""

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from core.exceptions import DataNotFoundError, ForecastError, ValidationError
from src.application.services.cash_flow_projection_service import (
    CashFlowProjectionService,
)
from src.application.services.dcf_assumptions_service import DCFAssumptionsService
from src.application.services.financial_metrics_service import FinancialMetricsService
from src.application.services.initial_numbers_service import InitialNumbersService
from src.domain.entities.cash_flow_projection import AnnualCashFlow, CashFlowProjection
from src.domain.entities.dcf_assumptions import DCFAssumptions
from src.domain.entities.initial_numbers import InitialNumbers
from src.domain.entities.monte_carlo import MonteCarloScenario
from src.domain.entities.property_data import SimplifiedPropertyInput


class TestCashFlowProjectionEdgeCases:
    """Test cash flow projection edge cases and error scenarios."""

    def test_calculate_cash_flow_with_extreme_negative_noi(self):
        """Test cash flow calculation with extremely negative NOI."""
        service = CashFlowProjectionService(Mock())

        # Create assumptions that lead to extreme negative NOI
        assumptions = DCFAssumptions(
            purchase_price=1000000,
            renovation_cost=500000,
            annual_rent_per_unit_residential=100,  # Very low rent
            annual_rent_per_unit_commercial=100,
            operating_expense_ratio=0.95,  # Very high expenses
            vacancy_rate=0.5,  # High vacancy
            rent_growth_rate=0.01,
            expense_growth_rate=0.15,  # High expense growth
            property_appreciation_rate=0.01,
            cap_rate_terminal=0.08,
            discount_rate=0.12,
            ltv_ratio=0.8,
            interest_rate=0.07,
            loan_term_years=30,
            closing_costs=25000,
            lender_reserves=50000,
        )

        initial_numbers = InitialNumbers(
            purchase_price=1000000,
            renovation_cost=500000,
            total_project_cost=1525000,
            loan_amount=800000,
            total_equity_required=725000,
            annual_debt_service=64000,
            residential_units=10,
            commercial_units=2,
            renovation_period_months=6,
            annual_rent_residential=12000,  # Total residential rent
            annual_rent_commercial=2400,  # Total commercial rent
            total_annual_rent=14400,
            operating_expenses=13680,  # Very high expenses
            net_operating_income=720,  # Very low NOI
            debt_service_coverage_ratio=0.01,  # Very low DSCR
            after_repair_value=1200000,
            ltv_ratio=0.67,
            cash_on_cash_return=0.001,
        )

        # This should handle extreme scenarios gracefully
        projection = service.calculate_cash_flow_projection(
            assumptions, initial_numbers
        )

        assert projection is not None
        assert len(projection.annual_cash_flows) == 6

        # NOI should be very low or negative
        for annual_cf in projection.annual_cash_flows:
            assert annual_cf.net_operating_income < 100000  # Very low

    def test_calculate_cash_flow_with_zero_rental_income(self):
        """Test cash flow calculation with zero rental income."""
        service = CashFlowProjectionService(Mock())

        assumptions = DCFAssumptions(
            purchase_price=1000000,
            renovation_cost=200000,
            annual_rent_per_unit_residential=0,  # Zero rent
            annual_rent_per_unit_commercial=0,  # Zero rent
            operating_expense_ratio=0.3,
            vacancy_rate=0.1,
            rent_growth_rate=0.03,
            expense_growth_rate=0.02,
            property_appreciation_rate=0.03,
            cap_rate_terminal=0.06,
            discount_rate=0.10,
            ltv_ratio=0.75,
            interest_rate=0.05,
            loan_term_years=30,
            closing_costs=20000,
            lender_reserves=30000,
        )

        initial_numbers = InitialNumbers(
            purchase_price=1000000,
            renovation_cost=200000,
            total_project_cost=1220000,
            loan_amount=750000,
            total_equity_required=470000,
            annual_debt_service=48000,
            residential_units=10,
            commercial_units=0,
            renovation_period_months=3,
            annual_rent_residential=0,
            annual_rent_commercial=0,
            total_annual_rent=0,
            operating_expenses=0,
            net_operating_income=-48000,  # Negative due to debt service
            debt_service_coverage_ratio=0,
            after_repair_value=1300000,
            ltv_ratio=0.58,
            cash_on_cash_return=-0.1,
        )

        # Should handle zero income scenario
        projection = service.calculate_cash_flow_projection(
            assumptions, initial_numbers
        )

        assert projection is not None
        # All cash flows should be negative
        for annual_cf in projection.annual_cash_flows:
            assert annual_cf.total_rental_income == 0
            assert annual_cf.net_operating_income <= 0

    def test_calculate_cash_flow_with_extreme_growth_rates(self):
        """Test cash flow calculation with extreme growth rates."""
        service = CashFlowProjectionService(Mock())

        assumptions = DCFAssumptions(
            purchase_price=1000000,
            renovation_cost=200000,
            annual_rent_per_unit_residential=2000,
            annual_rent_per_unit_commercial=3000,
            operating_expense_ratio=0.4,
            vacancy_rate=0.05,
            rent_growth_rate=0.5,  # Extreme 50% rent growth
            expense_growth_rate=0.3,  # Extreme 30% expense growth
            property_appreciation_rate=0.2,  # Extreme 20% appreciation
            cap_rate_terminal=0.04,
            discount_rate=0.08,
            ltv_ratio=0.8,
            interest_rate=0.06,
            loan_term_years=30,
            closing_costs=25000,
            lender_reserves=40000,
        )

        initial_numbers = InitialNumbers(
            purchase_price=1000000,
            renovation_cost=200000,
            total_project_cost=1240000,
            loan_amount=800000,
            total_equity_required=440000,
            annual_debt_service=57600,
            residential_units=5,
            commercial_units=2,
            renovation_period_months=4,
            annual_rent_residential=10000,
            annual_rent_commercial=6000,
            total_annual_rent=16000,
            operating_expenses=6400,
            net_operating_income=9600,
            debt_service_coverage_ratio=0.17,
            after_repair_value=1400000,
            ltv_ratio=0.57,
            cash_on_cash_return=0.045,
        )

        # Should handle extreme growth rates
        projection = service.calculate_cash_flow_projection(
            assumptions, initial_numbers
        )

        assert projection is not None
        # Rental income should grow dramatically
        year_1_income = projection.annual_cash_flows[0].total_rental_income
        year_6_income = projection.annual_cash_flows[5].total_rental_income

        # With 50% annual growth, income should multiply significantly
        assert year_6_income > year_1_income * 10


class TestFinancialMetricsEdgeCases:
    """Test financial metrics edge cases and error scenarios."""

    def test_calculate_metrics_with_all_negative_cash_flows(self):
        """Test metrics calculation with all negative cash flows."""
        service = FinancialMetricsService(Mock())

        # Create projection with all negative cash flows
        negative_cash_flows = []
        for year in range(1, 7):
            annual_cf = AnnualCashFlow(
                year=year,
                total_rental_income=50000,
                operating_expenses=80000,
                net_operating_income=-30000,
                debt_service=40000,
                before_tax_cash_flow=-70000,
                principal_paydown=5000,
                depreciation=20000,
                taxable_income=-90000,
                tax_benefit=25000,
                after_tax_cash_flow=-45000,
            )
            negative_cash_flows.append(annual_cf)

        projection = CashFlowProjection(
            property_id="test_property",
            assumptions_id="test_assumptions",
            annual_cash_flows=negative_cash_flows,
            terminal_value=800000,  # Still positive terminal value
            total_return=200000,
        )

        initial_numbers = InitialNumbers(
            purchase_price=1000000,
            renovation_cost=200000,
            total_project_cost=1200000,
            loan_amount=800000,
            total_equity_required=400000,
            annual_debt_service=60000,
            residential_units=10,
            commercial_units=0,
            renovation_period_months=6,
            annual_rent_residential=50000,
            annual_rent_commercial=0,
            total_annual_rent=50000,
            operating_expenses=80000,
            net_operating_income=-30000,
            debt_service_coverage_ratio=-0.5,
            after_repair_value=1200000,
            ltv_ratio=0.67,
            cash_on_cash_return=-0.175,
        )

        # Should handle all negative cash flows
        metrics = service.calculate_financial_metrics(projection, initial_numbers)

        assert metrics is not None
        assert metrics.net_present_value < 0  # Should be negative
        assert metrics.internal_rate_of_return < 0  # Should be negative
        assert metrics.investment_recommendation == "AVOID"

    def test_calculate_metrics_with_zero_terminal_value(self):
        """Test metrics calculation with zero terminal value."""
        service = FinancialMetricsService(Mock())

        # Create projection with zero terminal value
        cash_flows = []
        for year in range(1, 7):
            annual_cf = AnnualCashFlow(
                year=year,
                total_rental_income=100000,
                operating_expenses=40000,
                net_operating_income=60000,
                debt_service=45000,
                before_tax_cash_flow=15000,
                principal_paydown=5000,
                depreciation=20000,
                taxable_income=-5000,
                tax_benefit=1500,
                after_tax_cash_flow=16500,
            )
            cash_flows.append(annual_cf)

        projection = CashFlowProjection(
            property_id="test_property",
            assumptions_id="test_assumptions",
            annual_cash_flows=cash_flows,
            terminal_value=0,  # Zero terminal value
            total_return=99000,
        )

        initial_numbers = InitialNumbers(
            purchase_price=1000000,
            renovation_cost=200000,
            total_project_cost=1200000,
            loan_amount=800000,
            total_equity_required=400000,
            annual_debt_service=45000,
            residential_units=10,
            commercial_units=0,
            renovation_period_months=6,
            annual_rent_residential=100000,
            annual_rent_commercial=0,
            total_annual_rent=100000,
            operating_expenses=40000,
            net_operating_income=60000,
            debt_service_coverage_ratio=1.33,
            after_repair_value=1200000,
            ltv_ratio=0.67,
            cash_on_cash_return=0.04,
        )

        # Should handle zero terminal value
        metrics = service.calculate_financial_metrics(projection, initial_numbers)

        assert metrics is not None
        assert metrics.terminal_value.terminal_cash_flow == 0
        # NPV should be lower due to no terminal value
        assert metrics.net_present_value < 100000

    def test_calculate_irr_with_no_sign_changes(self):
        """Test IRR calculation with cash flows that have no sign changes."""
        service = FinancialMetricsService(Mock())

        # All positive cash flows (no initial investment represented)
        cash_flows = []
        for year in range(1, 7):
            annual_cf = AnnualCashFlow(
                year=year,
                total_rental_income=100000,
                operating_expenses=30000,
                net_operating_income=70000,
                debt_service=0,  # No debt
                before_tax_cash_flow=70000,
                principal_paydown=0,
                depreciation=20000,
                taxable_income=50000,
                tax_benefit=0,
                after_tax_cash_flow=70000,
            )
            cash_flows.append(annual_cf)

        projection = CashFlowProjection(
            property_id="test_property",
            assumptions_id="test_assumptions",
            annual_cash_flows=cash_flows,
            terminal_value=1500000,
            total_return=1920000,
        )

        initial_numbers = InitialNumbers(
            purchase_price=0,  # No initial investment
            renovation_cost=0,
            total_project_cost=0,
            loan_amount=0,
            total_equity_required=0,
            annual_debt_service=0,
            residential_units=10,
            commercial_units=0,
            renovation_period_months=0,
            annual_rent_residential=100000,
            annual_rent_commercial=0,
            total_annual_rent=100000,
            operating_expenses=30000,
            net_operating_income=70000,
            debt_service_coverage_ratio=float("inf"),
            after_repair_value=1500000,
            ltv_ratio=0,
            cash_on_cash_return=float("inf"),
        )

        # Should handle case with no initial investment (infinite IRR)
        metrics = service.calculate_financial_metrics(projection, initial_numbers)

        assert metrics is not None
        # IRR should be very high or infinite
        assert metrics.internal_rate_of_return > 1.0  # More than 100%


class TestInitialNumbersEdgeCases:
    """Test initial numbers calculation edge cases."""

    def test_calculate_with_zero_purchase_price_should_raise_error(self):
        """Test calculation with zero purchase price."""
        service = InitialNumbersService(Mock())

        property_input = SimplifiedPropertyInput(
            purchase_price=0,  # Zero price
            renovation_cost=100000,
            residential_units=5,
            commercial_units=0,
            renovation_period_months=6,
            annual_rent_per_unit_residential=2000,
            annual_rent_per_unit_commercial=0,
            equity_split_percentage=0.8,
            cash_percentage=0.3,
        )

        assumptions = DCFAssumptions(
            purchase_price=0,
            renovation_cost=100000,
            annual_rent_per_unit_residential=2000,
            annual_rent_per_unit_commercial=0,
            operating_expense_ratio=0.4,
            vacancy_rate=0.05,
            rent_growth_rate=0.03,
            expense_growth_rate=0.02,
            property_appreciation_rate=0.03,
            cap_rate_terminal=0.06,
            discount_rate=0.10,
            ltv_ratio=0.75,
            interest_rate=0.05,
            loan_term_years=30,
            closing_costs=0,
            lender_reserves=0,
        )

        # Should raise validation error for zero purchase price
        with pytest.raises(ValidationError) as exc_info:
            service.calculate_initial_numbers(property_input, assumptions)

        assert "purchase price" in str(exc_info.value).lower()

    def test_calculate_with_extreme_ltv_ratio(self):
        """Test calculation with extreme LTV ratio."""
        service = InitialNumbersService(Mock())

        property_input = SimplifiedPropertyInput(
            purchase_price=1000000,
            renovation_cost=200000,
            residential_units=10,
            commercial_units=0,
            renovation_period_months=6,
            annual_rent_per_unit_residential=2000,
            annual_rent_per_unit_commercial=0,
            equity_split_percentage=0.8,
            cash_percentage=0.3,
        )

        assumptions = DCFAssumptions(
            purchase_price=1000000,
            renovation_cost=200000,
            annual_rent_per_unit_residential=2000,
            annual_rent_per_unit_commercial=0,
            operating_expense_ratio=0.4,
            vacancy_rate=0.05,
            rent_growth_rate=0.03,
            expense_growth_rate=0.02,
            property_appreciation_rate=0.03,
            cap_rate_terminal=0.06,
            discount_rate=0.10,
            ltv_ratio=1.5,  # 150% LTV - extreme leverage
            interest_rate=0.05,
            loan_term_years=30,
            closing_costs=25000,
            lender_reserves=40000,
        )

        # Should handle extreme LTV but flag as high risk
        initial_numbers = service.calculate_initial_numbers(property_input, assumptions)

        assert initial_numbers is not None
        assert initial_numbers.ltv_ratio > 1.0  # Over-leveraged

        # Validation should flag this as problematic
        issues = service.validate_initial_numbers(initial_numbers)
        assert len(issues) > 0
        assert any("ltv" in issue.lower() for issue in issues)

    def test_calculate_with_negative_after_repair_value(self):
        """Test calculation resulting in negative after-repair value."""
        service = InitialNumbersService(Mock())

        property_input = SimplifiedPropertyInput(
            purchase_price=1000000,
            renovation_cost=200000,
            residential_units=2,  # Very few units
            commercial_units=0,
            renovation_period_months=12,  # Long renovation
            annual_rent_per_unit_residential=500,  # Very low rent
            annual_rent_per_unit_commercial=0,
            equity_split_percentage=0.8,
            cash_percentage=0.3,
        )

        assumptions = DCFAssumptions(
            purchase_price=1000000,
            renovation_cost=200000,
            annual_rent_per_unit_residential=500,
            annual_rent_per_unit_commercial=0,
            operating_expense_ratio=0.8,  # Very high expenses
            vacancy_rate=0.3,  # High vacancy
            rent_growth_rate=0.01,
            expense_growth_rate=0.05,
            property_appreciation_rate=0.01,
            cap_rate_terminal=0.15,  # Very high cap rate (low value)
            discount_rate=0.12,
            ltv_ratio=0.8,
            interest_rate=0.08,
            loan_term_years=30,
            closing_costs=50000,
            lender_reserves=100000,
        )

        # Should handle scenario where ARV might be very low
        initial_numbers = service.calculate_initial_numbers(property_input, assumptions)

        assert initial_numbers is not None
        # NOI should be very low or negative
        assert initial_numbers.net_operating_income < 5000

        # After-repair value should be very low
        assert initial_numbers.after_repair_value < initial_numbers.total_project_cost


class TestDCFAssumptionsEdgeCases:
    """Test DCF assumptions edge cases."""

    def test_create_assumptions_with_missing_parameters(self):
        """Test creating assumptions with missing Monte Carlo parameters."""
        service = DCFAssumptionsService(Mock())

        # Incomplete Monte Carlo scenario (missing some parameters)
        incomplete_scenario = MonteCarloScenario(
            scenario_id="incomplete_scenario",
            parameters={
                "treasury_10y": [0.03, 0.035, 0.04],
                "commercial_mortgage_rate": [0.05, 0.055, 0.06],
                # Missing other required parameters
            },
            market_classification="neutral",
            growth_score=0.5,
            risk_score=0.5,
        )

        property_input = SimplifiedPropertyInput(
            purchase_price=1000000,
            renovation_cost=200000,
            residential_units=10,
            commercial_units=2,
            renovation_period_months=6,
            annual_rent_per_unit_residential=2000,
            annual_rent_per_unit_commercial=3000,
            equity_split_percentage=0.8,
            cash_percentage=0.3,
        )

        # Should raise ValidationError for missing parameters
        with pytest.raises(ValidationError) as exc_info:
            service.create_dcf_assumptions_from_scenario(
                incomplete_scenario, property_input
            )

        assert "missing" in str(exc_info.value).lower()

    def test_create_assumptions_with_invalid_parameter_values(self):
        """Test creating assumptions with invalid parameter values."""
        service = DCFAssumptionsService(Mock())

        # Monte Carlo scenario with invalid values
        invalid_scenario = MonteCarloScenario(
            scenario_id="invalid_scenario",
            parameters={
                "treasury_10y": [-0.1, -0.05, 0.0],  # Negative rates
                "commercial_mortgage_rate": [0.0, 0.005, 0.01],  # Very low rates
                "cap_rate": [0.0, 0.01, 0.02],  # Very low cap rates
                "vacancy_rate": [0.8, 0.9, 1.0],  # Very high vacancy
                "rental_growth": [-0.5, -0.3, -0.1],  # Negative growth
                "expense_growth": [0.5, 0.6, 0.7],  # Very high expense growth
                "property_appreciation": [-0.2, -0.1, 0.0],  # Negative appreciation
                "ltv_ratio": [1.2, 1.5, 2.0],  # Extreme leverage
                "closing_cost_percentage": [0.2, 0.3, 0.4],  # Very high closing costs
                "lender_reserves_months": [24, 36, 48],  # Very high reserves
                "operating_expense_ratio": [0.9, 0.95, 1.0],  # Very high expense ratios
            },
            market_classification="stress",
            growth_score=0.1,
            risk_score=0.9,
        )

        property_input = SimplifiedPropertyInput(
            purchase_price=1000000,
            renovation_cost=200000,
            residential_units=10,
            commercial_units=2,
            renovation_period_months=6,
            annual_rent_per_unit_residential=2000,
            annual_rent_per_unit_commercial=3000,
            equity_split_percentage=0.8,
            cash_percentage=0.3,
        )

        # Should handle extreme values but may generate warnings
        assumptions = service.create_dcf_assumptions_from_scenario(
            invalid_scenario, property_input
        )

        assert assumptions is not None
        # Some values should be clamped to reasonable ranges
        assert assumptions.cap_rate_terminal > 0.01  # Should be positive
        assert assumptions.ltv_ratio <= 1.0  # Should be clamped to reasonable max

        # Compatibility validation should flag issues
        issues = service.validate_assumptions_compatibility(assumptions)
        assert len(issues) > 0
