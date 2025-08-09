"""
Monte Carlo Coverage Tests

Strategic tests to improve coverage of monte carlo entities.
"""

from datetime import date

import pytest

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


class TestMonteCarloEntitiesCoverage:
    """Strategic tests for Monte Carlo entities to improve coverage."""

    def test_scenario_id_creation_and_string_representation(self):
        """Test ScenarioId creation and string conversion."""
        scenario_id = ScenarioId(simulation_id="SIM_001", scenario_number=42)

        assert scenario_id.simulation_id == "SIM_001"
        assert scenario_id.scenario_number == 42
        assert str(scenario_id) == "SIM_001_0042"

    def test_scenario_metrics_validation_errors(self):
        """Test ScenarioMetrics validation errors."""
        with pytest.raises(ValueError, match="Growth score must be between 0 and 1"):
            ScenarioMetrics(
                growth_score=1.5,  # Invalid high score
                risk_score=0.5,
                market_scenario=MarketScenario.NEUTRAL_MARKET,
                volatility_measures={},
            )

        with pytest.raises(ValueError, match="Risk score must be between 0 and 1"):
            ScenarioMetrics(
                growth_score=0.5,
                risk_score=-0.1,  # Invalid negative score
                market_scenario=MarketScenario.BULL_MARKET,
                volatility_measures={},
            )

    def test_scenario_metrics_creation(self):
        """Test ScenarioMetrics creation with valid values."""
        volatility = {"cap_rate": 0.15, "rent_growth": 0.08}
        metrics = ScenarioMetrics(
            growth_score=0.7,
            risk_score=0.3,
            market_scenario=MarketScenario.GROWTH_MARKET,
            volatility_measures=volatility,
        )

        assert metrics.growth_score == 0.7
        assert metrics.risk_score == 0.3
        assert metrics.market_scenario == MarketScenario.GROWTH_MARKET
        assert metrics.volatility_measures == volatility

    def test_scenario_validation_errors(self):
        """Test Scenario validation errors."""
        scenario_id = ScenarioId("SIM_001", 1)
        metrics = ScenarioMetrics(0.5, 0.5, MarketScenario.NEUTRAL_MARKET, {})

        with pytest.raises(ValueError, match="Scenario must contain parameter values"):
            Scenario(
                scenario_id=scenario_id,
                parameter_values={},  # Empty parameters should fail
                metrics=metrics,
            )

        with pytest.raises(
            ValueError, match="All parameters must have the same forecast horizon"
        ):
            Scenario(
                scenario_id=scenario_id,
                parameter_values={
                    "cap_rate": [0.065, 0.067],  # 2 years
                    "rent_growth": [0.03, 0.032, 0.034],  # 3 years - mismatch
                },
                metrics=metrics,
            )

    def test_scenario_creation_and_methods(self):
        """Test Scenario creation and methods."""
        scenario_id = ScenarioId("SIM_002", 5)
        metrics = ScenarioMetrics(0.6, 0.4, MarketScenario.BULL_MARKET, {})

        scenario = Scenario(
            scenario_id=scenario_id,
            parameter_values={
                "cap_rate": [0.065, 0.067, 0.069],
                "rent_growth": [0.03, 0.032, 0.034],
            },
            metrics=metrics,
            percentile_rank=75.0,
        )

        assert scenario.scenario_id == scenario_id
        assert scenario.percentile_rank == 75.0
        assert scenario.horizon_years == 3

        # Test get_parameter_average
        avg_cap_rate = scenario.get_parameter_average("cap_rate")
        expected_avg = (0.065 + 0.067 + 0.069) / 3
        assert avg_cap_rate == pytest.approx(expected_avg, abs=0.001)

        # Test parameter not found error
        with pytest.raises(ValueError, match="Parameter unknown_param not found"):
            scenario.get_parameter_average("unknown_param")

    def test_correlation_matrix_validation_errors(self):
        """Test CorrelationMatrix validation errors."""
        with pytest.raises(
            ValueError, match="Matrix dimensions must match parameter count"
        ):
            CorrelationMatrix(
                matrix=[[1.0, 0.5], [0.5, 1.0]],  # 2x2 matrix
                parameter_names=["cap_rate", "rent_growth", "vacancy"],  # 3 params
                creation_date=date.today(),
            )

        with pytest.raises(ValueError, match="Row 1 has incorrect length"):
            CorrelationMatrix(
                matrix=[[1.0, 0.5], [0.5, 0.3, 0.2]],  # Row 1 has too many columns
                parameter_names=["cap_rate", "rent_growth"],
                creation_date=date.today(),
            )

        with pytest.raises(ValueError, match="Diagonal element \\[0,0\\] must be 1.0"):
            CorrelationMatrix(
                matrix=[[0.9, 0.5], [0.5, 1.0]],  # Diagonal not 1.0
                parameter_names=["cap_rate", "rent_growth"],
                creation_date=date.today(),
            )

    def test_correlation_matrix_creation_and_methods(self):
        """Test CorrelationMatrix creation and methods."""
        matrix = [[1.0, 0.6, -0.3], [0.6, 1.0, 0.2], [-0.3, 0.2, 1.0]]
        params = ["cap_rate", "rent_growth", "vacancy_rate"]

        corr_matrix = CorrelationMatrix(
            matrix=matrix, parameter_names=params, creation_date=date(2024, 1, 15)
        )

        assert corr_matrix.matrix == matrix
        assert corr_matrix.parameter_names == params
        assert corr_matrix.creation_date == date(2024, 1, 15)

        # Test get_correlation method
        assert corr_matrix.get_correlation("cap_rate", "rent_growth") == 0.6
        assert corr_matrix.get_correlation("cap_rate", "vacancy_rate") == -0.3
        assert corr_matrix.get_correlation("rent_growth", "rent_growth") == 1.0

        # Test parameter not found error
        with pytest.raises(
            ValueError, match="Parameter not found in correlation matrix"
        ):
            corr_matrix.get_correlation("cap_rate", "unknown_param")

    def test_simulation_summary_methods(self):
        """Test SimulationSummary methods."""
        param_stats = {
            "cap_rate": {"mean": 0.065, "std": 0.01, "p5": 0.055, "p95": 0.075},
            "rent_growth": {"mean": 0.03, "std": 0.005, "p10": 0.025, "p90": 0.035},
        }

        scenario_dist = {
            MarketScenario.BULL_MARKET: 100,
            MarketScenario.NEUTRAL_MARKET: 300,
            MarketScenario.BEAR_MARKET: 100,
        }

        extreme_scenarios = {
            "highest_growth": ScenarioId("SIM_001", 42),
            "highest_risk": ScenarioId("SIM_001", 123),
        }

        summary = SimulationSummary(
            parameter_statistics=param_stats,
            scenario_distribution=scenario_dist,
            extreme_scenarios=extreme_scenarios,
        )

        # Test get_parameter_percentile
        assert summary.get_parameter_percentile("cap_rate", 5) == 0.055
        assert summary.get_parameter_percentile("rent_growth", 90) == 0.035

        # Test parameter not found error
        with pytest.raises(ValueError, match="Parameter unknown_param not found"):
            summary.get_parameter_percentile("unknown_param", 50)

        # Test percentile not available error
        with pytest.raises(ValueError, match="Percentile 50 not available"):
            summary.get_parameter_percentile("cap_rate", 50)  # p50 not in test data

    def test_simulation_request_validation_errors(self):
        """Test SimulationRequest validation errors."""
        with pytest.raises(ValueError, match="Number of scenarios must be positive"):
            SimulationRequest(
                property_id="PROP_001",
                msa_code="35620",
                num_scenarios=0,  # Invalid zero scenarios
                horizon_years=5,
            )

        with pytest.raises(ValueError, match="Horizon years must be positive"):
            SimulationRequest(
                property_id="PROP_001",
                msa_code="35620",
                num_scenarios=1000,
                horizon_years=-1,  # Invalid negative horizon
            )

        with pytest.raises(
            ValueError, match="Confidence level must be between 0 and 1"
        ):
            SimulationRequest(
                property_id="PROP_001",
                msa_code="35620",
                num_scenarios=1000,
                horizon_years=5,
                confidence_level=1.5,  # Invalid high confidence
            )

    def test_simulation_request_creation(self):
        """Test SimulationRequest creation with valid values."""
        request = SimulationRequest(
            property_id="PROP_TEST_001",
            msa_code="35620",
            num_scenarios=5000,
            horizon_years=6,
            use_correlations=True,
            confidence_level=0.95,
        )

        assert request.property_id == "PROP_TEST_001"
        assert request.msa_code == "35620"
        assert request.num_scenarios == 5000
        assert request.horizon_years == 6
        assert request.use_correlations is True
        assert request.confidence_level == 0.95

    def test_simulation_result_validation_and_methods(self):
        """Test SimulationResult validation and methods."""
        request = SimulationRequest("PROP_001", "35620", 2, 3)

        scenario_id1 = ScenarioId("SIM_001", 1)
        scenario_id2 = ScenarioId("SIM_001", 2)

        metrics1 = ScenarioMetrics(0.6, 0.4, MarketScenario.BULL_MARKET, {})
        metrics2 = ScenarioMetrics(0.3, 0.7, MarketScenario.BEAR_MARKET, {})

        scenario1 = Scenario(
            scenario_id1, {"cap_rate": [0.06, 0.062, 0.064]}, metrics1, 25.0
        )
        scenario2 = Scenario(
            scenario_id2, {"cap_rate": [0.07, 0.072, 0.074]}, metrics2, 75.0
        )

        summary = SimulationSummary({}, {}, {})

        # Test scenario count mismatch validation
        with pytest.raises(
            ValueError, match="Number of scenarios doesn't match request"
        ):
            SimulationResult(
                simulation_id="SIM_001",
                request=request,
                scenarios=[scenario1],  # Only 1 scenario, but request expects 2
                summary=summary,
                correlation_matrix=None,
                simulation_date=date.today(),
                computation_time_seconds=1.5,
            )

        # Test successful creation
        result = SimulationResult(
            simulation_id="SIM_001",
            request=request,
            scenarios=[scenario1, scenario2],
            summary=summary,
            correlation_matrix=None,
            simulation_date=date(2024, 2, 15),
            computation_time_seconds=2.3,
        )

        assert result.simulation_id == "SIM_001"
        assert len(result.scenarios) == 2
        assert result.computation_time_seconds == 2.3

        # Test get_scenario_by_rank
        closest_to_30 = result.get_scenario_by_rank(30.0)
        assert closest_to_30 == scenario1  # 25.0 is closer to 30.0 than 75.0

        closest_to_80 = result.get_scenario_by_rank(80.0)
        assert closest_to_80 == scenario2  # 75.0 is closer to 80.0 than 25.0

        # Test get_scenarios_by_market_type
        bull_scenarios = result.get_scenarios_by_market_type(MarketScenario.BULL_MARKET)
        assert len(bull_scenarios) == 1
        assert bull_scenarios[0] == scenario1

        bear_scenarios = result.get_scenarios_by_market_type(MarketScenario.BEAR_MARKET)
        assert len(bear_scenarios) == 1
        assert bear_scenarios[0] == scenario2

    def test_market_scenario_enum_values(self):
        """Test MarketScenario enum values."""
        assert MarketScenario.BULL_MARKET.value == "bull_market"
        assert MarketScenario.BEAR_MARKET.value == "bear_market"
        assert MarketScenario.NEUTRAL_MARKET.value == "neutral_market"
        assert MarketScenario.GROWTH_MARKET.value == "growth_market"
        assert MarketScenario.STRESS_MARKET.value == "stress_market"

    def test_scenario_edge_cases(self):
        """Test edge cases for Scenario entity."""
        scenario_id = ScenarioId("EDGE_TEST", 999)
        metrics = ScenarioMetrics(
            0.0, 1.0, MarketScenario.STRESS_MARKET, {}
        )  # Extreme values

        # Test single year horizon
        scenario = Scenario(
            scenario_id=scenario_id,
            parameter_values={"single_param": [0.5]},  # Single year
            metrics=metrics,
        )

        assert scenario.horizon_years == 1
        assert scenario.get_parameter_average("single_param") == 0.5
