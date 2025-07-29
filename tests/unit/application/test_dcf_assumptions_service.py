"""
Unit Tests for DCF Assumptions Service

Tests the DCF assumptions service layer following BDD/TDD principles.
"""

from datetime import date
from unittest.mock import Mock, patch

import pytest

from core.exceptions import ValidationError
from src.application.services.dcf_assumptions_service import DCFAssumptionsService
from src.domain.entities.dcf_assumptions import DCFAssumptions
from src.domain.entities.property_data import (
    InvestorEquityStructure,
    RenovationInfo,
    RenovationStatus,
    ResidentialUnits,
    SimplifiedPropertyInput,
)


class TestDCFAssumptionsService:
    """Test cases for DCFAssumptionsService."""

    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return DCFAssumptionsService()

    @pytest.fixture
    def sample_property_data(self):
        """Sample property data for testing."""
        return SimplifiedPropertyInput(
            property_id="test_property_123",
            property_name="Test NYC Mixed-Use Property",
            analysis_date=date.today(),
            purchase_price=1000000,
            city="New York",
            state="NY",
            msa_code="35620",
            residential_units=ResidentialUnits(
                total_units=10, average_rent_per_unit=1500
            ),
            equity_structure=InvestorEquityStructure(
                investor_equity_share_pct=80, self_cash_percentage=20
            ),
            renovation_info=RenovationInfo(
                status=RenovationStatus.PLANNED, anticipated_duration_months=6
            ),
        )

    @pytest.fixture
    def sample_monte_carlo_scenario(self):
        """Sample Monte Carlo scenario for testing."""
        return {
            "scenario_id": "test_scenario_001",
            "forecasted_parameters": {
                "commercial_mortgage_rate": [0.045, 0.047, 0.048, 0.049, 0.050, 0.051],
                "treasury_10y": [0.035, 0.036, 0.037, 0.038, 0.039, 0.040],
                "fed_funds_rate": [0.025, 0.026, 0.027, 0.028, 0.029, 0.030],
                "cap_rate": [0.055, 0.056, 0.057, 0.058, 0.059, 0.060],
                "rent_growth": [0.035, 0.038, 0.040, 0.042, 0.045, 0.048],
                "expense_growth": [0.025, 0.027, 0.028, 0.030, 0.032, 0.034],
                "property_growth": [0.040, 0.042, 0.045, 0.047, 0.050, 0.052],
                "vacancy_rate": [0.050, 0.048, 0.045, 0.043, 0.040, 0.038],
                "ltv_ratio": [0.75, 0.75, 0.75, 0.75, 0.75, 0.75],
                "closing_cost_pct": [0.025, 0.025, 0.025, 0.025, 0.025, 0.025],
                "lender_reserves": [6.0, 6.0, 6.0, 6.0, 6.0, 6.0],
            },
        }

    def test_create_dcf_assumptions_from_scenario_should_return_valid_assumptions(
        self, service, sample_monte_carlo_scenario, sample_property_data
    ):
        """
        GIVEN valid Monte Carlo scenario and property data
        WHEN creating DCF assumptions
        THEN it should return valid DCFAssumptions object
        """
        # Act
        result = service.create_dcf_assumptions_from_scenario(
            sample_monte_carlo_scenario, sample_property_data
        )

        # Assert
        assert isinstance(result, DCFAssumptions)
        assert result.scenario_id == "test_scenario_001"
        assert result.property_id == "test_property_123"
        assert result.msa_code == "35620"
        assert result.investor_equity_share == 0.80
        assert result.ltv_ratio == 0.75
        assert len(result.commercial_mortgage_rate) == 6

    def test_create_dcf_assumptions_with_missing_forecasted_parameters_should_raise_validation_error(
        self, service, sample_property_data
    ):
        """
        GIVEN Monte Carlo scenario without forecasted_parameters
        WHEN creating DCF assumptions
        THEN it should raise ValidationError
        """
        # Arrange
        invalid_scenario = {"scenario_id": "test"}

        # Act & Assert
        with pytest.raises(
            ValidationError, match="Scenario missing 'forecasted_parameters'"
        ):
            service.create_dcf_assumptions_from_scenario(
                invalid_scenario, sample_property_data
            )

    def test_create_dcf_assumptions_with_invalid_parameter_structure_should_raise_validation_error(
        self, service, sample_property_data
    ):
        """
        GIVEN Monte Carlo scenario with invalid forecasted_parameters structure
        WHEN creating DCF assumptions
        THEN it should raise ValidationError
        """
        # Arrange
        invalid_scenario = {
            "scenario_id": "test",
            "forecasted_parameters": "not_a_dict",
        }

        # Act & Assert
        with pytest.raises(
            ValidationError, match="'forecasted_parameters' must be a dictionary"
        ):
            service.create_dcf_assumptions_from_scenario(
                invalid_scenario, sample_property_data
            )

    def test_create_dcf_assumptions_batch_should_process_multiple_scenarios(
        self, service, sample_monte_carlo_scenario, sample_property_data
    ):
        """
        GIVEN Monte Carlo results with multiple scenarios
        WHEN creating DCF assumptions batch
        THEN it should return list of DCFAssumptions objects
        """
        # Arrange
        scenario_2 = sample_monte_carlo_scenario.copy()
        scenario_2["scenario_id"] = "test_scenario_002"

        monte_carlo_results = {"scenarios": [sample_monte_carlo_scenario, scenario_2]}

        # Act
        result = service.create_dcf_assumptions_batch(
            monte_carlo_results, sample_property_data
        )

        # Assert
        assert len(result) == 2
        assert all(isinstance(dcf, DCFAssumptions) for dcf in result)
        assert result[0].scenario_id == "test_scenario_001"
        assert result[1].scenario_id == "test_scenario_002"

    def test_create_dcf_assumptions_batch_with_no_scenarios_should_raise_validation_error(
        self, service, sample_property_data
    ):
        """
        GIVEN Monte Carlo results with no scenarios
        WHEN creating DCF assumptions batch
        THEN it should raise ValidationError
        """
        # Arrange
        empty_results = {"scenarios": []}

        # Act & Assert
        with pytest.raises(
            ValidationError, match="No scenarios found in Monte Carlo results"
        ):
            service.create_dcf_assumptions_batch(empty_results, sample_property_data)

    def test_validate_assumptions_compatibility_should_identify_unreasonable_rates(
        self, service, sample_monte_carlo_scenario, sample_property_data
    ):
        """
        GIVEN DCF assumptions with unreasonable rates
        WHEN validating assumptions compatibility
        THEN it should return list of validation issues
        """
        # Arrange
        # Create scenario with high but acceptable mortgage rate for testing validation
        extreme_scenario = sample_monte_carlo_scenario.copy()
        extreme_scenario["forecasted_parameters"]["commercial_mortgage_rate"] = [
            0.18
        ] * 6  # 18% rate

        dcf_assumptions = service.create_dcf_assumptions_from_scenario(
            extreme_scenario, sample_property_data
        )

        # Act
        issues = service.validate_assumptions_compatibility(dcf_assumptions)

        # Assert
        assert len(issues) > 0
        assert any("Commercial mortgage rate" in issue for issue in issues)

    def test_extract_msa_code_should_derive_from_city_state_when_missing(self, service):
        """
        GIVEN property data without MSA code but with city/state
        WHEN extracting MSA code
        THEN it should derive correct MSA code
        """
        # Arrange
        property_data_no_msa = SimplifiedPropertyInput(
            property_id="test",
            property_name="Test Chicago Property",
            analysis_date=date.today(),
            purchase_price=1000000,
            city="Chicago",
            state="IL",
            msa_code=None,  # Missing MSA code
            residential_units=ResidentialUnits(
                total_units=5, average_rent_per_unit=1000
            ),
            equity_structure=InvestorEquityStructure(
                investor_equity_share_pct=80, self_cash_percentage=20
            ),
            renovation_info=RenovationInfo(
                status=RenovationStatus.PLANNED, anticipated_duration_months=3
            ),
        )

        # Act
        msa_code = service._extract_msa_code(property_data_no_msa)

        # Assert
        assert msa_code == "16980"  # Chicago MSA code

    def test_extract_msa_code_should_default_to_nyc_when_unknown_location(
        self, service
    ):
        """
        GIVEN property data with unknown city/state
        WHEN extracting MSA code
        THEN it should default to NYC MSA
        """
        # Arrange
        property_data_unknown = SimplifiedPropertyInput(
            property_id="test",
            property_name="Test Unknown Property",
            analysis_date=date.today(),
            purchase_price=1000000,
            city="Unknown City",
            state="ZZ",
            msa_code=None,
            residential_units=ResidentialUnits(
                total_units=5, average_rent_per_unit=1000
            ),
            equity_structure=InvestorEquityStructure(
                investor_equity_share_pct=80, self_cash_percentage=20
            ),
            renovation_info=RenovationInfo(
                status=RenovationStatus.PLANNED, anticipated_duration_months=3
            ),
        )

        # Act
        msa_code = service._extract_msa_code(property_data_unknown)

        # Assert
        assert msa_code == "35620"  # Default NYC MSA

    def test_get_assumption_summary_should_return_key_metrics(
        self, service, sample_monte_carlo_scenario, sample_property_data
    ):
        """
        GIVEN valid DCF assumptions
        WHEN getting assumption summary
        THEN it should return dictionary with key metrics
        """
        # Arrange
        dcf_assumptions = service.create_dcf_assumptions_from_scenario(
            sample_monte_carlo_scenario, sample_property_data
        )

        # Act
        summary = service.get_assumption_summary(dcf_assumptions)

        # Assert
        assert "scenario_id" in summary
        assert "property_id" in summary
        assert "year_1_mortgage_rate" in summary
        assert "exit_cap_rate" in summary
        assert "avg_rent_growth" in summary
        assert "ltv_ratio" in summary
        assert "investor_equity_share" in summary
        assert summary["scenario_id"] == "test_scenario_001"
        assert summary["property_id"] == "test_property_123"

    @patch("src.application.services.dcf_assumptions_service.get_logger")
    def test_create_dcf_assumptions_should_log_success(
        self, mock_logger, service, sample_monte_carlo_scenario, sample_property_data
    ):
        """
        GIVEN valid inputs
        WHEN creating DCF assumptions
        THEN it should log success message
        """
        # Arrange
        mock_logger_instance = Mock()
        mock_logger.return_value = mock_logger_instance
        service.logger = mock_logger_instance

        # Act
        service.create_dcf_assumptions_from_scenario(
            sample_monte_carlo_scenario, sample_property_data
        )

        # Assert
        mock_logger_instance.info.assert_called()
        logged_message = mock_logger_instance.info.call_args[0][0]
        assert "Created DCF assumptions for scenario" in logged_message
