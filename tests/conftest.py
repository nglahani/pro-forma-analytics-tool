"""
Pytest Configuration and Fixtures

Provides shared test fixtures and configuration for the test suite.
Implements BDD/TDD best practices with proper test isolation.
"""

import logging
import sqlite3
import tempfile
from datetime import date, datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest

# Import domain entities
from src.domain.entities.forecast import (
    DataPoint,
    ForecastPoint,
    ForecastResult,
    HistoricalData,
    ModelPerformance,
    ParameterId,
    ParameterType,
)
from src.domain.entities.monte_carlo import (
    MarketScenario,
    Scenario,
    ScenarioId,
    ScenarioMetrics,
    SimulationRequest,
)

# Import repositories
from src.domain.repositories.parameter_repository import (
    ForecastRepository,
    ParameterRepository,
)
from src.domain.repositories.simulation_repository import SimulationRepository

# Import infrastructure
from src.infrastructure.container import DependencyContainer
from src.infrastructure.repositories.sqlite_parameter_repository import (
    SQLiteForecastRepository,
    SQLiteParameterRepository,
)


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
def temp_database():
    """Provide a temporary SQLite database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_file:
        db_path = temp_file.name

    # Initialize database
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")

    yield db_path

    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def container(temp_database, test_logger):
    """Provide a configured dependency injection container for testing."""
    container = DependencyContainer()

    # Register test logger
    container.register_instance(logging.Logger, test_logger)

    # Register repository implementations with test database
    container.register_factory(
        ParameterRepository,
        lambda: SQLiteParameterRepository(temp_database, test_logger),
    )

    container.register_factory(
        ForecastRepository, lambda: SQLiteForecastRepository(temp_database, test_logger)
    )

    # Mock simulation repository for now
    mock_sim_repo = Mock(spec=SimulationRepository)
    container.register_instance(SimulationRepository, mock_sim_repo)

    yield container

    container.clear()


# Test Data Fixtures


@pytest.fixture
def sample_parameter_id():
    """Sample parameter ID for testing."""
    return ParameterId(
        name="cap_rate",
        geographic_code="35620",  # New York MSA
        parameter_type=ParameterType.MARKET_METRIC,
    )


@pytest.fixture
def sample_historical_data(sample_parameter_id):
    """Sample historical data for testing."""
    data_points = []
    base_date = date(2020, 1, 1)

    for i in range(60):  # 5 years of monthly data
        data_point = DataPoint(
            parameter_id=sample_parameter_id,
            date=date(base_date.year + i // 12, (i % 12) + 1, 1),
            value=0.05 + (i * 0.001),  # Gradually increasing cap rate
            data_source="test_data",
        )
        data_points.append(data_point)

    return HistoricalData(
        parameter_id=sample_parameter_id,
        data_points=data_points,
        start_date=data_points[0].date,
        end_date=data_points[-1].date,
    )


@pytest.fixture
def sample_forecast_result(sample_parameter_id):
    """Sample forecast result for testing."""
    # Create forecast points
    forecast_points = []
    base_date = date(2025, 1, 1)

    for i in range(12):  # 1 year of monthly forecasts
        forecast_point = ForecastPoint(
            date=date(base_date.year, (i % 12) + 1, 1),
            value=0.06 + (i * 0.001),
            lower_bound=0.055 + (i * 0.001),
            upper_bound=0.065 + (i * 0.001),
        )
        forecast_points.append(forecast_point)

    # Create model performance
    performance = ModelPerformance(mae=0.005, mape=8.5, rmse=0.008, r_squared=0.85)

    return ForecastResult(
        forecast_id="test_forecast_001",
        parameter_id=sample_parameter_id,
        forecast_points=forecast_points,
        model_performance=performance,
        model_type="prophet",
        forecast_date=datetime.now(),
        horizon_years=1,
        historical_data_points=60,
    )


@pytest.fixture
def sample_simulation_request():
    """Sample simulation request for testing."""
    return SimulationRequest(
        property_id="TEST_PROP_001",
        msa_code="35620",  # New York MSA
        num_scenarios=100,
        horizon_years=5,
        use_correlations=True,
        confidence_level=0.95,
    )


@pytest.fixture
def sample_scenario(sample_simulation_request):
    """Sample Monte Carlo scenario for testing."""
    scenario_id = ScenarioId(simulation_id="test_sim_001", scenario_number=1)

    # Sample parameter values for 5 years
    parameter_values = {
        "cap_rate": [0.06, 0.061, 0.062, 0.063, 0.064],
        "rent_growth": [0.03, 0.032, 0.031, 0.033, 0.034],
        "vacancy_rate": [0.08, 0.079, 0.081, 0.080, 0.078],
    }

    # Sample metrics
    metrics = ScenarioMetrics(
        growth_score=0.65,
        risk_score=0.35,
        market_scenario=MarketScenario.BULL_MARKET,
        volatility_measures={"overall": 0.15},
    )

    return Scenario(
        scenario_id=scenario_id,
        parameter_values=parameter_values,
        metrics=metrics,
        percentile_rank=75.0,
    )


# Mock Fixtures


@pytest.fixture
def mock_parameter_repository():
    """Mock parameter repository for testing."""
    return Mock(spec=ParameterRepository)


@pytest.fixture
def mock_forecast_repository():
    """Mock forecast repository for testing."""
    return Mock(spec=ForecastRepository)


@pytest.fixture
def mock_simulation_repository():
    """Mock simulation repository for testing."""
    return Mock(spec=SimulationRepository)


@pytest.fixture
def mock_forecasting_engine():
    """Mock forecasting engine for testing."""
    mock_engine = Mock()
    mock_engine.generate_forecast = Mock()
    mock_engine.build_correlation_matrix = Mock()
    return mock_engine


@pytest.fixture
def mock_monte_carlo_engine():
    """Mock Monte Carlo engine for testing."""
    mock_engine = Mock()
    mock_engine.run_simulation = Mock()
    mock_engine.build_correlation_matrix = Mock()
    return mock_engine


# Helper Functions


def create_test_data_point(
    parameter_name: str = "test_param",
    geographic_code: str = "TEST_GEO",
    date_value: date = None,
    value: float = 0.05,
) -> DataPoint:
    """Helper to create test data points."""
    parameter_id = ParameterId(
        name=parameter_name,
        geographic_code=geographic_code,
        parameter_type=ParameterType.MARKET_METRIC,
    )

    return DataPoint(
        parameter_id=parameter_id,
        date=date_value or date.today(),
        value=value,
        data_source="test",
    )


def assert_forecast_result_valid(forecast_result: ForecastResult):
    """Helper to validate forecast result structure."""
    assert forecast_result.forecast_id
    assert forecast_result.parameter_id
    assert len(forecast_result.forecast_points) > 0
    assert forecast_result.model_performance
    assert forecast_result.horizon_years > 0
    assert forecast_result.historical_data_points > 0

    # Validate forecast points
    for point in forecast_result.forecast_points:
        assert point.date
        assert isinstance(point.value, (int, float))
        assert isinstance(point.lower_bound, (int, float))
        assert isinstance(point.upper_bound, (int, float))
        assert point.lower_bound <= point.value <= point.upper_bound


def assert_scenario_valid(scenario: Scenario):
    """Helper to validate scenario structure."""
    assert scenario.scenario_id
    assert len(scenario.parameter_values) > 0
    assert scenario.metrics
    assert 0 <= scenario.metrics.growth_score <= 1
    assert 0 <= scenario.metrics.risk_score <= 1
    assert scenario.metrics.market_scenario in MarketScenario

    # All parameters should have same number of years
    year_counts = set(len(values) for values in scenario.parameter_values.values())
    assert len(year_counts) == 1  # All parameters have same length
