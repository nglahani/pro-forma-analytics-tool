#!/usr/bin/env python3
"""
Quick Monte Carlo Integration Test
"""

from core.property_inputs import create_sample_property
from monte_carlo.simulation_engine import monte_carlo_engine

def test_integration():
    print('=== MONTE CARLO INTEGRATION VALIDATION ===')
    print()

    # Test 1: Property Input to Monte Carlo Pipeline
    print('[1] Testing Property Input -> Monte Carlo Pipeline...')
    try:
        property_data = create_sample_property()
        print(f'   [OK] Created sample property: {property_data.property_name}')
        print(f'   [OK] MSA Code: {property_data.get_msa_code()}')
        print(f'   [OK] Purchase Price: ${property_data.financial_info.purchase_price:,.0f}')
        print(f'   [OK] Price per Unit: ${property_data.calculate_price_per_unit():,.0f}')
        print()
        
        # Test Monte Carlo integration
        print('[2] Testing Monte Carlo Scenario Generation...')
        monte_carlo_results = monte_carlo_engine.generate_scenarios(
            property_data=property_data,
            num_scenarios=50,
            horizon_years=5,
            use_correlations=True
        )
        
        print(f'   [OK] Generated {len(monte_carlo_results.scenarios)} scenarios')
        print(f'   [OK] Property ID: {monte_carlo_results.property_id}')
        print(f'   [OK] MSA Code: {monte_carlo_results.msa_code}')
        print(f'   [OK] Horizon: {monte_carlo_results.horizon_years} years')
        print()
        
        # Test scenario quality
        print('[3] Testing Scenario Quality...')
        first_scenario = monte_carlo_results.scenarios[0]
        param_count = len(first_scenario.forecasted_parameters)
        print(f'   [OK] Parameters per scenario: {param_count}')
        print(f'   [OK] Available parameters: {list(first_scenario.forecasted_parameters.keys())[:3]}...')
        
        # Test summary statistics
        if monte_carlo_results.summary_statistics:
            stat_count = len(monte_carlo_results.summary_statistics)
            print(f'   [OK] Summary statistics for {stat_count} parameters')
        
        # Test extreme scenarios
        if monte_carlo_results.extreme_scenarios:
            extreme_count = len(monte_carlo_results.extreme_scenarios)
            print(f'   [OK] Identified {extreme_count} extreme scenarios')
        
        print()
        print('[RESULT] INTEGRATION VALIDATION: PASSED')
        print('   Monte Carlo engine successfully integrates with property inputs')
        print('   System is ready for user input workflow development')
        
        return True
        
    except Exception as e:
        print(f'   [FAIL] Integration test failed: {e}')
        print('   Check forecasting data availability')
        return False

if __name__ == "__main__":
    test_integration()