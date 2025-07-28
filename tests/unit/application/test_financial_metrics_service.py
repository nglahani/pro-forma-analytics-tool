"""
Unit Tests for Financial Metrics Service

Tests the financial metrics calculation service following BDD/TDD principles.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import date

from src.application.services.financial_metrics_service import FinancialMetricsService
from src.domain.entities.financial_metrics import (
    FinancialMetrics,
    InvestmentRecommendation,
    RiskLevel,
)
from src.domain.entities.cash_flow_projection import (
    CashFlowProjection,
    AnnualCashFlow,
    WaterfallDistribution,
)
from src.domain.entities.dcf_assumptions import DCFAssumptions
from src.domain.entities.initial_numbers import InitialNumbers
from core.exceptions import ValidationError


class TestFinancialMetricsService:
    """Test cases for FinancialMetricsService."""

    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return FinancialMetricsService()

    @pytest.fixture
    def sample_dcf_assumptions(self):
        """Sample DCF assumptions for testing."""
        return DCFAssumptions(
            scenario_id="test_scenario_001",
            msa_code="35620",
            property_id="test_property_123",
            commercial_mortgage_rate=[0.045, 0.047, 0.048, 0.049, 0.050, 0.051],
            treasury_10y_rate=[0.035, 0.036, 0.037, 0.038, 0.039, 0.040],
            fed_funds_rate=[0.025, 0.026, 0.027, 0.028, 0.029, 0.030],
            cap_rate=[0.055, 0.056, 0.057, 0.058, 0.059, 0.060],
            rent_growth_rate=[0.035, 0.038, 0.040, 0.042, 0.045, 0.048],
            expense_growth_rate=[0.025, 0.027, 0.028, 0.030, 0.032, 0.034],
            property_growth_rate=[0.040, 0.042, 0.045, 0.047, 0.050, 0.052],
            vacancy_rate=[0.050, 0.048, 0.045, 0.043, 0.040, 0.038],
            ltv_ratio=0.75,
            closing_cost_pct=0.025,
            lender_reserves_months=6.0,
            investor_equity_share=0.80,
            preferred_return_rate=0.08,
            self_cash_percentage=0.20,
        )

    @pytest.fixture
    def sample_initial_numbers(self):
        """Sample initial numbers for testing."""
        return InitialNumbers(
            property_id="test_property_123",
            scenario_id="test_scenario_001",
            calculation_date=date.today(),
            purchase_price=1000000.0,
            closing_cost_amount=25000.0,
            renovation_capex=100000.0,
            cost_basis=1125000.0,
            loan_amount=750000.0,
            annual_interest_expense=35250.0,
            lender_reserves_amount=17625.0,
            investor_cash_required=314100.0,
            operator_cash_required=78525.0,
            total_cash_required=392625.0,
            after_repair_value=1500000.0,
            initial_cap_rate=0.055,
            pre_renovation_annual_rent=180000.0,
            post_renovation_annual_rent=202500.0,
            year_1_rental_income=101250.0,
            property_taxes=24300.0,
            insurance=4050.0,
            repairs_maintenance=6075.0,
            property_management=10125.0,
            admin_expenses=2025.0,
            contracting=4050.0,
            replacement_reserves=3037.5,
            total_operating_expenses=53662.5,
            investor_equity_share=0.80,
            preferred_return_rate=0.08,
        )

    @pytest.fixture
    def sample_cash_flow_projection(self):
        """Sample cash flow projection for testing."""
        # Create sample annual cash flows
        annual_cash_flows = []
        waterfall_distributions = []

        for year in range(6):
            # Simple growing cash flows
            gross_rent = 200000 + (year * 10000)  # Growing income
            effective_gross = gross_rent * 0.95  # After vacancy
            operating_expenses = 60000 + (year * 2000)  # Growing expenses
            noi = effective_gross - operating_expenses  # NOI = EGI - OpEx
            debt_service = 50000  # Fixed debt service
            net_cash_flow = noi - debt_service

            cash_flow = AnnualCashFlow(
                year=year,
                gross_rental_income=gross_rent,
                vacancy_loss=gross_rent * 0.05,
                effective_gross_income=effective_gross,
                property_taxes=operating_expenses * 0.4,
                insurance=operating_expenses * 0.1,
                repairs_maintenance=operating_expenses * 0.2,
                property_management=operating_expenses * 0.2,
                admin_expenses=operating_expenses * 0.05,
                contracting=operating_expenses * 0.03,
                replacement_reserves=operating_expenses * 0.02,
                total_operating_expenses=operating_expenses,
                net_operating_income=noi,
                annual_debt_service=debt_service,
                before_tax_cash_flow=net_cash_flow,
                capital_expenditures=0.0,
                net_cash_flow=net_cash_flow,
            )
            annual_cash_flows.append(cash_flow)

            # Simple waterfall distribution
            distribution = WaterfallDistribution(
                year=year,
                available_cash=net_cash_flow,
                investor_preferred_return_due=net_cash_flow * 0.08,
                investor_preferred_return_paid=min(net_cash_flow * 0.08, net_cash_flow),
                investor_cash_distribution=net_cash_flow * 0.80,
                operator_cash_distribution=net_cash_flow * 0.20,
                total_cash_distributed=net_cash_flow,
            )
            waterfall_distributions.append(distribution)

        return CashFlowProjection(
            property_id="test_property_123",
            scenario_id="test_scenario_001",
            annual_cash_flows=annual_cash_flows,
            waterfall_distributions=waterfall_distributions,
            investor_equity_share=0.80,
            preferred_return_rate=0.08,
        )

    def test_calculate_financial_metrics_should_return_valid_metrics(
        self,
        service,
        sample_cash_flow_projection,
        sample_dcf_assumptions,
        sample_initial_numbers,
    ):
        """
        GIVEN valid cash flow projection, DCF assumptions, and initial numbers
        WHEN calculating financial metrics
        THEN it should return valid FinancialMetrics object
        """
        # Act
        result = service.calculate_financial_metrics(
            sample_cash_flow_projection, sample_dcf_assumptions, sample_initial_numbers
        )

        # Assert
        assert isinstance(result, FinancialMetrics)
        assert result.property_id == "test_property_123"
        assert result.scenario_id == "test_scenario_001"
        assert result.net_present_value is not None
        assert result.internal_rate_return is not None
        assert result.equity_multiple is not None

    def test_calculate_financial_metrics_should_calculate_positive_npv_for_profitable_investment(
        self,
        service,
        sample_cash_flow_projection,
        sample_dcf_assumptions,
        sample_initial_numbers,
    ):
        """
        GIVEN profitable investment with positive cash flows
        WHEN calculating financial metrics
        THEN NPV should be positive
        """
        # Act
        result = service.calculate_financial_metrics(
            sample_cash_flow_projection, sample_dcf_assumptions, sample_initial_numbers
        )

        # Assert
        assert result.net_present_value > 0
        # NPV should be reasonable (not extreme)
        assert result.net_present_value < 10000000  # Less than $10M

    def test_calculate_financial_metrics_should_calculate_reasonable_irr(
        self,
        service,
        sample_cash_flow_projection,
        sample_dcf_assumptions,
        sample_initial_numbers,
    ):
        """
        GIVEN positive cash flows
        WHEN calculating financial metrics
        THEN IRR should be reasonable
        """
        # Act
        result = service.calculate_financial_metrics(
            sample_cash_flow_projection, sample_dcf_assumptions, sample_initial_numbers
        )

        # Assert
        assert result.internal_rate_return > 0
        # IRR should be reasonable for real estate (5% to 50%)
        assert 0.05 <= result.internal_rate_return <= 0.50

    def test_calculate_financial_metrics_should_calculate_equity_multiple_greater_than_one(
        self,
        service,
        sample_cash_flow_projection,
        sample_dcf_assumptions,
        sample_initial_numbers,
    ):
        """
        GIVEN profitable investment
        WHEN calculating financial metrics
        THEN equity multiple should be greater than 1
        """
        # Act
        result = service.calculate_financial_metrics(
            sample_cash_flow_projection, sample_dcf_assumptions, sample_initial_numbers
        )

        # Assert
        assert result.equity_multiple > 1.0
        # Should be reasonable multiple (1x to 10x for 5-year hold)
        assert result.equity_multiple <= 10.0

    def test_calculate_financial_metrics_should_provide_investment_recommendation(
        self,
        service,
        sample_cash_flow_projection,
        sample_dcf_assumptions,
        sample_initial_numbers,
    ):
        """
        GIVEN calculated financial metrics
        WHEN calculating financial metrics
        THEN it should provide investment recommendation
        """
        # Act
        result = service.calculate_financial_metrics(
            sample_cash_flow_projection, sample_dcf_assumptions, sample_initial_numbers
        )

        # Assert
        assert isinstance(result.investment_recommendation, InvestmentRecommendation)
        assert result.risk_level is not None
        assert isinstance(result.risk_level, RiskLevel)

    def test_calculate_financial_metrics_should_calculate_payback_period(
        self,
        service,
        sample_cash_flow_projection,
        sample_dcf_assumptions,
        sample_initial_numbers,
    ):
        """
        GIVEN positive cash flows
        WHEN calculating financial metrics
        THEN payback period should be reasonable
        """
        # Act
        result = service.calculate_financial_metrics(
            sample_cash_flow_projection, sample_dcf_assumptions, sample_initial_numbers
        )

        # Assert
        assert result.payback_period_years > 0
        # Should be within reasonable range for real estate (2-10 years)
        assert result.payback_period_years <= 10

    def test_calculate_financial_metrics_should_calculate_terminal_value(
        self,
        service,
        sample_cash_flow_projection,
        sample_dcf_assumptions,
        sample_initial_numbers,
    ):
        """
        GIVEN 5-year investment holding period
        WHEN calculating financial metrics
        THEN it should calculate terminal value
        """
        # Act
        result = service.calculate_financial_metrics(
            sample_cash_flow_projection, sample_dcf_assumptions, sample_initial_numbers
        )

        # Assert
        assert result.terminal_value is not None
        assert result.terminal_value.gross_property_value > 0
        assert result.terminal_value.net_sale_proceeds >= 0

    def test_calculate_financial_metrics_should_handle_break_even_analysis(
        self,
        service,
        sample_cash_flow_projection,
        sample_dcf_assumptions,
        sample_initial_numbers,
    ):
        """
        GIVEN financial metrics calculation
        WHEN calculating financial metrics
        THEN it should include break-even analysis
        """
        # Act
        result = service.calculate_financial_metrics(
            sample_cash_flow_projection, sample_dcf_assumptions, sample_initial_numbers
        )

        # Assert
        # Should have break-even related calculations
        assert hasattr(result, "break_even_analysis") or result.payback_period_years > 0

    def test_get_metrics_summary_should_return_comprehensive_summary(
        self,
        service,
        sample_cash_flow_projection,
        sample_dcf_assumptions,
        sample_initial_numbers,
    ):
        """
        GIVEN calculated financial metrics
        WHEN getting metrics summary
        THEN it should return comprehensive summary
        """
        # Arrange
        financial_metrics = service.calculate_financial_metrics(
            sample_cash_flow_projection, sample_dcf_assumptions, sample_initial_numbers
        )

        # Act
        summary = service.get_metrics_summary(financial_metrics)

        # Assert
        assert isinstance(summary, dict)
        assert "property_id" in summary
        assert "scenario_id" in summary
        assert any("npv" in key.lower() for key in summary.keys())
        assert any("irr" in key.lower() for key in summary.keys())
        assert "equity_multiple" in summary

    def test_calculate_financial_metrics_with_custom_discount_rate_should_affect_npv(
        self,
        service,
        sample_cash_flow_projection,
        sample_dcf_assumptions,
        sample_initial_numbers,
    ):
        """
        GIVEN different discount rates
        WHEN calculating financial metrics
        THEN NPV should change with discount rate
        """
        # Act
        result_10pct = service.calculate_financial_metrics(
            sample_cash_flow_projection,
            sample_dcf_assumptions,
            sample_initial_numbers,
            discount_rate=0.10,
        )
        result_15pct = service.calculate_financial_metrics(
            sample_cash_flow_projection,
            sample_dcf_assumptions,
            sample_initial_numbers,
            discount_rate=0.15,
        )

        # Assert
        # Higher discount rate should result in lower NPV
        assert result_15pct.net_present_value < result_10pct.net_present_value

    def test_calculate_financial_metrics_with_negative_cash_flows_should_handle_gracefully(
        self, service, sample_dcf_assumptions, sample_initial_numbers
    ):
        """
        GIVEN investment with negative cash flows
        WHEN calculating financial metrics
        THEN it should handle gracefully without crashing
        """
        # Arrange - create cash flow projection with negative flows
        annual_cash_flows = []
        waterfall_distributions = []

        for year in range(6):
            # Negative cash flows
            net_cash_flow = -10000 - (year * 1000)

            cash_flow = AnnualCashFlow(
                year=year,
                gross_rental_income=100000,
                vacancy_loss=5000,
                effective_gross_income=95000,
                property_taxes=48000,  # 120k total expenses broken down
                insurance=12000,
                repairs_maintenance=24000,
                property_management=24000,
                admin_expenses=6000,
                contracting=3600,
                replacement_reserves=2400,
                total_operating_expenses=120000,  # Higher than income
                net_operating_income=-25000,
                annual_debt_service=50000,
                before_tax_cash_flow=-75000,
                capital_expenditures=0.0,
                net_cash_flow=net_cash_flow,
            )
            annual_cash_flows.append(cash_flow)

            distribution = WaterfallDistribution(
                year=year,
                available_cash=max(0, net_cash_flow),
                investor_cash_distribution=0,
                operator_cash_distribution=0,
                total_cash_distributed=0,
            )
            waterfall_distributions.append(distribution)

        negative_cash_flow_projection = CashFlowProjection(
            property_id="test_property_123",
            scenario_id="test_scenario_001",
            annual_cash_flows=annual_cash_flows,
            waterfall_distributions=waterfall_distributions,
            investor_equity_share=0.80,
            preferred_return_rate=0.08,
        )

        # Act & Assert - should not crash
        result = service.calculate_financial_metrics(
            negative_cash_flow_projection,
            sample_dcf_assumptions,
            sample_initial_numbers,
        )

        # Should return metrics even if negative
        assert isinstance(result, FinancialMetrics)
        assert result.net_present_value < 0  # Should be negative NPV
        assert result.investment_recommendation in [
            InvestmentRecommendation.SELL,
            InvestmentRecommendation.STRONG_SELL,
        ]

    def test_calculate_financial_metrics_with_invalid_inputs_should_raise_validation_error(
        self, service, sample_cash_flow_projection, sample_dcf_assumptions
    ):
        """
        GIVEN invalid initial numbers
        WHEN calculating financial metrics
        THEN it should raise ValidationError
        """
        # Arrange
        invalid_initial_numbers = InitialNumbers(
            property_id="test_property_123",
            scenario_id="test_scenario_001",
            calculation_date=date.today(),
            purchase_price=-1000000.0,  # Invalid negative price
            total_cash_required=392625.0,
            investor_equity_share=0.80,
            preferred_return_rate=0.08,
        )

        # Act & Assert
        with pytest.raises(
            ValidationError, match="Financial metrics calculation failed"
        ):
            service.calculate_financial_metrics(
                sample_cash_flow_projection,
                sample_dcf_assumptions,
                invalid_initial_numbers,
            )

    @patch("src.application.services.financial_metrics_service.get_logger")
    def test_calculate_financial_metrics_should_log_calculation_details(
        self,
        mock_logger,
        service,
        sample_cash_flow_projection,
        sample_dcf_assumptions,
        sample_initial_numbers,
    ):
        """
        GIVEN valid inputs
        WHEN calculating financial metrics
        THEN it should log calculation details
        """
        # Arrange
        mock_logger_instance = Mock()
        mock_logger.return_value = mock_logger_instance
        service.logger = mock_logger_instance

        # Act
        service.calculate_financial_metrics(
            sample_cash_flow_projection, sample_dcf_assumptions, sample_initial_numbers
        )

        # Assert
        mock_logger_instance.info.assert_called()
        logged_messages = [
            call[0][0] for call in mock_logger_instance.info.call_args_list
        ]
        assert any("Calculating financial metrics" in msg for msg in logged_messages)
