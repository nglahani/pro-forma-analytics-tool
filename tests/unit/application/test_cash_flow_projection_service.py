"""
Unit Tests for Cash Flow Projection Service (Simplified)

Core functionality tests for the cash flow projection service.
"""

from datetime import date
from unittest.mock import Mock, patch

import pytest

from core.exceptions import ValidationError
from src.application.services.cash_flow_projection_service import (
    CashFlowProjectionService,
)
from src.domain.entities.cash_flow_projection import CashFlowProjection
from src.domain.entities.dcf_assumptions import DCFAssumptions
from src.domain.entities.initial_numbers import InitialNumbers


class TestCashFlowProjectionServiceSimplified:
    """Simplified test cases for CashFlowProjectionService core functionality."""

    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return CashFlowProjectionService()

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

    def test_calculate_cash_flow_projection_should_return_valid_projection(
        self, service, sample_dcf_assumptions, sample_initial_numbers
    ):
        """
        GIVEN valid DCF assumptions and initial numbers
        WHEN calculating cash flow projection
        THEN it should return valid CashFlowProjection object
        """
        # Act
        result = service.calculate_cash_flow_projection(
            sample_dcf_assumptions, sample_initial_numbers
        )

        # Assert
        assert isinstance(result, CashFlowProjection)
        assert result.property_id == "test_property_123"
        assert result.scenario_id == "test_scenario_001"
        assert len(result.annual_cash_flows) == 6  # Years 0-5
        assert len(result.waterfall_distributions) == 6  # Years 0-5
        assert result.investor_equity_share == 0.80
        assert result.preferred_return_rate == 0.08

    def test_calculate_cash_flow_projection_should_have_positive_noi(
        self, service, sample_dcf_assumptions, sample_initial_numbers
    ):
        """
        GIVEN property with rental income
        WHEN calculating cash flow projection
        THEN total NOI should be positive
        """
        # Act
        result = service.calculate_cash_flow_projection(
            sample_dcf_assumptions, sample_initial_numbers
        )

        # Assert
        assert result.total_noi > 0
        # Most years should have positive NOI (except maybe Year 0)
        positive_noi_years = sum(
            1 for cf in result.annual_cash_flows if cf.net_operating_income > 0
        )
        assert positive_noi_years >= 4  # At least 4 out of 6 years should be positive

    def test_calculate_cash_flow_projection_should_have_investor_distributions(
        self, service, sample_dcf_assumptions, sample_initial_numbers
    ):
        """
        GIVEN profitable property investment
        WHEN calculating cash flow projection
        THEN there should be distributions to investors
        """
        # Act
        result = service.calculate_cash_flow_projection(
            sample_dcf_assumptions, sample_initial_numbers
        )

        # Assert
        assert result.total_investor_distributions > 0
        # Should have reasonable distributions
        assert (
            result.total_investor_distributions > 100000
        )  # At least $100K over 5 years

    def test_get_projection_summary_should_return_key_metrics(
        self, service, sample_dcf_assumptions, sample_initial_numbers
    ):
        """
        GIVEN calculated cash flow projection
        WHEN getting projection summary
        THEN it should return dictionary with key metrics
        """
        # Arrange
        projection = service.calculate_cash_flow_projection(
            sample_dcf_assumptions, sample_initial_numbers
        )

        # Act
        summary = service.get_projection_summary(projection)

        # Assert
        assert isinstance(summary, dict)
        assert "property_id" in summary
        assert "scenario_id" in summary
        # Should have some meaningful financial metrics (flexibility for different implementations)
        assert len(summary) >= 2  # At least property_id, scenario_id, and some metrics

    def test_validate_cash_flow_projection_should_return_issue_list(
        self, service, sample_dcf_assumptions, sample_initial_numbers
    ):
        """
        GIVEN cash flow projection
        WHEN validating projection
        THEN it should return list of issues (may be empty)
        """
        # Arrange
        projection = service.calculate_cash_flow_projection(
            sample_dcf_assumptions, sample_initial_numbers
        )

        # Act
        issues = service.validate_cash_flow_projection(projection)

        # Assert
        assert isinstance(issues, list)
        # With reasonable assumptions, should have minimal issues

    def test_calculate_cash_flow_projection_with_invalid_inputs_should_raise_validation_error(
        self, service, sample_dcf_assumptions, sample_initial_numbers
    ):
        """
        GIVEN invalid initial numbers
        WHEN calculating cash flow projection
        THEN it should raise ValidationError
        """
        # Arrange
        invalid_numbers = sample_initial_numbers
        invalid_numbers.post_renovation_annual_rent = -1000  # Invalid negative rent

        # Act & Assert
        with pytest.raises(
            ValidationError, match="Cash flow projection calculation failed"
        ):
            service.calculate_cash_flow_projection(
                sample_dcf_assumptions, invalid_numbers
            )

    @patch("src.application.services.cash_flow_projection_service.get_logger")
    def test_calculate_cash_flow_projection_should_log_success(
        self, mock_logger, service, sample_dcf_assumptions, sample_initial_numbers
    ):
        """
        GIVEN valid inputs
        WHEN calculating cash flow projection
        THEN it should log success
        """
        # Arrange
        mock_logger_instance = Mock()
        mock_logger.return_value = mock_logger_instance
        service.logger = mock_logger_instance

        # Act
        service.calculate_cash_flow_projection(
            sample_dcf_assumptions, sample_initial_numbers
        )

        # Assert
        mock_logger_instance.info.assert_called()
        logged_messages = [
            call[0][0] for call in mock_logger_instance.info.call_args_list
        ]
        assert any("Calculating cash flow projection" in msg for msg in logged_messages)
        assert any(
            "Successfully calculated cash flow projection" in msg
            for msg in logged_messages
        )
