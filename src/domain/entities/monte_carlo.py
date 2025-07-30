"""
Domain Entities for Monte Carlo Simulation

Clean architecture implementation of Monte Carlo simulation entities.
"""

import uuid
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Dict, List, Optional


class MarketScenario(Enum):
    """Market scenario classifications."""

    BULL_MARKET = "bull_market"
    BEAR_MARKET = "bear_market"
    NEUTRAL_MARKET = "neutral_market"
    GROWTH_MARKET = "growth_market"
    STRESS_MARKET = "stress_market"


@dataclass(frozen=True)
class ScenarioId:
    """Value object for scenario identification."""

    simulation_id: str
    scenario_number: int

    def __str__(self) -> str:
        return f"{self.simulation_id}_{self.scenario_number:04d}"


@dataclass(frozen=True)
class ScenarioMetrics:
    """Metrics calculated for a single scenario."""

    growth_score: float
    risk_score: float
    market_scenario: MarketScenario
    volatility_measures: Dict[str, float]

    def __post_init__(self) -> None:
        if not 0 <= self.growth_score <= 1:
            raise ValueError("Growth score must be between 0 and 1")
        if not 0 <= self.risk_score <= 1:
            raise ValueError("Risk score must be between 0 and 1")


@dataclass(frozen=True)
class Scenario:
    """Single Monte Carlo scenario."""

    scenario_id: ScenarioId
    parameter_values: Dict[str, List[float]]  # parameter_name -> 5-year values
    metrics: ScenarioMetrics
    percentile_rank: Optional[float] = None

    def __post_init__(self) -> None:
        if not self.parameter_values:
            raise ValueError("Scenario must contain parameter values")

        # Validate all parameters have the same number of years
        year_counts = {
            param: len(values) for param, values in self.parameter_values.items()
        }
        if len(set(year_counts.values())) > 1:
            raise ValueError("All parameters must have the same forecast horizon")

    @property
    def horizon_years(self) -> int:
        """Get the forecast horizon in years."""
        if not self.parameter_values:
            return 0
        return len(next(iter(self.parameter_values.values())))

    def get_parameter_average(self, parameter_name: str) -> float:
        """Get the average value for a parameter across all years."""
        if parameter_name not in self.parameter_values:
            raise ValueError(f"Parameter {parameter_name} not found in scenario")
        return sum(self.parameter_values[parameter_name]) / len(
            self.parameter_values[parameter_name]
        )


@dataclass(frozen=True)
class CorrelationMatrix:
    """Parameter correlation matrix with metadata."""

    matrix: List[List[float]]
    parameter_names: List[str]
    creation_date: date

    def __post_init__(self) -> None:
        if len(self.matrix) != len(self.parameter_names):
            raise ValueError("Matrix dimensions must match parameter count")

        for i, row in enumerate(self.matrix):
            if len(row) != len(self.parameter_names):
                raise ValueError(f"Row {i} has incorrect length")

            # Verify diagonal elements are 1.0
            if abs(row[i] - 1.0) > 1e-6:
                raise ValueError(f"Diagonal element [{i},{i}] must be 1.0")

    def get_correlation(self, param1: str, param2: str) -> float:
        """Get correlation between two parameters."""
        try:
            idx1 = self.parameter_names.index(param1)
            idx2 = self.parameter_names.index(param2)
            return self.matrix[idx1][idx2]
        except ValueError:
            raise ValueError("Parameter not found in correlation matrix")


@dataclass(frozen=True)
class SimulationSummary:
    """Summary statistics across all scenarios."""

    parameter_statistics: Dict[
        str, Dict[str, float]
    ]  # param -> {mean, std, p5, p95, etc.}
    scenario_distribution: Dict[MarketScenario, int]
    extreme_scenarios: Dict[str, ScenarioId]

    def get_parameter_percentile(self, parameter_name: str, percentile: int) -> float:
        """Get a specific percentile for a parameter."""
        if parameter_name not in self.parameter_statistics:
            raise ValueError(f"Parameter {parameter_name} not found in summary")

        percentile_key = f"p{percentile}"
        if percentile_key not in self.parameter_statistics[parameter_name]:
            raise ValueError(f"Percentile {percentile} not available")

        return self.parameter_statistics[parameter_name][percentile_key]


@dataclass
class SimulationRequest:
    """Request for Monte Carlo simulation."""

    property_id: str
    msa_code: str
    num_scenarios: int
    horizon_years: int
    use_correlations: bool = True
    confidence_level: float = 0.95

    def __post_init__(self) -> None:
        if self.num_scenarios <= 0:
            raise ValueError("Number of scenarios must be positive")
        if self.horizon_years <= 0:
            raise ValueError("Horizon years must be positive")
        if not 0 < self.confidence_level < 1:
            raise ValueError("Confidence level must be between 0 and 1")


@dataclass(frozen=True)
class SimulationResult:
    """Complete Monte Carlo simulation result."""

    simulation_id: str
    request: SimulationRequest
    scenarios: List[Scenario]
    summary: SimulationSummary
    correlation_matrix: Optional[CorrelationMatrix]
    simulation_date: date
    computation_time_seconds: float

    def __post_init__(self) -> None:
        if len(self.scenarios) != self.request.num_scenarios:
            raise ValueError("Number of scenarios doesn't match request")

        if not self.simulation_id:
            object.__setattr__(self, "simulation_id", str(uuid.uuid4()))

    def get_scenario_by_rank(self, percentile: float) -> Scenario:
        """Get scenario closest to the specified percentile rank."""
        if not 0 <= percentile <= 100:
            raise ValueError("Percentile must be between 0 and 100")

        scenarios_with_ranks = [
            s for s in self.scenarios if s.percentile_rank is not None
        ]
        if not scenarios_with_ranks:
            raise ValueError("No scenarios have percentile ranks calculated")

        # Find scenario closest to target percentile
        closest_scenario = min(
            scenarios_with_ranks,
            key=lambda s: (
                abs(s.percentile_rank - percentile)
                if s.percentile_rank is not None
                else float("inf")
            ),
        )
        return closest_scenario

    def get_scenarios_by_market_type(
        self, market_scenario: MarketScenario
    ) -> List[Scenario]:
        """Get all scenarios of a specific market type."""
        return [
            s for s in self.scenarios if s.metrics.market_scenario == market_scenario
        ]
