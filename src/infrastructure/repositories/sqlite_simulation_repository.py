"""
SQLite Implementation of Simulation Repository

Concrete implementation of simulation repository using SQLite database
for Monte Carlo simulation data persistence.
"""

import json
import logging
import sqlite3
from dataclasses import asdict
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from ...domain.entities.monte_carlo import (
    CorrelationMatrix,
    MarketScenario,
    Scenario,
    ScenarioId,
    ScenarioMetrics,
    SimulationRequest,
    SimulationResult,
    SimulationSummary,
)
from ...domain.repositories.simulation_repository import SimulationRepository


class SQLiteSimulationRepository(SimulationRepository):
    """SQLite implementation of simulation repository."""

    def __init__(self, database_path: str, logger: Optional[logging.Logger] = None):
        self._db_path = database_path
        self._logger = logger or logging.getLogger(__name__)
        self._init_database()

    def _init_database(self) -> None:
        """Initialize database tables if they don't exist."""
        with sqlite3.connect(self._db_path) as conn:
            # Main simulation results table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS simulation_results (
                    simulation_id TEXT PRIMARY KEY,
                    property_id TEXT NOT NULL,
                    msa_code TEXT NOT NULL,
                    num_scenarios INTEGER NOT NULL,
                    horizon_years INTEGER NOT NULL,
                    use_correlations BOOLEAN NOT NULL,
                    confidence_level REAL NOT NULL,
                    simulation_date TEXT NOT NULL,
                    computation_time_seconds REAL NOT NULL,
                    summary_data TEXT NOT NULL,  -- JSON
                    correlation_matrix TEXT,     -- JSON, optional
                    created_at TEXT NOT NULL
                )
            """
            )

            # Individual scenarios table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS simulation_scenarios (
                    scenario_key TEXT PRIMARY KEY,  -- simulation_id_scenario_number
                    simulation_id TEXT NOT NULL,
                    scenario_number INTEGER NOT NULL,
                    parameter_values TEXT NOT NULL,  -- JSON
                    growth_score REAL NOT NULL,
                    risk_score REAL NOT NULL,
                    market_scenario TEXT NOT NULL,
                    volatility_measures TEXT NOT NULL,  -- JSON
                    percentile_rank REAL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (simulation_id) REFERENCES simulation_results (simulation_id)
                )
            """
            )

            # Create indexes for efficient querying
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_simulation_property 
                ON simulation_results(property_id, simulation_date DESC)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_simulation_msa 
                ON simulation_results(msa_code, simulation_date DESC)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_scenarios_simulation 
                ON simulation_scenarios(simulation_id, scenario_number)
            """
            )

    def save_simulation_result(self, result: SimulationResult) -> None:
        """Save a complete simulation result."""
        try:
            with sqlite3.connect(self._db_path) as conn:
                # Save main simulation result
                summary_data = self._serialize_simulation_summary(result.summary)
                correlation_matrix_json = None
                if result.correlation_matrix:
                    correlation_matrix_json = json.dumps(
                        {
                            "matrix": result.correlation_matrix.matrix,
                            "parameter_names": result.correlation_matrix.parameter_names,
                            "creation_date": result.correlation_matrix.creation_date.isoformat(),
                        }
                    )

                conn.execute(
                    """
                    INSERT OR REPLACE INTO simulation_results 
                    (simulation_id, property_id, msa_code, num_scenarios, horizon_years,
                     use_correlations, confidence_level, simulation_date, 
                     computation_time_seconds, summary_data, correlation_matrix, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        result.simulation_id,
                        result.request.property_id,
                        result.request.msa_code,
                        result.request.num_scenarios,
                        result.request.horizon_years,
                        result.request.use_correlations,
                        result.request.confidence_level,
                        result.simulation_date.isoformat(),
                        result.computation_time_seconds,
                        summary_data,
                        correlation_matrix_json,
                        datetime.now().isoformat(),
                    ),
                )

                # Save individual scenarios
                for scenario in result.scenarios:
                    scenario_key = str(scenario.scenario_id)
                    parameter_values_json = json.dumps(scenario.parameter_values)
                    volatility_measures_json = json.dumps(
                        scenario.metrics.volatility_measures
                    )

                    conn.execute(
                        """
                        INSERT OR REPLACE INTO simulation_scenarios 
                        (scenario_key, simulation_id, scenario_number, parameter_values,
                         growth_score, risk_score, market_scenario, volatility_measures,
                         percentile_rank, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            scenario_key,
                            result.simulation_id,
                            scenario.scenario_id.scenario_number,
                            parameter_values_json,
                            scenario.metrics.growth_score,
                            scenario.metrics.risk_score,
                            scenario.metrics.market_scenario.value,
                            volatility_measures_json,
                            scenario.percentile_rank,
                            datetime.now().isoformat(),
                        ),
                    )

                self._logger.info(
                    f"Saved simulation {result.simulation_id} with {len(result.scenarios)} scenarios"
                )

        except Exception as e:
            self._logger.error(f"Failed to save simulation result: {e}")
            raise

    def get_simulation_result(self, simulation_id: str) -> Optional[SimulationResult]:
        """Retrieve a simulation result by ID."""
        try:
            with sqlite3.connect(self._db_path) as conn:
                # Get main simulation data
                cursor = conn.execute(
                    """
                    SELECT property_id, msa_code, num_scenarios, horizon_years,
                           use_correlations, confidence_level, simulation_date,
                           computation_time_seconds, summary_data, correlation_matrix
                    FROM simulation_results 
                    WHERE simulation_id = ?
                """,
                    (simulation_id,),
                )

                main_row = cursor.fetchone()
                if not main_row:
                    return None

                (
                    property_id,
                    msa_code,
                    num_scenarios,
                    horizon_years,
                    use_correlations,
                    confidence_level,
                    simulation_date_str,
                    computation_time,
                    summary_data_json,
                    correlation_matrix_json,
                ) = main_row

                # Get scenarios
                scenarios_cursor = conn.execute(
                    """
                    SELECT scenario_number, parameter_values, growth_score, risk_score,
                           market_scenario, volatility_measures, percentile_rank
                    FROM simulation_scenarios 
                    WHERE simulation_id = ?
                    ORDER BY scenario_number
                """,
                    (simulation_id,),
                )

                scenarios = []
                for row in scenarios_cursor.fetchall():
                    (
                        scenario_num,
                        param_values_json,
                        growth_score,
                        risk_score,
                        market_scenario_str,
                        volatility_json,
                        percentile_rank,
                    ) = row

                    scenario = self._deserialize_scenario(
                        simulation_id,
                        scenario_num,
                        param_values_json,
                        growth_score,
                        risk_score,
                        market_scenario_str,
                        volatility_json,
                        percentile_rank,
                    )
                    scenarios.append(scenario)

                # Reconstruct simulation result
                request = SimulationRequest(
                    property_id=property_id,
                    msa_code=msa_code,
                    num_scenarios=num_scenarios,
                    horizon_years=horizon_years,
                    use_correlations=bool(use_correlations),
                    confidence_level=confidence_level,
                )

                summary = self._deserialize_simulation_summary(summary_data_json)

                correlation_matrix = None
                if correlation_matrix_json:
                    corr_data = json.loads(correlation_matrix_json)
                    correlation_matrix = CorrelationMatrix(
                        matrix=corr_data["matrix"],
                        parameter_names=corr_data["parameter_names"],
                        creation_date=date.fromisoformat(corr_data["creation_date"]),
                    )

                return SimulationResult(
                    simulation_id=simulation_id,
                    request=request,
                    scenarios=scenarios,
                    summary=summary,
                    correlation_matrix=correlation_matrix,
                    simulation_date=date.fromisoformat(simulation_date_str),
                    computation_time_seconds=computation_time,
                )

        except Exception as e:
            self._logger.error(f"Failed to retrieve simulation result: {e}")
            return None

    def get_simulation_results_for_property(
        self, property_id: str, limit: int = 10
    ) -> List[SimulationResult]:
        """Get recent simulation results for a property."""
        try:
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT simulation_id 
                    FROM simulation_results 
                    WHERE property_id = ?
                    ORDER BY simulation_date DESC, created_at DESC
                    LIMIT ?
                """,
                    (property_id, limit),
                )

                simulation_ids = [row[0] for row in cursor.fetchall()]

                results = []
                for sim_id in simulation_ids:
                    result = self.get_simulation_result(sim_id)
                    if result:
                        results.append(result)

                return results

        except Exception as e:
            self._logger.error(f"Failed to get simulations for property: {e}")
            return []

    def get_simulation_results_by_msa(
        self,
        msa_code: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 50,
    ) -> List[SimulationResult]:
        """Get simulation results for an MSA within a date range."""
        try:
            query = """
                SELECT simulation_id 
                FROM simulation_results 
                WHERE msa_code = ?
            """
            params = [msa_code]

            if start_date:
                query += " AND simulation_date >= ?"
                params.append(start_date.isoformat())

            if end_date:
                query += " AND simulation_date <= ?"
                params.append(end_date.isoformat())

            query += " ORDER BY simulation_date DESC, created_at DESC LIMIT ?"
            params.append(limit)

            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.execute(query, params)
                simulation_ids = [row[0] for row in cursor.fetchall()]

                results = []
                for sim_id in simulation_ids:
                    result = self.get_simulation_result(sim_id)
                    if result:
                        results.append(result)

                return results

        except Exception as e:
            self._logger.error(f"Failed to get simulations by MSA: {e}")
            return []

    def delete_old_simulations(self, older_than_days: int) -> int:
        """Delete simulation results older than specified days."""
        try:
            cutoff_date = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - older_than_days)

            with sqlite3.connect(self._db_path) as conn:
                # Get simulation IDs to delete
                cursor = conn.execute(
                    """
                    SELECT simulation_id 
                    FROM simulation_results 
                    WHERE created_at < ?
                """,
                    (cutoff_date.isoformat(),),
                )

                simulation_ids = [row[0] for row in cursor.fetchall()]

                if not simulation_ids:
                    return 0

                # Delete scenarios first (foreign key constraint)
                placeholders = ",".join(["?" for _ in simulation_ids])
                conn.execute(
                    f"""
                    DELETE FROM simulation_scenarios 
                    WHERE simulation_id IN ({placeholders})
                """,
                    simulation_ids,
                )

                # Delete main simulation results
                cursor = conn.execute(
                    f"""
                    DELETE FROM simulation_results 
                    WHERE simulation_id IN ({placeholders})
                """,
                    simulation_ids,
                )

                deleted_count = cursor.rowcount

                if deleted_count > 0:
                    self._logger.info(f"Deleted {deleted_count} old simulations")

                return deleted_count

        except Exception as e:
            self._logger.error(f"Failed to delete old simulations: {e}")
            return 0

    def get_simulation_summary_stats(
        self,
        msa_code: str,
        parameter_name: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Optional[Dict[str, float]]:
        """Get aggregated statistics for a parameter across multiple simulations."""
        try:
            # Build query to get parameter values from all matching simulations
            query = """
                SELECT ss.parameter_values
                FROM simulation_scenarios ss
                INNER JOIN simulation_results sr ON ss.simulation_id = sr.simulation_id
                WHERE sr.msa_code = ?
            """
            params = [msa_code]

            if start_date:
                query += " AND sr.simulation_date >= ?"
                params.append(start_date.isoformat())

            if end_date:
                query += " AND sr.simulation_date <= ?"
                params.append(end_date.isoformat())

            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.execute(query, params)

                parameter_values = []
                for row in cursor.fetchall():
                    param_data = json.loads(row[0])
                    if parameter_name in param_data:
                        # Get average value across all years for this scenario
                        values = param_data[parameter_name]
                        avg_value = sum(values) / len(values) if values else 0
                        parameter_values.append(avg_value)

                if not parameter_values:
                    return None

                # Calculate statistics
                import statistics

                stats = {
                    "count": len(parameter_values),
                    "mean": statistics.mean(parameter_values),
                    "median": statistics.median(parameter_values),
                    "std": (
                        statistics.stdev(parameter_values)
                        if len(parameter_values) > 1
                        else 0.0
                    ),
                    "min": min(parameter_values),
                    "max": max(parameter_values),
                }

                # Calculate percentiles
                if len(parameter_values) >= 10:
                    sorted_values = sorted(parameter_values)
                    stats["p5"] = statistics.quantiles(sorted_values, n=20)[
                        0
                    ]  # 5th percentile
                    stats["p25"] = statistics.quantiles(sorted_values, n=4)[
                        0
                    ]  # 25th percentile
                    stats["p75"] = statistics.quantiles(sorted_values, n=4)[
                        2
                    ]  # 75th percentile
                    stats["p95"] = statistics.quantiles(sorted_values, n=20)[
                        18
                    ]  # 95th percentile

                return stats

        except Exception as e:
            self._logger.error(f"Failed to get simulation summary stats: {e}")
            return None

    def _serialize_simulation_summary(self, summary: SimulationSummary) -> str:
        """Serialize simulation summary to JSON."""
        summary_data = {
            "parameter_statistics": summary.parameter_statistics,
            "scenario_distribution": {
                k.value: v for k, v in summary.scenario_distribution.items()
            },
            "extreme_scenarios": {
                k: str(v) for k, v in summary.extreme_scenarios.items()
            },
        }
        return json.dumps(summary_data)

    def _deserialize_simulation_summary(self, summary_json: str) -> SimulationSummary:
        """Deserialize simulation summary from JSON."""
        data = json.loads(summary_json)

        scenario_distribution = {
            MarketScenario(k): v for k, v in data["scenario_distribution"].items()
        }

        extreme_scenarios = {}
        for k, v in data["extreme_scenarios"].items():
            parts = v.split("_")
            if len(parts) >= 2:
                simulation_id = "_".join(parts[:-1])
                scenario_number = int(parts[-1])
                extreme_scenarios[k] = ScenarioId(simulation_id, scenario_number)

        return SimulationSummary(
            parameter_statistics=data["parameter_statistics"],
            scenario_distribution=scenario_distribution,
            extreme_scenarios=extreme_scenarios,
        )

    def _deserialize_scenario(
        self,
        simulation_id: str,
        scenario_number: int,
        parameter_values_json: str,
        growth_score: float,
        risk_score: float,
        market_scenario_str: str,
        volatility_json: str,
        percentile_rank: Optional[float],
    ) -> Scenario:
        """Deserialize a scenario from database row data."""
        scenario_id = ScenarioId(simulation_id, scenario_number)
        parameter_values = json.loads(parameter_values_json)
        volatility_measures = json.loads(volatility_json)
        market_scenario = MarketScenario(market_scenario_str)

        metrics = ScenarioMetrics(
            growth_score=growth_score,
            risk_score=risk_score,
            market_scenario=market_scenario,
            volatility_measures=volatility_measures,
        )

        return Scenario(
            scenario_id=scenario_id,
            parameter_values=parameter_values,
            metrics=metrics,
            percentile_rank=percentile_rank,
        )
