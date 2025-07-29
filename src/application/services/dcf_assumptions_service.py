"""
DCF Assumptions Service

Application service that converts Monte Carlo scenarios and property data
into DCF assumptions for financial analysis.
"""

from datetime import date
from typing import Any, Dict, List

from core.exceptions import ValidationError
from core.logging_config import get_logger
from src.domain.entities.dcf_assumptions import (
    MONTE_CARLO_PARAMETER_MAPPING,
    DCFAssumptions,
    validate_monte_carlo_parameters,
)
from src.domain.entities.property_data import SimplifiedPropertyInput


class DCFAssumptionsService:
    """Service for creating and managing DCF assumptions."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def create_dcf_assumptions_from_scenario(
        self,
        monte_carlo_scenario: Dict[str, Any],
        property_data: SimplifiedPropertyInput,
    ) -> DCFAssumptions:
        """
        Create DCF assumptions from a Monte Carlo scenario and property data.

        Args:
            monte_carlo_scenario: Dictionary containing scenario data with forecasted_parameters
            property_data: SimplifiedPropertyInput containing property-specific data

        Returns:
            DCFAssumptions object with all parameters mapped

        Raises:
            ValidationError: If required parameters are missing or invalid
        """
        try:
            # Validate scenario structure
            self._validate_scenario_structure(monte_carlo_scenario)

            # Extract forecasted parameters
            forecasted_params = monte_carlo_scenario["forecasted_parameters"]

            # Validate Monte Carlo parameters
            validation_issues = validate_monte_carlo_parameters(forecasted_params)
            if validation_issues:
                raise ValidationError(
                    f"Monte Carlo validation failed: {'; '.join(validation_issues)}"
                )

            # Create DCF assumptions
            dcf_assumptions = DCFAssumptions(
                scenario_id=monte_carlo_scenario.get(
                    "scenario_id", f"scenario_{date.today().strftime('%Y%m%d')}"
                ),
                msa_code=self._extract_msa_code(property_data),
                property_id=property_data.property_id,
                # Map forecasted parameters using our mapping
                commercial_mortgage_rate=forecasted_params[
                    MONTE_CARLO_PARAMETER_MAPPING["commercial_mortgage_rate"]
                ],
                treasury_10y_rate=forecasted_params[
                    MONTE_CARLO_PARAMETER_MAPPING["treasury_10y_rate"]
                ],
                fed_funds_rate=forecasted_params[
                    MONTE_CARLO_PARAMETER_MAPPING["fed_funds_rate"]
                ],
                cap_rate=forecasted_params[MONTE_CARLO_PARAMETER_MAPPING["cap_rate"]],
                rent_growth_rate=forecasted_params[
                    MONTE_CARLO_PARAMETER_MAPPING["rent_growth_rate"]
                ],
                expense_growth_rate=forecasted_params[
                    MONTE_CARLO_PARAMETER_MAPPING["expense_growth_rate"]
                ],
                property_growth_rate=forecasted_params[
                    MONTE_CARLO_PARAMETER_MAPPING["property_growth_rate"]
                ],
                vacancy_rate=forecasted_params[
                    MONTE_CARLO_PARAMETER_MAPPING["vacancy_rate"]
                ],
                # Static parameters (use first value from forecasted arrays)
                ltv_ratio=forecasted_params[MONTE_CARLO_PARAMETER_MAPPING["ltv_ratio"]][
                    0
                ],
                closing_cost_pct=forecasted_params[
                    MONTE_CARLO_PARAMETER_MAPPING["closing_cost_pct"]
                ][0],
                lender_reserves_months=forecasted_params[
                    MONTE_CARLO_PARAMETER_MAPPING["lender_reserves"]
                ][0],
                # Investment structure from property data
                investor_equity_share=property_data.equity_structure.investor_equity_share_pct
                / 100,
                preferred_return_rate=0.06,  # Default 6% - could be parameterized
                self_cash_percentage=property_data.equity_structure.self_cash_percentage
                / 100,
            )

            self.logger.info(
                f"Created DCF assumptions for scenario {dcf_assumptions.scenario_id}, "
                f"property {dcf_assumptions.property_id}"
            )

            return dcf_assumptions

        except Exception as e:
            self.logger.error(f"Failed to create DCF assumptions: {str(e)}")
            raise ValidationError(f"DCF assumptions creation failed: {str(e)}") from e

    def create_dcf_assumptions_batch(
        self,
        monte_carlo_results: Dict[str, Any],
        property_data: SimplifiedPropertyInput,
    ) -> List[DCFAssumptions]:
        """
        Create DCF assumptions for all scenarios in a Monte Carlo results set.

        Args:
            monte_carlo_results: Dictionary containing multiple scenarios
            property_data: SimplifiedPropertyInput containing property-specific data

        Returns:
            List of DCFAssumptions objects, one per scenario
        """
        try:
            scenarios = monte_carlo_results.get("scenarios", [])
            if not scenarios:
                raise ValidationError("No scenarios found in Monte Carlo results")

            dcf_assumptions_list = []

            for i, scenario in enumerate(scenarios):
                try:
                    dcf_assumptions = self.create_dcf_assumptions_from_scenario(
                        scenario, property_data
                    )
                    dcf_assumptions_list.append(dcf_assumptions)

                except Exception as e:
                    self.logger.warning(f"Failed to process scenario {i}: {str(e)}")
                    # Continue processing other scenarios
                    continue

            self.logger.info(
                f"Created {len(dcf_assumptions_list)} DCF assumptions from "
                f"{len(scenarios)} scenarios for property {property_data.property_id}"
            )

            if not dcf_assumptions_list:
                raise ValidationError(
                    "No valid DCF assumptions could be created from Monte Carlo results"
                )

            return dcf_assumptions_list

        except Exception as e:
            self.logger.error(f"Batch DCF assumptions creation failed: {str(e)}")
            raise

    def validate_assumptions_compatibility(
        self, assumptions: DCFAssumptions
    ) -> List[str]:
        """
        Validate that DCF assumptions are compatible with Excel model expectations.

        Args:
            assumptions: DCFAssumptions to validate

        Returns:
            List of validation issues (empty if valid)
        """
        issues = []

        try:
            # Check interest rate reasonableness
            for year, rate in enumerate(assumptions.commercial_mortgage_rate):
                if rate < 0.02 or rate > 0.15:
                    issues.append(
                        f"Commercial mortgage rate Year {year}: {rate:.1%} seems unreasonable"
                    )

            # Check cap rate progression (shouldn't vary wildly)
            cap_rates = assumptions.cap_rate
            for i in range(1, len(cap_rates)):
                year_change = abs(cap_rates[i] - cap_rates[i - 1])
                if year_change > 0.02:  # More than 2% change year-over-year
                    issues.append(
                        f"Large cap rate change Year {i-1} to {i}: "
                        f"{cap_rates[i-1]:.1%} to {cap_rates[i]:.1%}"
                    )

            # Check growth rates are reasonable
            for year, growth in enumerate(assumptions.rent_growth_rate):
                if growth < -0.05 or growth > 0.15:
                    issues.append(
                        f"Rent growth Year {year}: {growth:.1%} seems extreme"
                    )

            for year, growth in enumerate(assumptions.expense_growth_rate):
                if growth < -0.02 or growth > 0.10:
                    issues.append(
                        f"Expense growth Year {year}: {growth:.1%} seems extreme"
                    )

            # Check investment structure makes sense
            if (
                assumptions.investor_equity_share
                + (1 - assumptions.investor_equity_share)
                != 1.0
            ):
                issues.append("Investor equity share should complement to 100%")

            # Check LTV and cash percentage compatibility
            debt_financing = assumptions.ltv_ratio
            cash_financing = assumptions.self_cash_percentage
            if debt_financing + cash_financing > 1.1:  # Allow some flexibility
                issues.append(
                    f"LTV ({debt_financing:.1%}) + Cash ({cash_financing:.1%}) > 100%"
                )

        except Exception as e:
            issues.append(f"Validation error: {str(e)}")

        return issues

    def _validate_scenario_structure(self, scenario: Dict[str, Any]):
        """Validate that scenario has required structure."""
        if "forecasted_parameters" not in scenario:
            raise ValidationError("Scenario missing 'forecasted_parameters'")

        if not isinstance(scenario["forecasted_parameters"], dict):
            raise ValidationError("'forecasted_parameters' must be a dictionary")

    def _extract_msa_code(self, property_data: SimplifiedPropertyInput) -> str:
        """Extract MSA code from property data."""
        if property_data.msa_code:
            return property_data.msa_code

        # Try to derive from city/state if MSA code not provided
        if property_data.city and property_data.state:
            msa_mappings = {
                ("NEW YORK", "NY"): "35620",
                ("LOS ANGELES", "CA"): "31080",
                ("CHICAGO", "IL"): "16980",
                ("WASHINGTON", "DC"): "47900",
                ("MIAMI", "FL"): "33100",
            }

            city_state_key = (property_data.city.upper(), property_data.state.upper())
            if city_state_key in msa_mappings:
                return msa_mappings[city_state_key]

        # Default MSA if none can be determined
        self.logger.warning(
            f"Could not determine MSA code for property {property_data.property_id}, "
            f"using default NYC MSA"
        )
        return "35620"  # Default to NYC MSA

    def get_assumption_summary(self, assumptions: DCFAssumptions) -> Dict[str, Any]:
        """Get summary of key assumptions for reporting."""
        return {
            "scenario_id": assumptions.scenario_id,
            "property_id": assumptions.property_id,
            "msa_code": assumptions.msa_code,
            # Key financial assumptions
            "year_1_mortgage_rate": assumptions.commercial_mortgage_rate[1],
            "exit_cap_rate": assumptions.cap_rate[5],
            "avg_rent_growth": sum(assumptions.rent_growth_rate[1:])
            / 5,  # Years 1-5 average
            "avg_expense_growth": sum(assumptions.expense_growth_rate[1:]) / 5,
            "ltv_ratio": assumptions.ltv_ratio,
            "investor_equity_share": assumptions.investor_equity_share,
            "preferred_return": assumptions.preferred_return_rate,
            # Risk indicators
            "mortgage_rate_volatility": max(assumptions.commercial_mortgage_rate)
            - min(assumptions.commercial_mortgage_rate),
            "cap_rate_volatility": max(assumptions.cap_rate)
            - min(assumptions.cap_rate),
            "max_vacancy_rate": max(assumptions.vacancy_rate),
        }


# Convenience functions for easy usage
def create_dcf_assumptions(
    monte_carlo_scenario: Dict[str, Any], property_data: SimplifiedPropertyInput
) -> DCFAssumptions:
    """Convenience function to create DCF assumptions."""
    service = DCFAssumptionsService()
    return service.create_dcf_assumptions_from_scenario(
        monte_carlo_scenario, property_data
    )


def create_dcf_assumptions_batch(
    monte_carlo_results: Dict[str, Any], property_data: SimplifiedPropertyInput
) -> List[DCFAssumptions]:
    """Convenience function to create batch DCF assumptions."""
    service = DCFAssumptionsService()
    return service.create_dcf_assumptions_batch(monte_carlo_results, property_data)
