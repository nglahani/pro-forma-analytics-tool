"""
Infrastructure Configuration

Configures the dependency injection container with repository implementations
and other infrastructure concerns.
"""

import logging
from pathlib import Path
from typing import Optional

from config.settings import settings

from ..domain.repositories.parameter_repository import (
    CorrelationRepository,
    ForecastRepository,
    ParameterRepository,
)
from ..domain.repositories.simulation_repository import SimulationRepository
from .container import DependencyContainer
from .repositories.sqlite_parameter_repository import (
    SQLiteCorrelationRepository,
    SQLiteForecastRepository,
    SQLiteParameterRepository,
)
from .repositories.sqlite_simulation_repository import SQLiteSimulationRepository


def configure_repositories(container: DependencyContainer) -> None:
    """
    Configure repository implementations in the dependency container.

    Args:
        container: The dependency injection container to configure
    """
    logger = container.resolve(logging.Logger)

    # Get database paths from settings
    base_path = Path(settings.database.base_path)
    parameter_db_path = str(base_path / settings.database.property_data_db)
    forecast_db_path = str(base_path / settings.database.forecast_cache_db)
    simulation_db_path = str(
        base_path / settings.database.forecast_cache_db
    )  # Reuse forecast cache for simulations

    # Register repository implementations
    container.register_factory(
        ParameterRepository,
        lambda: SQLiteParameterRepository(parameter_db_path, logger),
    )

    container.register_factory(
        ForecastRepository, lambda: SQLiteForecastRepository(forecast_db_path, logger)
    )

    container.register_factory(
        CorrelationRepository,
        lambda: SQLiteCorrelationRepository(forecast_db_path, logger),
    )

    container.register_factory(
        SimulationRepository,
        lambda: SQLiteSimulationRepository(simulation_db_path, logger),
    )

    logger.info("Repository implementations configured successfully")


def configure_application_services(container: DependencyContainer) -> None:
    """
    Configure application services in the dependency container.

    Args:
        container: The dependency injection container to configure
    """
    # Import application services
    from ..application.services.cash_flow_projection_service import (
        CashFlowProjectionService,
    )
    from ..application.services.dcf_assumptions_service import DCFAssumptionsService
    from ..application.services.financial_metrics_service import FinancialMetricsService
    from ..application.services.forecasting_service import ForecastingApplicationService
    from ..application.services.initial_numbers_service import InitialNumbersService
    from ..application.services.monte_carlo_service import MonteCarloApplicationService

    # Register application services as singletons
    container.register_singleton(
        ForecastingApplicationService, ForecastingApplicationService
    )
    container.register_singleton(DCFAssumptionsService, DCFAssumptionsService)
    container.register_singleton(InitialNumbersService, InitialNumbersService)
    container.register_singleton(CashFlowProjectionService, CashFlowProjectionService)
    container.register_singleton(FinancialMetricsService, FinancialMetricsService)
    container.register_singleton(
        MonteCarloApplicationService, MonteCarloApplicationService
    )

    logger = container.resolve(logging.Logger)
    logger.info("Application services configured successfully")


def configure_forecasting_engines(container: DependencyContainer) -> None:
    """
    Configure forecasting engines in the dependency container.

    Args:
        container: The dependency injection container to configure
    """
    # Import forecasting engines
    from forecasting.prophet_engine import ProphetEngine
    from monte_carlo.simulation_engine import MonteCarloEngine

    # Register forecasting engines
    container.register_singleton(ProphetEngine, ProphetEngine)
    container.register_singleton(MonteCarloEngine, MonteCarloEngine)

    logger = container.resolve(logging.Logger)
    logger.info("Forecasting engines configured successfully")


def configure_production_container() -> DependencyContainer:
    """
    Create and configure a production-ready dependency container.

    Returns:
        Fully configured DependencyContainer instance
    """
    from .container import create_container

    container = create_container()

    # Configure all components
    configure_repositories(container)
    configure_application_services(container)
    configure_forecasting_engines(container)

    return container


def configure_test_container(
    parameter_db_path: Optional[str] = None,
    forecast_db_path: Optional[str] = None,
    simulation_db_path: Optional[str] = None,
) -> DependencyContainer:
    """
    Create and configure a test-friendly dependency container.

    Args:
        parameter_db_path: Override for parameter database path (for testing)
        forecast_db_path: Override for forecast database path (for testing)
        simulation_db_path: Override for simulation database path (for testing)

    Returns:
        Test-configured DependencyContainer instance
    """
    from .container import DependencyContainer

    container = DependencyContainer()

    # Configure basic logging
    logger = logging.getLogger("test_pro_forma_analytics")
    logger.setLevel(logging.WARNING)  # Reduce noise in tests
    container.register_instance(logging.Logger, logger)

    # Configure repositories with test database paths if provided
    if parameter_db_path:
        container.register_factory(
            ParameterRepository,
            lambda: SQLiteParameterRepository(parameter_db_path, logger),
        )

    if forecast_db_path:
        container.register_factory(
            ForecastRepository,
            lambda: SQLiteForecastRepository(forecast_db_path, logger),
        )

        container.register_factory(
            CorrelationRepository,
            lambda: SQLiteCorrelationRepository(forecast_db_path, logger),
        )

    if simulation_db_path:
        container.register_factory(
            SimulationRepository,
            lambda: SQLiteSimulationRepository(simulation_db_path, logger),
        )

    # Configure application services
    try:
        configure_application_services(container)
    except ImportError:
        # Some services might not be available in test environment
        logger.warning("Some application services not available for test configuration")

    return container


def get_configured_container() -> DependencyContainer:
    """
    Get a fully configured container for production use.

    Returns:
        Configured DependencyContainer instance
    """
    from .container import get_container

    # Check if container is already configured
    container = get_container()

    # Check if repositories are registered (simple configuration check)
    try:
        container.resolve(ParameterRepository)
        # Already configured
        return container
    except ValueError:
        # Not configured yet, configure it
        configured_container = configure_production_container()
        from .container import set_container

        set_container(configured_container)
        return configured_container
