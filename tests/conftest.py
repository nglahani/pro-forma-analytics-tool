"""
Pytest Configuration and Fixtures

Provides shared test fixtures and configuration for the test suite.
Simplified to focus on core DCF business logic testing with proper resource cleanup.
"""

import logging
from datetime import date

import pytest
from fastapi.testclient import TestClient

from src.application.factories.service_factory import ServiceFactory
from src.presentation.api.main import app


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


@pytest.fixture
def api_client():
    """
    Provide a properly configured TestClient with resource cleanup.

    This fixture ensures that database connections and other resources
    are properly closed after each test, preventing resource leaks.
    Replaces individual TestClient(app) calls throughout test suite.
    """
    with TestClient(app) as client:
        yield client


@pytest.fixture
def valid_api_key():
    """Return valid API key for testing."""
    return "dev_test_key_12345678901234567890123"


@pytest.fixture
def invalid_api_key():
    """Return invalid API key for testing."""
    return "invalid_key_123"


@pytest.fixture
def sample_property_request():
    """Create a valid property analysis request for testing."""
    return {
        "property_data": {
            "property_id": "TEST_GLOBAL_001",
            "property_name": "Global Test Property",
            "analysis_date": date.today().isoformat(),
            "residential_units": {
                "total_units": 20,
                "average_rent_per_unit": 2000,
                "unit_types": "Mixed: 10x1BR, 10x2BR",
            },
            "renovation_info": {
                "status": "not_needed",
                "anticipated_duration_months": 0,
            },
            "commercial_units": {
                "has_commercial_space": False,
                "total_commercial_sqft": 0,
                "average_rent_per_sqft": 0,
                "total_units": 0,
                "average_rent_per_unit": 0,
            },
            "financing_info": {
                "equity_percentage": 0.25,
                "cash_percentage": 0.20,
            },
            "equity_structure": {
                "investor_equity_share_pct": 75.0,
                "self_cash_percentage": 25.0,
                "number_of_investors": 1,
            },
            "location_info": {
                "city": "Charlotte",
                "state": "NC",
                "zip_code": "28202",
                "msa_code": "16740",
            },
        }
    }


# Configure pytest for better debugging
def pytest_configure(config):
    """Configure pytest settings for cleaner output."""
    config.option.tb = "short"
