"""
Unit tests for Cash Flow Projection functionality.

Tests the calculation of annual cash flows and waterfall distributions.
"""

import pytest

from core.exceptions import ValidationError
from src.application.services.cash_flow_projection_service import (
    CashFlowProjectionService,
)
from src.domain.entities.cash_flow_projection import (
    AnnualCashFlow,
    CashFlowProjection,
    WaterfallDistribution,
)
from src.domain.entities.dcf_assumptions import DCFAssumptions
from src.domain.entities.initial_numbers import InitialNumbers


class TestAnnualCashFlow:
    """Test Annual Cash Flow entity."""

    def test_annual_cash_flow_creation(self):
        """Test basic annual cash flow creation."""
        cash_flow = AnnualCashFlow(
            year=1,
            gross_rental_income=100000,
            vacancy_loss=5000,
            effective_gross_income=95000,
            property_taxes=12000,
            insurance=2000,
            repairs_maintenance=3000,
            property_management=5000,
            admin_expenses=1000,
            contracting=2000,
            replacement_reserves=1500,
            total_operating_expenses=26500,
            net_operating_income=68500,
            annual_debt_service=40000,
            before_tax_cash_flow=28500,
            capital_expenditures=0,
            net_cash_flow=28500,
        )

        assert cash_flow.year == 1
        assert cash_flow.gross_rental_income == 100000
        assert cash_flow.net_operating_income == 68500
        assert cash_flow.net_cash_flow == 28500

    def test_income_calculation_validation(self):
        """Test validation of income calculations."""
        with pytest.raises(ValidationError):
            # Effective gross income doesn't match calculation
            AnnualCashFlow(
                year=1,
                gross_rental_income=100000,
                vacancy_loss=5000,
                effective_gross_income=90000,  # Should be 95000
                total_operating_expenses=25000,
                net_operating_income=65000,
                annual_debt_service=40000,
                before_tax_cash_flow=25000,
                net_cash_flow=25000,
            )

    def test_expense_calculation_validation(self):
        """Test validation of expense calculations."""
        with pytest.raises(ValidationError):
            # Total expenses don't match components
            AnnualCashFlow(
                year=1,
                gross_rental_income=100000,
                vacancy_loss=5000,
                effective_gross_income=95000,
                property_taxes=12000,
                insurance=2000,
                repairs_maintenance=3000,
                property_management=5000,
                admin_expenses=1000,
                contracting=2000,
                replacement_reserves=1500,
                total_operating_expenses=30000,  # Should be 26500
                net_operating_income=65000,
                annual_debt_service=40000,
                before_tax_cash_flow=25000,
                net_cash_flow=25000,
            )

    def test_invalid_year(self):
        """Test validation of invalid year."""
        with pytest.raises(ValidationError):
            AnnualCashFlow(
                year=10,  # Invalid: must be 0-5
                gross_rental_income=100000,
                vacancy_loss=5000,
                effective_gross_income=95000,
                total_operating_expenses=25000,
                net_operating_income=70000,
                annual_debt_service=40000,
                before_tax_cash_flow=30000,
                net_cash_flow=30000,
            )


class TestWaterfallDistribution:
    """Test Waterfall Distribution entity."""

    def test_waterfall_distribution_creation(self):
        """Test basic waterfall distribution creation."""
        distribution = WaterfallDistribution(
            year=1,
            available_cash=25000,
            investor_preferred_return_due=12000,
            investor_preferred_return_paid=12000,
            investor_preferred_return_accrued=0,
            cumulative_unpaid_preferred=0,
            investor_cash_distribution=22000,
            operator_cash_distribution=3000,
            total_cash_distributed=25000,
            remaining_cash=0,
        )

        assert distribution.year == 1
        assert distribution.available_cash == 25000
        assert distribution.total_cash_distributed == 25000
        assert distribution.remaining_cash == 0

    def test_distribution_calculation_validation(self):
        """Test validation of distribution calculations."""
        with pytest.raises(ValidationError):
            # Total distributed doesn't match sum
            WaterfallDistribution(
                year=1,
                available_cash=25000,
                investor_preferred_return_due=12000,
                investor_preferred_return_paid=12000,
                investor_preferred_return_accrued=0,
                cumulative_unpaid_preferred=0,
                investor_cash_distribution=20000,
                operator_cash_distribution=3000,
                total_cash_distributed=25000,  # Should be 23000
                remaining_cash=2000,
            )

    def test_negative_amounts_validation(self):
        """Test validation of negative amounts."""
        with pytest.raises(ValidationError):
            WaterfallDistribution(
                year=1,
                available_cash=-5000,  # Negative not allowed
                investor_preferred_return_due=12000,
                investor_preferred_return_paid=0,
                investor_preferred_return_accrued=12000,
                cumulative_unpaid_preferred=12000,
                investor_cash_distribution=0,
                operator_cash_distribution=0,
                total_cash_distributed=0,
                remaining_cash=0,
            )


class TestCashFlowProjection:
    """Test Cash Flow Projection entity."""

    def create_sample_cash_flows(self) -> list:
        """Create sample cash flows for testing."""
        cash_flows = []
        for year in range(6):
            if year == 0:
                # Year 0: No income, renovation expenses
                cash_flow = AnnualCashFlow(
                    year=year,
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
                    capital_expenditures=100000,
                    net_cash_flow=-100000,
                )
            else:
                # Years 1-5: Operating cash flows
                gross_income = 100000 * (1.03**year)
                vacancy = 5000 * (1.03**year)
                effective_income = gross_income - vacancy

                # Individual expense components
                property_taxes = 12000 * (1.02**year)
                insurance = 2000 * (1.02**year)
                repairs_maintenance = 3000 * (1.02**year)
                property_management = 5000 * (1.02**year)
                admin_expenses = 1000 * (1.02**year)
                contracting = 1500 * (1.02**year)
                replacement_reserves = 1500 * (1.02**year)
                total_expenses = (
                    property_taxes
                    + insurance
                    + repairs_maintenance
                    + property_management
                    + admin_expenses
                    + contracting
                    + replacement_reserves
                )

                noi = effective_income - total_expenses
                debt_service = 40000
                btcf = noi - debt_service

                cash_flow = AnnualCashFlow(
                    year=year,
                    gross_rental_income=gross_income,
                    vacancy_loss=vacancy,
                    effective_gross_income=effective_income,
                    property_taxes=property_taxes,
                    insurance=insurance,
                    repairs_maintenance=repairs_maintenance,
                    property_management=property_management,
                    admin_expenses=admin_expenses,
                    contracting=contracting,
                    replacement_reserves=replacement_reserves,
                    total_operating_expenses=total_expenses,
                    net_operating_income=noi,
                    annual_debt_service=debt_service,
                    before_tax_cash_flow=btcf,
                    capital_expenditures=0,
                    net_cash_flow=btcf,
                )
            cash_flows.append(cash_flow)

        return cash_flows

    def create_sample_distributions(self) -> list:
        """Create sample waterfall distributions for testing."""
        distributions = []
        cumulative_unpaid = 0.0

        for year in range(6):
            if year == 0:
                distribution = WaterfallDistribution(
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
            else:
                available_cash = 30000 * (1.05**year)
                preferred_due = 12000
                preferred_paid = min(available_cash, preferred_due + cumulative_unpaid)
                remaining = available_cash - preferred_paid

                distribution = WaterfallDistribution(
                    year=year,
                    available_cash=available_cash,
                    investor_preferred_return_due=preferred_due,
                    investor_preferred_return_paid=preferred_paid,
                    investor_preferred_return_accrued=max(
                        0, preferred_due + cumulative_unpaid - preferred_paid
                    ),
                    cumulative_unpaid_preferred=max(
                        0, cumulative_unpaid + preferred_due - preferred_paid
                    ),
                    investor_cash_distribution=preferred_paid + remaining * 0.8,
                    operator_cash_distribution=remaining * 0.2,
                    total_cash_distributed=available_cash,
                    remaining_cash=0,
                )
                cumulative_unpaid = distribution.cumulative_unpaid_preferred

            distributions.append(distribution)

        return distributions

    def test_cash_flow_projection_creation(self):
        """Test basic cash flow projection creation."""
        cash_flows = self.create_sample_cash_flows()
        distributions = self.create_sample_distributions()

        projection = CashFlowProjection(
            property_id="TEST_PROP_001",
            scenario_id="TEST_SCENARIO_001",
            annual_cash_flows=cash_flows,
            waterfall_distributions=distributions,
            investor_equity_share=0.8,
            preferred_return_rate=0.06,
        )

        assert projection.property_id == "TEST_PROP_001"
        assert projection.scenario_id == "TEST_SCENARIO_001"
        assert len(projection.annual_cash_flows) == 6
        assert len(projection.waterfall_distributions) == 6
        assert projection.investor_equity_share == 0.8

    def test_get_cash_flow_by_year(self):
        """Test getting cash flow for specific year."""
        cash_flows = self.create_sample_cash_flows()
        distributions = self.create_sample_distributions()

        projection = CashFlowProjection(
            property_id="TEST_PROP_001",
            scenario_id="TEST_SCENARIO_001",
            annual_cash_flows=cash_flows,
            waterfall_distributions=distributions,
            investor_equity_share=0.8,
            preferred_return_rate=0.06,
        )

        year_1_cf = projection.get_cash_flow_by_year(1)
        assert year_1_cf is not None
        assert year_1_cf.year == 1

        # Test invalid year
        invalid_cf = projection.get_cash_flow_by_year(10)
        assert invalid_cf is None

    def test_performance_metrics(self):
        """Test performance metrics calculation."""
        cash_flows = self.create_sample_cash_flows()
        distributions = self.create_sample_distributions()

        projection = CashFlowProjection(
            property_id="TEST_PROP_001",
            scenario_id="TEST_SCENARIO_001",
            annual_cash_flows=cash_flows,
            waterfall_distributions=distributions,
            investor_equity_share=0.8,
            preferred_return_rate=0.06,
        )

        metrics = projection.get_performance_metrics()

        assert "average_annual_noi" in metrics
        assert "average_annual_cash_flow" in metrics
        assert "total_investor_distributions" in metrics
        assert metrics["years_projected"] == 6

    def test_serialization(self):
        """Test to_dict and from_dict serialization."""
        cash_flows = self.create_sample_cash_flows()
        distributions = self.create_sample_distributions()

        original = CashFlowProjection(
            property_id="TEST_PROP_001",
            scenario_id="TEST_SCENARIO_001",
            annual_cash_flows=cash_flows,
            waterfall_distributions=distributions,
            investor_equity_share=0.8,
            preferred_return_rate=0.06,
        )

        # Serialize
        data_dict = original.to_dict()

        # Deserialize
        restored = CashFlowProjection.from_dict(data_dict)

        assert restored.property_id == original.property_id
        assert restored.scenario_id == original.scenario_id
        assert len(restored.annual_cash_flows) == len(original.annual_cash_flows)
        assert restored.investor_equity_share == original.investor_equity_share

    def test_validation_errors(self):
        """Test validation of invalid projections."""
        cash_flows = self.create_sample_cash_flows()
        distributions = self.create_sample_distributions()

        with pytest.raises(ValidationError):
            # Invalid investor equity share
            CashFlowProjection(
                property_id="TEST_PROP_001",
                scenario_id="TEST_SCENARIO_001",
                annual_cash_flows=cash_flows,
                waterfall_distributions=distributions,
                investor_equity_share=1.5,  # Invalid: > 100%
                preferred_return_rate=0.06,
            )


class TestCashFlowProjectionService:
    """Test Cash Flow Projection Service."""

    def create_sample_dcf_assumptions(self) -> DCFAssumptions:
        """Create sample DCF assumptions for testing."""
        return DCFAssumptions(
            scenario_id="test_scenario_001",
            msa_code="35620",
            property_id="TEST_PROP_001",
            commercial_mortgage_rate=[0.06, 0.065, 0.067, 0.069, 0.071, 0.073],
            treasury_10y_rate=[0.04, 0.042, 0.044, 0.046, 0.048, 0.050],
            fed_funds_rate=[0.02, 0.025, 0.03, 0.032, 0.034, 0.036],
            cap_rate=[0.07, 0.07, 0.07, 0.07, 0.07, 0.065],
            rent_growth_rate=[0.0, 0.03, 0.032, 0.029, 0.031, 0.028],
            expense_growth_rate=[0.0, 0.02, 0.025, 0.022, 0.024, 0.021],
            property_growth_rate=[0.0, 0.02, 0.025, 0.018, 0.022, 0.019],
            vacancy_rate=[0.0, 0.05, 0.04, 0.06, 0.045, 0.05],
            ltv_ratio=0.75,
            closing_cost_pct=0.05,
            lender_reserves_months=3.0,
            investor_equity_share=0.75,
            preferred_return_rate=0.06,
            self_cash_percentage=0.30,
        )

    def create_sample_initial_numbers(self) -> InitialNumbers:
        """Create sample initial numbers for testing."""
        return InitialNumbers(
            property_id="TEST_PROP_001",
            scenario_id="test_scenario_001",
            purchase_price=1000000,
            closing_cost_amount=50000,
            renovation_capex=100000,
            cost_basis=1150000,
            loan_amount=750000,
            annual_interest_expense=45000,
            lender_reserves_amount=11250,
            investor_cash_required=300000,
            operator_cash_required=100000,
            total_cash_required=400000,
            after_repair_value=1300000,
            initial_cap_rate=0.065,
            pre_renovation_annual_rent=80000,
            post_renovation_annual_rent=90000,
            year_1_rental_income=85000,
            property_taxes=10800,
            insurance=1800,
            repairs_maintenance=2700,
            property_management=4500,
            admin_expenses=900,
            contracting=1800,
            replacement_reserves=1350,
            total_operating_expenses=23850,
            investor_equity_share=0.75,
            preferred_return_rate=0.06,
        )

    def test_calculate_cash_flow_projection(self):
        """Test calculating complete cash flow projection."""
        service = CashFlowProjectionService()
        dcf_assumptions = self.create_sample_dcf_assumptions()
        initial_numbers = self.create_sample_initial_numbers()

        projection = service.calculate_cash_flow_projection(
            dcf_assumptions, initial_numbers
        )

        assert projection.property_id == "TEST_PROP_001"
        assert projection.scenario_id == "test_scenario_001"
        assert len(projection.annual_cash_flows) == 6
        assert len(projection.waterfall_distributions) == 6

        # Check Year 0 (renovation year)
        year_0_cf = projection.get_cash_flow_by_year(0)
        assert year_0_cf.gross_rental_income == 0
        assert year_0_cf.capital_expenditures == 100000

        # Check Year 1 (first operational year)
        year_1_cf = projection.get_cash_flow_by_year(1)
        assert year_1_cf.gross_rental_income > 0
        assert year_1_cf.net_operating_income > 0

    def test_waterfall_distribution_calculation(self):
        """Test waterfall distribution calculations."""
        service = CashFlowProjectionService()
        dcf_assumptions = self.create_sample_dcf_assumptions()
        initial_numbers = self.create_sample_initial_numbers()

        projection = service.calculate_cash_flow_projection(
            dcf_assumptions, initial_numbers
        )

        # Check Year 1 distribution
        year_1_dist = projection.get_distribution_by_year(1)
        assert year_1_dist.investor_preferred_return_due > 0
        assert year_1_dist.available_cash >= 0

        # Check that distributions are reasonable
        total_investor = sum(
            d.investor_cash_distribution for d in projection.waterfall_distributions
        )
        total_operator = sum(
            d.operator_cash_distribution for d in projection.waterfall_distributions
        )

        assert total_investor > 0
        assert total_operator >= 0  # Could be 0 if no excess cash

    def test_projection_validation(self):
        """Test validation of cash flow projections."""
        service = CashFlowProjectionService()
        dcf_assumptions = self.create_sample_dcf_assumptions()
        initial_numbers = self.create_sample_initial_numbers()

        projection = service.calculate_cash_flow_projection(
            dcf_assumptions, initial_numbers
        )
        issues = service.validate_cash_flow_projection(projection)

        # Should have minimal issues for reasonable inputs
        major_issues = [
            issue
            for issue in issues
            if "negative" in issue.lower() or "extreme" in issue.lower()
        ]
        assert len(major_issues) == 0

    def test_projection_summary(self):
        """Test getting projection summary."""
        service = CashFlowProjectionService()
        dcf_assumptions = self.create_sample_dcf_assumptions()
        initial_numbers = self.create_sample_initial_numbers()

        projection = service.calculate_cash_flow_projection(
            dcf_assumptions, initial_numbers
        )
        summary = service.get_projection_summary(projection)

        assert "property_id" in summary
        assert "annual_summary" in summary
        assert "performance_metrics" in summary
        assert "key_totals" in summary

        # Check annual summary has 6 years
        assert len(summary["annual_summary"]) == 6

    def test_annual_returns_calculation(self):
        """Test annual returns calculation."""
        service = CashFlowProjectionService()
        dcf_assumptions = self.create_sample_dcf_assumptions()
        initial_numbers = self.create_sample_initial_numbers()

        projection = service.calculate_cash_flow_projection(
            dcf_assumptions, initial_numbers
        )
        annual_returns = service.calculate_annual_returns(projection)

        # Should have returns for Years 1-5
        assert len(annual_returns) == 5

        for year in range(1, 6):
            assert year in annual_returns
            assert "noi" in annual_returns[year]
            assert "investor_distribution" in annual_returns[year]
