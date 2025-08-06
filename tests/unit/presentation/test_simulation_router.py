"""
Unit tests for Simulation Router endpoints.

Tests the simulation router endpoints for Monte Carlo simulation functionality.
"""

from datetime import date
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from src.presentation.api.routers.simulation import router


class TestSimulationRouterEndpoints:
    """Test simulation router API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client with mocked app."""
        from fastapi import FastAPI

        # Mock authentication dependency at module level
        with patch(
            "src.presentation.api.routers.simulation.require_permission"
        ) as mock_auth:
            mock_auth.return_value = lambda: True

            app = FastAPI()
            app.include_router(router)

            yield TestClient(app)

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

    @pytest.fixture
    def mock_monte_carlo_service(self):
        """Mock Monte Carlo service."""
        with patch(
            "src.application.factories.service_factory.ServiceFactory"
        ) as mock_factory:
            mock_service = Mock()
            mock_factory.return_value.get_monte_carlo_service.return_value = (
                mock_service
            )

            # Mock successful Monte Carlo result
            mock_service.generate_monte_carlo_scenarios.return_value = {
                "simulation_id": "sim_12345",
                "total_scenarios": 5000,
                "successful_scenarios": 4987,
                "npv_statistics": {
                    "mean": 2500000,
                    "median": 2450000,
                    "std_dev": 800000,
                    "percentiles": {
                        "p5": 1200000,
                        "p25": 1950000,
                        "p50": 2450000,
                        "p75": 3100000,
                        "p95": 4200000,
                    },
                },
                "irr_statistics": {
                    "mean": 0.185,
                    "median": 0.178,
                    "std_dev": 0.045,
                    "percentiles": {
                        "p5": 0.125,
                        "p25": 0.155,
                        "p50": 0.178,
                        "p75": 0.210,
                        "p95": 0.265,
                    },
                },
                "risk_metrics": {
                    "value_at_risk_5": -500000,
                    "expected_shortfall": -750000,
                    "probability_of_loss": 0.12,
                    "sharpe_ratio": 1.85,
                },
                "scenario_distribution": {
                    "bull_market": 25,
                    "bear_market": 18,
                    "neutral_market": 35,
                    "growth_market": 15,
                    "stress_market": 7,
                },
            }

            yield mock_service

    def test_run_monte_carlo_simulation_success(
        self, client, sample_monte_carlo_request, mock_monte_carlo_service
    ):
        """Test successful Monte Carlo simulation."""
        response = client.post(
            "/api/v1/simulation/monte-carlo", json=sample_monte_carlo_request
        )

        assert response.status_code == 200
        data = response.json()
        assert data["simulation_id"] == "sim_12345"
        assert data["total_scenarios"] == 5000
        assert data["successful_scenarios"] == 4987
        assert "npv_statistics" in data
        assert "irr_statistics" in data
        assert "risk_metrics" in data

    def test_run_monte_carlo_simulation_invalid_request(self, client):
        """Test Monte Carlo simulation with invalid request data."""
        invalid_request = {
            "property_data": {
                "property_id": "INVALID",
                # Missing required fields
            },
            "simulation_count": -1000,  # Invalid count
        }

        response = client.post("/api/v1/simulation/monte-carlo", json=invalid_request)
        assert response.status_code == 422  # Validation error

    def test_run_monte_carlo_simulation_service_error(
        self, client, sample_monte_carlo_request
    ):
        """Test Monte Carlo simulation when service raises error."""
        with patch(
            "src.application.factories.service_factory.ServiceFactory"
        ) as mock_factory:
            mock_service = Mock()
            mock_factory.return_value.get_monte_carlo_service.return_value = (
                mock_service
            )
            mock_service.generate_monte_carlo_scenarios.side_effect = Exception(
                "Service error"
            )

            response = client.post(
                "/api/v1/simulation/monte-carlo", json=sample_monte_carlo_request
            )

            assert response.status_code == 500

    def test_run_monte_carlo_simulation_minimum_parameters(self, client):
        """Test Monte Carlo simulation with minimum required parameters."""
        minimal_request = {
            "property_data": {
                "property_id": "MIN_TEST_001",
                "property_name": "Minimal Test Property",
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
                "city": "Chicago",
                "state": "IL",
                "purchase_price": 1000000.0,
            }
        }

        with patch(
            "src.application.factories.service_factory.ServiceFactory"
        ) as mock_factory:
            mock_service = Mock()
            mock_factory.return_value.get_monte_carlo_service.return_value = (
                mock_service
            )
            mock_service.generate_monte_carlo_scenarios.return_value = {
                "simulation_id": "sim_min_001",
                "total_scenarios": 10000,  # Default
                "successful_scenarios": 9985,
            }

            response = client.post(
                "/api/v1/simulation/monte-carlo", json=minimal_request
            )
            assert response.status_code == 200

    def test_run_monte_carlo_simulation_custom_percentiles(
        self, client, sample_monte_carlo_request, mock_monte_carlo_service
    ):
        """Test Monte Carlo simulation with custom percentiles."""
        sample_monte_carlo_request["percentiles"] = [1, 10, 50, 90, 99]

        response = client.post(
            "/api/v1/simulation/monte-carlo", json=sample_monte_carlo_request
        )

        assert response.status_code == 200

    def test_run_monte_carlo_simulation_high_scenario_count(
        self, client, sample_monte_carlo_request, mock_monte_carlo_service
    ):
        """Test Monte Carlo simulation with high scenario count."""
        sample_monte_carlo_request["simulation_count"] = 50000

        response = client.post(
            "/api/v1/simulation/monte-carlo", json=sample_monte_carlo_request
        )

        assert response.status_code == 200

    def test_get_simulation_status_success(self, client):
        """Test getting simulation status for existing simulation."""
        simulation_id = "sim_12345"

        with patch(
            "src.application.factories.service_factory.ServiceFactory"
        ) as mock_factory:
            mock_service = Mock()
            mock_factory.return_value.get_monte_carlo_service.return_value = (
                mock_service
            )
            mock_service.get_simulation_status.return_value = {
                "simulation_id": simulation_id,
                "status": "completed",
                "progress_percentage": 100,
                "scenarios_completed": 5000,
                "scenarios_total": 5000,
                "estimated_completion_time": None,
                "started_at": "2024-01-01T10:00:00Z",
                "completed_at": "2024-01-01T10:05:30Z",
            }

            response = client.get(f"/api/v1/simulation/status/{simulation_id}")

            assert response.status_code == 200
            data = response.json()
            assert data["simulation_id"] == simulation_id
            assert data["status"] == "completed"
            assert data["progress_percentage"] == 100

    def test_get_simulation_status_not_found(self, client):
        """Test getting simulation status for non-existent simulation."""
        simulation_id = "non_existent_sim"

        with patch(
            "src.application.factories.service_factory.ServiceFactory"
        ) as mock_factory:
            mock_service = Mock()
            mock_factory.return_value.get_monte_carlo_service.return_value = (
                mock_service
            )
            mock_service.get_simulation_status.return_value = None

            response = client.get(f"/api/v1/simulation/status/{simulation_id}")

            assert response.status_code == 404

    def test_get_simulation_status_in_progress(self, client):
        """Test getting simulation status for in-progress simulation."""
        simulation_id = "sim_in_progress"

        with patch(
            "src.application.factories.service_factory.ServiceFactory"
        ) as mock_factory:
            mock_service = Mock()
            mock_factory.return_value.get_monte_carlo_service.return_value = (
                mock_service
            )
            mock_service.get_simulation_status.return_value = {
                "simulation_id": simulation_id,
                "status": "running",
                "progress_percentage": 65,
                "scenarios_completed": 3250,
                "scenarios_total": 5000,
                "estimated_completion_time": "2024-01-01T10:08:00Z",
                "started_at": "2024-01-01T10:00:00Z",
                "completed_at": None,
            }

            response = client.get(f"/api/v1/simulation/status/{simulation_id}")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "running"
            assert data["progress_percentage"] == 65

    def test_get_simulation_results_success(self, client, mock_monte_carlo_service):
        """Test getting simulation results for completed simulation."""
        simulation_id = "sim_completed"

        mock_monte_carlo_service.get_simulation_results.return_value = {
            "simulation_id": simulation_id,
            "property_id": "TEST_PROP_001",
            "total_scenarios": 5000,
            "successful_scenarios": 4987,
            "results": {
                "npv_statistics": {"mean": 2500000, "percentiles": {"p50": 2450000}},
                "irr_statistics": {"mean": 0.185, "percentiles": {"p50": 0.178}},
            },
        }

        response = client.get(f"/api/v1/simulation/results/{simulation_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["simulation_id"] == simulation_id
        assert "results" in data

    def test_get_simulation_results_not_found(self, client):
        """Test getting simulation results for non-existent simulation."""
        simulation_id = "non_existent"

        with patch(
            "src.application.factories.service_factory.ServiceFactory"
        ) as mock_factory:
            mock_service = Mock()
            mock_factory.return_value.get_monte_carlo_service.return_value = (
                mock_service
            )
            mock_service.get_simulation_results.return_value = None

            response = client.get(f"/api/v1/simulation/results/{simulation_id}")

            assert response.status_code == 404

    def test_get_simulation_results_not_completed(self, client):
        """Test getting simulation results for incomplete simulation."""
        simulation_id = "sim_running"

        with patch(
            "src.application.factories.service_factory.ServiceFactory"
        ) as mock_factory:
            mock_service = Mock()
            mock_factory.return_value.get_monte_carlo_service.return_value = (
                mock_service
            )
            mock_service.get_simulation_results.side_effect = ValueError(
                "Simulation not completed"
            )

            response = client.get(f"/api/v1/simulation/results/{simulation_id}")

            assert response.status_code == 400

    def test_delete_simulation_success(self, client):
        """Test deleting a simulation successfully."""
        simulation_id = "sim_to_delete"

        with patch(
            "src.application.factories.service_factory.ServiceFactory"
        ) as mock_factory:
            mock_service = Mock()
            mock_factory.return_value.get_monte_carlo_service.return_value = (
                mock_service
            )
            mock_service.delete_simulation.return_value = True

            response = client.delete(f"/api/v1/simulation/{simulation_id}")

            assert response.status_code == 204

    def test_delete_simulation_not_found(self, client):
        """Test deleting a non-existent simulation."""
        simulation_id = "non_existent"

        with patch(
            "src.application.factories.service_factory.ServiceFactory"
        ) as mock_factory:
            mock_service = Mock()
            mock_factory.return_value.get_monte_carlo_service.return_value = (
                mock_service
            )
            mock_service.delete_simulation.return_value = False

            response = client.delete(f"/api/v1/simulation/{simulation_id}")

            assert response.status_code == 404

    def test_list_simulations_success(self, client):
        """Test listing simulations successfully."""
        with patch(
            "src.application.factories.service_factory.ServiceFactory"
        ) as mock_factory:
            mock_service = Mock()
            mock_factory.return_value.get_monte_carlo_service.return_value = (
                mock_service
            )
            mock_service.list_simulations.return_value = [
                {
                    "simulation_id": "sim_001",
                    "property_id": "PROP_001",
                    "status": "completed",
                    "created_at": "2024-01-01T10:00:00Z",
                    "scenarios": 5000,
                },
                {
                    "simulation_id": "sim_002",
                    "property_id": "PROP_002",
                    "status": "running",
                    "created_at": "2024-01-01T11:00:00Z",
                    "scenarios": 10000,
                },
            ]

            response = client.get("/api/v1/simulation/")

            assert response.status_code == 200
            data = response.json()
            assert len(data["simulations"]) == 2
            assert data["simulations"][0]["simulation_id"] == "sim_001"

    def test_list_simulations_with_filters(self, client):
        """Test listing simulations with status filter."""
        with patch(
            "src.application.factories.service_factory.ServiceFactory"
        ) as mock_factory:
            mock_service = Mock()
            mock_factory.return_value.get_monte_carlo_service.return_value = (
                mock_service
            )
            mock_service.list_simulations.return_value = [
                {
                    "simulation_id": "sim_completed",
                    "status": "completed",
                    "property_id": "PROP_001",
                    "created_at": "2024-01-01T10:00:00Z",
                    "scenarios": 5000,
                }
            ]

            response = client.get("/api/v1/simulation/?status=completed&limit=10")

            assert response.status_code == 200

    def test_cancel_simulation_success(self, client):
        """Test cancelling a running simulation."""
        simulation_id = "sim_running"

        with patch(
            "src.application.factories.service_factory.ServiceFactory"
        ) as mock_factory:
            mock_service = Mock()
            mock_factory.return_value.get_monte_carlo_service.return_value = (
                mock_service
            )
            mock_service.cancel_simulation.return_value = True

            response = client.post(f"/api/v1/simulation/{simulation_id}/cancel")

            assert response.status_code == 200

    def test_cancel_simulation_not_found(self, client):
        """Test cancelling a non-existent simulation."""
        simulation_id = "non_existent"

        with patch(
            "src.application.factories.service_factory.ServiceFactory"
        ) as mock_factory:
            mock_service = Mock()
            mock_factory.return_value.get_monte_carlo_service.return_value = (
                mock_service
            )
            mock_service.cancel_simulation.return_value = False

            response = client.post(f"/api/v1/simulation/{simulation_id}/cancel")

            assert response.status_code == 404

    def test_router_configuration(self):
        """Test that router has correct configuration."""
        assert router.prefix == "/api/v1/simulation"
        assert "simulation" in router.tags
        assert 401 in router.responses
        assert 404 in router.responses
        assert 500 in router.responses

    def test_monte_carlo_request_validation_edge_cases(self, client):
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
            response = client.post("/api/v1/simulation/monte-carlo", json=request)
            assert response.status_code == 422  # Validation error
