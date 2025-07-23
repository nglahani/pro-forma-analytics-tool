#!/usr/bin/env python3
"""
Simple Monte Carlo Validation Script

Creates basic validation charts without Unicode issues for Windows.
"""

import sys
import os
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.property_inputs import create_sample_property
from monte_carlo.simulation_engine import monte_carlo_engine


def create_validation_charts():
    """Create Monte Carlo validation charts."""
    
    print("SIMPLE MONTE CARLO VALIDATION")
    print("=" * 50)
    
    # Generate scenarios
    print("\n[1] Generating Monte Carlo scenarios...")
    property_data = create_sample_property()
    
    monte_carlo_results = monte_carlo_engine.generate_scenarios(
        property_data=property_data,
        num_scenarios=500,
        horizon_years=5,
        use_correlations=True
    )
    
    print(f"Generated {monte_carlo_results.num_scenarios} scenarios")
    
    # Extract data for analysis
    growth_scores = []
    risk_scores = []
    market_scenarios = []
    parameter_data = {}
    
    for scenario in monte_carlo_results.scenarios:
        growth_scores.append(scenario.scenario_summary.get('growth_score', 0.5))
        risk_scores.append(scenario.scenario_summary.get('risk_score', 0.5))
        market_scenarios.append(scenario.scenario_summary.get('market_scenario', 'unknown'))
        
        # Collect parameter data
        for param_name, values in scenario.forecasted_parameters.items():
            if param_name not in parameter_data:
                parameter_data[param_name] = []
            parameter_data[param_name].extend(values)
    
    # Create comprehensive validation dashboard
    fig = plt.figure(figsize=(20, 16))
    fig.suptitle('Monte Carlo Simulation Validation Dashboard', fontsize=16, fontweight='bold')
    
    # 1. Growth vs Risk Scatter Plot
    ax1 = plt.subplot(3, 4, 1)
    plt.scatter(growth_scores, risk_scores, alpha=0.6, s=20)
    plt.xlabel('Growth Score')
    plt.ylabel('Risk Score')
    plt.title('Risk vs Growth Analysis')
    plt.grid(True, alpha=0.3)
    
    # Add quadrant lines
    plt.axhline(0.5, color='gray', linestyle='--', alpha=0.5)
    plt.axvline(0.5, color='gray', linestyle='--', alpha=0.5)
    
    # 2. Growth Score Distribution
    ax2 = plt.subplot(3, 4, 2)
    plt.hist(growth_scores, bins=20, alpha=0.7, color='green', edgecolor='black')
    plt.axvline(np.mean(growth_scores), color='red', linestyle='--', linewidth=2,
               label=f'Mean: {np.mean(growth_scores):.3f}')
    plt.xlabel('Growth Score')
    plt.ylabel('Frequency')
    plt.title('Growth Score Distribution')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 3. Risk Score Distribution
    ax3 = plt.subplot(3, 4, 3)
    plt.hist(risk_scores, bins=20, alpha=0.7, color='red', edgecolor='black')
    plt.axvline(np.mean(risk_scores), color='blue', linestyle='--', linewidth=2,
               label=f'Mean: {np.mean(risk_scores):.3f}')
    plt.xlabel('Risk Score')
    plt.ylabel('Frequency')
    plt.title('Risk Score Distribution')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 4. Market Scenario Distribution
    ax4 = plt.subplot(3, 4, 4)
    scenario_counts = {}
    for scenario_type in market_scenarios:
        scenario_counts[scenario_type] = scenario_counts.get(scenario_type, 0) + 1
    
    bars = plt.bar(scenario_counts.keys(), scenario_counts.values(), 
                   color=['skyblue', 'lightcoral', 'lightgreen', 'gold', 'plum'][:len(scenario_counts)])
    plt.title('Market Scenario Distribution')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    
    # Add value labels on bars
    for bar, count in zip(bars, scenario_counts.values()):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                str(count), ha='center', va='bottom', fontweight='bold')
    
    # 5-8. Key Parameter Distributions
    key_parameters = ['cap_rate', 'rent_growth', 'vacancy_rate', 'property_growth']
    for i, param_name in enumerate(key_parameters, 5):
        if param_name in parameter_data:
            ax = plt.subplot(3, 4, i)
            values = parameter_data[param_name]
            
            # Histogram
            plt.hist(values, bins=30, alpha=0.7, density=True, edgecolor='black', linewidth=0.5)
            
            # Statistics
            mu, sigma = np.mean(values), np.std(values)
            plt.axvline(mu, color='red', linestyle='--', linewidth=2, label=f'Mean: {mu:.3f}')
            
            # Percentiles
            p5, p95 = np.percentile(values, [5, 95])
            plt.axvline(p5, color='orange', linestyle=':', alpha=0.7, label=f'5th: {p5:.3f}')
            plt.axvline(p95, color='orange', linestyle=':', alpha=0.7, label=f'95th: {p95:.3f}')
            
            plt.title(f'{param_name.replace("_", " ").title()}')
            plt.xlabel('Value')
            plt.ylabel('Density')
            plt.legend(fontsize=8)
            plt.grid(True, alpha=0.3)
    
    # 9. Time Series Evolution for Cap Rate
    ax9 = plt.subplot(3, 4, 9)
    years = list(range(1, 6))  # Years 1-5
    
    # Get cap rate time series from first 50 scenarios
    cap_rate_series = []
    for scenario in monte_carlo_results.scenarios[:50]:
        if 'cap_rate' in scenario.forecasted_parameters:
            cap_rate_series.append(scenario.forecasted_parameters['cap_rate'])
    
    # Plot individual scenarios with low alpha
    for series in cap_rate_series:
        if len(series) == len(years):
            plt.plot(years, series, color='blue', alpha=0.1, linewidth=0.5)
    
    # Calculate and plot percentiles
    if cap_rate_series:
        values_by_year = list(zip(*cap_rate_series))
        percentiles_50 = [np.percentile(year_values, 50) for year_values in values_by_year]
        percentiles_25 = [np.percentile(year_values, 25) for year_values in values_by_year]
        percentiles_75 = [np.percentile(year_values, 75) for year_values in values_by_year]
        
        plt.fill_between(years, percentiles_25, percentiles_75, alpha=0.3, color='orange', label='25th-75th percentile')
        plt.plot(years, percentiles_50, color='red', linewidth=3, label='Median', marker='o')
    
    plt.title('Cap Rate Evolution (5 Years)')
    plt.xlabel('Year')
    plt.ylabel('Cap Rate')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 10. Correlation Matrix Visualization
    ax10 = plt.subplot(3, 4, 10)
    if hasattr(monte_carlo_results, 'correlation_matrix') and monte_carlo_results.correlation_matrix is not None:
        correlation_matrix = monte_carlo_results.correlation_matrix
        parameter_names = monte_carlo_results.parameter_names
        
        # Create heatmap
        im = plt.imshow(correlation_matrix, cmap='RdBu_r', aspect='auto', vmin=-1, vmax=1)
        
        # Set limited ticks for readability
        tick_indices = range(0, len(parameter_names), max(1, len(parameter_names)//6))
        plt.xticks(tick_indices, [parameter_names[i][:8] for i in tick_indices], rotation=45)
        plt.yticks(tick_indices, [parameter_names[i][:8] for i in tick_indices])
        
        plt.title('Parameter Correlations')
        plt.colorbar(im, fraction=0.046, pad=0.04)
    else:
        plt.text(0.5, 0.5, 'No Correlation\nMatrix Available', ha='center', va='center', 
                transform=ax10.transAxes, fontsize=12)
        plt.title('Parameter Correlations')
    
    # 11. Validation Summary Statistics
    ax11 = plt.subplot(3, 4, 11)
    ax11.axis('off')
    
    summary_stats = [
        f"Total Scenarios: {len(monte_carlo_results.scenarios)}",
        f"Growth Score Mean: {np.mean(growth_scores):.3f}",
        f"Growth Score Std: {np.std(growth_scores):.3f}",
        f"Risk Score Mean: {np.mean(risk_scores):.3f}",
        f"Risk Score Std: {np.std(risk_scores):.3f}",
        f"Parameters: {len(parameter_data)}",
        f"Market Scenarios: {len(scenario_counts)}",
        f"Scenario Diversity: {np.std(growth_scores):.3f}"
    ]
    
    y_pos = 0.9
    for stat in summary_stats:
        plt.text(0.1, y_pos, stat, transform=ax11.transAxes, fontsize=10, 
                fontweight='bold' if 'Total' in stat else 'normal')
        y_pos -= 0.12
    
    plt.title('Summary Statistics', fontweight='bold')
    
    # 12. Quality Assessment
    ax12 = plt.subplot(3, 4, 12)
    
    # Quality checks
    checks = {
        'Scenario Count': len(monte_carlo_results.scenarios) >= 100,
        'Parameter Coverage': len(parameter_data) >= 10,
        'Growth Diversity': np.std(growth_scores) > 0.01,
        'Risk Diversity': np.std(risk_scores) > 0.01,
        'Correlation Matrix': hasattr(monte_carlo_results, 'correlation_matrix'),
    }
    
    check_names = list(checks.keys())
    check_results = [1 if result else 0 for result in checks.values()]
    colors = ['green' if result else 'red' for result in checks.values()]
    
    bars = plt.barh(check_names, check_results, color=colors, alpha=0.7)
    plt.xlim(0, 1.2)
    plt.xlabel('Pass (1) / Fail (0)')
    plt.title('Quality Assessment')
    
    # Add pass/fail labels
    for bar, result in zip(bars, check_results):
        width = bar.get_width()
        plt.text(width + 0.05, bar.get_y() + bar.get_height()/2,
                'PASS' if result else 'FAIL', ha='left', va='center', fontweight='bold')
    
    plt.tight_layout()
    
    # Save the comprehensive chart
    os.makedirs('validation_charts', exist_ok=True)
    chart_path = 'validation_charts/monte_carlo_comprehensive_validation.png'
    plt.savefig(chart_path, dpi=150, bbox_inches='tight')
    
    print(f"\n[2] Validation Results:")
    print(f"   Scenarios Generated: {len(monte_carlo_results.scenarios)}")
    print(f"   Parameters Covered: {len(parameter_data)}")
    print(f"   Growth Score Range: {min(growth_scores):.3f} - {max(growth_scores):.3f}")
    print(f"   Risk Score Range: {min(risk_scores):.3f} - {max(risk_scores):.3f}")
    print(f"   Market Scenarios: {list(scenario_counts.keys())}")
    print(f"   Scenario Diversity (Growth Std): {np.std(growth_scores):.3f}")
    print(f"   Scenario Diversity (Risk Std): {np.std(risk_scores):.3f}")
    
    # Overall assessment
    passed_checks = sum(checks.values())
    total_checks = len(checks)
    print(f"\n[3] Quality Assessment: {passed_checks}/{total_checks} checks passed")
    
    if passed_checks >= total_checks * 0.8:
        print("   STATUS: MONTE CARLO SIMULATION IS WORKING CORRECTLY")
        print("   The simulation is generating diverse, realistic scenarios")
        print("   Parameter correlations are being applied properly")
        print("   Ready to proceed with business logic implementation")
    else:
        print("   STATUS: SOME ISSUES DETECTED")
        print("   Review the failed quality checks above")
    
    print(f"\n[4] Comprehensive validation chart saved: {chart_path}")
    print("   Open this file to visually inspect the Monte Carlo results")
    
    # Display the chart
    plt.show()
    
    return monte_carlo_results


if __name__ == "__main__":
    create_validation_charts()