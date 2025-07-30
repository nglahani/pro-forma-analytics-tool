"""
Unit Tests for Monte Carlo Service

Tests the Monte Carlo application service following BDD/TDD principles.
"""

from datetime import date
from unittest.mock import Mock, patch

import pytest

from src.application.services.monte_carlo_service import MonteCarloApplicationService
from src.domain.entities.monte_carlo import (
    CorrelationMatrix,
    MarketScenario,
    Scenario,
    ScenarioId,
    ScenarioMetrics,
    SimulationRequest,
    SimulationResult,
    SimulationSummary,
)


class TestMonteCarloApplicationService:
    """Test cases for MonteCarloApplicationService."""

    @pytest.fixture
    def mock_simulation_repository(self):
        """Mock simulation repository."""
        return Mock()

    @pytest.fixture
    def mock_forecasting_service(self):
        """Mock forecasting service."""
        return Mock()

    @pytest.fixture
    def mock_monte_carlo_engine(self):
        """Mock Monte Carlo engine."""
        return Mock()

    @pytest.fixture
    def service(
        self,
        mock_simulation_repository,
        mock_forecasting_service,
        mock_monte_carlo_engine,
    ):
        """Create service instance for testing."""
        return MonteCarloApplicationService(
            simulation_repository=mock_simulation_repository,
            forecasting_service=mock_forecasting_service,
            monte_carlo_engine=mock_monte_carlo_engine,
        )

    @pytest.fixture
    def sample_simulation_request(self):
        """Sample simulation request for testing."""
        return SimulationRequest(
            property_id="test_property_123",
            msa_code="35620",
            num_scenarios=2,  # Use small number for testing
            horizon_years=5,
            use_correlations=True,
            confidence_level=0.95,
        )

    @pytest.fixture
    def sample_scenarios(self):
        """Sample scenarios for testing."""
        scenarios = []
        for i in range(2):  # Match the num_scenarios
            scenario = Scenario(
                scenario_id=ScenarioId("test_simulation", i),
                parameter_values={"cap_rate": [0.05, 0.05, 0.05, 0.05, 0.05]},
                metrics=ScenarioMetrics(
                    growth_score=0.5,
                    risk_score=0.5,
                    market_scenario=MarketScenario.NEUTRAL_MARKET,
                    volatility_measures={},
                ),
            )
            scenarios.append(scenario)
        return scenarios

    def test_run_simulation_should_return_valid_simulation_result(
        self,
        service,
        sample_simulation_request,
        sample_scenarios,
        mock_forecasting_service,
        mock_monte_carlo_engine,
    ):
        """
        GIVEN valid simulation request
        WHEN running simulation
        THEN it should return valid SimulationResult
        """
        # Arrange
        mock_forecasting_service.generate_multiple_forecasts.return_value = []
        mock_monte_carlo_engine.run_simulation.return_value = SimulationResult(
            simulation_id="test_simulation_001",
            request=sample_simulation_request,
            scenarios=sample_scenarios,
            summary=SimulationSummary(
                parameter_statistics={},
                scenario_distribution={MarketScenario.NEUTRAL_MARKET: 2},
                extreme_scenarios={},
            ),
            correlation_matrix=None,
            simulation_date=date.today(),
            computation_time_seconds=1.5,
        )

        # Act
        result = service.run_simulation(sample_simulation_request)

        # Assert
        assert isinstance(result, SimulationResult)
        assert result.simulation_id == "test_simulation_001"
        assert result.request.msa_code == "35620"
        assert result.request.num_scenarios == 2

    def test_run_simulation_should_generate_forecasts_for_all_parameters(
        self,
        service,
        sample_simulation_request,
        sample_scenarios,
        mock_forecasting_service,
        mock_monte_carlo_engine,
    ):
        """
        GIVEN simulation request with multiple parameters
        WHEN running simulation
        THEN it should generate forecasts for all parameters
        """
        # Arrange
        mock_forecasting_service.generate_multiple_forecasts.return_value = []
        mock_monte_carlo_engine.run_simulation.return_value = SimulationResult(
            simulation_id="test_simulation_001",
            request=sample_simulation_request,
            scenarios=sample_scenarios,
            summary=SimulationSummary(
                parameter_statistics={},
                scenario_distribution={MarketScenario.NEUTRAL_MARKET: 2},
                extreme_scenarios={},
            ),
            correlation_matrix=None,
            simulation_date=date.today(),
            computation_time_seconds=1.5,
        )

        # Act
        service.run_simulation(sample_simulation_request)

        # Assert
        # Should call generate_multiple_forecasts
        mock_forecasting_service.generate_multiple_forecasts.assert_called_once()

    def test_run_simulation_should_save_results_to_repository(
        self,
        service,
        sample_simulation_request,
        sample_scenarios,
        mock_simulation_repository,
        mock_forecasting_service,
        mock_monte_carlo_engine,
    ):
        """
        GIVEN completed simulation
        WHEN running simulation
        THEN it should save results to repository
        """
        # Arrange
        mock_forecasting_service.generate_multiple_forecasts.return_value = []
        simulation_result = SimulationResult(
            simulation_id="test_simulation_001",
            request=sample_simulation_request,
            scenarios=sample_scenarios,
            summary=SimulationSummary(
                parameter_statistics={},
                scenario_distribution={MarketScenario.NEUTRAL_MARKET: 2},
                extreme_scenarios={},
            ),
            correlation_matrix=None,
            simulation_date=date.today(),
            computation_time_seconds=1.5,
        )
        mock_monte_carlo_engine.run_simulation.return_value = simulation_result

        # Act
        service.run_simulation(sample_simulation_request)

        # Assert - Check that save_simulation_result was called (ignore timing-dependent fields)
        mock_simulation_repository.save_simulation_result.assert_called_once()
        saved_result = mock_simulation_repository.save_simulation_result.call_args[0][0]

        # Verify key fields match
        assert saved_result.simulation_id == simulation_result.simulation_id
        assert saved_result.request == simulation_result.request
        assert len(saved_result.scenarios) == len(simulation_result.scenarios)
        assert saved_result.correlation_matrix == simulation_result.correlation_matrix
        assert saved_result.simulation_date == simulation_result.simulation_date
        # Don't check computation_time_seconds as it's timing-dependent

    def test_run_simulation_with_correlation_analysis_should_build_correlation_matrix(
        self,
        service,
        sample_simulation_request,
        sample_scenarios,
        mock_forecasting_service,
        mock_monte_carlo_engine,
    ):
        """
        GIVEN simulation request with correlation analysis enabled
        WHEN running simulation
        THEN it should build correlation matrix
        """
        # Arrange
        sample_simulation_request.use_correlations = True
        mock_forecasting_service.generate_multiple_forecasts.return_value = []
        mock_monte_carlo_engine.run_simulation.return_value = SimulationResult(
            simulation_id="test_simulation_001",
            request=sample_simulation_request,
            scenarios=sample_scenarios,
            summary=SimulationSummary(
                parameter_statistics={},
                scenario_distribution={MarketScenario.NEUTRAL_MARKET: 2},
                extreme_scenarios={},
            ),
            correlation_matrix=CorrelationMatrix(
                parameter_names=["cap_rate", "rent_growth"],
                matrix=[[1.0, 0.2], [0.2, 1.0]],
                creation_date=date.today(),
            ),
            simulation_date=date.today(),
            computation_time_seconds=1.5,
        )

        # Act
        result = service.run_simulation(sample_simulation_request)

        # Assert
        assert result.correlation_matrix is not None
        assert isinstance(result.correlation_matrix, CorrelationMatrix)

    def test_get_simulation_results_should_return_cached_results(
        self, service, mock_simulation_repository
    ):
        """
        GIVEN saved simulation results
        WHEN getting simulation results by MSA
        THEN it should return cached results from repository
        """
        # Arrange
        expected_results = [
            SimulationResult(
                simulation_id="test_1",
                request=SimulationRequest(
                    property_id="test_property_123",
                    msa_code="35620",
                    num_scenarios=1,
                    horizon_years=5,
                ),
                scenarios=[
                    Scenario(
                        scenario_id=ScenarioId("test_simulation", 1),
                        parameter_values={"cap_rate": [0.05, 0.05, 0.05, 0.05, 0.05]},
                        metrics=ScenarioMetrics(
                            growth_score=0.5,
                            risk_score=0.5,
                            market_scenario=MarketScenario.NEUTRAL_MARKET,
                            volatility_measures={},
                        ),
                    )
                ],
                summary=SimulationSummary(
                    parameter_statistics={},
                    scenario_distribution={MarketScenario.NEUTRAL_MARKET: 1},
                    extreme_scenarios={},
                ),
                correlation_matrix=None,
                simulation_date=date.today(),
                computation_time_seconds=1.5,
            )
        ]
        mock_simulation_repository.get_simulation_results_by_msa.return_value = (
            expected_results
        )

        # Act
        result = service.get_simulation_results(msa_code="35620")

        # Assert
        assert result == expected_results
        mock_simulation_repository.get_simulation_results_by_msa.assert_called_once_with(
            "35620", limit=10
        )

    def test_run_simulation_with_invalid_request_should_raise_validation_error(
        self, service, mock_forecasting_service
    ):
        """
        GIVEN invalid simulation request
        WHEN running simulation
        THEN it should raise ValidationError
        """
        # Arrange - create invalid request
        with pytest.raises(ValueError):
            invalid_request = SimulationRequest(
                property_id="",  # Invalid empty property ID
                msa_code="35620",
                num_scenarios=0,  # Invalid zero scenarios
                horizon_years=0,  # Invalid zero horizon
            )

    def test_run_simulation_with_forecasting_failure_should_handle_gracefully(
        self,
        service,
        sample_simulation_request,
        mock_forecasting_service,
        mock_monte_carlo_engine,
    ):
        """
        GIVEN forecasting service failure
        WHEN running simulation
        THEN it should handle gracefully
        """
        # Arrange
        mock_forecasting_service.generate_multiple_forecasts.side_effect = Exception(
            "Forecasting failed"
        )

        # Act & Assert
        with pytest.raises(Exception):
            service.run_simulation(sample_simulation_request)

    @patch("src.application.services.monte_carlo_service.time")
    def test_run_simulation_should_track_execution_time(
        self,
        mock_time,
        service,
        sample_simulation_request,
        sample_scenarios,
        mock_forecasting_service,
        mock_monte_carlo_engine,
    ):
        """
        GIVEN simulation execution
        WHEN running simulation
        THEN it should track execution time
        """
        # Arrange
        mock_time.time.side_effect = [0.0, 2.5]  # Start and end times
        mock_forecasting_service.generate_multiple_forecasts.return_value = []
        mock_monte_carlo_engine.run_simulation.return_value = SimulationResult(
            simulation_id="test_simulation_001",
            request=sample_simulation_request,
            scenarios=sample_scenarios,
            summary=SimulationSummary(
                parameter_statistics={},
                scenario_distribution={MarketScenario.NEUTRAL_MARKET: 2},
                extreme_scenarios={},
            ),
            correlation_matrix=None,
            simulation_date=date.today(),
            computation_time_seconds=2.5,
        )

        # Act
        result = service.run_simulation(sample_simulation_request)

        # Assert
        assert result.computation_time_seconds > 0

    def test_validate_simulation_quality_should_return_quality_metrics(self, service):
        """
        GIVEN simulation result
        WHEN validating simulation quality
        THEN it should return quality metrics
        """
        # Arrange
        scenarios = []
        for i in range(5):  # Use 5 scenarios for quality test
            scenario = Scenario(
                scenario_id=ScenarioId("test_simulation", i),
                parameter_values={"cap_rate": [0.05, 0.05, 0.05, 0.05, 0.05]},
                metrics=ScenarioMetrics(
                    growth_score=0.5,
                    risk_score=0.5,
                    market_scenario=MarketScenario.NEUTRAL_MARKET,
                    volatility_measures={},
                ),
            )
            scenarios.append(scenario)

        simulation_result = SimulationResult(
            simulation_id="test_simulation_001",
            request=SimulationRequest(
                property_id="test_property_123",
                msa_code="35620",
                num_scenarios=5,  # Match scenarios count
                horizon_years=5,
            ),
            scenarios=scenarios,
            summary=SimulationSummary(
                parameter_statistics={},
                scenario_distribution={MarketScenario.NEUTRAL_MARKET: 5},
                extreme_scenarios={},
            ),
            correlation_matrix=None,
            simulation_date=date.today(),
            computation_time_seconds=1.5,
        )

        # Act
        quality_metrics = service.validate_simulation_quality(simulation_result)

        # Assert
        assert isinstance(quality_metrics, dict)
        assert "scenario_count_valid" in quality_metrics
        assert "overall_quality" in quality_metrics

    def test_analyze_parameter_trends_should_return_trend_statistics(
        self, service, mock_simulation_repository
    ):
        """
        GIVEN parameter trend analysis request
        WHEN analyzing parameter trends
        THEN it should return trend statistics
        """
        # Arrange
        expected_stats = {"mean": 0.055, "std": 0.01, "trend": "increasing"}
        mock_simulation_repository.get_simulation_summary_stats.return_value = (
            expected_stats
        )

        # Act
        result = service.analyze_parameter_trends("35620", "cap_rate", 90)

        # Assert
        assert result == expected_stats
        mock_simulation_repository.get_simulation_summary_stats.assert_called_once()
