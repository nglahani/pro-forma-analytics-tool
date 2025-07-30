"""
Repository Interfaces for Monte Carlo Simulation Data

Abstracts data access for simulation results and related data.
"""

from abc import ABC, abstractmethod
from datetime import date
from typing import Dict, List, Optional

from ..entities.monte_carlo import SimulationResult


class SimulationRepository(ABC):
    """Abstract repository for Monte Carlo simulation operations."""

    @abstractmethod
    def save_simulation_result(self, result: SimulationResult) -> None:
        """
        Save a complete simulation result.

        Args:
            result: Simulation result to save
        """
        pass

    @abstractmethod
    def get_simulation_result(self, simulation_id: str) -> Optional[SimulationResult]:
        """
        Retrieve a simulation result by ID.

        Args:
            simulation_id: Unique simulation identifier

        Returns:
            SimulationResult if found, None otherwise
        """
        pass

    @abstractmethod
    def get_simulation_results_for_property(
        self, property_id: str, limit: int = 10
    ) -> List[SimulationResult]:
        """
        Get recent simulation results for a property.

        Args:
            property_id: Property identifier
            limit: Maximum number of results to return

        Returns:
            List of simulation results, most recent first
        """
        pass

    @abstractmethod
    def get_simulation_results_by_msa(
        self,
        msa_code: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 50,
    ) -> List[SimulationResult]:
        """
        Get simulation results for an MSA within a date range.

        Args:
            msa_code: MSA identifier
            start_date: Optional start date filter
            end_date: Optional end date filter
            limit: Maximum number of results to return

        Returns:
            List of simulation results
        """
        pass

    @abstractmethod
    def delete_old_simulations(self, older_than_days: int) -> int:
        """
        Delete simulation results older than specified days.

        Args:
            older_than_days: Delete simulations older than this many days

        Returns:
            Number of simulations deleted
        """
        pass

    @abstractmethod
    def get_simulation_summary_stats(
        self,
        msa_code: str,
        parameter_name: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Optional[Dict[str, float]]:
        """
        Get aggregated statistics for a parameter across multiple simulations.

        Args:
            msa_code: MSA identifier
            parameter_name: Parameter to analyze
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            Dictionary of statistics if data available, None otherwise
        """
        pass
