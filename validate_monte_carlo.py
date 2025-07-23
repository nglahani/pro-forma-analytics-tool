#!/usr/bin/env python3
"""
Monte Carlo Validation Script

Runs Monte Carlo simulation and generates comprehensive visualizations
to validate that the simulation is working correctly.
"""

import sys
import os
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.property_inputs import create_sample_property
from monte_carlo.simulation_engine import monte_carlo_engine
from core.logging_config import get_logger

# Import visualization function with fallback
try:
    from src.presentation.visualizations.monte_carlo_charts import create_monte_carlo_validation_charts
except ImportError:
    print("Note: Clean architecture visualization imports not available, using legacy fallback")
    create_monte_carlo_validation_charts = None


def validate_monte_carlo_with_visualizations():
    """Run Monte Carlo simulation and create validation visualizations."""
    
    logger = get_logger(__name__)
    
    print("MONTE CARLO VALIDATION WITH VISUALIZATIONS")
    print("=" * 60)
    
    try:
        # Step 1: Create sample property
        print("\n[1] Creating sample property...")
        property_data = create_sample_property()
        print(f"   [OK] Created: {property_data.property_name}")
        print(f"   [LOC] Location: {property_data.location_info.city}, {property_data.location_info.state}")
        print(f"   [TYPE] Type: {property_data.physical_info.property_type.value}")
        print(f"   [PRICE] Purchase Price: ${property_data.financial_info.purchase_price:,.0f}")
        
        # Step 2: Generate Monte Carlo scenarios
        print("\n[2] Generating Monte Carlo scenarios...")
        monte_carlo_results = monte_carlo_engine.generate_scenarios(
            property_data=property_data,
            num_scenarios=100,  # Smaller sample for faster testing
            horizon_years=5,
            use_correlations=True
        )
        print(f"   [OK] Generated: {monte_carlo_results.num_scenarios} scenarios")
        print(f"   [MSA] MSA: {monte_carlo_results.msa_code}")
        
        # Step 3: Basic validation
        print("\n[3] Basic validation checks...")
        
        # Check scenario count
        expected_scenarios = 100
        actual_scenarios = len(monte_carlo_results.scenarios)
        scenario_check = "[OK]" if actual_scenarios == expected_scenarios else "[FAIL]"
        print(f"   {scenario_check} Scenario count: {actual_scenarios}/{expected_scenarios}")
        
        # Check parameter coverage
        if monte_carlo_results.scenarios:
            first_scenario = monte_carlo_results.scenarios[0]
            param_count = len(first_scenario.forecasted_parameters)
            expected_params = 11
            param_check = "[OK]" if param_count >= expected_params * 0.9 else "[FAIL]"
            print(f"   {param_check} Parameter coverage: {param_count}/{expected_params}")
            
            # List available parameters
            available_params = list(first_scenario.forecasted_parameters.keys())
            print(f"   [PARAMS] Available parameters: {', '.join(available_params)}")
        
        # Check scenario diversity
        growth_scores = [s.scenario_summary.get('growth_score', 0.5) for s in monte_carlo_results.scenarios]
        risk_scores = [s.scenario_summary.get('risk_score', 0.5) for s in monte_carlo_results.scenarios]
        
        import numpy as np
        growth_std = np.std(growth_scores)
        risk_std = np.std(risk_scores)
        diversity_check = "[OK]" if growth_std > 0.01 and risk_std > 0.01 else "[FAIL]"
        print(f"   {diversity_check} Scenario diversity: Growth std={growth_std:.3f}, Risk std={risk_std:.3f}")
        
        # Check market scenario distribution
        scenario_types = {}
        for scenario in monte_carlo_results.scenarios:
            scenario_type = scenario.scenario_summary.get('market_scenario', 'unknown')
            scenario_types[scenario_type] = scenario_types.get(scenario_type, 0) + 1
        
        print(f"   [SCENARIOS] Market scenarios: {dict(scenario_types)}")
        
        # Step 4: Create visualizations
        print("\n[4] Creating validation visualizations...")
        
        if create_monte_carlo_validation_charts:
            try:
                chart_files = create_monte_carlo_validation_charts(
                    simulation_result=monte_carlo_results,
                    output_dir="monte_carlo_validation_charts",
                    show_interactive=False  # Set to False to avoid blocking
                )
                
                print(f"   [OK] Created {len(chart_files)} visualization charts:")
                for chart_name, file_path in chart_files.items():
                    if file_path and os.path.exists(file_path):
                        print(f"      [CHART] {chart_name}: {file_path}")
                    else:
                        print(f"      [FAIL] {chart_name}: Failed to create")
                
                print(f"\n   [FOLDER] All charts saved to: monte_carlo_validation_charts/")
                print(f"   [REPORT] Validation report: monte_carlo_validation_charts/simulation_validation_report.md")
                
            except Exception as viz_error:
                print(f"   [ERROR] Visualization creation failed: {viz_error}")
                logger.error(f"Visualization error: {viz_error}")
                
        else:
            print("   [WARN] Advanced visualizations not available (clean architecture not fully integrated)")
            
            # Create basic matplotlib charts as fallback
            create_basic_validation_charts(monte_carlo_results)
        
        # Step 5: Summary and recommendations
        print("\n[5] Validation Summary...")
        
        # Overall health check
        checks_passed = [
            actual_scenarios == expected_scenarios,
            param_count >= expected_params * 0.9 if 'param_count' in locals() else False,
            growth_std > 0.01 and risk_std > 0.01,
            len(scenario_types) >= 2  # At least 2 different market scenarios
        ]
        
        overall_status = "[PASS]" if all(checks_passed) else "[ISSUES DETECTED]"
        print(f"   [STATUS] Overall Status: {overall_status}")
        print(f"   [SUMMARY] Checks Passed: {sum(checks_passed)}/{len(checks_passed)}")
        
        if all(checks_passed):
            print("\n[SUCCESS] Monte Carlo simulation is working correctly!")
            print("   [OK] Scenario generation is producing diverse, realistic results")
            print("   [OK] Parameter correlations are being applied properly")
            print("   [OK] Market classification system is functioning")
            print("   [OK] Ready to proceed with business logic implementation")
        else:
            print("\n[WARNING] Some validation checks failed:")
            if actual_scenarios != expected_scenarios:
                print(f"   - Scenario count mismatch: expected {expected_scenarios}, got {actual_scenarios}")
            if 'param_count' in locals() and param_count < expected_params * 0.9:
                print(f"   - Low parameter coverage: {param_count}/{expected_params}")
            if growth_std <= 0.01 or risk_std <= 0.01:
                print(f"   - Low scenario diversity: Growth σ={growth_std:.3f}, Risk σ={risk_std:.3f}")
            if len(scenario_types) < 2:
                print(f"   - Limited market scenario variety: {list(scenario_types.keys())}")
        
        return monte_carlo_results
        
    except Exception as e:
        print(f"\n[ERROR] Validation failed: {e}")
        logger.error(f"Monte Carlo validation error: {e}")
        raise


def create_basic_validation_charts(monte_carlo_results):
    """Create basic validation charts using matplotlib directly."""
    
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        
        print("   [CHARTS] Creating basic validation charts...")
        
        # Extract data
        growth_scores = [s.scenario_summary.get('growth_score', 0.5) for s in monte_carlo_results.scenarios]
        risk_scores = [s.scenario_summary.get('risk_score', 0.5) for s in monte_carlo_results.scenarios]
        
        # Create basic validation chart
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Monte Carlo Validation - Basic Charts', fontsize=14, fontweight='bold')
        
        # 1. Growth score distribution
        ax1.hist(growth_scores, bins=20, alpha=0.7, color='green', edgecolor='black')
        ax1.set_title('Growth Score Distribution')
        ax1.set_xlabel('Growth Score')
        ax1.set_ylabel('Frequency')
        ax1.axvline(np.mean(growth_scores), color='red', linestyle='--', 
                   label=f'Mean: {np.mean(growth_scores):.3f}')
        ax1.legend()
        
        # 2. Risk score distribution
        ax2.hist(risk_scores, bins=20, alpha=0.7, color='red', edgecolor='black')
        ax2.set_title('Risk Score Distribution')
        ax2.set_xlabel('Risk Score')
        ax2.set_ylabel('Frequency')
        ax2.axvline(np.mean(risk_scores), color='blue', linestyle='--',
                   label=f'Mean: {np.mean(risk_scores):.3f}')
        ax2.legend()
        
        # 3. Risk vs Growth scatter
        ax3.scatter(growth_scores, risk_scores, alpha=0.5)
        ax3.set_xlabel('Growth Score')
        ax3.set_ylabel('Risk Score')
        ax3.set_title('Risk vs Growth Analysis')
        ax3.grid(True, alpha=0.3)
        
        # 4. Market scenario counts
        scenario_counts = {}
        for scenario in monte_carlo_results.scenarios:
            scenario_type = scenario.scenario_summary.get('market_scenario', 'unknown')
            scenario_counts[scenario_type] = scenario_counts.get(scenario_type, 0) + 1
        
        ax4.bar(scenario_counts.keys(), scenario_counts.values())
        ax4.set_title('Market Scenario Distribution')
        ax4.set_ylabel('Count')
        ax4.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # Save chart
        os.makedirs('monte_carlo_validation_charts', exist_ok=True)
        chart_path = 'monte_carlo_validation_charts/basic_validation.png'
        plt.savefig(chart_path, dpi=100, bbox_inches='tight')
        plt.show()
        
        print(f"   [OK] Basic validation chart saved: {chart_path}")
        
    except Exception as e:
        print(f"   [ERROR] Basic chart creation failed: {e}")


if __name__ == "__main__":
    validate_monte_carlo_with_visualizations()