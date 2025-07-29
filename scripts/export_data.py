"""
Data Export Script

Export market data from SQLite databases to CSV/Excel formats for analysis.
"""

import pandas as pd
import sqlite3
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data.databases.database_manager import db_manager


def export_parameter_data(parameter_name: str, output_format: str = 'csv'):
    """Export data for a specific parameter to CSV or Excel."""
    
    # Get all MSAs for this parameter
    if parameter_name in ['treasury_10y', 'fed_funds_rate', 'commercial_mortgage_rate']:
        geo_codes = ['NATIONAL']
    else:
        geo_codes = ['16980', '31080', '33100', '35620', '47900']  # All MSAs
    
    all_data = []
    
    for geo_code in geo_codes:
        try:
            data = db_manager.get_parameter_data(parameter_name, geo_code)
            for record in data:
                all_data.append({
                    'date': record['date'],
                    'parameter': parameter_name,
                    'geographic_code': geo_code,
                    'value': record['value'],
                    'data_source': record.get('data_source', 'Unknown')
                })
        except Exception as e:
            print(f"Warning: Could not export {parameter_name} for {geo_code}: {e}")
    
    if not all_data:
        print(f"No data found for parameter: {parameter_name}")
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(all_data)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(['geographic_code', 'date'])
    
    # Export
    output_dir = Path('exports')
    output_dir.mkdir(exist_ok=True)
    
    if output_format.lower() == 'excel':
        output_file = output_dir / f"{parameter_name}_data.xlsx"
        df.to_excel(output_file, index=False)
    else:
        output_file = output_dir / f"{parameter_name}_data.csv"
        df.to_csv(output_file, index=False)
    
    print(f"Exported {len(df)} records to: {output_file}")
    return output_file


def export_all_data(output_format: str = 'excel'):
    """Export all parameters to a single Excel file with multiple sheets."""
    
    parameters = [
        'treasury_10y', 'fed_funds_rate', 'commercial_mortgage_rate',
        'cap_rate', 'vacancy_rate', 'rent_growth', 'property_growth', 'expense_growth',
        'ltv_ratio', 'closing_cost_pct', 'lender_reserves'
    ]
    
    output_dir = Path('exports')
    output_dir.mkdir(exist_ok=True)
    
    if output_format.lower() == 'excel':
        output_file = output_dir / "all_market_data.xlsx"
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            for param in parameters:
                # Get all data for this parameter
                all_data = []
                
                if param in ['treasury_10y', 'fed_funds_rate', 'commercial_mortgage_rate']:
                    geo_codes = ['NATIONAL']
                else:
                    geo_codes = ['16980', '31080', '33100', '35620', '47900']
                
                for geo_code in geo_codes:
                    try:
                        data = db_manager.get_parameter_data(param, geo_code)
                        for record in data:
                            all_data.append({
                                'date': record['date'],
                                'geographic_code': geo_code,
                                'value': record['value'],
                                'data_source': record.get('data_source', 'Unknown')
                            })
                    except Exception as e:
                        print(f"Warning: Could not export {param} for {geo_code}: {e}")
                
                if all_data:
                    df = pd.DataFrame(all_data)
                    df['date'] = pd.to_datetime(df['date'])
                    df = df.sort_values(['geographic_code', 'date'])
                    
                    # Clean sheet name (Excel has restrictions)
                    sheet_name = param.replace('_', ' ').title()[:31]
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    print(f"Added {param}: {len(df)} records")
        
        print(f"\nExported all data to: {output_file}")
        return output_file
    
    else:
        # Export each parameter to separate CSV
        for param in parameters:
            export_parameter_data(param, 'csv')


def main():
    """Main function for command line usage."""
    
    import argparse
    
    parser = argparse.ArgumentParser(description='Export market data to CSV/Excel')
    parser.add_argument('--parameter', help='Specific parameter to export')
    parser.add_argument('--format', choices=['csv', 'excel'], default='excel', 
                       help='Output format')
    parser.add_argument('--all', action='store_true', 
                       help='Export all parameters')
    
    args = parser.parse_args()
    
    if args.all:
        export_all_data(args.format)
    elif args.parameter:
        export_parameter_data(args.parameter, args.format)
    else:
        print("Please specify --parameter <name> or --all")
        print("\nAvailable parameters:")
        print("  Interest Rates: treasury_10y, fed_funds_rate, commercial_mortgage_rate")
        print("  Real Estate: cap_rate, vacancy_rate, rent_growth, property_growth, expense_growth")
        print("  Lending: ltv_ratio, closing_cost_pct, lender_reserves")


if __name__ == "__main__":
    main()