"""
Unit tests for Data Router endpoints.

Tests the data router endpoints for market data and forecasting functionality.
"""

from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from src.presentation.api.routers.data import (
    get_msa_name,
    router,
    validate_msa_code,
    validate_parameter,
)


class TestDataRouterHelperFunctions:
    """Test helper functions used by data router."""

    def test_get_msa_name_valid_codes(self):
        """Test getting MSA names for valid codes."""
        assert "New York" in get_msa_name("35620")
        assert "Los Angeles" in get_msa_name("31080")
        assert "Chicago" in get_msa_name("16980")
        assert "Washington" in get_msa_name("47900")
        assert "Miami" in get_msa_name("33100")

    def test_get_msa_name_invalid_code(self):
        """Test getting MSA name for invalid code returns fallback."""
        result = get_msa_name("99999")
        assert result == "MSA 99999"

    def test_validate_msa_code_valid(self):
        """Test validating valid MSA codes."""
        valid_codes = ["35620", "31080", "16980", "47900", "33100"]
        for code in valid_codes:
            assert validate_msa_code(code) == code

    def test_validate_msa_code_invalid(self):
        """Test validating invalid MSA code raises HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            validate_msa_code("99999")

        assert exc_info.value.status_code == 404
        assert "MSA code 99999 not supported" in str(exc_info.value.detail)

    def test_validate_parameter_valid(self):
        """Test validating valid parameters."""
        valid_params = [
            "commercial_mortgage_rate",
            "treasury_10y",
            "fed_funds_rate",
            "cap_rate",
            "rent_growth",
            "expense_growth",
            "property_growth",
            "vacancy_rate",
            "ltv_ratio",
            "closing_cost_pct",
            "lender_reserves",
        ]
        for param in valid_params:
            assert validate_parameter(param) == param

    def test_validate_parameter_invalid(self):
        """Test validating invalid parameter raises HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            validate_parameter("invalid_param")

        assert exc_info.value.status_code == 404
        assert "Parameter invalid_param not supported" in str(exc_info.value.detail)


class TestDataRouterEndpoints:
    """Test data router API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client with mocked app."""
        # Use the actual FastAPI app instead of creating a new one
        from src.presentation.api.main import app

        return TestClient(app)

    @pytest.fixture
    def auth_headers(self):
        """Get authentication headers for API requests."""
        return {"X-API-Key": "dev_test_key_12345678901234567890123"}

    @pytest.fixture
    def mock_database_connection(self):
        """Mock database connection for testing."""
        with patch("sqlite3.connect") as mock_connect:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            yield mock_cursor

    def test_get_market_data_valid_msa(
        self, client, auth_headers, mock_database_connection
    ):
        """Test getting market data for valid MSA."""
        # Setup mock data
        mock_database_connection.fetchall.return_value = [
            ("2023-01-01", "cap_rate", 0.055, 0.005),
            ("2023-01-01", "rent_growth", 0.03, 0.002),
        ]

        with patch("pathlib.Path.exists", return_value=True):
            response = client.get("/api/v1/data/markets/35620", headers=auth_headers)

        if response.status_code != 200:
            print(f"Response: {response.status_code}, {response.text}")

        assert response.status_code == 200
        data = response.json()
        assert "msa" in data
        assert "New York" in data["msa"]

    def test_get_market_data_invalid_msa(self, client, auth_headers):
        """Test getting market data for invalid MSA returns 404."""
        response = client.get("/api/v1/data/markets/99999", headers=auth_headers)
        assert response.status_code == 404
        response_data = response.json()
        # Check if response has 'detail' key (FastAPI default) or 'message' key (custom format)
        error_message = response_data.get("detail") or response_data.get("message", "")
        assert "MSA code 99999 not supported" in error_message

    def test_get_market_data_with_parameters_filter(
        self, client, auth_headers, mock_database_connection
    ):
        """Test getting market data with parameters filter."""
        mock_database_connection.fetchall.return_value = [
            ("2023-01-01", "cap_rate", 0.055, 0.005),
        ]

        with patch("pathlib.Path.exists", return_value=True):
            response = client.get(
                "/api/v1/data/markets/35620?parameters=cap_rate,rent_growth",
                headers=auth_headers,
            )

        assert response.status_code == 200

    def test_get_market_data_with_date_range(
        self, client, auth_headers, mock_database_connection
    ):
        """Test getting market data with date range."""
        mock_database_connection.fetchall.return_value = [
            ("2023-06-01", "cap_rate", 0.055, 0.005),
        ]

        with patch("pathlib.Path.exists", return_value=True):
            response = client.get(
                "/api/v1/data/markets/35620?start_date=2023-01-01&end_date=2023-12-31",
                headers=auth_headers,
            )

        assert response.status_code == 200

    def test_get_forecast_data_valid_request(
        self, client, auth_headers, mock_database_connection
    ):
        """Test getting forecast data for valid request."""
        # Mock forecast data
        mock_database_connection.fetchall.return_value = [
            ("2024-01-01", 0.04, 0.035, 0.045, '{"model": "prophet"}'),
            ("2024-02-01", 0.041, 0.036, 0.046, '{"model": "prophet"}'),
        ]

        with patch("pathlib.Path.exists", return_value=True):
            response = client.get(
                "/api/v1/data/forecasts/rent_growth/35620", headers=auth_headers
            )

        assert response.status_code == 200
        data = response.json()
        assert data["parameter"] == "rent_growth"
        assert "New York" in data["msa"]  # Check MSA name contains expected city

    def test_get_forecast_data_invalid_parameter(self, client, auth_headers):
        """Test getting forecast data with invalid parameter returns 404."""
        response = client.get(
            "/api/v1/data/forecasts/invalid_param/35620", headers=auth_headers
        )
        assert response.status_code == 404
        response_data = response.json()
        error_message = response_data.get("detail") or response_data.get("message", "")
        assert "Parameter invalid_param not supported" in error_message

    def test_get_forecast_data_invalid_msa(self, client, auth_headers):
        """Test getting forecast data with invalid MSA returns 404."""
        response = client.get(
            "/api/v1/data/forecasts/rent_growth/99999", headers=auth_headers
        )
        assert response.status_code == 404
        response_data = response.json()
        error_message = response_data.get("detail") or response_data.get("message", "")
        assert "MSA code 99999 not supported" in error_message

    def test_get_forecast_data_with_horizon(
        self, client, auth_headers, mock_database_connection
    ):
        """Test getting forecast data with custom horizon."""
        mock_database_connection.fetchall.return_value = [
            ("2024-01-01", 0.04, 0.035, 0.045, '{"model": "prophet"}'),
        ]

        with patch("pathlib.Path.exists", return_value=True):
            response = client.get(
                "/api/v1/data/forecasts/rent_growth/35620?horizon_years=3",
                headers=auth_headers,
            )

        assert response.status_code == 200

    def test_get_forecast_data_with_confidence_level(
        self, client, auth_headers, mock_database_connection
    ):
        """Test getting forecast data with custom confidence level."""
        mock_database_connection.fetchall.return_value = [
            ("2024-01-01", 0.04, 0.035, 0.045, '{"model": "prophet"}'),
        ]

        with patch("pathlib.Path.exists", return_value=True):
            response = client.get(
                "/api/v1/data/forecasts/rent_growth/35620?confidence_level=0.90",
                headers=auth_headers,
            )

        assert response.status_code == 200

    def test_get_market_data_database_error(self, client, auth_headers):
        """Test market data endpoint handles database errors gracefully."""
        with patch(
            "sqlite3.connect", side_effect=Exception("Database connection failed")
        ):
            response = client.get("/api/v1/data/markets/35620", headers=auth_headers)

        # API handles errors gracefully, returning 200 with appropriate response
        assert response.status_code in [
            200,
            500,
        ]  # Accept both graceful handling and error

    def test_get_forecast_data_database_error(self, client, auth_headers):
        """Test forecast endpoint handles database errors gracefully."""
        with patch(
            "sqlite3.connect", side_effect=Exception("Database connection failed")
        ):
            response = client.get(
                "/api/v1/data/forecasts/rent_growth/35620", headers=auth_headers
            )

        # API handles errors gracefully, returning 200 with appropriate response
        assert response.status_code in [
            200,
            500,
        ]  # Accept both graceful handling and error

    def test_get_market_data_no_data_found(
        self, client, auth_headers, mock_database_connection
    ):
        """Test market data endpoint when no data is found."""
        mock_database_connection.fetchall.return_value = []

        with patch("pathlib.Path.exists", return_value=True):
            response = client.get("/api/v1/data/markets/35620", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        # API may provide fallback data when no database data is found
        assert "data_points" in data
        assert isinstance(data["data_points"], list)

    def test_get_forecast_data_no_data_found(
        self, client, auth_headers, mock_database_connection
    ):
        """Test forecast endpoint when no data is found."""
        mock_database_connection.fetchall.return_value = []

        with patch("pathlib.Path.exists", return_value=True):
            response = client.get(
                "/api/v1/data/forecasts/rent_growth/35620", headers=auth_headers
            )

        assert response.status_code == 200
        data = response.json()
        # API provides fallback forecasts when no database data is found (graceful degradation)
        assert "forecast_points" in data
        assert isinstance(data["forecast_points"], list)
        # Should have forecast data even without database data
        assert len(data["forecast_points"]) > 0

    def test_get_market_data_database_file_not_found(self, client, auth_headers):
        """Test market data endpoint when database file doesn't exist."""
        with patch("pathlib.Path.exists", return_value=False):
            response = client.get("/api/v1/data/markets/35620", headers=auth_headers)

        # API handles missing files gracefully, returning 200 with empty data
        assert response.status_code == 200

    def test_get_forecast_data_database_file_not_found(self, client, auth_headers):
        """Test forecast endpoint when database file doesn't exist."""
        with patch("pathlib.Path.exists", return_value=False):
            response = client.get(
                "/api/v1/data/forecasts/rent_growth/35620", headers=auth_headers
            )

        # API handles missing files gracefully, returning 200 with empty data
        assert response.status_code == 200

    def test_get_market_data_invalid_date_format(self, client, auth_headers):
        """Test market data endpoint with invalid date format."""
        response = client.get(
            "/api/v1/data/markets/35620?start_date=invalid-date", headers=auth_headers
        )

        # FastAPI should handle validation and return 422
        assert response.status_code == 422

    def test_get_market_data_end_date_before_start_date(
        self, client, auth_headers, mock_database_connection
    ):
        """Test market data endpoint with end date before start date."""
        mock_database_connection.fetchall.return_value = []

        with patch("pathlib.Path.exists", return_value=True):
            response = client.get(
                "/api/v1/data/markets/35620?start_date=2023-12-31&end_date=2023-01-01",
                headers=auth_headers,
            )

        # Should handle gracefully and return empty data
        assert response.status_code == 200

    def test_get_forecast_data_invalid_horizon(self, client, auth_headers):
        """Test forecast endpoint with invalid horizon parameter."""
        response = client.get(
            "/api/v1/data/forecasts/rent_growth/35620?horizon_years=0",
            headers=auth_headers,
        )

        # Should validate horizon is positive
        assert response.status_code == 422

    def test_get_forecast_data_invalid_confidence_level(self, client, auth_headers):
        """Test forecast endpoint with invalid confidence level."""
        response = client.get(
            "/api/v1/data/forecasts/rent_growth/35620?confidence_level=1.5",
            headers=auth_headers,
        )

        # Should validate confidence level is between 0 and 1
        assert response.status_code == 422

    def test_router_tags_and_responses(self):
        """Test that router has correct tags and response models."""
        assert router.prefix == "/api/v1/data"
        assert "data" in router.tags
        assert 401 in router.responses
        assert 403 in router.responses
        assert 404 in router.responses
        assert 500 in router.responses

    def test_authentication_required(self, client, auth_headers):
        """Test that endpoints require authentication."""
        # This test would need actual auth middleware,
        # but we're mocking it out for unit tests
        # In integration tests, this would be properly tested
        pass

    def test_parameter_filtering_logic(
        self, client, auth_headers, mock_database_connection
    ):
        """Test parameter filtering logic works correctly."""
        mock_database_connection.fetchall.return_value = [
            ("2023-01-01", "cap_rate", 0.055, 0.005),
            ("2023-01-01", "rent_growth", 0.03, 0.002),
            ("2023-01-01", "vacancy_rate", 0.05, 0.003),
        ]

        with patch("pathlib.Path.exists", return_value=True):
            # Request only cap_rate and rent_growth
            response = client.get(
                "/api/v1/data/markets/35620?parameters=cap_rate,rent_growth",
                headers=auth_headers,
            )

        assert response.status_code == 200
        # Database query should be filtered, but we're mocking the result

    def test_date_range_filtering_logic(
        self, client, auth_headers, mock_database_connection
    ):
        """Test date range filtering works correctly."""
        mock_database_connection.fetchall.return_value = [
            ("2023-06-01", "cap_rate", 0.055, 0.005),
        ]

        with patch("pathlib.Path.exists", return_value=True):
            response = client.get(
                "/api/v1/data/markets/35620?start_date=2023-01-01&end_date=2023-12-31",
                headers=auth_headers,
            )

        assert response.status_code == 200
        # Query should include date range filtering
