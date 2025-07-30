"""
Unit tests for Financial Metrics functionality.

Tests the calculation of NPV, IRR, and investment recommendations.
"""


import pytest

from core.exceptions import ValidationError
from src.application.services.financial_metrics_service import FinancialMetricsService
from src.domain.entities.cash_flow_projection import (
    AnnualCashFlow,
    CashFlowProjection,
    WaterfallDistribution,
)
from src.domain.entities.dcf_assumptions import DCFAssumptions
from src.domain.entities.financial_metrics import (
    CashFlowSummary,
    FinancialMetrics,
    InvestmentRecommendation,
    RiskLevel,
    TerminalValue,
)
from src.domain.entities.initial_numbers import InitialNumbers


class TestTerminalValue:
    """Test Terminal Value entity."""

    def test_terminal_value_creation(self):
        """Test basic terminal value creation."""
        terminal_value = TerminalValue(
            year=5,
            final_noi=100000,
            exit_cap_rate=0.06,
            remaining_loan_balance=500000,
            selling_costs_rate=0.03,
        )

        assert terminal_value.year == 5
        assert terminal_value.final_noi == 100000
        assert terminal_value.exit_cap_rate == 0.06
        assert terminal_value.gross_property_value == 100000 / 0.06  # NOI / Cap Rate
        assert terminal_value.selling_costs_amount > 0
        assert terminal_value.net_sale_proceeds > 0

    def test_terminal_value_validation(self):
        """Test terminal value validation."""
        with pytest.raises(ValidationError):
            # Invalid exit year
            TerminalValue(
                year=15,  # Too high
                final_noi=100000,
                exit_cap_rate=0.06,
                remaining_loan_balance=500000,
            )

        with pytest.raises(ValidationError):
            # Invalid cap rate
            TerminalValue(
                year=5,
                final_noi=100000,
                exit_cap_rate=0.30,  # Too high
                remaining_loan_balance=500000,
            )


class TestCashFlowSummary:
    """Test Cash Flow Summary entity."""

    def test_cash_flow_summary_creation(self):
        """Test basic cash flow summary creation."""
        summary = CashFlowSummary(
            initial_investment=1000000,
            annual_cash_flows=[50000, 60000, 70000, 80000, 90000],
            terminal_cash_flow=200000,
        )

        assert summary.initial_investment == 1000000
        assert len(summary.annual_cash_flows) == 5
        assert summary.terminal_cash_flow == 200000
        assert len(summary.total_cash_flows) == 6  # Initial + 5 years
        assert summary.total_cash_flows[0] == -1000000  # Negative initial investment
        assert summary.total_cash_flows[-1] == 90000 + 200000  # Last year + terminal

    def test_cash_flow_summary_validation(self):
        """Test cash flow summary validation."""
        with pytest.raises(ValidationError):
            # Invalid initial investment
            CashFlowSummary(
                initial_investment=0,  # Must be positive
                annual_cash_flows=[50000, 60000],
                terminal_cash_flow=100000,
            )


class TestFinancialMetrics:
    """Test Financial Metrics entity."""

    def create_sample_terminal_value(self) -> TerminalValue:
        """Create sample terminal value for testing."""
        return TerminalValue(
            year=5,
            final_noi=120000,
            exit_cap_rate=0.065,
            remaining_loan_balance=600000,
            selling_costs_rate=0.03,
        )

    def test_financial_metrics_creation(self):
        """Test basic financial metrics creation."""
        terminal_value = self.create_sample_terminal_value()

        metrics = FinancialMetrics(
            property_id="TEST_PROP_001",
            scenario_id="TEST_SCENARIO_001",
            initial_investment=1000000,
            total_distributions=350000,
            terminal_value=terminal_value,
            net_present_value=250000,
            internal_rate_return=0.15,
            modified_irr=0.13,
            cash_on_cash_return_year_1=0.08,
            average_annual_return=0.12,
            equity_multiple=1.8,
            total_return_multiple=1.8,
            payback_period_years=4.2,
            return_on_investment=0.80,
            annualized_return=0.15,
            discount_rate=0.10,
            investment_horizon_years=5,
            risk_level=RiskLevel.MODERATE,
            investment_recommendation=InvestmentRecommendation.BUY,
            recommendation_rationale="Strong NPV and good IRR",
            debt_service_coverage_avg=1.4,
            loan_to_value_ratio=0.75,
            cap_rate_year_1=0.07,
        )

        assert metrics.property_id == "TEST_PROP_001"
        assert metrics.net_present_value == 250000
        assert metrics.internal_rate_return == 0.15
        assert metrics.investment_recommendation == InvestmentRecommendation.BUY
        assert metrics.risk_level == RiskLevel.MODERATE

    def test_investment_summary(self):
        """Test getting investment summary."""
        terminal_value = self.create_sample_terminal_value()

        metrics = FinancialMetrics(
            property_id="TEST_PROP_001",
            scenario_id="TEST_SCENARIO_001",
            initial_investment=1000000,
            total_distributions=350000,
            terminal_value=terminal_value,
            net_present_value=250000,
            internal_rate_return=0.15,
            equity_multiple=1.8,
            payback_period_years=4.2,
            investment_recommendation=InvestmentRecommendation.BUY,
            risk_level=RiskLevel.MODERATE,
        )

        summary = metrics.get_investment_summary()

        assert "property_id" in summary
        assert "net_present_value" in summary
        assert "internal_rate_return" in summary
        assert "investment_recommendation" in summary
        assert summary["initial_investment"] == 1000000
        assert summary["total_distributions"] == 350000

    def test_metrics_validation(self):
        """Test financial metrics validation."""
        terminal_value = self.create_sample_terminal_value()

        with pytest.raises(ValidationError):
            # Invalid IRR
            FinancialMetrics(
                property_id="TEST_PROP_001",
                scenario_id="TEST_SCENARIO_001",
                initial_investment=1000000,
                total_distributions=350000,
                terminal_value=terminal_value,
                internal_rate_return=10.0,  # Too high (1000%)
                equity_multiple=1.8,
            )

    def test_serialization(self):
        """Test to_dict and from_dict serialization."""
        terminal_value = self.create_sample_terminal_value()

        original = FinancialMetrics(
            property_id="TEST_PROP_001",
            scenario_id="TEST_SCENARIO_001",
            initial_investment=1000000,
            total_distributions=350000,
            terminal_value=terminal_value,
            net_present_value=250000,
            internal_rate_return=0.15,
            equity_multiple=1.8,
            investment_recommendation=InvestmentRecommendation.BUY,
            risk_level=RiskLevel.MODERATE,
        )

        # Serialize
        data_dict = original.to_dict()

        # Deserialize
        restored = FinancialMetrics.from_dict(data_dict)

        assert restored.property_id == original.property_id
        assert restored.net_present_value == original.net_present_value
        assert restored.internal_rate_return == original.internal_rate_return
        assert restored.investment_recommendation == original.investment_recommendation


class TestFinancialMetricsService:
    """Test Financial Metrics Service."""

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

    def create_sample_cash_flow_projection(self) -> CashFlowProjection:
        """Create sample cash flow projection for testing."""
        annual_cash_flows = []
        waterfall_distributions = []

        for year in range(6):
            if year == 0:
                # Year 0: Acquisition year
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
                # Years 1-5: Operating years
                gross_income = 95000 * (1.03**year)
                vacancy_loss = gross_income * 0.05
                effective_income = gross_income - vacancy_loss

                # Calculate individual expense components
                operating_expenses = 25000 * (1.02**year)
                property_taxes = operating_expenses * 0.4
                insurance = operating_expenses * 0.1
                repairs_maintenance = operating_expenses * 0.15
                property_management = operating_expenses * 0.2
                admin_expenses = operating_expenses * 0.05
                contracting = operating_expenses * 0.05
                replacement_reserves = operating_expenses * 0.05

                noi = effective_income - operating_expenses
                debt_service = 45000
                cash_flow_amount = noi - debt_service

                cash_flow = AnnualCashFlow(
                    year=year,
                    gross_rental_income=gross_income,
                    vacancy_loss=vacancy_loss,
                    effective_gross_income=effective_income,
                    property_taxes=property_taxes,
                    insurance=insurance,
                    repairs_maintenance=repairs_maintenance,
                    property_management=property_management,
                    admin_expenses=admin_expenses,
                    contracting=contracting,
                    replacement_reserves=replacement_reserves,
                    total_operating_expenses=operating_expenses,
                    net_operating_income=noi,
                    annual_debt_service=debt_service,
                    before_tax_cash_flow=cash_flow_amount,
                    capital_expenditures=0,
                    net_cash_flow=cash_flow_amount,
                )

                # Simple waterfall distribution
                preferred_due = 18000  # 6% of 300k investor cash
                preferred_paid = min(cash_flow_amount, preferred_due)
                remaining = max(0, cash_flow_amount - preferred_paid)

                distribution = WaterfallDistribution(
                    year=year,
                    available_cash=cash_flow_amount,
                    investor_preferred_return_due=preferred_due,
                    investor_preferred_return_paid=preferred_paid,
                    investor_preferred_return_accrued=max(
                        0, preferred_due - preferred_paid
                    ),
                    cumulative_unpaid_preferred=0,
                    investor_cash_distribution=preferred_paid + remaining * 0.75,
                    operator_cash_distribution=remaining * 0.25,
                    total_cash_distributed=cash_flow_amount,
                    remaining_cash=0,
                )

            annual_cash_flows.append(cash_flow)
            waterfall_distributions.append(distribution)

        return CashFlowProjection(
            property_id="TEST_PROP_001",
            scenario_id="test_scenario_001",
            annual_cash_flows=annual_cash_flows,
            waterfall_distributions=waterfall_distributions,
            investor_equity_share=0.75,
            preferred_return_rate=0.06,
        )

    def test_calculate_financial_metrics(self):
        """Test calculating comprehensive financial metrics."""
        service = FinancialMetricsService()
        dcf_assumptions = self.create_sample_dcf_assumptions()
        initial_numbers = self.create_sample_initial_numbers()
        cash_flow_projection = self.create_sample_cash_flow_projection()

        metrics = service.calculate_financial_metrics(
            cash_flow_projection, dcf_assumptions, initial_numbers, discount_rate=0.10
        )

        assert metrics.property_id == "TEST_PROP_001"
        assert metrics.scenario_id == "test_scenario_001"
        assert metrics.initial_investment > 0
        assert metrics.net_present_value != 0  # Should calculate some NPV
        assert -1.0 < metrics.internal_rate_return < 10.0  # Reasonable IRR range
        assert metrics.equity_multiple > 0
        assert metrics.payback_period_years > 0
        assert isinstance(metrics.investment_recommendation, InvestmentRecommendation)
        assert isinstance(metrics.risk_level, RiskLevel)

    def test_terminal_value_calculation(self):
        """Test terminal value calculation."""
        service = FinancialMetricsService()
        dcf_assumptions = self.create_sample_dcf_assumptions()
        initial_numbers = self.create_sample_initial_numbers()
        cash_flow_projection = self.create_sample_cash_flow_projection()

        terminal_value = service._calculate_terminal_value(
            cash_flow_projection, dcf_assumptions, initial_numbers
        )

        assert terminal_value.year == 5
        assert terminal_value.final_noi > 0
        assert terminal_value.exit_cap_rate > 0
        assert terminal_value.gross_property_value > 0
        assert terminal_value.selling_costs_amount > 0
        assert terminal_value.net_sale_proceeds >= 0

    def test_npv_calculation(self):
        """Test NPV calculation."""
        service = FinancialMetricsService()

        # Simple cash flow: -1000, 200, 300, 400, 500
        cash_flows = [-1000, 200, 300, 400, 500]
        npv = service._calculate_npv(cash_flows, 0.10)

        # Manual calculation for verification
        expected_npv = (
            -1000 + 200 / 1.1 + 300 / (1.1**2) + 400 / (1.1**3) + 500 / (1.1**4)
        )

        assert abs(npv - expected_npv) < 0.01

    def test_irr_calculation(self):
        """Test IRR calculation."""
        service = FinancialMetricsService()

        # Cash flow with known IRR
        cash_flows = [-1000, 200, 300, 400, 500]
        irr = service._calculate_irr(cash_flows)

        # Verify IRR by checking NPV at calculated rate is close to 0
        npv_at_irr = sum(cf / ((1 + irr) ** i) for i, cf in enumerate(cash_flows))

        assert abs(npv_at_irr) < 0.01  # NPV should be close to 0 at IRR
        assert 0.05 < irr < 0.50  # Reasonable IRR range

    def test_payback_period_calculation(self):
        """Test payback period calculation."""
        service = FinancialMetricsService()

        # Cash flows: -1000, 300, 400, 500 -> payback between years 2-3
        cash_flows = [-1000, 300, 400, 500]
        payback = service._calculate_payback_period(cash_flows)

        # Should payback during year 3: 300 + 400 = 700, need 300 more
        # 300/500 = 0.6, so payback = 2 + 0.6 = 2.6 years
        expected_payback = 2 + (300 / 500)

        assert abs(payback - expected_payback) < 0.1

    def test_risk_assessment(self):
        """Test risk level assessment."""
        service = FinancialMetricsService()

        # Low risk scenario
        low_risk = service._assess_risk_level(
            irr=0.15, equity_multiple=2.0, avg_dscr=2.0, ltv_ratio=0.60
        )
        assert low_risk in [RiskLevel.LOW, RiskLevel.MODERATE]

        # High risk scenario
        high_risk = service._assess_risk_level(
            irr=0.05, equity_multiple=1.1, avg_dscr=1.1, ltv_ratio=0.90
        )
        assert high_risk in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]

    def test_investment_recommendation(self):
        """Test investment recommendation generation."""
        service = FinancialMetricsService()

        # Strong investment scenario
        strong_rec, rationale = service._generate_investment_recommendation(
            npv=500000,
            irr=0.20,
            equity_multiple=2.5,
            payback_period=3.0,
            risk_level=RiskLevel.LOW,
        )

        assert strong_rec in [
            InvestmentRecommendation.BUY,
            InvestmentRecommendation.STRONG_BUY,
        ]
        assert len(rationale) > 0

        # Poor investment scenario
        poor_rec, rationale = service._generate_investment_recommendation(
            npv=-200000,
            irr=0.05,
            equity_multiple=0.8,
            payback_period=8.0,
            risk_level=RiskLevel.VERY_HIGH,
        )

        assert poor_rec in [
            InvestmentRecommendation.SELL,
            InvestmentRecommendation.STRONG_SELL,
        ]
        assert len(rationale) > 0

    def test_metrics_summary(self):
        """Test getting comprehensive metrics summary."""
        service = FinancialMetricsService()
        dcf_assumptions = self.create_sample_dcf_assumptions()
        initial_numbers = self.create_sample_initial_numbers()
        cash_flow_projection = self.create_sample_cash_flow_projection()

        metrics = service.calculate_financial_metrics(
            cash_flow_projection, dcf_assumptions, initial_numbers
        )

        summary = service.get_metrics_summary(metrics)

        assert "investment_summary" in summary
        assert "profitability_analysis" in summary
        assert "risk_analysis" in summary
        assert "investment_recommendation" in summary

        # Check key fields exist
        assert "net_present_value" in summary["investment_summary"]
        assert "internal_rate_return" in summary["profitability_analysis"]
        assert "risk_level" in summary["risk_analysis"]
        assert "recommendation" in summary["investment_recommendation"]

    def test_scenario_comparison(self):
        """Test comparing multiple scenarios."""
        service = FinancialMetricsService()

        # Create multiple metrics for comparison
        metrics_list = []
        for i in range(3):
            dcf_assumptions = self.create_sample_dcf_assumptions()
            initial_numbers = self.create_sample_initial_numbers()
            cash_flow_projection = self.create_sample_cash_flow_projection()

            # Modify scenario ID for differentiation
            dcf_assumptions.scenario_id = f"scenario_{i+1}"
            cash_flow_projection.scenario_id = f"scenario_{i+1}"

            metrics = service.calculate_financial_metrics(
                cash_flow_projection, dcf_assumptions, initial_numbers
            )
            metrics_list.append(metrics)

        comparison = service.compare_scenarios(metrics_list)

        assert "scenario_count" in comparison
        assert comparison["scenario_count"] == 3
        assert "best_npv_scenario" in comparison
        assert "best_irr_scenario" in comparison
        assert "summary_statistics" in comparison
        assert "recommendations" in comparison
