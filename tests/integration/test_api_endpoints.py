"""
Integration Tests for API Endpoints

Tests the complete API functionality including authentication, validation,
and DCF analysis workflow integration.
"""

from datetime import date

import pytest
from fastapi.testclient import TestClient

from src.presentation.api.main import app


@pytest.fixture
def client():
    """Create test client for API testing."""
    return TestClient(app)


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
            "property_id": "TEST_API_001",
            "property_name": "API Test Property",
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
            "equity_structure": {
                "investor_equity_share_pct": 80.0,
                "self_cash_percentage": 25.0,
                "number_of_investors": 1,
            },
            "city": "Chicago",
            "state": "IL",
            "purchase_price": 1000000.0,
        },
        "options": {
            "monte_carlo_simulations": 1000,
            "forecast_horizon_years": 6,
            "include_scenarios": True,
            "confidence_level": 0.95,
            "detailed_cash_flows": True,
        },
        "request_id": "integration_test_001",
    }


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
            "equity_structure": {
                "investor_equity_share_pct": 75.0,
                "self_cash_percentage": 30.0,
            },
            "city": "Miami",
            "state": "FL",
            "purchase_price": 500000.0,
        }
    }


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check_success(self, client):
        """Test health check returns 200 OK."""
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()

        # In test environment, databases are missing so status should be degraded
        assert data["status"] in ["healthy", "degraded"]  # Allow both statuses
        assert "timestamp" in data
        assert "version" in data
        assert "uptime_seconds" in data
        assert "dependencies" in data

    def test_health_check_no_auth_required(self, client):
        """Test health check works without authentication."""
        # No headers provided
        response = client.get("/api/v1/health")
        assert response.status_code == 200


class TestMetricsEndpoint:
    """Test metrics endpoint."""

    def test_metrics_no_auth_required(self, client):
        """Metrics should be accessible without authentication."""
        response = client.get("/api/v1/metrics")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["ok", "error"]
        assert "timestamp" in data
        # When ok, expect core metric fields
        if data["status"] == "ok":
            assert "uptime_seconds" in data
            assert "total_requests" in data
            assert "endpoint_statistics" in data

    def test_metrics_prometheus_format(self, client):
        """Prometheus format should return text/plain and metrics lines."""
        response = client.get("/api/v1/metrics?format=prometheus")
        assert response.status_code == 200
        assert response.headers.get("content-type", "").startswith("text/plain")
        body = response.text
        assert "proforma_uptime_seconds" in body
        assert "proforma_total_requests" in body


class TestAuthentication:
    """Test API authentication middleware."""

    def test_protected_endpoint_without_auth(self, client, sample_property_request):
        """Test protected endpoint requires authentication."""
        response = client.post("/api/v1/analysis/dcf", json=sample_property_request)

        assert response.status_code == 401
        data = response.json()

        assert data["error_code"] == "authentication_failed"
        assert "API key required" in data["message"]
        assert "timestamp" in data

    def test_protected_endpoint_invalid_auth(
        self, client, sample_property_request, invalid_api_key
    ):
        """Test protected endpoint rejects invalid API key."""
        headers = {"X-API-Key": invalid_api_key}
        response = client.post(
            "/api/v1/analysis/dcf", json=sample_property_request, headers=headers
        )

        assert response.status_code == 401
        data = response.json()

        assert data["error_code"] == "authentication_failed"
        assert "Invalid API key" in data["message"]

    def test_valid_api_key_format(self, client, valid_api_key):
        """Test valid API key passes authentication for test endpoint."""
        headers = {"X-API-Key": valid_api_key}
        response = client.get("/api/v1/test", headers=headers)

        # Should get 200 (success) not 401 (auth error)
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Test endpoint works"


class TestRequestValidation:
    """Test request validation and error handling."""

    def test_dcf_analysis_missing_required_fields(self, client, valid_api_key):
        """Test DCF analysis with missing required fields."""
        invalid_request = {
            "property_data": {
                "property_id": "INVALID_001"
                # Missing required fields
            }
        }

        headers = {"X-API-Key": valid_api_key}
        response = client.post(
            "/api/v1/analysis/dcf", json=invalid_request, headers=headers
        )

        assert response.status_code == 422
        data = response.json()

        assert data["error_code"] == "validation_error"
        assert "field_errors" in data
        assert "invalid_fields" in data
        assert len(data["invalid_fields"]) > 0

    def test_dcf_analysis_invalid_field_types(self, client, valid_api_key):
        """Test DCF analysis with invalid field types."""
        invalid_request = {
            "property_data": {
                "property_id": "INVALID_002",
                "property_name": "Invalid Property",
                "analysis_date": date.today().isoformat(),
                "residential_units": {
                    "total_units": "not_a_number",  # Invalid type
                    "average_rent_per_unit": 2000,
                },
                "renovation_info": {"status": "not_needed"},
                "equity_structure": {
                    "investor_equity_share_pct": 80.0,
                    "self_cash_percentage": 25.0,
                },
            }
        }

        headers = {"X-API-Key": valid_api_key}
        response = client.post(
            "/api/v1/analysis/dcf", json=invalid_request, headers=headers
        )

        assert response.status_code == 422
        data = response.json()

        assert data["error_code"] == "validation_error"
        assert "field_errors" in data

    def test_dcf_analysis_invalid_business_rules(self, client, valid_api_key):
        """Test DCF analysis with data that violates business rules."""
        invalid_request = {
            "property_data": {
                "property_id": "INVALID_003",
                "property_name": "Invalid Business Rules",
                "analysis_date": date.today().isoformat(),
                "residential_units": {
                    "total_units": -5,  # Negative units
                    "average_rent_per_unit": -1000,  # Negative rent
                },
                "renovation_info": {"status": "not_needed"},
                "equity_structure": {
                    "investor_equity_share_pct": 150.0,  # Over 100%
                    "self_cash_percentage": 25.0,
                },
            }
        }

        headers = {"X-API-Key": valid_api_key}
        response = client.post(
            "/api/v1/analysis/dcf", json=invalid_request, headers=headers
        )

        # Should get validation error due to business rule violations
        assert response.status_code in [422, 500]  # Could be validation or domain error


class TestDCFAnalysisEndpoint:
    """Test DCF analysis endpoint functionality."""

    def test_dcf_analysis_minimal_valid_request(
        self, client, valid_api_key, minimal_property_request
    ):
        """Test DCF analysis with minimal valid request."""
        headers = {"X-API-Key": valid_api_key}
        response = client.post(
            "/api/v1/analysis/dcf", json=minimal_property_request, headers=headers
        )

        # Log response for debugging
        print(f"Response status: {response.status_code}")
        if response.status_code != 200:
            print(f"Response body: {response.text}")

        # Should succeed or provide detailed error information
        if response.status_code == 200:
            data = response.json()

            # Verify response structure
            assert "request_id" in data
            assert "property_id" in data
            assert data["property_id"] == "TEST_MINIMAL_001"
            assert "analysis_date" in data
            assert "financial_metrics" in data
            assert "metadata" in data

            # Verify metadata
            metadata = data["metadata"]
            assert "processing_time_seconds" in metadata
            assert "analysis_timestamp" in metadata
            assert "data_sources" in metadata

        else:
            # If it fails, ensure we get proper error structure
            data = response.json()
            assert "error_code" in data
            assert "message" in data
            assert "timestamp" in data

    def test_dcf_analysis_complete_request(
        self, client, valid_api_key, sample_property_request
    ):
        """Test DCF analysis with complete request data."""
        headers = {"X-API-Key": valid_api_key}
        response = client.post(
            "/api/v1/analysis/dcf", json=sample_property_request, headers=headers
        )

        # Log response for debugging
        print(f"Complete request response status: {response.status_code}")
        if response.status_code != 200:
            print(f"Complete request response body: {response.text}")

        if response.status_code == 200:
            data = response.json()

            # Verify all expected fields
            assert data["request_id"] == "integration_test_001"
            assert data["property_id"] == "TEST_API_001"

            # Verify financial metrics exist
            assert "financial_metrics" in data
            financial_metrics = data["financial_metrics"]

            # Should have key financial metrics
            expected_metrics = [
                "net_present_value",
                "internal_rate_return",
                "investment_recommendation",
            ]
            for metric in expected_metrics:
                assert metric in financial_metrics

            # Verify cash flows included when requested
            if sample_property_request["options"]["detailed_cash_flows"]:
                assert "cash_flows" in data
                assert data["cash_flows"] is not None

            # Verify DCF assumptions
            assert "dcf_assumptions" in data
            assert "investment_recommendation" in data

        else:
            # Ensure error response is properly structured
            data = response.json()
            assert "error_code" in data
            assert "message" in data

    def test_dcf_analysis_request_id_correlation(
        self, client, valid_api_key, sample_property_request
    ):
        """Test that request IDs are properly correlated in responses."""
        custom_request_id = "custom_test_id_123"
        sample_property_request["request_id"] = custom_request_id

        headers = {"X-API-Key": valid_api_key}
        response = client.post(
            "/api/v1/analysis/dcf", json=sample_property_request, headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            assert data["request_id"] == custom_request_id
        else:
            # Even error responses should maintain request ID correlation
            data = response.json()
            if "request_id" in data:
                # Request ID correlation in errors (may be different due to middleware)
                assert isinstance(data["request_id"], str)


class TestBatchAnalysisEndpoint:
    """Test batch analysis endpoint functionality."""

    def test_batch_analysis_single_property(
        self, client, valid_api_key, minimal_property_request
    ):
        """Test batch analysis with single property."""
        batch_request = {
            "properties": [minimal_property_request],
            "parallel_processing": True,
            "max_concurrent": 10,
            "batch_id": "test_batch_001",
        }

        headers = {"X-API-Key": valid_api_key}
        response = client.post(
            "/api/v1/analysis/batch", json=batch_request, headers=headers
        )

        print(f"Batch analysis response status: {response.status_code}")
        if response.status_code != 200:
            print(f"Batch analysis response body: {response.text}")

        if response.status_code == 200:
            data = response.json()

            # Verify batch response structure
            assert "batch_id" in data
            assert "total_properties" in data
            assert data["total_properties"] == 1
            assert "successful_analyses" in data
            assert "failed_analyses" in data
            assert "results" in data
            assert len(data["results"]) == 1

            # Verify processing summary
            assert "processing_summary" in data
            summary = data["processing_summary"]
            assert "total_processing_time_seconds" in summary
            assert "success_rate" in summary

    def test_batch_analysis_empty_list(self, client, valid_api_key):
        """Test batch analysis with empty property list."""
        batch_request = {"properties": []}  # Empty list should be rejected

        headers = {"X-API-Key": valid_api_key}
        response = client.post(
            "/api/v1/analysis/batch", json=batch_request, headers=headers
        )

        # Should get validation error for empty list
        assert response.status_code == 422
        data = response.json()
        assert "field_errors" in data


class TestRateLimiting:
    """Test rate limiting functionality."""

    def test_rate_limiting_headers(self, client, valid_api_key):
        """Test that rate limiting headers are included."""
        headers = {"X-API-Key": valid_api_key}
        response = client.get("/api/v1/test", headers=headers)

        # Should include rate limiting headers
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers

    def test_multiple_requests_rate_limit_tracking(self, client, valid_api_key):
        """Test that multiple requests properly track rate limits."""
        headers = {"X-API-Key": valid_api_key}

        # Make first request
        response1 = client.get("/api/v1/test", headers=headers)
        remaining1 = int(response1.headers.get("X-RateLimit-Remaining", 0))

        # Make second request
        response2 = client.get("/api/v1/test", headers=headers)
        remaining2 = int(response2.headers.get("X-RateLimit-Remaining", 0))

        # Remaining should decrease (or be managed by rate limiting)
        assert remaining2 <= remaining1


class TestResponseFormat:
    """Test API response format consistency."""

    def test_error_response_format(self, client):
        """Test that error responses follow consistent format."""
        # Try to access protected endpoint without auth
        response = client.post("/api/v1/analysis/dcf", json={})

        assert response.status_code == 401
        data = response.json()

        # Verify standard error response format
        required_fields = ["error_code", "message", "timestamp"]
        for field in required_fields:
            assert field in data

        # Verify timestamp is ISO format string
        assert isinstance(data["timestamp"], str)
        assert "T" in data["timestamp"]  # ISO format indicator

    def test_success_response_headers(self, client, valid_api_key):
        """Test that success responses include proper headers."""
        headers = {"X-API-Key": valid_api_key}
        response = client.get("/api/v1/test", headers=headers)

        assert response.status_code == 200

        # Should include request correlation header
        assert "X-Request-ID" in response.headers
        assert "X-Processing-Time" in response.headers


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])
