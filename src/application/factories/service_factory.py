"""
Simple Service Factory

Provides a lightweight alternative to complex dependency injection.
Creates service instances with minimal configuration.
"""

import logging
from typing import Optional

from ..services.cash_flow_projection_service import CashFlowProjectionService
from ..services.dcf_assumptions_service import DCFAssumptionsService
from ..services.financial_metrics_service import FinancialMetricsService
from ..services.initial_numbers_service import InitialNumbersService


class ServiceFactory:
    """Simple factory for creating application services."""

    def __init__(self) -> None:
        self.logger = self._create_logger()

    def _create_logger(self) -> logging.Logger:
        """Create configured logger."""
        logger = logging.getLogger("pro_forma_analytics")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def create_dcf_assumptions_service(self) -> DCFAssumptionsService:
        """Create DCF assumptions service."""
        return DCFAssumptionsService()

    def create_initial_numbers_service(self) -> InitialNumbersService:
        """Create initial numbers service."""
        return InitialNumbersService()

    def create_cash_flow_projection_service(self) -> CashFlowProjectionService:
        """Create cash flow projection service."""
        return CashFlowProjectionService()

    def create_financial_metrics_service(self) -> FinancialMetricsService:
        """Create financial metrics service."""
        return FinancialMetricsService()


# Global factory instance
_factory: Optional[ServiceFactory] = None


def get_service_factory() -> ServiceFactory:
    """Get the global service factory instance."""
    global _factory
    if _factory is None:
        _factory = ServiceFactory()
    return _factory


def create_all_services() -> dict:
    """Create all main application services."""
    factory = get_service_factory()

    return {
        "dcf_assumptions": factory.create_dcf_assumptions_service(),
        "initial_numbers": factory.create_initial_numbers_service(),
        "cash_flow_projection": factory.create_cash_flow_projection_service(),
        "financial_metrics": factory.create_financial_metrics_service(),
    }
