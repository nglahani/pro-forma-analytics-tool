"""
Initial Numbers Coverage Tests

Strategic tests to improve coverage of initial numbers entities.
"""

from datetime import date

import pytest

from core.exceptions import ValidationError
from src.domain.entities.initial_numbers import InitialNumbers


class TestInitialNumbersEntitiesCoverage:
    """Strategic tests for Initial Numbers entities to improve coverage."""

    def test_initial_numbers_creation_with_minimal_required_values(self):
        """Test InitialNumbers creation with minimal required values."""
        initial_numbers = InitialNumbers(
            property_id="PROP_TEST_001",
            scenario_id="SCENARIO_001",
            purchase_price=100000.0,  # Required positive value
            cost_basis=100000.0,  # Required positive value
            total_cash_required=100000.0,  # Required positive value
            investor_cash_required=90000.0,  # 90% investor
            operator_cash_required=10000.0,  # 10% operator
        )

        assert initial_numbers.property_id == "PROP_TEST_001"
        assert initial_numbers.scenario_id == "SCENARIO_001"
        assert initial_numbers.calculation_date == date.today()

        # Test required financial fields
        assert initial_numbers.purchase_price == 100000.0
        assert initial_numbers.cost_basis == 100000.0
        assert initial_numbers.total_cash_required == 100000.0

        # Test default values for optional fields
        assert initial_numbers.closing_cost_amount == 0.0
        assert initial_numbers.renovation_capex == 0.0
        assert initial_numbers.loan_amount == 0.0
        assert initial_numbers.annual_interest_expense == 0.0
        assert initial_numbers.lender_reserves_amount == 0.0

    def test_initial_numbers_with_all_fields_populated(self):
        """Test InitialNumbers with all fields populated."""
        test_date = date(2024, 3, 15)

        initial_numbers = InitialNumbers(
            property_id="PROP_FULL_001",
            scenario_id="FULL_SCENARIO_001",
            calculation_date=test_date,
            purchase_price=2500000.0,
            closing_cost_amount=125000.0,
            renovation_capex=400000.0,
            cost_basis=3025000.0,
            loan_amount=1875000.0,  # 75% LTV
            annual_interest_expense=121875.0,  # 6.5% interest
            lender_reserves_amount=18750.0,  # 1% of loan
            investor_cash_required=500000.0,
            operator_cash_required=150000.0,
            total_cash_required=650000.0,
            after_repair_value=3500000.0,
            initial_cap_rate=0.065,
            pre_renovation_annual_rent=180000.0,
            post_renovation_annual_rent=227500.0,
            year_1_rental_income=0.0,  # Due to renovation period
        )

        # Test all populated values
        assert initial_numbers.property_id == "PROP_FULL_001"
        assert initial_numbers.scenario_id == "FULL_SCENARIO_001"
        assert initial_numbers.calculation_date == test_date
        assert initial_numbers.purchase_price == 2500000.0
        assert initial_numbers.closing_cost_amount == 125000.0
        assert initial_numbers.renovation_capex == 400000.0
        assert initial_numbers.cost_basis == 3025000.0
        assert initial_numbers.loan_amount == 1875000.0
        assert initial_numbers.annual_interest_expense == 121875.0
        assert initial_numbers.lender_reserves_amount == 18750.0
        assert initial_numbers.investor_cash_required == 500000.0
        assert initial_numbers.operator_cash_required == 150000.0
        assert initial_numbers.total_cash_required == 650000.0
        assert initial_numbers.after_repair_value == 3500000.0
        assert initial_numbers.initial_cap_rate == 0.065
        assert initial_numbers.pre_renovation_annual_rent == 180000.0
        assert initial_numbers.post_renovation_annual_rent == 227500.0
        assert initial_numbers.year_1_rental_income == 0.0

    def test_initial_numbers_property_acquisition_scenario(self):
        """Test realistic property acquisition scenario."""
        initial_numbers = InitialNumbers(
            property_id="NYC_MULTIFAMILY_001",
            scenario_id="BULL_MARKET_2024",
            purchase_price=4500000.0,
            closing_cost_amount=225000.0,  # 5% closing costs
            renovation_capex=800000.0,  # Major renovation
            cost_basis=5525000.0,  # Total project cost
            loan_amount=3375000.0,  # 75% LTV on purchase
            annual_interest_expense=236250.0,  # 7% interest rate
            lender_reserves_amount=202500.0,  # 6 months reserves
            investor_cash_required=1800000.0,
            operator_cash_required=350000.0,
            total_cash_required=2150000.0,
            after_repair_value=6200000.0,  # Significant value-add
            initial_cap_rate=0.058,
            pre_renovation_annual_rent=400000.0,
            post_renovation_annual_rent=580000.0,
            year_1_rental_income=290000.0,  # Partial renovation impact
        )

        # Test business logic consistency
        total_acquisition = (
            initial_numbers.purchase_price + initial_numbers.closing_cost_amount
        )
        assert total_acquisition == 4725000.0

        # Test LTV calculation
        ltv_ratio = initial_numbers.loan_amount / initial_numbers.purchase_price
        assert ltv_ratio == 0.75  # 75% LTV

        # Test cash requirement calculation
        cash_for_acquisition = total_acquisition - initial_numbers.loan_amount
        # Additional cash for renovation and reserves
        total_cash_estimate = (
            cash_for_acquisition
            + initial_numbers.renovation_capex
            + initial_numbers.lender_reserves_amount
        )
        # Should be close to total_cash_required (allowing for some operational cash buffer)
        assert abs(total_cash_estimate - initial_numbers.total_cash_required) < 500000

    def test_initial_numbers_minimal_cash_deal(self):
        """Test all-cash deal scenario."""
        initial_numbers = InitialNumbers(
            property_id="CASH_DEAL_001",
            scenario_id="LOW_LEVERAGE_001",
            purchase_price=1000000.0,
            closing_cost_amount=40000.0,
            renovation_capex=0.0,  # No renovation needed
            cost_basis=1040000.0,
            loan_amount=0.0,  # All cash
            annual_interest_expense=0.0,  # No loan, no interest
            lender_reserves_amount=0.0,  # No loan, no reserves
            investor_cash_required=936000.0,  # 90% investor contribution
            operator_cash_required=104000.0,  # 10% operator contribution
            total_cash_required=1040000.0,
            after_repair_value=1000000.0,  # No value-add
            initial_cap_rate=0.055,
            pre_renovation_annual_rent=65000.0,
            post_renovation_annual_rent=65000.0,  # Same rent
            year_1_rental_income=65000.0,  # Full rent from day 1
        )

        # Test all-cash scenario
        assert initial_numbers.loan_amount == 0.0
        assert initial_numbers.annual_interest_expense == 0.0
        assert initial_numbers.lender_reserves_amount == 0.0

        # Test equity split
        total_equity = (
            initial_numbers.investor_cash_required
            + initial_numbers.operator_cash_required
        )
        assert total_equity == initial_numbers.total_cash_required

        # Test cap rate calculation
        implied_cap_rate = (
            initial_numbers.year_1_rental_income / initial_numbers.purchase_price
        )
        assert implied_cap_rate == 0.065  # 6.5% cap rate

    def test_initial_numbers_value_add_scenario(self):
        """Test heavy value-add renovation scenario."""
        initial_numbers = InitialNumbers(
            property_id="VALUE_ADD_001",
            scenario_id="HEAVY_RENOVATION_001",
            purchase_price=1800000.0,
            closing_cost_amount=90000.0,
            renovation_capex=1200000.0,  # Heavy renovation
            cost_basis=3090000.0,
            loan_amount=1350000.0,  # 75% of purchase
            annual_interest_expense=94500.0,  # 7% interest
            lender_reserves_amount=81000.0,  # 6 months P&I reserves
            investor_cash_required=1400000.0,
            operator_cash_required=340000.0,
            total_cash_required=1740000.0,
            after_repair_value=4200000.0,  # Significant upside
            initial_cap_rate=0.062,
            pre_renovation_annual_rent=120000.0,  # Low rent
            post_renovation_annual_rent=275000.0,  # Significant rent bump
            year_1_rental_income=45000.0,  # Limited income during reno
        )

        # Test value-add economics
        value_creation = initial_numbers.after_repair_value - initial_numbers.cost_basis
        assert value_creation == 1110000.0  # Significant value creation

        # Test rent growth from renovation
        rent_increase = (
            initial_numbers.post_renovation_annual_rent
            - initial_numbers.pre_renovation_annual_rent
        )
        assert rent_increase == 155000.0  # 129% rent increase

        # Test renovation impact on Year 1 income
        renovation_income_impact = (
            initial_numbers.year_1_rental_income
            / initial_numbers.post_renovation_annual_rent
        )
        assert renovation_income_impact < 0.2  # Less than 20% of full rent in Year 1

    def test_initial_numbers_string_representation(self):
        """Test string representation of InitialNumbers."""
        initial_numbers = InitialNumbers(
            property_id="STRING_TEST_001",
            scenario_id="STRING_SCENARIO",
            purchase_price=2000000.0,
            cost_basis=2000000.0,
            total_cash_required=500000.0,
            investor_cash_required=450000.0,  # 90% investor
            operator_cash_required=50000.0,  # 10% operator
        )

        str_repr = str(initial_numbers)
        assert "STRING_TEST_001" in str_repr
        assert "STRING_SCENARIO" in str_repr
        # Should contain key financial figures
        assert "2000000" in str_repr or "$2,000,000" in str_repr

    def test_initial_numbers_data_consistency_checks(self):
        """Test data consistency and business rule validation."""
        # Create realistic but potentially inconsistent data
        initial_numbers = InitialNumbers(
            property_id="CONSISTENCY_TEST",
            scenario_id="VALIDATION_SCENARIO",
            purchase_price=3000000.0,
            closing_cost_amount=150000.0,
            renovation_capex=500000.0,
            cost_basis=3650000.0,  # Should equal purchase + closing + renovation
            loan_amount=2250000.0,  # 75% LTV
            total_cash_required=1400000.0,  # Should roughly match cash needs
            investor_cash_required=1260000.0,  # 90% of total cash
            operator_cash_required=140000.0,  # 10% of total cash
            after_repair_value=4500000.0,
            pre_renovation_annual_rent=220000.0,
            post_renovation_annual_rent=315000.0,
        )

        # Test cost basis consistency
        expected_cost_basis = (
            initial_numbers.purchase_price
            + initial_numbers.closing_cost_amount
            + initial_numbers.renovation_capex
        )
        assert initial_numbers.cost_basis == expected_cost_basis

        # Test that after-repair value exceeds cost basis (value creation)
        assert initial_numbers.after_repair_value > initial_numbers.cost_basis

        # Test that post-renovation rent exceeds pre-renovation rent
        assert (
            initial_numbers.post_renovation_annual_rent
            > initial_numbers.pre_renovation_annual_rent
        )

    def test_initial_numbers_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Test with very small amounts
        small_deal = InitialNumbers(
            property_id="SMALL_DEAL",
            scenario_id="MINIMUM_VIABLE",
            purchase_price=50000.0,  # Very small property
            closing_cost_amount=2500.0,  # 5% closing
            cost_basis=52500.0,  # Purchase + closing
            total_cash_required=52500.0,  # All cash small deal
            investor_cash_required=47250.0,  # 90% investor
            operator_cash_required=5250.0,  # 10% operator
            pre_renovation_annual_rent=6000.0,  # $500/month
            post_renovation_annual_rent=6000.0,
        )

        assert small_deal.purchase_price == 50000.0
        assert small_deal.loan_amount == 0.0  # Assume all cash for small deal

        # Test with very large amounts
        large_deal = InitialNumbers(
            property_id="LARGE_DEAL",
            scenario_id="INSTITUTIONAL_SIZE",
            purchase_price=100000000.0,  # $100M deal
            closing_cost_amount=3000000.0,  # 3% closing
            cost_basis=103000000.0,  # Purchase + closing
            loan_amount=75000000.0,  # 75% LTV
            total_cash_required=28000000.0,  # Large equity check
            investor_cash_required=25200000.0,  # 90% investor
            operator_cash_required=2800000.0,  # 10% operator
        )

        assert large_deal.purchase_price == 100000000.0
        assert large_deal.loan_amount == 75000000.0

    def test_initial_numbers_validation_errors(self):
        """Test comprehensive validation error scenarios."""
        # Test empty property_id
        with pytest.raises(ValidationError, match="Property ID is required"):
            InitialNumbers(
                property_id="",
                scenario_id="TEST",
                purchase_price=1000000,
                cost_basis=1000000,
                total_cash_required=1000000,
                investor_cash_required=900000,
                operator_cash_required=100000,
            )

        # Test empty scenario_id
        with pytest.raises(ValidationError, match="Scenario ID is required"):
            InitialNumbers(
                property_id="TEST",
                scenario_id="",
                purchase_price=1000000,
                cost_basis=1000000,
                total_cash_required=1000000,
                investor_cash_required=900000,
                operator_cash_required=100000,
            )

        # Test negative purchase price
        with pytest.raises(ValidationError, match="Purchase price must be positive"):
            InitialNumbers(
                property_id="TEST",
                scenario_id="TEST",
                purchase_price=-1000000,
                cost_basis=1000000,
                total_cash_required=1000000,
                investor_cash_required=900000,
                operator_cash_required=100000,
            )

        # Test negative closing costs
        with pytest.raises(ValidationError, match="Closing costs cannot be negative"):
            InitialNumbers(
                property_id="TEST",
                scenario_id="TEST",
                purchase_price=1000000,
                closing_cost_amount=-50000,
                cost_basis=1000000,
                total_cash_required=1000000,
                investor_cash_required=900000,
                operator_cash_required=100000,
            )

        # Test negative renovation capex
        with pytest.raises(
            ValidationError, match="Renovation CapEx cannot be negative"
        ):
            InitialNumbers(
                property_id="TEST",
                scenario_id="TEST",
                purchase_price=1000000,
                renovation_capex=-200000,
                cost_basis=1000000,
                total_cash_required=1000000,
                investor_cash_required=900000,
                operator_cash_required=100000,
            )

        # Test cost basis mismatch
        with pytest.raises(
            ValidationError, match="Cost basis.*doesn't match expected calculation"
        ):
            InitialNumbers(
                property_id="TEST",
                scenario_id="TEST",
                purchase_price=1000000,
                closing_cost_amount=50000,
                renovation_capex=200000,
                cost_basis=2000000,  # Wrong calculation
                total_cash_required=1000000,
                investor_cash_required=900000,
                operator_cash_required=100000,
            )

        # Test loan amount exceeds purchase price
        with pytest.raises(
            ValidationError, match="Loan amount cannot exceed purchase price"
        ):
            InitialNumbers(
                property_id="TEST",
                scenario_id="TEST",
                purchase_price=1000000,
                cost_basis=1000000,
                loan_amount=1500000,  # 150% LTV
                total_cash_required=1000000,
                investor_cash_required=900000,
                operator_cash_required=100000,
            )

        # Test negative interest expense
        with pytest.raises(
            ValidationError, match="Annual interest expense cannot be negative"
        ):
            InitialNumbers(
                property_id="TEST",
                scenario_id="TEST",
                purchase_price=1000000,
                cost_basis=1000000,
                annual_interest_expense=-50000,
                total_cash_required=1000000,
                investor_cash_required=900000,
                operator_cash_required=100000,
            )

        # Test invalid investor equity share
        with pytest.raises(
            ValidationError, match="Investor equity share must be between 0% and 100%"
        ):
            InitialNumbers(
                property_id="TEST",
                scenario_id="TEST",
                purchase_price=1000000,
                cost_basis=1000000,
                total_cash_required=1000000,
                investor_cash_required=900000,
                operator_cash_required=100000,
                investor_equity_share=1.5,  # 150%
            )

    def test_initial_numbers_calculation_methods(self):
        """Test calculation methods and edge cases."""
        initial_numbers = InitialNumbers(
            property_id="CALC_TEST",
            scenario_id="CALC_SCENARIO",
            purchase_price=2000000,
            cost_basis=2000000,
            loan_amount=1500000,  # 75% LTV
            annual_interest_expense=105000,  # 7% interest
            total_cash_required=500000,
            investor_cash_required=450000,
            operator_cash_required=50000,
            year_1_rental_income=200000,
            # Operating expense components that add up to 80000
            property_taxes=25000,
            insurance=8000,
            repairs_maintenance=15000,
            property_management=12000,
            admin_expenses=5000,
            contracting=10000,
            replacement_reserves=5000,
            total_operating_expenses=80000,
            post_renovation_annual_rent=220000,
        )

        # Test LTV calculation
        ltv = initial_numbers.calculate_ltv_ratio()
        assert ltv == 0.75

        # Test debt service coverage ratio
        dscr = initial_numbers.calculate_debt_service_coverage_ratio()
        expected_noi = 200000 - 80000  # 120000
        expected_dscr = 120000 / 105000
        assert dscr == pytest.approx(expected_dscr, rel=0.01)

        # Test cash on cash return
        cocr = initial_numbers.calculate_cash_on_cash_return()
        cash_flow = 120000 - 105000  # NOI - debt service = 15000
        expected_cocr = 15000 / 500000
        assert cocr == pytest.approx(expected_cocr, rel=0.01)

        # Test price per unit calculation
        price_per_unit = initial_numbers.calculate_price_per_unit(20)
        assert price_per_unit == 100000  # 2M / 20 units

        # Test gross rent multiplier
        grm = initial_numbers.calculate_gross_rent_multiplier()
        assert grm == pytest.approx(2000000 / 220000, rel=0.01)

        # Test edge case: zero units
        zero_unit_price = initial_numbers.calculate_price_per_unit(0)
        assert zero_unit_price == 0.0

        # Test edge case: zero interest (all cash deal)
        cash_deal = InitialNumbers(
            property_id="CASH_TEST",
            scenario_id="CASH",
            purchase_price=1000000,
            cost_basis=1000000,
            annual_interest_expense=0,  # No debt
            total_cash_required=1000000,
            investor_cash_required=900000,
            operator_cash_required=100000,
            year_1_rental_income=80000,
            # Operating expense components that add up to 30000
            property_taxes=10000,
            insurance=5000,
            repairs_maintenance=8000,
            property_management=4000,
            admin_expenses=2000,
            contracting=1000,
            replacement_reserves=0,
            total_operating_expenses=30000,
        )

        dscr_cash = cash_deal.calculate_debt_service_coverage_ratio()
        assert dscr_cash == float("inf")  # No debt service
