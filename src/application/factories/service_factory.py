"""
Simple Service Factory

Provides a lightweight alternative to complex dependency injection.
Creates service instances with minimal configuration.
"""

import logging
from typing import Dict, Optional

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

    def validate_services_health(self) -> Dict[str, bool]:
        """
        Validate that all core services can be created successfully.

        Returns:
            Dict mapping service names to health status (True if healthy)
        """
        health_status = {}

        try:
            self.create_dcf_assumptions_service()
            health_status["dcf_assumptions"] = True
        except Exception as e:
            self.logger.error(f"DCF Assumptions Service health check failed: {e}")
            health_status["dcf_assumptions"] = False

        try:
            self.create_initial_numbers_service()
            health_status["initial_numbers"] = True
        except Exception as e:
            self.logger.error(f"Initial Numbers Service health check failed: {e}")
            health_status["initial_numbers"] = False

        try:
            self.create_cash_flow_projection_service()
            health_status["cash_flow_projection"] = True
        except Exception as e:
            self.logger.error(f"Cash Flow Projection Service health check failed: {e}")
            health_status["cash_flow_projection"] = False

        try:
            self.create_financial_metrics_service()
            health_status["financial_metrics"] = True
        except Exception as e:
            self.logger.error(f"Financial Metrics Service health check failed: {e}")
            health_status["financial_metrics"] = False

        return health_status


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
