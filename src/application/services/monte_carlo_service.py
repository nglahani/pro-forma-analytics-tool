"""
Monte Carlo Application Service

Orchestrates Monte Carlo simulation workflows using clean architecture principles.
"""

from datetime import date
from typing import List, Dict, Optional
import logging
import time

from ...domain.entities.monte_carlo import (
    SimulationRequest,
    SimulationResult,
    CorrelationMatrix,
)
from ...domain.entities.forecast import ParameterId
from ...domain.repositories.simulation_repository import SimulationRepository
from .forecasting_service import ForecastingApplicationService


class MonteCarloApplicationService:
    """Application service for Monte Carlo simulation workflows."""

    def __init__(
        self,
        simulation_repository: SimulationRepository,
        forecasting_service: ForecastingApplicationService,
        monte_carlo_engine: "MonteCarloEngine",  # Forward reference
        logger: Optional[logging.Logger] = None,
    ):
        self._simulation_repo = simulation_repository
        self._forecasting_service = forecasting_service
        self._monte_carlo_engine = monte_carlo_engine
        self._logger = logger or logging.getLogger(__name__)

    def run_simulation(self, request: SimulationRequest) -> SimulationResult:
        """
        Run a complete Monte Carlo simulation.

        This method orchestrates the simulation workflow:
        1. Generate/retrieve forecasts for all parameters
        2. Build correlation matrix if requested
        3. Run Monte Carlo simulation
        4. Calculate scenario metrics and classifications
        5. Save results

        Args:
            request: Simulation request parameters

        Returns:
            SimulationResult containing all scenarios and analysis

        Raises:
            SimulationError: If simulation fails
            DataNotFoundError: If required data is missing
        """
        start_time = time.time()

        self._logger.info(
            f"Starting Monte Carlo simulation: {request.num_scenarios} scenarios, "
            f"{request.horizon_years} years, MSA {request.msa_code}"
        )

        try:
            # Step 1: Get required parameter IDs for the MSA
            parameter_ids = self._get_required_parameter_ids(request.msa_code)

            # Step 2: Generate forecasts for all parameters
            forecasts = self._forecasting_service.generate_multiple_forecasts(
                parameter_ids=parameter_ids,
                horizon_years=request.horizon_years,
                model_type="prophet",
                confidence_level=request.confidence_level,
            )

            if len(forecasts) != len(parameter_ids):
                missing_count = len(parameter_ids) - len(forecasts)
                self._logger.warning(f"Missing {missing_count} forecasts")

            # Step 3: Build correlation matrix if requested
            correlation_matrix = None
            if request.use_correlations:
                correlation_matrix = self._monte_carlo_engine.build_correlation_matrix(
                    forecasts, request.msa_code
                )

            # Step 4: Run Monte Carlo simulation
            simulation_result = self._monte_carlo_engine.run_simulation(
                request=request,
                forecasts=forecasts,
                correlation_matrix=correlation_matrix,
            )

            # Update computation time
            computation_time = time.time() - start_time
            # Create new result with updated computation time since dataclass is frozen
            from dataclasses import replace

            simulation_result = replace(
                simulation_result, computation_time_seconds=computation_time
            )

            # Step 5: Save results
            self._simulation_repo.save_simulation_result(simulation_result)

            self._logger.info(
                f"Completed simulation {simulation_result.simulation_id} "
                f"in {computation_time:.2f} seconds"
            )

            return simulation_result

        except Exception as e:
            computation_time = time.time() - start_time
            self._logger.error(
                f"Simulation failed after {computation_time:.2f} seconds: {e}"
            )
            raise SimulationError(f"Monte Carlo simulation failed: {e}") from e

    def get_simulation_results(
        self,
        property_id: Optional[str] = None,
        msa_code: Optional[str] = None,
        limit: int = 10,
    ) -> List[SimulationResult]:
        """
        Retrieve historical simulation results.

        Args:
            property_id: Optional property filter
            msa_code: Optional MSA filter
            limit: Maximum number of results

        Returns:
            List of simulation results
        """
        if property_id:
            return self._simulation_repo.get_simulation_results_for_property(
                property_id, limit
            )
        elif msa_code:
            return self._simulation_repo.get_simulation_results_by_msa(
                msa_code, limit=limit
            )
        else:
            raise ValueError("Must specify either property_id or msa_code")

    def analyze_parameter_trends(
        self, msa_code: str, parameter_name: str, days_back: int = 90
    ) -> Optional[Dict[str, float]]:
        """
        Analyze trends for a parameter across recent simulations.

        Args:
            msa_code: MSA identifier
            parameter_name: Parameter to analyze
            days_back: How many days back to analyze

        Returns:
            Dictionary of trend statistics if data available
        """
        end_date = date.today()
        start_date = date.fromordinal(end_date.toordinal() - days_back)

        return self._simulation_repo.get_simulation_summary_stats(
            msa_code=msa_code,
            parameter_name=parameter_name,
            start_date=start_date,
            end_date=end_date,
        )

    def validate_simulation_quality(
        self,
        simulation_result: SimulationResult,
        quality_checks: Optional[Dict[str, any]] = None,
    ) -> Dict[str, bool]:
        """
        Validate simulation quality and completeness.

        Args:
            simulation_result: Simulation to validate
            quality_checks: Optional custom quality checks

        Returns:
            Dictionary of quality check results
        """
        checks = quality_checks or {}
        results = {}

        # Check scenario count
        expected_scenarios = simulation_result.request.num_scenarios
        actual_scenarios = len(simulation_result.scenarios)
        results["scenario_count_valid"] = actual_scenarios == expected_scenarios

        # Check parameter completeness
        first_scenario = (
            simulation_result.scenarios[0] if simulation_result.scenarios else None
        )
        if first_scenario:
            expected_params = 11  # All pro forma parameters
            actual_params = len(first_scenario.parameter_values)
            results["parameter_completeness"] = actual_params >= expected_params * 0.9
        else:
            results["parameter_completeness"] = False

        # Check correlation matrix validity
        if simulation_result.correlation_matrix:
            matrix_size = len(simulation_result.correlation_matrix.parameter_names)
            results["correlation_matrix_valid"] = matrix_size >= 5
        else:
            results["correlation_matrix_valid"] = (
                not simulation_result.request.use_correlations
            )

        # Check scenario diversity
        if simulation_result.scenarios:
            growth_scores = [
                s.metrics.growth_score for s in simulation_result.scenarios
            ]
            growth_std = (
                float(
                    sum(
                        (x - sum(growth_scores) / len(growth_scores)) ** 2
                        for x in growth_scores
                    )
                    / len(growth_scores)
                )
                ** 0.5
            )
            results["scenario_diversity"] = growth_std > 0.01  # Minimum diversity
        else:
            results["scenario_diversity"] = False

        # Overall quality
        results["overall_quality"] = all(results.values())

        # Log quality summary
        passed_checks = sum(results.values())
        total_checks = len(results) - 1  # Exclude overall_quality
        self._logger.info(
            f"Simulation quality: {passed_checks}/{total_checks} checks passed"
        )

        return results

    def cleanup_old_simulations(self, older_than_days: int = 90) -> int:
        """
        Clean up old simulation results to manage storage.

        Args:
            older_than_days: Delete simulations older than this many days

        Returns:
            Number of simulations deleted
        """
        deleted_count = self._simulation_repo.delete_old_simulations(older_than_days)

        if deleted_count > 0:
            self._logger.info(f"Cleaned up {deleted_count} old simulation results")

        return deleted_count

    def _get_required_parameter_ids(self, msa_code: str) -> List[ParameterId]:
        """
        Get the list of required parameter IDs for a simulation.

        Args:
            msa_code: MSA identifier

        Returns:
            List of parameter IDs needed for simulation
        """
        # Standard pro forma parameters
        required_params = [
            ("treasury_10y", "NATIONAL"),
            ("commercial_mortgage_rate", "NATIONAL"),
            ("fed_funds_rate", "NATIONAL"),
            ("cap_rate", msa_code),
            ("vacancy_rate", msa_code),
            ("rent_growth", msa_code),
            ("expense_growth", msa_code),
            ("ltv_ratio", msa_code),
            ("closing_cost_pct", msa_code),
            ("lender_reserves", msa_code),
            ("property_growth", msa_code),
        ]

        parameter_ids = []
        for param_name, geo_code in required_params:
            # Import here to avoid circular imports
            from ...domain.entities.forecast import ParameterId, ParameterType

            param_id = ParameterId(
                name=param_name,
                geographic_code=geo_code,
                parameter_type=self._get_parameter_type(param_name),
            )
            parameter_ids.append(param_id)

        return parameter_ids

    def _get_parameter_type(self, param_name: str) -> "ParameterType":
        """Map parameter name to type."""
        from ...domain.entities.forecast import ParameterType

        type_mapping = {
            "treasury_10y": ParameterType.INTEREST_RATE,
            "commercial_mortgage_rate": ParameterType.INTEREST_RATE,
            "fed_funds_rate": ParameterType.INTEREST_RATE,
            "cap_rate": ParameterType.MARKET_METRIC,
            "vacancy_rate": ParameterType.MARKET_METRIC,
            "rent_growth": ParameterType.GROWTH_METRIC,
            "expense_growth": ParameterType.GROWTH_METRIC,
            "property_growth": ParameterType.GROWTH_METRIC,
            "ltv_ratio": ParameterType.LENDING_REQUIREMENT,
            "closing_cost_pct": ParameterType.LENDING_REQUIREMENT,
            "lender_reserves": ParameterType.LENDING_REQUIREMENT,
        }

        return type_mapping.get(param_name, ParameterType.MARKET_METRIC)


class SimulationError(Exception):
    """Raised when Monte Carlo simulation fails."""

    pass
