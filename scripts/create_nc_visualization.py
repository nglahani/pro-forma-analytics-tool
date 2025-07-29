"""
North Carolina Market Data Visualization

Creates comprehensive charts showing the current state of North Carolina
market data collection with proper historical coverage.
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

def create_output_directory():
    """Create output directory for graphs."""
    output_dir = Path('validation_charts')
    output_dir.mkdir(exist_ok=True)
    return output_dir

def create_comprehensive_nc_chart():
    """Create comprehensive North Carolina market data visualization."""
    
    print("Creating comprehensive North Carolina market data visualization...")
    
    # North Carolina MSA names
    msa_names = {
        '16740': 'Charlotte',
        '39580': 'Raleigh', 
        '24660': 'Greensboro',
        '20500': 'Durham'
    }
    
    # Create figure with subplots
    fig, axes = plt.subplots(3, 1, figsize=(16, 12))
    
    # 1. Interest Rates (National data)
    print("Plotting interest rates...")
    conn = sqlite3.connect('data/databases/market_data.db')
    
    ir_df = pd.read_sql("SELECT * FROM interest_rates ORDER BY date", conn)
    ir_df['date'] = pd.to_datetime(ir_df['date'])
    
    ax1 = axes[0]
    for param in ir_df['parameter_name'].unique():
        param_data = ir_df[ir_df['parameter_name'] == param]
        ax1.plot(param_data['date'], param_data['value'] * 100, 
                marker='o', linewidth=2, markersize=3, 
                label=param.replace('_', ' ').title())
    
    ax1.set_title('Interest Rates Over Time (2010-2025)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Interest Rate (%)', fontsize=11)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax1.xaxis.set_major_locator(mdates.YearLocator(2))
    
    # Add data source annotation
    ax1.text(0.02, 0.98, "Data Source: FRED", transform=ax1.transAxes, 
            fontsize=9, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # 2. Cap Rates by North Carolina MSA
    print("Plotting cap rates...")
    cap_df = pd.read_sql("SELECT * FROM cap_rates ORDER BY date, geographic_code", conn)
    conn.close()
    
    ax2 = axes[1]
    if not cap_df.empty:
        cap_df['date'] = pd.to_datetime(cap_df['date'])
        
        for msa_code in cap_df['geographic_code'].unique():
            msa_data = cap_df[cap_df['geographic_code'] == msa_code]
            msa_name = msa_names.get(msa_code, f'MSA {msa_code}')
            
            ax2.plot(msa_data['date'], msa_data['value'] * 100,
                    marker='s', linewidth=2, markersize=3, label=msa_name)
        
        ax2.set_title('Multifamily Cap Rates by North Carolina MSA (2015-2025)', 
                     fontsize=14, fontweight='bold')
        ax2.set_ylabel('Cap Rate (%)', fontsize=11)
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax2.xaxis.set_major_locator(mdates.YearLocator(2))
        
        # Add data source annotation
        ax2.text(0.02, 0.98, "Data Source: Enhanced Real Estate (Treasury + Risk Premium)", 
                transform=ax2.transAxes, fontsize=9, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    else:
        ax2.text(0.5, 0.5, 'No Cap Rate Data Available', 
                transform=ax2.transAxes, ha='center', va='center', fontsize=12)
        ax2.set_title('Cap Rates - No Data', fontsize=14)
    
    # 3. Vacancy Rates by North Carolina MSA  
    print("Plotting vacancy rates...")
    conn = sqlite3.connect('data/databases/property_data.db')
    vacancy_df = pd.read_sql("SELECT * FROM rental_market_data WHERE metric_name='vacancy_rate' ORDER BY date, geographic_code", conn)
    conn.close()
    
    ax3 = axes[2]
    if not vacancy_df.empty:
        vacancy_df['date'] = pd.to_datetime(vacancy_df['date'])
        
        for msa_code in vacancy_df['geographic_code'].unique():
            msa_data = vacancy_df[vacancy_df['geographic_code'] == msa_code]
            msa_name = msa_names.get(msa_code, f'MSA {msa_code}')
            
            ax3.plot(msa_data['date'], msa_data['value'] * 100,
                    marker='^', linewidth=2, markersize=3, label=msa_name)
        
        ax3.set_title('Rental Vacancy Rates by North Carolina MSA (2020-2025)', 
                     fontsize=14, fontweight='bold')
        ax3.set_ylabel('Vacancy Rate (%)', fontsize=11)
        ax3.legend(fontsize=10)
        ax3.grid(True, alpha=0.3)
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax3.xaxis.set_major_locator(mdates.YearLocator(1))
        
        # Add data source annotation
        ax3.text(0.02, 0.98, "Data Source: Enhanced Real Estate (Economic Cycle Model)", 
                transform=ax3.transAxes, fontsize=9, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
    else:
        ax3.text(0.5, 0.5, 'No Vacancy Rate Data Available', 
                transform=ax3.transAxes, ha='center', va='center', fontsize=12)
        ax3.set_title('Vacancy Rates - No Data', fontsize=14)
    
    # Format x-axis for all subplots
    for ax in axes:
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    # Add overall title and layout
    fig.suptitle('North Carolina Real Estate Market Data - Historical Overview', 
                fontsize=16, fontweight='bold', y=0.95)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.92)
    
    # Save the chart
    output_path = create_output_directory() / 'north_carolina_market_data_comprehensive.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved comprehensive chart: {output_path}")
    
    plt.close()

def create_data_summary():
    """Create summary of current North Carolina data."""
    
    print("Creating North Carolina data summary...")
    
    summary_data = []
    
    # Check interest rates
    conn = sqlite3.connect('data/databases/market_data.db')
    ir_df = pd.read_sql("SELECT COUNT(*) as count, MIN(date) as min_date, MAX(date) as max_date FROM interest_rates", conn)
    if ir_df.iloc[0]['count'] > 0:
        summary_data.append({
            'Data Category': 'Interest Rates',
            'Geographic Level': 'National',
            'Records': ir_df.iloc[0]['count'],
            'Date Range': f"{ir_df.iloc[0]['min_date']} to {ir_df.iloc[0]['max_date']}",
            'Parameters': 'treasury_10y, fed_funds_rate',
            'Data Source': 'FRED'
        })
    
    # Check cap rates
    cap_df = pd.read_sql("SELECT COUNT(*) as count, MIN(date) as min_date, MAX(date) as max_date FROM cap_rates", conn)
    if cap_df.iloc[0]['count'] > 0:
        msa_df = pd.read_sql("SELECT DISTINCT geographic_code FROM cap_rates", conn)
        msas = ', '.join(sorted(msa_df['geographic_code'].tolist()))
        summary_data.append({
            'Data Category': 'Cap Rates',
            'Geographic Level': 'MSA (NC)',
            'Records': cap_df.iloc[0]['count'],
            'Date Range': f"{cap_df.iloc[0]['min_date']} to {cap_df.iloc[0]['max_date']}",
            'Parameters': f'cap_rate for MSAs: {msas}',
            'Data Source': 'Enhanced Real Estate'
        })
    conn.close()
    
    # Check vacancy rates
    conn = sqlite3.connect('data/databases/property_data.db')
    vac_df = pd.read_sql("SELECT COUNT(*) as count, MIN(date) as min_date, MAX(date) as max_date FROM rental_market_data WHERE metric_name='vacancy_rate'", conn)
    if vac_df.iloc[0]['count'] > 0:
        msa_df = pd.read_sql("SELECT DISTINCT geographic_code FROM rental_market_data WHERE metric_name='vacancy_rate'", conn)
        msas = ', '.join(sorted(msa_df['geographic_code'].tolist()))
        summary_data.append({
            'Data Category': 'Vacancy Rates',
            'Geographic Level': 'MSA (NC)',
            'Records': vac_df.iloc[0]['count'],
            'Date Range': f"{vac_df.iloc[0]['min_date']} to {vac_df.iloc[0]['max_date']}",
            'Parameters': f'vacancy_rate for MSAs: {msas}',
            'Data Source': 'Enhanced Real Estate'
        })
    conn.close()
    
    # Create summary DataFrame and display
    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        
        print("\n" + "="*120)
        print("NORTH CAROLINA MARKET DATA SUMMARY")
        print("="*120)
        print(summary_df.to_string(index=False))
        
        # Save summary
        output_dir = create_output_directory()
        summary_df.to_csv(output_dir / 'north_carolina_data_summary.csv', index=False)
        print(f"\nSummary saved to: {output_dir / 'north_carolina_data_summary.csv'}")
    else:
        print("No data found to summarize")

def main():
    """Generate North Carolina market data visualizations."""
    print("NORTH CAROLINA MARKET DATA VISUALIZATION")
    print("="*50)
    
    create_data_summary()
    create_comprehensive_nc_chart()
    
    print("\n" + "="*50)
    print("NORTH CAROLINA VISUALIZATION COMPLETE")
    print("="*50)

if __name__ == "__main__":
    main()