#!/usr/bin/env python3
"""
Memory Profiling Script

Profiles memory usage during DCF workflow execution to detect memory leaks
and optimization opportunities.
"""

import json
import os
import sys
import tracemalloc
from pathlib import Path
from datetime import date

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.application.services.dcf_assumptions_service import DCFAssumptionsService
    from src.application.services.initial_numbers_service import InitialNumbersService
    from src.application.services.cash_flow_projection_service import CashFlowProjectionService
    from src.application.services.financial_metrics_service import FinancialMetricsService
    from src.domain.entities.property_data import (
        SimplifiedPropertyInput, ResidentialUnits, CommercialUnits,
        RenovationInfo, InvestorEquityStructure, RenovationStatus
    )
except ImportError as e:
    print(f"[ERROR] Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


def create_test_property() -> SimplifiedPropertyInput:
    """Create a test property for memory profiling."""
    return SimplifiedPropertyInput(
        property_id="MEMORY_TEST_001",
        property_name="Memory Profiling Test Property",
        analysis_date=date.today(),
        residential_units=ResidentialUnits(
            total_units=50,
            average_rent_per_unit=2500
        ),
        commercial_units=CommercialUnits(
            total_units=5,
            average_rent_per_unit=4000
        ),
        renovation_info=RenovationInfo(
            status=RenovationStatus.PLANNED,
            anticipated_duration_months=12
        ),
        equity_structure=InvestorEquityStructure(
            investor_equity_share_pct=70.0,
            self_cash_percentage=25.0
        ),
        city="Chicago",
        state="IL",
        msa_code="16980",
        purchase_price=5000000
    )


def create_test_scenario() -> dict:
    """Create a test Monte Carlo scenario."""
    return {
        'scenario_id': 'MEMORY_TEST_SCENARIO',
        'forecasted_parameters': {
            'commercial_mortgage_rate': [0.065, 0.067, 0.069, 0.071, 0.073, 0.075],
            'treasury_10y': [0.040, 0.042, 0.044, 0.046, 0.048, 0.050],
            'fed_funds_rate': [0.025, 0.030, 0.035, 0.037, 0.039, 0.041],
            'cap_rate': [0.070, 0.070, 0.070, 0.070, 0.070, 0.070],
            'rent_growth': [0.0, 0.025, 0.028, 0.026, 0.024, 0.022],
            'expense_growth': [0.0, 0.022, 0.025, 0.023, 0.024, 0.026],
            'property_growth': [0.0, 0.018, 0.020, 0.019, 0.017, 0.016],
            'vacancy_rate': [0.0, 0.05, 0.045, 0.055, 0.050, 0.050],
            'ltv_ratio': [0.75, 0.75, 0.75, 0.75, 0.75, 0.75],
            'closing_cost_pct': [0.050, 0.050, 0.050, 0.050, 0.050, 0.050],
            'lender_reserves': [3.0, 3.0, 3.0, 3.0, 3.0, 3.0]
        }
    }


def profile_dcf_workflow():
    """Profile memory usage during complete DCF workflow."""
    print("[MEMORY] Starting memory profiling of DCF workflow...")
    
    # Start memory tracing
    tracemalloc.start()
    
    # Take initial snapshot
    snapshot_initial = tracemalloc.take_snapshot()
    
    # Initialize services
    dcf_service = DCFAssumptionsService()
    initial_numbers_service = InitialNumbersService()
    cash_flow_service = CashFlowProjectionService()
    financial_metrics_service = FinancialMetricsService()
    
    snapshot_services = tracemalloc.take_snapshot()
    
    # Create test data
    property_data = create_test_property()
    scenario = create_test_scenario()
    
    snapshot_data = tracemalloc.take_snapshot()
    
    # Phase 1: DCF Assumptions
    dcf_assumptions = dcf_service.create_dcf_assumptions_from_scenario(scenario, property_data)
    snapshot_phase1 = tracemalloc.take_snapshot()
    
    # Phase 2: Initial Numbers
    initial_numbers = initial_numbers_service.calculate_initial_numbers(property_data, dcf_assumptions)
    snapshot_phase2 = tracemalloc.take_snapshot()
    
    # Phase 3: Cash Flow Projections
    cash_flow_projection = cash_flow_service.calculate_cash_flow_projection(dcf_assumptions, initial_numbers)
    snapshot_phase3 = tracemalloc.take_snapshot()
    
    # Phase 4: Financial Metrics
    financial_metrics = financial_metrics_service.calculate_financial_metrics(  # noqa: F841
        cash_flow_projection, dcf_assumptions, initial_numbers, discount_rate=0.10
    )
    snapshot_final = tracemalloc.take_snapshot()
    
    # Analyze memory usage
    results = {
        "workflow_phases": {},
        "top_memory_consumers": {},
        "memory_leaks": []
    }
    
    # Calculate memory usage for each phase
    phases = [
        ("Initial", snapshot_initial),
        ("Services Initialized", snapshot_services),
        ("Data Created", snapshot_data),
        ("Phase 1 Complete", snapshot_phase1),
        ("Phase 2 Complete", snapshot_phase2),
        ("Phase 3 Complete", snapshot_phase3),
        ("Phase 4 Complete", snapshot_final)
    ]
    
    for i, (phase_name, snapshot) in enumerate(phases):
        if i == 0:
            peak_memory = snapshot.get_peak_memory_size()
            current_memory = sum(stat.size for stat in snapshot.statistics('filename'))
        else:
            # Compare with previous snapshot
            top_stats = snapshot.compare_to(phases[i-1][1], 'lineno')
            peak_memory = snapshot.get_peak_memory_size()
            current_memory = sum(stat.size for stat in snapshot.statistics('filename'))
            
            results["workflow_phases"][phase_name] = {
                "peak_memory_mb": peak_memory / 1024 / 1024,
                "current_memory_mb": current_memory / 1024 / 1024,
                "memory_increase_mb": (current_memory - sum(stat.size for stat in phases[i-1][1].statistics('filename'))) / 1024 / 1024
            }
    
    # Find top memory consumers
    top_stats = snapshot_final.statistics('lineno')[:10]
    for stat in top_stats:
        results["top_memory_consumers"][str(stat.traceback)] = {
            "size_mb": stat.size / 1024 / 1024,
            "count": stat.count
        }
    
    # Stop tracing
    tracemalloc.stop()
    
    return results


def profile_multiple_iterations():
    """Profile memory usage across multiple workflow iterations to detect leaks."""
    print("[MEMORY] Profiling multiple iterations for memory leaks...")
    
    tracemalloc.start()
    baseline_snapshot = tracemalloc.take_snapshot()
    
    # Run workflow multiple times
    for i in range(5):
        property_data = create_test_property()
        scenario = create_test_scenario()
        
        # Run complete workflow
        dcf_service = DCFAssumptionsService()
        initial_numbers_service = InitialNumbersService()
        cash_flow_service = CashFlowProjectionService()
        financial_metrics_service = FinancialMetricsService()
        
        dcf_assumptions = dcf_service.create_dcf_assumptions_from_scenario(scenario, property_data)
        initial_numbers = initial_numbers_service.calculate_initial_numbers(property_data, dcf_assumptions)
        cash_flow_projection = cash_flow_service.calculate_cash_flow_projection(dcf_assumptions, initial_numbers)
        financial_metrics = financial_metrics_service.calculate_financial_metrics(  # noqa: F841
            cash_flow_projection, dcf_assumptions, initial_numbers, discount_rate=0.10
        )
        
        # Force garbage collection
        import gc
        gc.collect()
    
    final_snapshot = tracemalloc.take_snapshot()
    tracemalloc.stop()
    
    # Compare memory usage
    top_stats = final_snapshot.compare_to(baseline_snapshot, 'lineno')
    
    memory_leaks = []
    for stat in top_stats[:5]:
        if stat.size_diff > 1024 * 1024:  # More than 1MB increase
            memory_leaks.append({
                "location": str(stat.traceback),
                "size_increase_mb": stat.size_diff / 1024 / 1024,
                "count_increase": stat.count_diff
            })
    
    return memory_leaks


def main():
    """Main profiling function."""
    print("[MEMORY] Memory Profiling for Pro-Forma Analytics Tool")
    print("=" * 60)
    
    try:
        # Profile single workflow execution
        workflow_results = profile_dcf_workflow()
        
        # Profile multiple iterations for leaks
        leak_results = profile_multiple_iterations()
        
        # Combine results
        results = {
            "single_workflow": workflow_results,
            "memory_leaks": leak_results,
            "summary": {
                "max_memory_mb": max(phase["peak_memory_mb"] for phase in workflow_results["workflow_phases"].values()),
                "total_phases": len(workflow_results["workflow_phases"]),
                "potential_leaks": len(leak_results)
            }
        }
        
        # Save results
        results_file = project_root / "performance_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Print summary
        print(f"\n[RESULTS] Memory Profiling Results:")
        print(f"   Max Memory Usage: {results['summary']['max_memory_mb']:.2f} MB")
        print(f"   Potential Memory Leaks: {results['summary']['potential_leaks']}")
        
        if results['summary']['potential_leaks'] > 0:
            print(f"\n[WARNING] Potential memory leaks detected!")
            for leak in leak_results:
                print(f"   - {leak['size_increase_mb']:.2f} MB increase: {leak['location']}")
        else:
            print(f"\n[PASS] No significant memory leaks detected")
        
        print(f"\nDetailed results saved to: {results_file}")
        
    except Exception as e:
        print(f"[ERROR] Memory profiling failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()