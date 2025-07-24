#!/usr/bin/env python3
"""
Property Data Collection Launcher

Launches the interactive property data collector with proper imports.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now import and run the collector
try:
    from user_input.property_collector import PropertyInputCollector
    
    def main():
        """Launch the property collector."""
        print("\n" + "="*60)
        print("[PROPERTY] DATA COLLECTION SYSTEM")
        print("="*60)
        print("Welcome! This system will guide you through collecting")
        print("property information for comprehensive investment analysis.")
        print()
        print("Features:")
        print("• Step-by-step guided input with validation")
        print("• Automatic calculation of key metrics")
        print("• Integration with Monte Carlo analysis")
        print("• Property data saved for future analysis")
        print()
        
        try:
            collector = PropertyInputCollector()
            property_data = collector.collect_property_data()
            
            if property_data:
                print(f"\n[SUCCESS] Property data collected!")
                print(f"Property '{property_data.property_name}' has been collected and saved.")
                print(f"Property ID: {property_data.property_id}")
                
                # Ask if user wants to run Monte Carlo analysis
                print("\n" + "="*60)
                print("[MONTE CARLO] ANALYSIS")
                print("="*60)
                
                run_analysis = input("\nWould you like to run Monte Carlo analysis now? (y/n): ").strip().lower()
                
                if run_analysis in ['y', 'yes']:
                    print("\n[RUNNING] Monte Carlo analysis...")
                    print("This may take a moment...")
                    
                    try:
                        from monte_carlo.simulation_engine import monte_carlo_engine
                        
                        results = monte_carlo_engine.generate_scenarios(
                            property_data=property_data,
                            num_scenarios=100,  # Reasonable number for demo
                            horizon_years=5,
                            use_correlations=True
                        )
                        
                        print(f"\n[COMPLETE] Analysis finished!")
                        print(f"Generated {len(results.scenarios)} investment scenarios")
                        print(f"Property: {results.property_id}")
                        print(f"Market Area: {results.msa_code}")
                        print(f"Forecast Horizon: {results.horizon_years} years")
                        
                        if results.scenarios:
                            # Calculate summary statistics
                            growth_scores = [s.scenario_summary.get('growth_score', 0) for s in results.scenarios]
                            risk_scores = [s.scenario_summary.get('risk_score', 0) for s in results.scenarios]
                            
                            import numpy as np
                            
                            print(f"\n[ANALYSIS] Scenario Results:")
                            print(f"Growth Potential: {min(growth_scores):.3f} to {max(growth_scores):.3f} (avg: {np.mean(growth_scores):.3f})")
                            print(f"Risk Assessment: {min(risk_scores):.3f} to {max(risk_scores):.3f} (avg: {np.mean(risk_scores):.3f})")
                            
                            # Market scenario breakdown
                            market_scenarios = {}
                            for scenario in results.scenarios:
                                market_type = scenario.scenario_summary.get('market_scenario', 'unknown')
                                market_scenarios[market_type] = market_scenarios.get(market_type, 0) + 1
                            
                            print(f"\n[SCENARIOS] Market Distribution:")
                            for scenario_type, count in market_scenarios.items():
                                percentage = (count / len(results.scenarios)) * 100
                                print(f"{scenario_type.replace('_', ' ').title()}: {count} scenarios ({percentage:.1f}%)")
                            
                            # Show extreme scenarios
                            if results.extreme_scenarios:
                                print(f"\n[EXTREMES] Key Scenarios:")
                                for scenario_name, scenario in results.extreme_scenarios.items():
                                    growth = scenario.scenario_summary.get('growth_score', 0)
                                    risk = scenario.scenario_summary.get('risk_score', 0)
                                    scenario_type = scenario_name.replace('_', ' ').title()
                                    print(f"{scenario_type}: Growth={growth:.3f}, Risk={risk:.3f}")
                        
                        print(f"\n[NEXT STEPS]")
                        print("• Review the scenario analysis above")
                        print("• Consider the growth vs risk trade-offs")
                        print("• Use this data for investment decision making")
                        print("• Run additional properties for comparison")
                        
                    except Exception as mc_error:
                        print(f"\n[FAIL] Monte Carlo analysis failed: {mc_error}")
                        print("This may be due to missing forecast data for the selected MSA.")
                        print("Try using New York (NYC) MSA which has complete data.")
                else:
                    print("\n[SKIP] Analysis skipped. Property data has been saved.")
                    print("You can run Monte Carlo analysis later using the saved property data.")
                
                print(f"\n" + "="*60)
                print("[COMPLETE] COLLECTION FINISHED")
                print("="*60)
                print("Your property data is ready for investment analysis!")
                
            else:
                print("\n[CANCEL] Property data collection was cancelled or failed.")
                print("No data was saved.")
            
        except KeyboardInterrupt:
            print("\n\n[CANCEL] Collection cancelled by user (Ctrl+C).")
            print("No data was saved.")
        except Exception as e:
            print(f"\n[ERROR] Error during collection: {e}")
            print("Please check your inputs and try again.")
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"[ERROR] Import error: {e}")
    print("Please ensure you're running from the project root directory.")
    sys.exit(1)