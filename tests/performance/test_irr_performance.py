"""
IRR Calculation Performance Tests

Compare the performance of the new SciPy-based IRR calculation
against various test cases and scenarios.
"""

import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.application.services.financial_metrics_service import FinancialMetricsService


class TestIRRPerformance:
    """Performance tests for IRR calculation."""

    def setup_method(self):
        """Setup test fixtures."""
        self.service = FinancialMetricsService()

        # Various test cash flow scenarios
        self.test_scenarios = {
            "simple_positive": [-1000, 200, 300, 400, 500],
            "real_estate_typical": [-2500000, 350000, 375000, 400000, 425000, 3200000],
            "negative_years": [-1000, -100, 200, 300, 800],
            "high_return": [-1000, 500, 600, 700, 800],
            "break_even": [-1000, 250, 250, 250, 250],
            "volatile": [-5000, 1000, -500, 2000, 4000],
            "large_terminal": [-10000, 100, 150, 200, 15000],
            "declining": [-1000, 500, 400, 300, 200],
        }

    def test_irr_calculation_speed(self):
        """Test IRR calculation speed for various scenarios."""
        print("\n=== IRR Performance Benchmark ===")

        results = {}

        for scenario_name, cash_flows in self.test_scenarios.items():
            # Measure execution time
            start_time = time.perf_counter()

            # Run IRR calculation multiple times for better measurement
            iterations = 100
            irr_results = []

            for _ in range(iterations):
                irr = self.service._calculate_irr(cash_flows)
                irr_results.append(irr)

            end_time = time.perf_counter()
            avg_time = (
                (end_time - start_time) / iterations * 1000
            )  # Convert to milliseconds

            # Validate consistency
            irr_std = np.std(irr_results)
            avg_irr = np.mean(irr_results)

            results[scenario_name] = {
                "avg_time_ms": avg_time,
                "avg_irr": avg_irr,
                "irr_std": irr_std,
                "cash_flows": cash_flows,
            }

            print(
                f"{scenario_name:20} | {avg_time:6.2f}ms | IRR: {avg_irr:6.1%} | Std: {irr_std:.6f}"
            )

        # Overall performance summary
        avg_performance = np.mean([r["avg_time_ms"] for r in results.values()])
        print(f"\nAverage IRR calculation time: {avg_performance:.2f}ms")

        # Performance assertions
        assert (
            avg_performance < 50.0
        ), f"IRR calculation too slow: {avg_performance:.2f}ms > 50ms"

        # Consistency assertions
        for scenario_name, result in results.items():
            assert (
                result["irr_std"] < 1e-10
            ), f"IRR calculation inconsistent for {scenario_name}: std={result['irr_std']}"

    def test_irr_edge_cases_performance(self):
        """Test performance on edge cases."""
        print("\n=== IRR Edge Cases Performance ===")

        edge_cases = {
            "all_negative": [-1000, -100, -200, -300],
            "all_positive": [1000, 100, 200, 300],
            "zero_irr": [-1000, 1000, 0, 0, 0],
            "single_period": [-1000, 1200],
            "no_solution": [-1000, 100, 100, 100, 100],  # Very low return
            "extreme_high": [-1000, 10000, 20000, 30000],  # Very high return
            "tiny_amounts": [-0.01, 0.002, 0.003, 0.008],
            "large_amounts": [-10000000, 2000000, 3000000, 8000000],
        }

        for case_name, cash_flows in edge_cases.items():
            start_time = time.perf_counter()

            irr = self.service._calculate_irr(cash_flows)

            end_time = time.perf_counter()
            execution_time = (end_time - start_time) * 1000

            print(f"{case_name:20} | {execution_time:6.2f}ms | IRR: {irr:8.1%}")

            # Should complete quickly even for edge cases
            assert (
                execution_time < 100.0
            ), f"Edge case {case_name} too slow: {execution_time:.2f}ms"

            # Should return valid result (0.0 for no solution cases is acceptable)
            assert isinstance(irr, float), f"IRR should return float for {case_name}"
            assert not np.isnan(irr), f"IRR should not be NaN for {case_name}"

    def test_irr_batch_performance(self):
        """Test performance when calculating IRR for many scenarios."""
        print("\n=== IRR Batch Processing Performance ===")

        # Generate 100 random real estate-like cash flow scenarios
        np.random.seed(42)  # For reproducible results
        batch_scenarios = []

        for i in range(100):
            initial_investment = np.random.uniform(1000000, 10000000)  # $1M - $10M
            annual_cash_flows = np.random.uniform(
                50000, 500000, 4
            )  # 4 years of cash flows
            terminal_value = np.random.uniform(800000, 12000000)  # Terminal value

            cash_flows = (
                [-initial_investment] + list(annual_cash_flows) + [terminal_value]
            )
            batch_scenarios.append(cash_flows)

        # Measure batch processing time
        start_time = time.perf_counter()

        irr_results = []
        for cash_flows in batch_scenarios:
            irr = self.service._calculate_irr(cash_flows)
            irr_results.append(irr)

        end_time = time.perf_counter()
        total_time = end_time - start_time
        avg_time_per_calculation = (total_time / len(batch_scenarios)) * 1000

        print(f"Processed {len(batch_scenarios)} IRR calculations in {total_time:.3f}s")
        print(f"Average time per calculation: {avg_time_per_calculation:.2f}ms")
        print(f"IRR results range: {min(irr_results):.1%} to {max(irr_results):.1%}")
        print(
            f"Valid IRR count: {sum(1 for irr in irr_results if irr > 0)}/{len(irr_results)}"
        )

        # Performance assertions for batch processing
        assert (
            avg_time_per_calculation < 20.0
        ), f"Batch IRR processing too slow: {avg_time_per_calculation:.2f}ms per calculation"
        assert (
            total_time < 5.0
        ), f"Total batch processing time too slow: {total_time:.3f}s"

        # Quality assertions - more realistic criteria for random scenarios
        valid_irr_count = sum(
            1 for irr in irr_results if -0.5 < irr < 3.0
        )  # Broader reasonable IRR range
        successful_calculations = sum(
            1 for irr in irr_results if irr != 0.0
        )  # Non-zero results

        print(
            f"Successful calculations (non-zero): {successful_calculations}/{len(batch_scenarios)}"
        )

        # Most calculations should succeed (not return 0.0 due to failure)
        assert (
            successful_calculations > len(batch_scenarios) * 0.7
        ), f"Too many failed IRR calculations: {successful_calculations}/{len(batch_scenarios)}"

    def test_irr_accuracy_validation(self):
        """Validate IRR accuracy by checking NPV at calculated IRR."""
        print("\n=== IRR Accuracy Validation ===")

        validation_cases = [
            [-1000, 200, 300, 400, 500],  # Known case
            [-2500000, 350000, 375000, 400000, 425000, 3200000],  # Real estate
            [-5000, 500, 600, 700, 800, 900],  # High return
        ]

        for i, cash_flows in enumerate(validation_cases):
            irr = self.service._calculate_irr(cash_flows)

            # Calculate NPV at the calculated IRR - should be very close to 0
            npv_at_irr = sum(cf / ((1 + irr) ** t) for t, cf in enumerate(cash_flows))

            print(f"Case {i+1}: IRR={irr:.4%}, NPV@IRR={npv_at_irr:.6f}")

            # NPV at IRR should be very close to zero (within reasonable tolerance)
            if irr > 0:  # Only validate for cases where IRR was found
                assert (
                    abs(npv_at_irr) < 1e-3
                ), f"NPV at IRR should be ~0, got {npv_at_irr:.6f}"


if __name__ == "__main__":
    # Run performance tests directly
    test_instance = TestIRRPerformance()
    test_instance.setup_method()

    print("Running IRR Performance Benchmarks...")
    test_instance.test_irr_calculation_speed()
    test_instance.test_irr_edge_cases_performance()
    test_instance.test_irr_batch_performance()
    test_instance.test_irr_accuracy_validation()
    print("\n✅ All IRR performance tests completed successfully!")
