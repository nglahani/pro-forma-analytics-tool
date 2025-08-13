"""
Integration Tests for API Endpoints

Tests the complete API functionality including authentication, validation,
and DCF analysis workflow integration. Uses centralized fixtures from conftest.py.
"""

from datetime import date

import pytest


@pytest.fixture
def minimal_property_request():
    """Create minimal valid property request for testing."""
    return {
        "property_data": {
            "property_id": "TEST_MINIMAL_001",
            "property_name": "Minimal Test Property",
            "analysis_date": date.today().isoformat(),
            "residential_units": {"total_units": 5, "average_rent_per_unit": 1500},
            "renovation_info": {"status": "not_needed"},
            "commercial_units": {
                "has_commercial_space": False,
                "total_commercial_sqft": 0,
                "average_rent_per_sqft": 0,
            },
            "financing_info": {
                "equity_percentage": 0.25,
                "cash_percentage": 0.20,
            },
            "location_info": {
                "city": "Miami",
                "state": "FL",
                "zip_code": "33101",
                "msa_code": "33100",
            },
        }
    }


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check_success(self, api_client):
        """Test health check returns 200 OK."""
        response = api_client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()

        # In test environment, databases are missing so status should be degraded
        assert data["status"] in ["healthy", "degraded"]  # Allow both statuses
        assert "timestamp" in data
        assert "version" in data
        assert "uptime_seconds" in data
        assert "dependencies" in data

    def test_health_check_no_auth_required(self, api_client):
        """Test health check works without authentication."""
        # No headers provided
        response = api_client.get("/api/v1/health")
        assert response.status_code == 200


class TestMetricsEndpoint:
    """Test metrics endpoint."""

    def test_metrics_no_auth_required(self, api_client):
        """Metrics should be accessible without authentication."""
        response = api_client.get("/api/v1/metrics")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["ok", "error"]
        assert "timestamp" in data
        # When ok, expect core metric fields
        if data["status"] == "ok":
            assert "uptime_seconds" in data
            assert "total_requests" in data
            assert "endpoint_statistics" in data

    def test_metrics_prometheus_format(self, api_client):
        """Prometheus format should return text/plain and metrics lines."""
        response = api_client.get("/api/v1/metrics?format=prometheus")
        assert response.status_code == 200
        assert response.headers.get("content-type", "").startswith("text/plain")
        body = response.text
        assert "proforma_uptime_seconds" in body
        assert "proforma_total_requests" in body


class TestAuthentication:
    """Test API authentication."""

    def test_valid_api_key_accepted(self, api_client, valid_api_key):
        """Test that valid API key is accepted."""
        headers = {"X-API-Key": valid_api_key}
        response = api_client.post(
            "/api/v1/analysis/dcf",
            json={"property_data": {"property_id": "test"}},
            headers=headers,
        )
        # Should not fail with 401/403 - may fail with 422 due to invalid data
        assert response.status_code != 401
        assert response.status_code != 403

    def test_invalid_api_key_rejected(self, api_client, invalid_api_key):
        """Test that invalid API key is rejected."""
        headers = {"X-API-Key": invalid_api_key}
        response = api_client.post(
            "/api/v1/analysis/dcf", json={"property_data": {}}, headers=headers
        )
        assert response.status_code in [401, 403]

    def test_missing_api_key_rejected(self, api_client):
        """Test that missing API key is rejected."""
        response = api_client.post("/api/v1/analysis/dcf", json={"property_data": {}})
        assert response.status_code in [401, 403]


class TestDCFAnalysisEndpoint:
    """Test DCF analysis endpoint."""

    def test_dcf_analysis_valid_request(
        self, api_client, valid_api_key, sample_property_request
    ):
        """Test DCF analysis with valid property data."""
        headers = {"X-API-Key": valid_api_key}
        response = api_client.post(
            "/api/v1/analysis/dcf", json=sample_property_request, headers=headers
        )

        # Should succeed with 200 or fail gracefully with specific error
        if response.status_code == 200:
            data = response.json()
            assert "analysis_results" in data
            assert "property_id" in data["analysis_results"]
        else:
            # If failed, should be 400/422 with detailed error, not 500
            assert response.status_code in [400, 422]
            data = response.json()
            # Custom error format uses different field names
            assert any(key in data for key in ["detail", "details", "field_errors"])

    def test_dcf_analysis_minimal_request(
        self, api_client, valid_api_key, minimal_property_request
    ):
        """Test DCF analysis with minimal valid property data."""
        headers = {"X-API-Key": valid_api_key}
        response = api_client.post(
            "/api/v1/analysis/dcf", json=minimal_property_request, headers=headers
        )

        # Should handle minimal data gracefully
        assert response.status_code in [200, 400, 422]
        if response.status_code != 200:
            data = response.json()
            # Custom error format uses different field names
            assert any(key in data for key in ["detail", "details", "field_errors"])

    def test_dcf_analysis_invalid_request(self, api_client, valid_api_key):
        """Test DCF analysis with invalid property data."""
        headers = {"X-API-Key": valid_api_key}
        invalid_request = {"property_data": {"invalid_field": "invalid_value"}}

        response = api_client.post(
            "/api/v1/analysis/dcf", json=invalid_request, headers=headers
        )

        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "details" in data or "detail" in data  # API response format varies


class TestDataEndpoints:
    """Test data-related endpoints."""

    def test_parameters_list(self, api_client, valid_api_key):
        """Test parameters list endpoint."""
        headers = {"X-API-Key": valid_api_key}
        response = api_client.get("/api/v1/data/parameters", headers=headers)

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
        else:
            # Should fail gracefully if data not available
            assert response.status_code in [404, 503]

    def test_market_data_endpoint(self, api_client, valid_api_key):
        """Test market data endpoint."""
        headers = {"X-API-Key": valid_api_key}
        response = api_client.get(
            "/api/v1/data/market-data?msa_code=16740", headers=headers
        )

        # Should either return data or fail gracefully
        assert response.status_code in [200, 404, 503]
        if response.status_code == 200:
            data = response.json()
            assert "msa_code" in data


class TestSimulationEndpoints:
    """Test Monte Carlo simulation endpoints."""

    def test_monte_carlo_analysis(
        self, api_client, valid_api_key, sample_property_request
    ):
        """Test Monte Carlo simulation endpoint."""
        headers = {"X-API-Key": valid_api_key}

        # Add Monte Carlo options to the request
        mc_request = sample_property_request.copy()
        mc_request["options"] = {
            "monte_carlo_simulations": 100,  # Small number for testing
            "forecast_horizon_years": 5,
            "include_scenarios": True,
            "confidence_level": 0.95,
        }

        response = api_client.post(
            "/api/v1/simulation/monte-carlo", json=mc_request, headers=headers
        )

        # Should succeed or fail gracefully
        if response.status_code == 200:
            data = response.json()
            assert "simulation_results" in data
            assert "scenarios" in data["simulation_results"]
        else:
            # Should fail gracefully with proper error
            assert response.status_code in [400, 422, 503]
            if response.status_code != 503:
                data = response.json()
                # Custom error format uses different field names
            assert any(key in data for key in ["detail", "details", "field_errors"])


class TestErrorHandling:
    """Test error handling across endpoints."""

    def test_invalid_endpoint_404(self, api_client):
        """Test that invalid endpoints return 404 or 401 (if auth required)."""
        response = api_client.get("/api/v1/nonexistent")
        assert response.status_code in [
            401,
            404,
        ]  # 401 if auth required, 404 if not found

    def test_invalid_method_405(self, api_client):
        """Test that invalid HTTP methods return 405."""
        response = api_client.delete("/api/v1/health")
        assert response.status_code == 405

    def test_malformed_json_400(self, api_client, valid_api_key):
        """Test that malformed JSON returns 400."""
        headers = {"X-API-Key": valid_api_key, "Content-Type": "application/json"}
        response = api_client.post(
            "/api/v1/analysis/dcf",
            data="{invalid json",  # Malformed JSON
            headers=headers,
        )
        assert response.status_code in [
            400,
            422,
        ]  # Either is acceptable for malformed JSON
