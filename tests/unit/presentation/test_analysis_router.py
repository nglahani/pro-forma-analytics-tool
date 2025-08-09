"""
Unit tests for Analysis Router endpoints.

Tests the analysis router endpoints for DCF analysis functionality.
"""

from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from src.presentation.api.main import app


@pytest.fixture
def client():
    """Create test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Get authentication headers for API requests."""
    return {"X-API-Key": "dev_test_key_12345678901234567890123"}


@pytest.fixture
def mock_services():
    """Mock all required services for analysis router."""
    with patch(
        "src.presentation.api.dependencies.get_dcf_services"
    ) as mock_get_dcf_services, patch(
        "src.presentation.api.dependencies.get_dcf_assumptions_service"
    ) as mock_dcf_assumptions, patch(
        "src.presentation.api.dependencies.get_initial_numbers_service"
    ) as mock_initial_numbers, patch(
        "src.presentation.api.dependencies.get_cash_flow_projection_service"
    ) as mock_cash_flow, patch(
        "src.presentation.api.dependencies.get_financial_metrics_service"
    ) as mock_financial_metrics, patch(
        "src.presentation.api.dependencies.get_forecasting_service"
    ) as mock_forecasting, patch(
        "src.presentation.api.dependencies.get_monte_carlo_service"
    ) as mock_monte_carlo:

        # Mock individual services
        mock_dcf_assumptions_service = Mock()
        mock_initial_numbers_service = Mock()
        mock_cash_flow_service = Mock()
        mock_financial_metrics_service = Mock()
        mock_forecasting_service = Mock()
        mock_monte_carlo_service = Mock()

        # Set up return values
        mock_dcf_assumptions.return_value = mock_dcf_assumptions_service
        mock_initial_numbers.return_value = mock_initial_numbers_service
        mock_cash_flow.return_value = mock_cash_flow_service
        mock_financial_metrics.return_value = mock_financial_metrics_service
        mock_forecasting.return_value = mock_forecasting_service
        mock_monte_carlo.return_value = mock_monte_carlo_service

        # Create services dict for easier access in tests
        services = Mock()
        services.dcf_assumptions = mock_dcf_assumptions_service
        services.initial_numbers = mock_initial_numbers_service
        services.cash_flow_projection = mock_cash_flow_service
        services.financial_metrics = mock_financial_metrics_service
        services.forecasting = mock_forecasting_service
        services.monte_carlo = mock_monte_carlo_service

        # Mock get_dcf_services to return services dict
        mock_get_dcf_services.return_value = {
            "dcf_assumptions": mock_dcf_assumptions_service,
            "initial_numbers": mock_initial_numbers_service,
            "cash_flow_projection": mock_cash_flow_service,
            "financial_metrics": mock_financial_metrics_service,
        }

        yield services


class TestAnalysisRouter:
    """Test analysis router endpoints."""

    def test_single_property_dcf_analysis_success(
        self, client, auth_headers, mock_services
    ):
        """Test successful single property DCF analysis."""
        # Mock service responses
        mock_assumptions = Mock()
        mock_assumptions.scenario_name = "TEST_SCENARIO"
        mock_services.dcf_assumptions.create_dcf_assumptions_from_scenario.return_value = (
            mock_assumptions
        )

        mock_initial = Mock()
        mock_initial.total_cash_required = 100000
        mock_initial.ltv_ratio = 0.75
        mock_services.initial_numbers.calculate_initial_numbers.return_value = (
            mock_initial
        )

        mock_projection = Mock()
        mock_projection.total_noi = 50000
        mock_projection.total_distributions = 75000
        mock_services.cash_flow_projection.calculate_cash_flow_projection.return_value = (
            mock_projection
        )

        mock_metrics = Mock()
        mock_metrics.npv = 1000000
        mock_metrics.irr = 0.15
        mock_metrics.equity_multiple = 2.5
        mock_metrics.investment_recommendation = "STRONG_BUY"
        mock_services.financial_metrics.calculate_financial_metrics.return_value = (
            mock_metrics
        )

        request_data = {
            "property_data": {
                "property_id": "TEST_PROP_001",
                "property_name": "Test Property NYC",
                "analysis_date": "2024-01-15",
                "purchase_price": 1000000,
                "city": "New York",
                "state": "NY",
                "msa_code": "35620",
                "property_address": "123 Test St, New York, NY 10001",
                "residential_units": {
                    "total_units": 10,
                    "average_rent_per_unit": 2500,
                    "unit_types": "1-bedroom and 2-bedroom",
                },
                "renovation_info": {
                    "status": "planned",
                    "anticipated_duration_months": 12,
                },
                "equity_structure": {
                    "investor_equity_share_pct": 25,
                    "self_cash_percentage": 100,
                },
            },
            "options": {
                "forecast_horizon_years": 5,
                "monte_carlo_simulations": 500,
                "detailed_cash_flows": True,
            },
        }

        response = client.post(
            "/api/v1/analysis/dcf", json=request_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Print response for debugging
        print(f"Response keys: {list(data.keys())}")

        # Check for actual response structure
        assert "financial_metrics" in data
        assert "analysis_metadata" in data
        assert data["financial_metrics"]["npv"] is not None
        assert data["financial_metrics"]["irr"] is not None

    def test_single_property_dcf_analysis_validation_error(self, client, auth_headers):
        """Test single property DCF analysis with validation error."""
        invalid_request = {
            "property": {
                "purchase_price": -1000000,  # Invalid negative price
                "residential_units": 10,
            }
        }

        response = client.post(
            "/api/v1/analysis/dcf/single", json=invalid_request, headers=auth_headers
        )

        assert response.status_code == 422  # Validation error

    def test_single_property_dcf_analysis_service_error(
        self, client, auth_headers, mock_services
    ):
        """Test single property DCF analysis with service error."""
        mock_services.dcf_assumptions.create_dcf_assumptions_from_scenario.side_effect = Exception(
            "Service error"
        )

        request_data = {
            "property": {
                "purchase_price": 1000000,
                "residential_units": 10,
                "commercial_units": 0,
                "renovation_months": 12,
                "address": {
                    "street": "123 Test St",
                    "city": "New York",
                    "state": "NY",
                    "zip_code": "10001",
                },
                "financials": {
                    "avg_rent_per_unit": 2500,
                    "commercial_rent_psf": 0,
                    "equity_percentage": 25,
                    "cash_percentage": 100,
                    "closing_costs": 50000,
                },
            },
            "scenario": {
                "name": "TEST_SCENARIO",
                "mortgage_rate": 0.065,
                "cap_rate": 0.055,
            },
        }

        response = client.post(
            "/api/v1/analysis/dcf", json=request_data, headers=auth_headers
        )

        assert response.status_code == 500

    def test_single_property_dcf_analysis_with_monte_carlo(
        self, client, auth_headers, mock_services
    ):
        """Test single property DCF analysis with Monte Carlo simulation."""
        # Mock service responses
        mock_assumptions = Mock()
        mock_assumptions.scenario_name = "TEST_SCENARIO"
        mock_services.dcf_assumptions.create_dcf_assumptions_from_scenario.return_value = (
            mock_assumptions
        )

        mock_initial = Mock()
        mock_initial.total_cash_required = 100000
        mock_initial.ltv_ratio = 0.75
        mock_services.initial_numbers.calculate_initial_numbers.return_value = (
            mock_initial
        )

        mock_projection = Mock()
        mock_projection.total_noi = 50000
        mock_projection.total_distributions = 75000
        mock_services.cash_flow_projection.calculate_cash_flow_projection.return_value = (
            mock_projection
        )

        mock_metrics = Mock()
        mock_metrics.npv = 1000000
        mock_metrics.irr = 0.15
        mock_metrics.equity_multiple = 2.5
        mock_services.financial_metrics.calculate_financial_metrics.return_value = (
            mock_metrics
        )

        # Mock Monte Carlo service
        mock_simulation = Mock()
        mock_simulation.simulation_id = "test_simulation_123"
        mock_simulation.scenario_count = 500
        mock_services.monte_carlo.run_simulation.return_value = mock_simulation

        request_data = {
            "property": {
                "purchase_price": 1000000,
                "residential_units": 10,
                "commercial_units": 0,
                "renovation_months": 12,
                "address": {
                    "street": "123 Test St",
                    "city": "New York",
                    "state": "NY",
                    "zip_code": "10001",
                },
                "financials": {
                    "avg_rent_per_unit": 2500,
                    "commercial_rent_psf": 0,
                    "equity_percentage": 25,
                    "cash_percentage": 100,
                    "closing_costs": 50000,
                },
            },
            "scenario": {
                "name": "TEST_SCENARIO",
                "mortgage_rate": 0.065,
                "cap_rate": 0.055,
            },
            "analysis_options": {
                "forecast_horizon_years": 5,
                "monte_carlo_simulations": 500,
                "detailed_cash_flows": True,
            },
        }

        response = client.post(
            "/api/v1/analysis/dcf", json=request_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "monte_carlo_results" in data

        # Verify Monte Carlo service was called
        mock_services.monte_carlo.run_simulation.assert_called_once()

    def test_batch_property_dcf_analysis_success(
        self, client, auth_headers, mock_services
    ):
        """Test successful batch property DCF analysis."""
        # Mock successful analysis for each property
        mock_assumptions = Mock()
        mock_assumptions.scenario_name = "TEST_SCENARIO"
        mock_services.dcf_assumptions.create_dcf_assumptions_from_scenario.return_value = (
            mock_assumptions
        )

        mock_initial = Mock()
        mock_initial.total_cash_required = 100000
        mock_services.initial_numbers.calculate_initial_numbers.return_value = (
            mock_initial
        )

        mock_projection = Mock()
        mock_projection.total_noi = 50000
        mock_services.cash_flow_projection.calculate_cash_flow_projection.return_value = (
            mock_projection
        )

        mock_metrics = Mock()
        mock_metrics.npv = 1000000
        mock_metrics.irr = 0.15
        mock_services.financial_metrics.calculate_financial_metrics.return_value = (
            mock_metrics
        )

        request_data = {
            "properties": [
                {
                    "property": {
                        "purchase_price": 1000000,
                        "residential_units": 10,
                        "commercial_units": 0,
                        "renovation_months": 12,
                        "address": {
                            "street": "123 Test St",
                            "city": "New York",
                            "state": "NY",
                            "zip_code": "10001",
                        },
                        "financials": {
                            "avg_rent_per_unit": 2500,
                            "commercial_rent_psf": 0,
                            "equity_percentage": 25,
                            "cash_percentage": 100,
                            "closing_costs": 50000,
                        },
                    },
                    "scenario": {"name": "TEST_SCENARIO_1", "mortgage_rate": 0.065},
                }
            ],
            "analysis_options": {
                "forecast_horizon_years": 5,
                "monte_carlo_simulations": 0,
            },
        }

        response = client.post(
            "/api/v1/analysis/batch", json=request_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "results" in data
        assert len(data["results"]) == 1
        assert data["batch_summary"]["total_properties"] == 1
        assert data["batch_summary"]["successful_analyses"] == 1

    def test_batch_property_dcf_analysis_partial_failure(
        self, client, auth_headers, mock_services
    ):
        """Test batch property DCF analysis with some failures."""
        # First property succeeds, second fails
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                mock_assumptions = Mock()
                mock_assumptions.scenario_name = "TEST_SCENARIO"
                return mock_assumptions
            else:
                raise Exception("Service error for second property")

        mock_services.dcf_assumptions.create_dcf_assumptions_from_scenario.side_effect = (
            side_effect
        )

        # Mock other services for successful case
        mock_initial = Mock()
        mock_initial.total_cash_required = 100000
        mock_services.initial_numbers.calculate_initial_numbers.return_value = (
            mock_initial
        )

        mock_projection = Mock()
        mock_projection.total_noi = 50000
        mock_services.cash_flow_projection.calculate_cash_flow_projection.return_value = (
            mock_projection
        )

        mock_metrics = Mock()
        mock_metrics.npv = 1000000
        mock_services.financial_metrics.calculate_financial_metrics.return_value = (
            mock_metrics
        )

        request_data = {
            "properties": [
                {
                    "property": {
                        "purchase_price": 1000000,
                        "residential_units": 10,
                        "commercial_units": 0,
                        "renovation_months": 12,
                        "address": {
                            "street": "123 Test St",
                            "city": "New York",
                            "state": "NY",
                            "zip_code": "10001",
                        },
                        "financials": {
                            "avg_rent_per_unit": 2500,
                            "commercial_rent_psf": 0,
                            "equity_percentage": 25,
                            "cash_percentage": 100,
                            "closing_costs": 50000,
                        },
                    },
                    "scenario": {"name": "TEST_SCENARIO_1"},
                },
                {
                    "property": {
                        "purchase_price": 2000000,
                        "residential_units": 20,
                        "commercial_units": 0,
                        "renovation_months": 12,
                        "address": {
                            "street": "456 Test Ave",
                            "city": "New York",
                            "state": "NY",
                            "zip_code": "10002",
                        },
                        "financials": {
                            "avg_rent_per_unit": 3000,
                            "commercial_rent_psf": 0,
                            "equity_percentage": 25,
                            "cash_percentage": 100,
                            "closing_costs": 100000,
                        },
                    },
                    "scenario": {"name": "TEST_SCENARIO_2"},
                },
            ]
        }

        response = client.post(
            "/api/v1/analysis/batch", json=request_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["results"]) == 2
        assert data["batch_summary"]["total_properties"] == 2
        assert data["batch_summary"]["successful_analyses"] == 1
        assert data["batch_summary"]["failed_analyses"] == 1

    def test_batch_property_dcf_analysis_validation_error(self, client, auth_headers):
        """Test batch property DCF analysis with validation error."""
        invalid_request = {"properties": []}  # Empty list should cause validation error

        response = client.post(
            "/api/v1/analysis/dcf/batch", json=invalid_request, headers=auth_headers
        )

        assert response.status_code == 422

    def test_batch_property_dcf_analysis_empty_properties(self, client, auth_headers):
        """Test batch analysis with empty properties list."""
        request_data = {
            "properties": [],
            "analysis_options": {
                "forecast_horizon_years": 5,
                "monte_carlo_simulations": 0,
            },
        }

        response = client.post(
            "/api/v1/analysis/batch", json=request_data, headers=auth_headers
        )

        assert response.status_code == 422

    def test_analysis_options_defaults(self, client, auth_headers, mock_services):
        """Test that analysis options have sensible defaults."""
        mock_assumptions = Mock()
        mock_assumptions.scenario_name = "TEST_SCENARIO"
        mock_services.dcf_assumptions.create_dcf_assumptions_from_scenario.return_value = (
            mock_assumptions
        )

        mock_initial = Mock()
        mock_services.initial_numbers.calculate_initial_numbers.return_value = (
            mock_initial
        )

        mock_projection = Mock()
        mock_services.cash_flow_projection.calculate_cash_flow_projection.return_value = (
            mock_projection
        )

        mock_metrics = Mock()
        mock_metrics.npv = 1000000
        mock_services.financial_metrics.calculate_financial_metrics.return_value = (
            mock_metrics
        )

        # Request without analysis_options
        request_data = {
            "property": {
                "purchase_price": 1000000,
                "residential_units": 10,
                "commercial_units": 0,
                "renovation_months": 12,
                "address": {
                    "street": "123 Test St",
                    "city": "New York",
                    "state": "NY",
                    "zip_code": "10001",
                },
                "financials": {
                    "avg_rent_per_unit": 2500,
                    "commercial_rent_psf": 0,
                    "equity_percentage": 25,
                    "cash_percentage": 100,
                    "closing_costs": 50000,
                },
            },
            "scenario": {"name": "TEST_SCENARIO", "mortgage_rate": 0.065},
        }

        response = client.post(
            "/api/v1/analysis/dcf", json=request_data, headers=auth_headers
        )

        assert response.status_code == 200

    def test_router_configuration(self):
        """Test router configuration and metadata."""
        from src.presentation.api.routers.analysis import router

        assert router.prefix == "/api/v1/analysis"
        assert "analysis" in router.tags

    def test_error_response_format(self, client, auth_headers, mock_services):
        """Test that error responses have consistent format."""
        # Force a service error
        mock_services.dcf_assumptions.create_dcf_assumptions_from_scenario.side_effect = ValueError(
            "Test error"
        )

        request_data = {
            "property": {
                "purchase_price": 1000000,
                "residential_units": 10,
                "commercial_units": 0,
                "renovation_months": 12,
                "address": {
                    "street": "123 Test St",
                    "city": "New York",
                    "state": "NY",
                    "zip_code": "10001",
                },
                "financials": {
                    "avg_rent_per_unit": 2500,
                    "commercial_rent_psf": 0,
                    "equity_percentage": 25,
                    "cash_percentage": 100,
                    "closing_costs": 50000,
                },
            },
            "scenario": {"name": "TEST_SCENARIO"},
        }

        response = client.post(
            "/api/v1/analysis/dcf", json=request_data, headers=auth_headers
        )

        assert response.status_code == 500
        data = response.json()
        assert "success" in data
        assert data["success"] is False
        assert "error" in data

    def test_concurrent_batch_processing_limit(
        self, client, auth_headers, mock_services
    ):
        """Test that batch processing respects concurrency limits."""
        # Mock successful responses for all services
        mock_assumptions = Mock()
        mock_services.dcf_assumptions.create_dcf_assumptions_from_scenario.return_value = (
            mock_assumptions
        )
        mock_services.initial_numbers.calculate_initial_numbers.return_value = Mock()
        mock_services.cash_flow_projection.calculate_cash_flow_projection.return_value = (
            Mock()
        )
        mock_services.financial_metrics.calculate_financial_metrics.return_value = (
            Mock()
        )

        # Create a large batch (more than typical concurrency limit)
        properties = []
        for i in range(10):
            properties.append(
                {
                    "property": {
                        "purchase_price": 1000000 + i * 100000,
                        "residential_units": 10 + i,
                        "commercial_units": 0,
                        "renovation_months": 12,
                        "address": {
                            "street": f"{i} Test St",
                            "city": "New York",
                            "state": "NY",
                            "zip_code": f"1000{i}",
                        },
                        "financials": {
                            "avg_rent_per_unit": 2500,
                            "commercial_rent_psf": 0,
                            "equity_percentage": 25,
                            "cash_percentage": 100,
                            "closing_costs": 50000,
                        },
                    },
                    "scenario": {"name": f"TEST_SCENARIO_{i}"},
                }
            )

        request_data = {
            "properties": properties,
            "analysis_options": {
                "forecast_horizon_years": 5,
                "monte_carlo_simulations": 0,
            },
        }

        response = client.post(
            "/api/v1/analysis/batch", json=request_data, headers=auth_headers
        )

        # Should handle large batches gracefully
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["batch_summary"]["total_properties"] == 10
