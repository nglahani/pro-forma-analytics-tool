#!/usr/bin/env python3
"""
Unified Monte Carlo Validation System

Consolidates all Monte Carlo validation functionality into a single script
with multiple modes: simple, comprehensive, and custom validation.
"""

import sys
import os
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import logging
from typing import List, Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.property_inputs import create_sample_property
from monte_carlo.simulation_engine import monte_carlo_engine
from core.logging_config import get_logger

# Import visualization with fallback
try:
    from src.presentation.visualizations.monte_carlo_charts import create_monte_carlo_validation_charts
    CLEAN_ARCH_AVAILABLE = True
except ImportError:
    CLEAN_ARCH_AVAILABLE = False
    print("Note: Clean architecture visualizations not available")


class MonteCarloValidator:
    """Unified Monte Carlo validation system."""
    
    def __init__(self, output_dir: str = "monte_carlo_validation_charts"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.logger = get_logger(self.__class__.__name__)
    
    def validate_simple(self, num_scenarios: int = 100) -> Dict[str, Any]:
        """Simple validation with basic charts - quick test."""
        print("SIMPLE MONTE CARLO VALIDATION")
        print("=" * 50)
        
        # Generate scenarios
        print(f"\n[1] Generating {num_scenarios} Monte Carlo scenarios...")
        property_data = create_sample_property()
        
        monte_carlo_results = monte_carlo_engine.generate_scenarios(
            property_data=property_data,
            num_scenarios=num_scenarios,
            horizon_years=5,
            use_correlations=True
        )
        
        print(f"Generated {monte_carlo_results.num_scenarios} scenarios")
        
        # Extract data
        growth_scores = []
        risk_scores = []
        market_scenarios = []
        
        for scenario in monte_carlo_results.scenarios:
            growth_scores.append(scenario.scenario_summary.get('growth_score', 0.5))
            risk_scores.append(scenario.scenario_summary.get('risk_score', 0.5))
            market_scenarios.append(scenario.scenario_summary.get('market_scenario', 'unknown'))
        
        # Create simple charts
        self._create_simple_charts(growth_scores, risk_scores, market_scenarios)
        
        # Return summary
        return {
            'num_scenarios': len(growth_scores),
            'avg_growth': np.mean(growth_scores),
            'avg_risk': np.mean(risk_scores),
            'growth_range': (min(growth_scores), max(growth_scores)),
            'risk_range': (min(risk_scores), max(risk_scores)),
            'market_scenarios': dict(zip(*np.unique(market_scenarios, return_counts=True)))
        }
    
    def validate_comprehensive(self, num_scenarios: int = 500) -> Dict[str, Any]:
        """Comprehensive validation with detailed analysis."""
        print("COMPREHENSIVE MONTE CARLO VALIDATION")
        print("=" * 60)
        
        # Step 1: Create sample property
        print("\n[1] Creating sample property...")
        property_data = create_sample_property()
        print(f"   [OK] Created: {property_data.property_name}")
        print(f"   [LOC] Location: {property_data.location_info.city}, {property_data.location_info.state}")
        print(f"   [TYPE] Type: {property_data.physical_info.property_type.value}")
        print(f"   [PRICE] Purchase Price: ${property_data.financial_info.purchase_price:,.0f}")
        
        # Step 2: Generate scenarios
        print(f"\n[2] Generating {num_scenarios} Monte Carlo scenarios...")
        monte_carlo_results = monte_carlo_engine.generate_scenarios(
            property_data=property_data,
            num_scenarios=num_scenarios,
            horizon_years=5,
            use_correlations=True
        )
        
        print(f"   [SUCCESS] Generated {monte_carlo_results.num_scenarios} scenarios")
        
        # Step 3: Analyze results
        print("\n[3] Analyzing Monte Carlo results...")
        analysis = self._analyze_comprehensive_results(monte_carlo_results)
        
        # Step 4: Create visualizations
        print("\n[4] Creating validation charts...")
        self._create_comprehensive_charts(monte_carlo_results, analysis)
        
        # Step 5: Use clean architecture if available
        if CLEAN_ARCH_AVAILABLE:
            print("\n[5] Creating clean architecture visualizations...")
            try:
                create_monte_carlo_validation_charts(monte_carlo_results, str(self.output_dir))
                print("   [SUCCESS] Clean architecture charts created")
            except Exception as e:
                print(f"   [WARNING] Clean architecture charts failed: {e}")
        
        return analysis
    
    def validate_custom(self, scenarios: int, years: int, correlations: bool = True) -> Dict[str, Any]:
        """Custom validation with user-specified parameters."""
        print(f"CUSTOM MONTE CARLO VALIDATION")
        print(f"Scenarios: {scenarios}, Years: {years}, Correlations: {correlations}")
        print("=" * 60)
        
        property_data = create_sample_property()
        
        monte_carlo_results = monte_carlo_engine.generate_scenarios(
            property_data=property_data,
            num_scenarios=scenarios,
            horizon_years=years,
            use_correlations=correlations
        )
        
        analysis = self._analyze_comprehensive_results(monte_carlo_results)
        self._create_comprehensive_charts(monte_carlo_results, analysis)
        
        return analysis
    
    def _create_simple_charts(self, growth_scores: List[float], risk_scores: List[float], 
                            market_scenarios: List[str]):
        """Create simple validation charts."""
        print("\n[2] Creating simple validation charts...")
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Monte Carlo Validation - Simple Mode', fontsize=16)
        
        # Growth score distribution
        ax1.hist(growth_scores, bins=20, alpha=0.7, color='green', edgecolor='black')
        ax1.set_title('Growth Score Distribution')
        ax1.set_xlabel('Growth Score')
        ax1.set_ylabel('Frequency')
        ax1.grid(True, alpha=0.3)
        
        # Risk score distribution
        ax2.hist(risk_scores, bins=20, alpha=0.7, color='red', edgecolor='black')
        ax2.set_title('Risk Score Distribution')
        ax2.set_xlabel('Risk Score')
        ax2.set_ylabel('Frequency')
        ax2.grid(True, alpha=0.3)
        
        # Risk vs Growth scatter
        ax3.scatter(risk_scores, growth_scores, alpha=0.6, s=30)
        ax3.set_title('Risk vs Growth Relationship')
        ax3.set_xlabel('Risk Score')
        ax3.set_ylabel('Growth Score')
        ax3.grid(True, alpha=0.3)
        
        # Market scenario distribution
        scenario_counts = {}
        for scenario in market_scenarios:
            scenario_counts[scenario] = scenario_counts.get(scenario, 0) + 1
        
        ax4.bar(scenario_counts.keys(), scenario_counts.values(), alpha=0.7)
        ax4.set_title('Market Scenario Distribution')
        ax4.set_xlabel('Market Scenario')
        ax4.set_ylabel('Count')
        ax4.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        chart_path = self.output_dir / "simple_validation_charts.png"
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"   [SUCCESS] Simple charts saved to: {chart_path}")
    
    def _create_comprehensive_charts(self, monte_carlo_results, analysis: Dict[str, Any]):
        """Create comprehensive validation charts."""
        
        # Extract data
        growth_scores = analysis['growth_scores']
        risk_scores = analysis['risk_scores']
        market_scenarios = analysis['market_scenarios']
        
        # Create comprehensive dashboard
        fig = plt.figure(figsize=(16, 12))
        fig.suptitle('Monte Carlo Validation Dashboard - Comprehensive Mode', fontsize=18)
        
        # Create grid layout
        gs = fig.add_gridspec(3, 3, height_ratios=[1, 1, 1], width_ratios=[1, 1, 1])
        
        # 1. Growth distribution
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.hist(growth_scores, bins=30, alpha=0.7, color='green', edgecolor='black')
        ax1.set_title('Growth Score Distribution')
        ax1.set_xlabel('Growth Score')
        ax1.set_ylabel('Frequency')
        ax1.grid(True, alpha=0.3)
        
        # 2. Risk distribution
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.hist(risk_scores, bins=30, alpha=0.7, color='red', edgecolor='black')
        ax2.set_title('Risk Score Distribution')
        ax2.set_xlabel('Risk Score')
        ax2.set_ylabel('Frequency')
        ax2.grid(True, alpha=0.3)
        
        # 3. Risk vs Growth scatter
        ax3 = fig.add_subplot(gs[0, 2])
        scatter = ax3.scatter(risk_scores, growth_scores, 
                            c=range(len(risk_scores)), cmap='viridis', alpha=0.6, s=20)
        ax3.set_title('Risk vs Growth Relationship')
        ax3.set_xlabel('Risk Score')
        ax3.set_ylabel('Growth Score')
        ax3.grid(True, alpha=0.3)
        plt.colorbar(scatter, ax=ax3, label='Scenario Index')
        
        # 4. Market scenarios pie chart
        ax4 = fig.add_subplot(gs[1, 0])
        scenario_counts = analysis['scenario_counts']
        ax4.pie(scenario_counts.values(), labels=scenario_counts.keys(), autopct='%1.1f%%')
        ax4.set_title('Market Scenario Distribution')
        
        # 5. Statistical summary
        ax5 = fig.add_subplot(gs[1, 1])
        ax5.axis('off')
        stats_text = f"""
        STATISTICAL SUMMARY
        
        Scenarios Generated: {analysis['num_scenarios']}
        
        Growth Scores:
          Mean: {analysis['growth_mean']:.3f}
          Std: {analysis['growth_std']:.3f}
          Range: [{analysis['growth_min']:.3f}, {analysis['growth_max']:.3f}]
        
        Risk Scores:
          Mean: {analysis['risk_mean']:.3f}
          Std: {analysis['risk_std']:.3f}
          Range: [{analysis['risk_min']:.3f}, {analysis['risk_max']:.3f}]
        
        Correlation (Risk vs Growth): {analysis['risk_growth_correlation']:.3f}
        """
        ax5.text(0.1, 0.9, stats_text, transform=ax5.transAxes, fontsize=10, 
                verticalalignment='top', fontfamily='monospace')
        
        # 6. Quality metrics
        ax6 = fig.add_subplot(gs[1, 2])
        quality_metrics = analysis['quality_metrics']
        metrics_labels = list(quality_metrics.keys())
        metrics_values = [1 if v else 0 for v in quality_metrics.values()]
        colors = ['green' if v else 'red' for v in quality_metrics.values()]
        
        bars = ax6.bar(metrics_labels, metrics_values, color=colors, alpha=0.7)
        ax6.set_title('Quality Check Results')
        ax6.set_ylabel('Pass (1) / Fail (0)')
        ax6.tick_params(axis='x', rotation=45)
        ax6.set_ylim(0, 1.2)
        
        # Add pass/fail labels
        for i, (bar, passed) in enumerate(zip(bars, quality_metrics.values())):
            ax6.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                    'PASS' if passed else 'FAIL', ha='center', va='bottom', fontweight='bold')
        
        # 7. Time series evolution (if available)
        ax7 = fig.add_subplot(gs[2, :])
        if 'time_series_data' in analysis:
            time_data = analysis['time_series_data']
            for i, scenario_data in enumerate(time_data[:10]):  # Show first 10 scenarios
                ax7.plot(scenario_data, alpha=0.6, linewidth=1)
            ax7.set_title('Time Series Evolution (First 10 Scenarios)')
            ax7.set_xlabel('Years')
            ax7.set_ylabel('Value')
            ax7.grid(True, alpha=0.3)
        else:
            ax7.text(0.5, 0.5, 'Time Series Data Not Available', 
                    transform=ax7.transAxes, ha='center', va='center', fontsize=14)
            ax7.set_title('Time Series Evolution')
        
        plt.tight_layout()
        chart_path = self.output_dir / "comprehensive_validation_dashboard.png"
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"   [SUCCESS] Comprehensive dashboard saved to: {chart_path}")
    
    def _analyze_comprehensive_results(self, monte_carlo_results) -> Dict[str, Any]:
        """Analyze Monte Carlo results comprehensively."""
        
        # Extract data
        growth_scores = []
        risk_scores = []
        market_scenarios = []
        
        for scenario in monte_carlo_results.scenarios:
            growth_scores.append(scenario.scenario_summary.get('growth_score', 0.5))
            risk_scores.append(scenario.scenario_summary.get('risk_score', 0.5))
            market_scenarios.append(scenario.scenario_summary.get('market_scenario', 'unknown'))
        
        # Calculate statistics
        growth_array = np.array(growth_scores)
        risk_array = np.array(risk_scores)
        
        # Scenario counts
        scenario_counts = {}
        for scenario in market_scenarios:
            scenario_counts[scenario] = scenario_counts.get(scenario, 0) + 1
        
        # Quality metrics
        quality_metrics = {
            'growth_range_ok': growth_array.max() - growth_array.min() > 0.1,
            'risk_range_ok': risk_array.max() - risk_array.min() > 0.1,
            'scenarios_diverse': len(scenario_counts) >= 3,
            'correlation_reasonable': abs(np.corrcoef(risk_array, growth_array)[0, 1]) < 0.8,
            'no_extreme_outliers': (np.abs(growth_array - growth_array.mean()) < 3 * growth_array.std()).all()
        }
        
        analysis = {
            'num_scenarios': len(growth_scores),
            'growth_scores': growth_scores,
            'risk_scores': risk_scores,
            'market_scenarios': market_scenarios,
            'scenario_counts': scenario_counts,
            'growth_mean': float(growth_array.mean()),
            'growth_std': float(growth_array.std()),
            'growth_min': float(growth_array.min()),
            'growth_max': float(growth_array.max()),
            'risk_mean': float(risk_array.mean()),
            'risk_std': float(risk_array.std()),
            'risk_min': float(risk_array.min()),
            'risk_max': float(risk_array.max()),
            'risk_growth_correlation': float(np.corrcoef(risk_array, growth_array)[0, 1]),
            'quality_metrics': quality_metrics
        }
        
        # Print analysis summary
        print(f"   Scenarios: {analysis['num_scenarios']}")
        print(f"   Growth: {analysis['growth_mean']:.3f} ± {analysis['growth_std']:.3f}")
        print(f"   Risk: {analysis['risk_mean']:.3f} ± {analysis['risk_std']:.3f}")
        print(f"   Correlation: {analysis['risk_growth_correlation']:.3f}")
        print(f"   Quality checks: {sum(quality_metrics.values())}/{len(quality_metrics)} passed")
        
        return analysis


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description='Unified Monte Carlo Validation System')
    parser.add_argument('--mode', choices=['simple', 'comprehensive', 'custom'], 
                       default='simple', help='Validation mode')
    parser.add_argument('--scenarios', type=int, default=100, 
                       help='Number of scenarios to generate')
    parser.add_argument('--years', type=int, default=5, 
                       help='Investment horizon in years')
    parser.add_argument('--no-correlations', action='store_true', 
                       help='Disable parameter correlations')
    parser.add_argument('--output-dir', default='monte_carlo_validation_charts',
                       help='Output directory for charts')
    
    args = parser.parse_args()
    
    # Create validator
    validator = MonteCarloValidator(args.output_dir)
    
    # Run validation based on mode
    if args.mode == 'simple':
        results = validator.validate_simple(args.scenarios)
    elif args.mode == 'comprehensive':
        results = validator.validate_comprehensive(args.scenarios)
    elif args.mode == 'custom':
        results = validator.validate_custom(args.scenarios, args.years, not args.no_correlations)
    
    # Print final summary
    print(f"\n" + "=" * 60)
    print("VALIDATION COMPLETE")
    print("=" * 60)
    print(f"Mode: {args.mode}")
    print(f"Scenarios: {results['num_scenarios']}")
    print(f"Charts saved to: {args.output_dir}/")
    
    if 'quality_metrics' in results:
        passed = sum(results['quality_metrics'].values())
        total = len(results['quality_metrics'])
        print(f"Quality checks: {passed}/{total} passed")
        
        if passed == total:
            print("[SUCCESS] All quality checks passed!")
        else:
            print("[WARNING] Some quality checks failed - review results")


if __name__ == "__main__":
    main()