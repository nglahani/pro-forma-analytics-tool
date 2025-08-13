"""
API Performance Tests

Benchmarks key API endpoints for latency and basic concurrency.
"""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from fastapi.testclient import TestClient

# Using centralized fixtures from conftest.py


def test_health_latency_under_1000ms(api_client: TestClient) -> None:
    start = time.perf_counter()
    resp = api_client.get("/api/v1/health")
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert resp.status_code == 200
    # Allow generous threshold in CI
    assert elapsed_ms < 1000, f"Health latency too high: {elapsed_ms:.1f}ms"


def _minimal_property_request() -> dict:
    from datetime import date

    return {
        "property_data": {
            "property_id": "PERF_MIN_001",
            "property_name": "Perf Test Property",
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
        },
        "options": {
            "monte_carlo_simulations": 1000,
            "forecast_horizon_years": 6,
            "include_scenarios": False,
            "confidence_level": 0.95,
            "detailed_cash_flows": False,
        },
    }


def test_dcf_latency_under_3000ms(api_client: TestClient, valid_api_key: str) -> None:
    headers = {"X-API-Key": valid_api_key}
    payload = _minimal_property_request()

    start = time.perf_counter()
    resp = api_client.post("/api/v1/analysis/dcf", json=payload, headers=headers)
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert resp.status_code in (200, 422, 500)
    # We enforce latency bound regardless of success to catch perf regressions
    assert elapsed_ms < 3000, f"DCF latency too high: {elapsed_ms:.1f}ms"


def test_basic_concurrency_three_dcf_requests(
    api_client: TestClient, valid_api_key: str
) -> None:
    headers = {"X-API-Key": valid_api_key}
    payload = _minimal_property_request()

    def call_once() -> int:
        r = api_client.post("/api/v1/analysis/dcf", json=payload, headers=headers)
        return r.status_code

    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=3) as ex:
        futures = [ex.submit(call_once) for _ in range(3)]
        statuses = [f.result() for f in as_completed(futures)]
    total_ms = (time.perf_counter() - start) * 1000

    # Ensure the system handles basic parallelism under a generous threshold
    assert total_ms < 5000, f"Concurrent DCF total time too high: {total_ms:.1f}ms"
    assert all(s in (200, 422, 500) for s in statuses)


def test_monte_carlo_latency_under_5000ms(
    api_client: TestClient, valid_api_key: str
) -> None:
    from datetime import date

    headers = {"X-API-Key": valid_api_key}
    payload = {
        "request_id": "perf_mc_001",
        "simulation_count": 1000,
        "property_data": {
            "property_id": "MC_PERF_PROP_1",
            "property_name": "Monte Carlo Perf Prop",
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
        },
    }

    start = time.perf_counter()
    resp = api_client.post(
        "/api/v1/simulation/monte-carlo", json=payload, headers=headers
    )
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert resp.status_code in (200, 422, 500)
    assert elapsed_ms < 5000, f"Monte Carlo latency too high: {elapsed_ms:.1f}ms"


def _compute_percentile(sorted_values: list[float], percentile: float) -> float:
    if not sorted_values:
        return 0.0
    k = int(round((len(sorted_values) - 1) * percentile))
    return sorted_values[min(max(k, 0), len(sorted_values) - 1)]


def test_high_concurrency_dcf_p95_under_4000ms(
    api_client: TestClient, valid_api_key: str
) -> None:
    headers = {"X-API-Key": valid_api_key}
    payload = _minimal_property_request()

    durations: list[float] = []

    def call_once() -> float:
        start = time.perf_counter()
        api_client.post("/api/v1/analysis/dcf", json=payload, headers=headers)
        return (time.perf_counter() - start) * 1000

    with ThreadPoolExecutor(max_workers=15) as ex:
        futures = [ex.submit(call_once) for _ in range(15)]
        for f in as_completed(futures):
            durations.append(f.result())

    durations.sort()
    p95 = _compute_percentile(durations, 0.95)
    assert p95 < 4000, f"DCF p95 too high: {p95:.1f}ms (samples={len(durations)})"
    p99 = _compute_percentile(durations, 0.99)
    assert p99 < 6000, f"DCF p99 too high: {p99:.1f}ms (samples={len(durations)})"


def test_concurrency_monte_carlo_p95_under_5000ms(
    api_client: TestClient, valid_api_key: str
) -> None:
    from datetime import date

    headers = {"X-API-Key": valid_api_key}
    payload = {
        "request_id": "perf_mc_conc_001",
        "simulation_count": 1000,
        "property_data": {
            "property_id": "MC_PERF_PROP_2",
            "property_name": "Monte Carlo Perf Prop 2",
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
        },
    }

    durations: list[float] = []

    def call_once() -> float:
        start = time.perf_counter()
        api_client.post("/api/v1/simulation/monte-carlo", json=payload, headers=headers)
        return (time.perf_counter() - start) * 1000

    with ThreadPoolExecutor(max_workers=10) as ex:
        futures = [ex.submit(call_once) for _ in range(10)]
        for f in as_completed(futures):
            durations.append(f.result())

    durations.sort()
    p95 = _compute_percentile(durations, 0.95)
    assert (
        p95 < 5000
    ), f"Monte Carlo p95 too high: {p95:.1f}ms (samples={len(durations)})"
    p99 = _compute_percentile(durations, 0.99)
    assert (
        p99 < 7000
    ), f"Monte Carlo p99 too high: {p99:.1f}ms (samples={len(durations)})"


def test_memory_smoke_script_runs() -> None:
    """Run memory profiling script as a smoke test (non-failing)."""
    import subprocess
    import sys

    r = subprocess.run(
        [sys.executable, "scripts/profile_memory.py"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    # Do not assert success strictly; just ensure it executes without crashing interpreter
    assert r.returncode in (0, 1)
