"""
Unit tests for DCF Assumptions functionality.

Tests the conversion of Monte Carlo scenarios to DCF assumptions.
"""

import pytest
from datetime import date
from src.domain.entities.dcf_assumptions import (
    DCFAssumptions,
    validate_monte_carlo_parameters,
)
from src.application.services.dcf_assumptions_service import DCFAssumptionsService
from src.domain.entities.property_data import (
    SimplifiedPropertyInput,
    ResidentialUnits,
    CommercialUnits,
    RenovationInfo,
    InvestorEquityStructure,
    RenovationStatus,
)
from core.exceptions import ValidationError


class TestDCFAssumptions:
    """Test DCF Assumptions entity."""

    def test_dcf_assumptions_creation(self):
        """Test basic DCF assumptions creation."""
        assumptions = DCFAssumptions(
            scenario_id="test_scenario_001",
            msa_code="35620",
            property_id="test_property_001",
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
            investor_equity_share=0.80,
            preferred_return_rate=0.06,
            self_cash_percentage=0.25,
        )

        assert assumptions.scenario_id == "test_scenario_001"
        assert assumptions.msa_code == "35620"
        assert assumptions.ltv_ratio == 0.75
        assert len(assumptions.commercial_mortgage_rate) == 6

    def test_get_year_assumptions(self):
        """Test getting assumptions for a specific year."""
        assumptions = DCFAssumptions(
            scenario_id="test_scenario_001",
            msa_code="35620",
            property_id="test_property_001",
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
            investor_equity_share=0.80,
            preferred_return_rate=0.06,
            self_cash_percentage=0.25,
        )

        year_1_assumptions = assumptions.get_year_assumptions(1)

        assert year_1_assumptions["commercial_mortgage_rate"] == 0.065
        assert year_1_assumptions["rent_growth_rate"] == 0.03
        assert year_1_assumptions["vacancy_rate"] == 0.05

    def test_terminal_assumptions(self):
        """Test getting terminal (Year 5) assumptions."""
        assumptions = DCFAssumptions(
            scenario_id="test_scenario_001",
            msa_code="35620",
            property_id="test_property_001",
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
            investor_equity_share=0.80,
            preferred_return_rate=0.06,
            self_cash_percentage=0.25,
        )

        terminal_assumptions = assumptions.get_terminal_assumptions()

        assert terminal_assumptions["cap_rate"] == 0.065  # Exit cap rate
        assert terminal_assumptions["commercial_mortgage_rate"] == 0.073
        assert terminal_assumptions["property_growth_rate"] == 0.019

    def test_calculate_loan_amount(self):
        """Test loan amount calculation."""
        assumptions = DCFAssumptions(
            scenario_id="test_scenario_001",
            msa_code="35620",
            property_id="test_property_001",
            commercial_mortgage_rate=[0.06] * 6,
            treasury_10y_rate=[0.04] * 6,
            fed_funds_rate=[0.02] * 6,
            cap_rate=[0.07] * 6,
            rent_growth_rate=[0.0, 0.03, 0.03, 0.03, 0.03, 0.03],
            expense_growth_rate=[0.0, 0.02, 0.02, 0.02, 0.02, 0.02],
            property_growth_rate=[0.0, 0.02, 0.02, 0.02, 0.02, 0.02],
            vacancy_rate=[0.0, 0.05, 0.05, 0.05, 0.05, 0.05],
            ltv_ratio=0.75,
            closing_cost_pct=0.05,
            lender_reserves_months=3.0,
            investor_equity_share=0.80,
            preferred_return_rate=0.06,
            self_cash_percentage=0.25,
        )

        purchase_price = 1000000
        loan_amount = assumptions.calculate_loan_amount(purchase_price)

        assert loan_amount == 750000  # 75% of 1M

    def test_validation_errors(self):
        """Test validation of invalid assumptions."""
        with pytest.raises(ValidationError):
            # Invalid LTV ratio
            DCFAssumptions(
                scenario_id="test_scenario_001",
                msa_code="35620",
                property_id="test_property_001",
                commercial_mortgage_rate=[0.06] * 6,
                treasury_10y_rate=[0.04] * 6,
                fed_funds_rate=[0.02] * 6,
                cap_rate=[0.07] * 6,
                rent_growth_rate=[0.0, 0.03, 0.03, 0.03, 0.03, 0.03],
                expense_growth_rate=[0.0, 0.02, 0.02, 0.02, 0.02, 0.02],
                property_growth_rate=[0.0, 0.02, 0.02, 0.02, 0.02, 0.02],
                vacancy_rate=[0.0, 0.05, 0.05, 0.05, 0.05, 0.05],
                ltv_ratio=1.5,  # Invalid: > 100%
                closing_cost_pct=0.05,
                lender_reserves_months=3.0,
                investor_equity_share=0.80,
                preferred_return_rate=0.06,
                self_cash_percentage=0.25,
            )

    def test_serialization(self):
        """Test to_dict and from_dict serialization."""
        original = DCFAssumptions(
            scenario_id="test_scenario_001",
            msa_code="35620",
            property_id="test_property_001",
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
            investor_equity_share=0.80,
            preferred_return_rate=0.06,
            self_cash_percentage=0.25,
        )

        # Serialize
        data_dict = original.to_dict()

        # Deserialize
        restored = DCFAssumptions.from_dict(data_dict)

        assert restored.scenario_id == original.scenario_id
        assert restored.ltv_ratio == original.ltv_ratio
        assert restored.commercial_mortgage_rate == original.commercial_mortgage_rate


class TestDCFAssumptionsService:
    """Test DCF Assumptions Service."""

    def create_sample_property(self) -> SimplifiedPropertyInput:
        """Create sample property for testing."""
        return SimplifiedPropertyInput(
            property_id="TEST_PROP_001",
            property_name="Test Property",
            analysis_date=date.today(),
            residential_units=ResidentialUnits(
                total_units=20, average_rent_per_unit=2500
            ),
            commercial_units=CommercialUnits(total_units=2, average_rent_per_unit=4000),
            renovation_info=RenovationInfo(
                status=RenovationStatus.PLANNED, anticipated_duration_months=6
            ),
            equity_structure=InvestorEquityStructure(
                investor_equity_share_pct=80.0, self_cash_percentage=25.0
            ),
            city="New York",
            state="NY",
            msa_code="35620",
            purchase_price=2000000,
        )

    def create_sample_monte_carlo_scenario(self) -> dict:
        """Create sample Monte Carlo scenario for testing."""
        return {
            "scenario_id": "test_scenario_001",
            "forecasted_parameters": {
                "commercial_mortgage_rate": [0.06, 0.065, 0.067, 0.069, 0.071, 0.073],
                "treasury_10y": [0.04, 0.042, 0.044, 0.046, 0.048, 0.050],
                "fed_funds_rate": [0.02, 0.025, 0.03, 0.032, 0.034, 0.036],
                "cap_rate": [0.07, 0.07, 0.07, 0.07, 0.07, 0.065],
                "rent_growth": [0.0, 0.03, 0.032, 0.029, 0.031, 0.028],
                "expense_growth": [0.0, 0.02, 0.025, 0.022, 0.024, 0.021],
                "property_growth": [0.0, 0.02, 0.025, 0.018, 0.022, 0.019],
                "vacancy_rate": [0.0, 0.05, 0.04, 0.06, 0.045, 0.05],
                "ltv_ratio": [0.75, 0.75, 0.75, 0.75, 0.75, 0.75],
                "closing_cost_pct": [0.05, 0.05, 0.05, 0.05, 0.05, 0.05],
                "lender_reserves": [3.0, 3.0, 3.0, 3.0, 3.0, 3.0],
            },
        }

    def test_create_dcf_assumptions_from_scenario(self):
        """Test creating DCF assumptions from Monte Carlo scenario."""
        service = DCFAssumptionsService()
        property_data = self.create_sample_property()
        scenario = self.create_sample_monte_carlo_scenario()

        assumptions = service.create_dcf_assumptions_from_scenario(
            scenario, property_data
        )

        assert assumptions.scenario_id == "test_scenario_001"
        assert assumptions.property_id == "TEST_PROP_001"
        assert assumptions.msa_code == "35620"
        assert assumptions.ltv_ratio == 0.75
        assert assumptions.investor_equity_share == 0.80
        assert len(assumptions.commercial_mortgage_rate) == 6

    def test_validate_assumptions_compatibility(self):
        """Test assumptions validation."""
        service = DCFAssumptionsService()
        property_data = self.create_sample_property()
        scenario = self.create_sample_monte_carlo_scenario()

        assumptions = service.create_dcf_assumptions_from_scenario(
            scenario, property_data
        )
        issues = service.validate_assumptions_compatibility(assumptions)

        # Should have no validation issues for reasonable assumptions
        assert len(issues) == 0

    def test_get_assumption_summary(self):
        """Test getting assumption summary."""
        service = DCFAssumptionsService()
        property_data = self.create_sample_property()
        scenario = self.create_sample_monte_carlo_scenario()

        assumptions = service.create_dcf_assumptions_from_scenario(
            scenario, property_data
        )
        summary = service.get_assumption_summary(assumptions)

        assert "scenario_id" in summary
        assert "year_1_mortgage_rate" in summary
        assert "exit_cap_rate" in summary
        assert summary["ltv_ratio"] == 0.75
        assert summary["investor_equity_share"] == 0.80


class TestMonteCarloParameterValidation:
    """Test Monte Carlo parameter validation."""

    def test_validate_complete_parameters(self):
        """Test validation of complete parameter set."""
        parameters = {
            "commercial_mortgage_rate": [0.06] * 6,
            "treasury_10y": [0.04] * 6,
            "fed_funds_rate": [0.02] * 6,
            "cap_rate": [0.07] * 6,
            "rent_growth": [0.0, 0.03, 0.03, 0.03, 0.03, 0.03],
            "expense_growth": [0.0, 0.02, 0.02, 0.02, 0.02, 0.02],
            "property_growth": [0.0, 0.02, 0.02, 0.02, 0.02, 0.02],
            "vacancy_rate": [0.0, 0.05, 0.05, 0.05, 0.05, 0.05],
            "ltv_ratio": [0.75] * 6,
            "closing_cost_pct": [0.05] * 6,
            "lender_reserves": [3.0] * 6,
        }

        issues = validate_monte_carlo_parameters(parameters)
        assert len(issues) == 0

    def test_validate_missing_parameters(self):
        """Test validation with missing parameters."""
        parameters = {
            "commercial_mortgage_rate": [0.06] * 6,
            "cap_rate": [0.07] * 6,
            # Missing other required parameters
        }

        issues = validate_monte_carlo_parameters(parameters)
        assert len(issues) > 0
        assert any("Missing parameter" in issue for issue in issues)

    def test_validate_wrong_length_parameters(self):
        """Test validation with wrong length parameters."""
        parameters = {
            "commercial_mortgage_rate": [0.06] * 6,
            "treasury_10y": [0.04] * 6,
            "fed_funds_rate": [0.02] * 6,
            "cap_rate": [0.07] * 4,  # Wrong length!
            "rent_growth": [0.0, 0.03, 0.03, 0.03, 0.03, 0.03],
            "expense_growth": [0.0, 0.02, 0.02, 0.02, 0.02, 0.02],
            "property_growth": [0.0, 0.02, 0.02, 0.02, 0.02, 0.02],
            "vacancy_rate": [0.0, 0.05, 0.05, 0.05, 0.05, 0.05],
            "ltv_ratio": [0.75] * 6,
            "closing_cost_pct": [0.05] * 6,
            "lender_reserves": [3.0] * 6,
        }

        issues = validate_monte_carlo_parameters(parameters)
        assert len(issues) > 0
        assert any("should have 6 years of data" in issue for issue in issues)
