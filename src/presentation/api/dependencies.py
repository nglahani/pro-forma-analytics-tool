"""
FastAPI Dependencies

Dependency injection functions for service access and request handling.
"""

import sys
from pathlib import Path
from typing import Any, Dict

from fastapi import Depends

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.application.factories.service_factory import (
    get_service_factory,
)
from src.application.services.cash_flow_projection_service import (
    CashFlowProjectionService,
)
from src.application.services.dcf_assumptions_service import DCFAssumptionsService
from src.application.services.financial_metrics_service import FinancialMetricsService
from src.application.services.initial_numbers_service import InitialNumbersService


def get_dcf_services() -> Dict[str, Any]:
    """
    Get all DCF analysis services.

    Returns:
        Dictionary containing all DCF service instances
    """
    factory = get_service_factory()

    return {
        "dcf_assumptions": factory.create_dcf_assumptions_service(),
        "initial_numbers": factory.create_initial_numbers_service(),
        "cash_flow_projection": factory.create_cash_flow_projection_service(),
        "financial_metrics": factory.create_financial_metrics_service(),
    }


def get_dcf_assumptions_service() -> DCFAssumptionsService:
    """FastAPI dependency for DCF assumptions service."""
    factory = get_service_factory()
    return factory.create_dcf_assumptions_service()


def get_initial_numbers_service() -> InitialNumbersService:
    """FastAPI dependency for initial numbers service."""
    factory = get_service_factory()
    return factory.create_initial_numbers_service()


def get_cash_flow_projection_service() -> CashFlowProjectionService:
    """FastAPI dependency for cash flow projection service."""
    factory = get_service_factory()
    return factory.create_cash_flow_projection_service()


def get_financial_metrics_service() -> FinancialMetricsService:
    """FastAPI dependency for financial metrics service."""
    factory = get_service_factory()
    return factory.create_financial_metrics_service()


def get_forecasting_service():
    """FastAPI dependency for forecasting service - placeholder."""
    # For now, return None as these services need complex initialization
    return None


def get_monte_carlo_service():
    """FastAPI dependency for Monte Carlo service - placeholder."""
    # For now, return None as these services need complex initialization
    return None


class DCFServices:
    """Container for all DCF services with dependency injection."""

    def __init__(
        self,
        dcf_assumptions: DCFAssumptionsService = Depends(get_dcf_assumptions_service),
        initial_numbers: InitialNumbersService = Depends(get_initial_numbers_service),
        cash_flow_projection: CashFlowProjectionService = Depends(
            get_cash_flow_projection_service
        ),
        financial_metrics: FinancialMetricsService = Depends(
            get_financial_metrics_service
        ),
        forecasting=Depends(get_forecasting_service),
        monte_carlo=Depends(get_monte_carlo_service),
    ):
        self.dcf_assumptions = dcf_assumptions
        self.initial_numbers = initial_numbers
        self.cash_flow_projection = cash_flow_projection
        self.financial_metrics = financial_metrics
        self.forecasting = forecasting
        self.monte_carlo = monte_carlo
