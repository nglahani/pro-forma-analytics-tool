#!/usr/bin/env python3
"""
Quick Analysis Workflow

Simple workflow to load property data from input files and run complete pro forma analysis.
This provides the streamlined input file -> database -> valuation workflow you requested.
"""

import sys
from pathlib import Path
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from input_file_processor import InputFileProcessor
from database.property_database import property_db
from core.logging_config import get_logger

logger = get_logger(__name__)


class QuickAnalysisWorkflow:
    """Streamlined workflow from input file to pro forma valuation."""
    
    def __init__(self):
        self.processor = InputFileProcessor()
    
    def run_complete_analysis(self, input_file: str, user_id: str = "default_user") -> bool:
        """Run complete analysis workflow from input file to valuation results."""
        
        print("=" * 70)
        print("QUICK ANALYSIS WORKFLOW")
        print("=" * 70)
        print(f"Processing: {input_file}")
        print()
        
        # Step 1: Process input file
        print("Step 1: Processing input file...")
        property_data = self.processor.process_file(input_file)
        
        if not property_data:
            print("[ERROR] Failed to process input file")
            return False
        
        print(f"[SUCCESS] Processed property: {property_data.property_name}")
        
        # Step 2: Load to database
        print("\nStep 2: Loading to database...")
        if not self.processor.load_to_database(property_data, user_id):
            print("[ERROR] Failed to load to database")
            return False
        
        print(f"[SUCCESS] Property {property_data.property_id} loaded to database")
        
        # Step 3: Display property summary
        print("\nStep 3: Property Summary")
        print("-" * 40)
        self._display_property_summary(property_data)
        
        # Step 4: Run pro forma analysis
        print("\nStep 4: Running Pro Forma Analysis...")
        analysis_successful = self._run_pro_forma_analysis(property_data)
        
        if analysis_successful:
            print("\n" + "=" * 70)
            print("WORKFLOW COMPLETE - ANALYSIS SUCCESSFUL")
            print("=" * 70)
            print("Your property has been processed and analyzed!")
            print(f"Property ID: {property_data.property_id}")
            print("Results are saved in the database for further review.")
            return True
        else:
            print("\n" + "=" * 70)
            print("WORKFLOW PARTIAL SUCCESS")
            print("=" * 70)
            print("Property loaded successfully, but analysis had issues.")
            print("You can still access the property data from the database.")
            return False
    
    def _display_property_summary(self, property_data):
        """Display a summary of the property data."""
        metrics = property_data.calculate_key_metrics()
        
        print(f"Property Name: {property_data.property_name}")
        print(f"Property ID: {property_data.property_id}")
        print(f"Location: {property_data.city}, {property_data.state}")
        print(f"Property Type: {metrics['property_type'].replace('_', ' ').title()}")
        print(f"Total Units: {metrics['total_units']}")
        print(f"Mixed Use: {'Yes' if metrics['is_mixed_use'] else 'No'}")
        print(f"Annual Gross Rent: ${metrics['annual_gross_rent']:,.0f}")
        
        if property_data.purchase_price:
            print(f"Purchase Price: ${property_data.purchase_price:,.0f}")
            print(f"Price per Unit: ${metrics['price_per_unit']:,.0f}")
            print(f"Gross Cap Rate: {metrics['gross_cap_rate']*100:.1f}%")
        
        # Show renovation details
        if property_data.renovation_info.anticipated_duration_months:
            print(f"Renovation: {property_data.renovation_info.anticipated_duration_months} months planned")
        
        # Show investor structure
        print(f"Investor Equity Share: {property_data.equity_structure.investor_equity_share_pct:.1f}%")
        print(f"Self Cash Percentage: {property_data.equity_structure.self_cash_percentage:.1f}%")
    
    def _run_pro_forma_analysis(self, property_data) -> bool:
        """Run Monte Carlo pro forma analysis."""
        
        if not property_data.msa_code:
            print("[WARNING] No MSA code - analysis may be limited")
            print("For full analysis, ensure your input file specifies a supported MSA")
            return False
        
        try:
            # Convert to legacy format for Monte Carlo engine
            legacy_property = property_data.to_legacy_format()
            
            print(f"Running Monte Carlo simulation for MSA {property_data.msa_code}...")
            
            # Import and run Monte Carlo analysis
            from monte_carlo.simulation_engine import monte_carlo_engine
            
            results = monte_carlo_engine.generate_scenarios(
                property_data=legacy_property,
                num_scenarios=100,  # More scenarios for better analysis
                horizon_years=10,   # Longer horizon for investment analysis
                use_correlations=True
            )
            
            if not results.scenarios:
                print("[ERROR] No scenarios generated")
                return False
            
            print(f"[SUCCESS] Generated {len(results.scenarios)} investment scenarios")
            
            # Save results to database
            if property_db.save_analysis_results(property_data.property_id, results):
                print("[SUCCESS] Analysis results saved to database")
            else:
                print("[WARNING] Results generated but not saved")
            
            # Display analysis summary
            self._display_analysis_results(results)
            
            return True
            
        except ImportError as e:
            print(f"[ERROR] Monte Carlo engine not available: {e}")
            return False
        except Exception as e:
            print(f"[ERROR] Analysis failed: {e}")
            return False
    
    def _display_analysis_results(self, results):
        """Display summary of Monte Carlo analysis results."""
        import numpy as np
        
        print("\nAnalysis Results:")
        print("-" * 30)
        
        # Extract scenario metrics
        growth_scores = [s.scenario_summary.get('growth_score', 0) for s in results.scenarios]
        risk_scores = [s.scenario_summary.get('risk_score', 0) for s in results.scenarios]
        
        if growth_scores and risk_scores:
            avg_growth = np.mean(growth_scores)
            avg_risk = np.mean(risk_scores)
            
            print(f"Scenarios Generated: {len(results.scenarios)}")
            print(f"Growth Potential Range: {min(growth_scores):.3f} - {max(growth_scores):.3f}")
            print(f"Risk Assessment Range: {min(risk_scores):.3f} - {max(risk_scores):.3f}")
            print(f"Average Growth Score: {avg_growth:.3f}")
            print(f"Average Risk Score: {avg_risk:.3f}")
            
            # Investment recommendation
            print("\nInvestment Recommendation:")
            if avg_growth > 0.55 and avg_risk < 0.45:
                print("[STRONG BUY] - Excellent growth potential with low risk")
            elif avg_growth > 0.45 and avg_risk < 0.55:
                print("[BUY] - Good growth potential with moderate risk")
            elif avg_growth > 0.35:
                print("[CONSIDER] - Moderate potential, evaluate risk tolerance")
            else:
                print("[CAUTION] - Lower growth potential, consider alternatives")
        
        else:
            print("Analysis completed but detailed metrics unavailable")


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Quick Property Analysis Workflow')
    parser.add_argument('input_file', nargs='?', 
                        default='property_input_template.json',
                        help='Path to property input file (default: property_input_template.json)')
    parser.add_argument('--user-id', default='default_user', 
                        help='User ID for database entries')
    
    args = parser.parse_args()
    
    # Check if default template exists
    if args.input_file == 'property_input_template.json':
        template_path = Path(args.input_file)
        if not template_path.exists():
            print("Default template not found. Creating sample template...")
            # You could auto-create the template here if needed
            print(f"Please create {args.input_file} or specify an existing input file")
            return
    
    workflow = QuickAnalysisWorkflow()
    success = workflow.run_complete_analysis(args.input_file, args.user_id)
    
    if success:
        print("\n[SUCCESS] Complete workflow successful!")
        
        # Show database stats
        stats = property_db.get_database_stats()
        print(f"\nDatabase Status:")
        print(f"Total Properties: {stats.get('total_properties', 0)}")
        print(f"Total Analyses: {stats.get('total_analyses', 0)}")
        
        print("\nNext steps:")
        print("1. Review the analysis results above")
        print("2. Access saved data for detailed review")
        print("3. Compare with other properties")
        print("4. Use results for investment decisions")
    else:
        print("\n[ERROR] Workflow completed with issues")
        print("Check the error messages above for details")


if __name__ == "__main__":
    main()