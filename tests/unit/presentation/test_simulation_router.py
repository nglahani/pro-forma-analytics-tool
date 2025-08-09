"""
Basic Simulation Router Tests

Tests for the implemented Monte Carlo simulation endpoint only.
"""

from datetime import date

import pytest
from fastapi.testclient import TestClient

from src.presentation.api.routers.simulation import router


class TestBasicSimulationRouter:
    """Test basic simulation router functionality."""

    @pytest.fixture
    def client(self):
        """Create test client with main app."""
        from src.presentation.api.main import app

        return TestClient(app)

    @pytest.fixture
    def auth_headers(self):
        """Get authentication headers for API requests."""
        return {"X-API-Key": "dev_test_key_12345678901234567890123"}

    @pytest.fixture
    def sample_monte_carlo_request(self):
        """Sample Monte Carlo request for testing."""
        return {
            "property_data": {
                "property_id": "TEST_MC_001",
                "property_name": "Monte Carlo Test Property",
                "analysis_date": date.today().isoformat(),
                "residential_units": {
                    "total_units": 50,
                    "average_rent_per_unit": 2500,
                    "unit_types": "Mixed: 25x1BR, 25x2BR",
                },
                "renovation_info": {
                    "status": "planned",
                    "anticipated_duration_months": 6,
                    "estimated_cost": 500000,
                },
                "equity_structure": {
                    "investor_equity_share_pct": 80.0,
                    "self_cash_percentage": 25.0,
                    "number_of_investors": 2,
                },
                "city": "New York",
                "state": "NY",
                "msa_code": "35620",
                "purchase_price": 8000000.0,
            },
            "simulation_count": 5000,
            "correlation_window_years": 5,
            "include_distributions": True,
            "percentiles": [5, 25, 50, 75, 95],
            "request_id": "test_mc_request_001",
        }

    def test_run_monte_carlo_simulation_success(
        self, client, auth_headers, sample_monte_carlo_request
    ):
        """Test successful Monte Carlo simulation."""
        response = client.post(
            "/api/v1/simulation/monte-carlo",
            json=sample_monte_carlo_request,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "request_id" in data
        assert "property_id" in data
        assert "simulation_timestamp" in data
        assert "simulation_count" in data
        assert "scenarios" in data
        assert "risk_metrics" in data
        assert "scenario_classification" in data
        assert "processing_time_seconds" in data

    def test_run_monte_carlo_simulation_validation_error(self, client, auth_headers):
        """Test Monte Carlo simulation with invalid request data."""
        invalid_request = {
            "property_data": {
                "property_id": "INVALID",
                # Missing required fields
            },
            "simulation_count": -1000,  # Invalid count
        }

        response = client.post(
            "/api/v1/simulation/monte-carlo", json=invalid_request, headers=auth_headers
        )
        assert response.status_code == 422  # Validation error

    def test_router_configuration(self):
        """Test that router has correct configuration."""
        assert router.prefix == "/api/v1/simulation"
        assert "simulation" in router.tags
        assert 401 in router.responses
        assert 404 in router.responses
        assert 500 in router.responses

    def test_monte_carlo_request_validation_edge_cases(self, client, auth_headers):
        """Test Monte Carlo request validation for edge cases."""
        # Test with simulation count at boundaries
        edge_case_requests = [
            {"simulation_count": 499},  # Below minimum
            {"simulation_count": 50001},  # Above maximum
            {"correlation_window_years": 2},  # Below minimum
            {"correlation_window_years": 16},  # Above maximum
            {"percentiles": [-5, 50, 105]},  # Invalid percentiles
        ]

        base_request = {
            "property_data": {
                "property_id": "EDGE_TEST",
                "property_name": "Edge Case Test",
                "analysis_date": date.today().isoformat(),
                "residential_units": {
                    "total_units": 10,
                    "average_rent_per_unit": 2000,
                    "unit_types": "1BR",
                },
                "renovation_info": {
                    "status": "not_needed",
                    "anticipated_duration_months": 0,
                },
                "equity_structure": {
                    "investor_equity_share_pct": 100.0,
                    "self_cash_percentage": 30.0,
                    "number_of_investors": 1,
                },
                "city": "Test City",
                "state": "TS",
                "purchase_price": 1000000.0,
            }
        }

        for edge_case in edge_case_requests:
            request = {**base_request, **edge_case}
            response = client.post(
                "/api/v1/simulation/monte-carlo", json=request, headers=auth_headers
            )
            assert response.status_code == 422  # Validation error
