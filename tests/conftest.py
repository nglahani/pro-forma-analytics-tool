"""
Pytest Configuration and Fixtures

Provides shared test fixtures and configuration for the test suite.
Simplified to focus on core DCF business logic testing.
"""

import logging

import pytest

from src.application.factories.service_factory import ServiceFactory


@pytest.fixture(scope="session")
def test_logger():
    """Provide a test logger."""
    logger = logging.getLogger("test_pro_forma_analytics")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


@pytest.fixture
def service_factory():
    """Create a fresh service factory for testing."""
    factory = ServiceFactory()
    yield factory
    # Cleanup: Close any database connections
    try:
        if hasattr(factory, "_parameter_repository") and factory._parameter_repository:
            if hasattr(factory._parameter_repository, "_connection"):
                factory._parameter_repository._connection.close()
        if (
            hasattr(factory, "_simulation_repository")
            and factory._simulation_repository
        ):
            if hasattr(factory._simulation_repository, "_connection"):
                factory._simulation_repository._connection.close()
    except Exception:
        pass  # Ignore cleanup errors
