"""
Historical Data Visualization

Creates simple graphs of the historical data in the databases for manual verification.
Generates separate plots for different data categories and saves them as PNG files.
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
from datetime import datetime
import seaborn as sns

# Set style for better-looking plots
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

def create_output_directory():
    """Create output directory for graphs."""
    output_dir = Path('validation_charts')
    output_dir.mkdir(exist_ok=True)
    return output_dir

def load_data_from_db(db_path: Path, table_name: str) -> pd.DataFrame:
    """Load data from database table."""
    if not db_path.exists():
        print(f"Database not found: {db_path}")
        return pd.DataFrame()
    
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        print(f"Error loading {table_name} from {db_path}: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def plot_interest_rates():
    """Plot interest rates data."""
    print("Creating interest rates visualization...")
    
    db_path = Path('data/databases/market_data.db')
    df = load_data_from_db(db_path, 'interest_rates')
    
    if df.empty:
        print("No interest rates data found")
        return
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot each parameter
    for param in df['parameter_name'].unique():
        param_data = df[df['parameter_name'] == param].sort_values('date')
        ax.plot(param_data['date'], param_data['value'] * 100, 
               marker='o', linewidth=2, markersize=6, label=param.replace('_', ' ').title())
    
    ax.set_title('Interest Rates Over Time', fontsize=16, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Interest Rate (%)', fontsize=12)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    
    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45)
    
    # Add data source annotation
    data_sources = df['data_source'].unique()
    ax.text(0.02, 0.98, f"Data Sources: {', '.join(data_sources)}", 
           transform=ax.transAxes, fontsize=9, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    
    output_path = create_output_directory() / 'interest_rates_history.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_path}")
    
    plt.close()

def plot_property_market_data():
    """Plot rental market data by MSA."""
    print("Creating property market data visualization...")
    
    db_path = Path('data/databases/property_data.db')
    df = load_data_from_db(db_path, 'rental_market_data')
    
    if df.empty:
        print("No rental market data found")
        return
    
    # North Carolina MSA code mapping for better labels  
    msa_names = {
        '16740': 'Charlotte',
        '39580': 'Raleigh', 
        '24660': 'Greensboro',
        '20500': 'Durham'
    }
    
    # Get unique metrics
    metrics = df['metric_name'].unique()
    
    # Create subplots for each metric
    fig, axes = plt.subplots(len(metrics), 1, figsize=(14, 4*len(metrics)))
    if len(metrics) == 1:
        axes = [axes]
    
    for idx, metric in enumerate(metrics):
        ax = axes[idx]
        metric_data = df[df['metric_name'] == metric].sort_values('date')
        
        # Plot each MSA
        for msa_code in metric_data['geographic_code'].unique():
            msa_data = metric_data[metric_data['geographic_code'] == msa_code]
            msa_name = msa_names.get(msa_code, f'MSA {msa_code}')
            
            # Convert to percentage if it's a rate
            if 'growth' in metric or 'rate' in metric:
                values = msa_data['value'] * 100
                ylabel = f'{metric.replace("_", " ").title()} (%)'
            else:
                values = msa_data['value']
                ylabel = metric.replace('_', ' ').title()
            
            ax.plot(msa_data['date'], values, 
                   marker='o', linewidth=2, markersize=4, label=msa_name)
        
        ax.set_title(f'{metric.replace("_", " ").title()} by Metropolitan Area', 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel('Date', fontsize=11)
        ax.set_ylabel(ylabel, fontsize=11)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.xaxis.set_major_locator(mdates.YearLocator(2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    # Add data source annotation to the last subplot
    data_sources = df['data_source'].unique()
    axes[-1].text(0.02, -0.15, f"Data Sources: {', '.join(data_sources)}", 
                 transform=axes[-1].transAxes, fontsize=9,
                 bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    plt.tight_layout()
    
    output_path = create_output_directory() / 'property_market_data_history.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_path}")
    
    plt.close()

def plot_lending_requirements():
    """Plot lending requirements data by MSA."""
    print("Creating lending requirements visualization...")
    
    db_path = Path('data/databases/economic_data.db')
    df = load_data_from_db(db_path, 'lending_requirements')
    
    if df.empty:
        print("No lending requirements data found")
        return
    
    # North Carolina MSA code mapping
    msa_names = {
        '16740': 'Charlotte',
        '39580': 'Raleigh',
        '24660': 'Greensboro', 
        '20500': 'Durham'
    }
    
    # Get unique metrics
    metrics = df['metric_name'].unique()
    
    # Create subplots for each metric
    fig, axes = plt.subplots(len(metrics), 1, figsize=(14, 4*len(metrics)))
    if len(metrics) == 1:
        axes = [axes]
    
    for idx, metric in enumerate(metrics):
        ax = axes[idx]
        metric_data = df[df['metric_name'] == metric].sort_values('date')
        
        # Plot each MSA
        for msa_code in metric_data['geographic_code'].unique():
            msa_data = metric_data[metric_data['geographic_code'] == msa_code]
            msa_name = msa_names.get(msa_code, f'MSA {msa_code}')
            
            # Format values based on metric type
            if 'ratio' in metric:
                values = msa_data['value'] * 100
                ylabel = f'{metric.replace("_", " ").title()} (%)'
            elif 'pct' in metric or 'cost' in metric:
                values = msa_data['value'] * 100
                ylabel = f'{metric.replace("_", " ").title()} (%)'
            else:
                values = msa_data['value']
                ylabel = metric.replace('_', ' ').title()
            
            ax.plot(msa_data['date'], values,
                   marker='s', linewidth=2, markersize=4, label=msa_name)
        
        ax.set_title(f'{metric.replace("_", " ").title()} by Metropolitan Area',
                    fontsize=14, fontweight='bold')
        ax.set_xlabel('Date', fontsize=11)
        ax.set_ylabel(ylabel, fontsize=11)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.xaxis.set_major_locator(mdates.YearLocator(2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    # Add data source annotation
    data_sources = df['data_source'].unique()
    axes[-1].text(0.02, -0.15, f"Data Sources: {', '.join(data_sources)}", 
                 transform=axes[-1].transAxes, fontsize=9,
                 bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
    
    plt.tight_layout()
    
    output_path = create_output_directory() / 'lending_requirements_history.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_path}")
    
    plt.close()

def create_data_summary():
    """Create a summary table of all available data."""
    print("Creating data summary...")
    
    summary_data = []
    
    # Check each database
    databases = {
        'Market Data': {'path': 'data/databases/market_data.db', 'tables': ['interest_rates', 'cap_rates']},
        'Property Data': {'path': 'data/databases/property_data.db', 'tables': ['rental_market_data', 'operating_expenses']},
        'Economic Data': {'path': 'data/databases/economic_data.db', 'tables': ['lending_requirements', 'property_growth']}
    }
    
    for db_category, db_info in databases.items():
        db_path = Path(db_info['path'])
        
        if not db_path.exists():
            continue
            
        conn = sqlite3.connect(db_path)
        
        for table in db_info['tables']:
            try:
                # Get record count and date range
                count_df = pd.read_sql(f"SELECT COUNT(*) as count FROM {table}", conn)
                count = count_df.iloc[0]['count']
                
                if count > 0:
                    # Get date range
                    date_df = pd.read_sql(f"SELECT MIN(date) as min_date, MAX(date) as max_date FROM {table}", conn)
                    min_date = date_df.iloc[0]['min_date']
                    max_date = date_df.iloc[0]['max_date']
                    
                    # Get unique parameters/metrics
                    if table == 'interest_rates':
                        param_col = 'parameter_name'
                    else:
                        param_col = 'metric_name'
                    
                    try:
                        param_df = pd.read_sql(f"SELECT DISTINCT {param_col} FROM {table}", conn)
                        parameters = ', '.join(param_df[param_col].tolist())
                    except:
                        parameters = "Unknown structure"
                    
                    summary_data.append({
                        'Database': db_category,
                        'Table': table,
                        'Records': count,
                        'Date Range': f"{min_date} to {max_date}",
                        'Parameters/Metrics': parameters
                    })
                else:
                    summary_data.append({
                        'Database': db_category,
                        'Table': table,
                        'Records': 0,
                        'Date Range': 'No data',
                        'Parameters/Metrics': 'No data'
                    })
                    
            except Exception as e:
                summary_data.append({
                    'Database': db_category,
                    'Table': table,
                    'Records': 'Error',
                    'Date Range': str(e),
                    'Parameters/Metrics': 'Error'
                })
        
        conn.close()
    
    # Create summary DataFrame and display
    summary_df = pd.DataFrame(summary_data)
    
    print("\n" + "="*100)
    print("DATA SUMMARY - CURRENT DATABASE CONTENTS")
    print("="*100)
    print(summary_df.to_string(index=False))
    
    # Save summary to file
    output_dir = create_output_directory()
    summary_df.to_csv(output_dir / 'data_summary.csv', index=False)
    print(f"\nSummary saved to: {output_dir / 'data_summary.csv'}")

def main():
    """Generate all visualizations."""
    print("HISTORICAL DATA VISUALIZATION")
    print("="*50)
    print("Generating graphs for manual data verification...\n")
    
    # Create data summary first
    create_data_summary()
    
    # Generate visualizations
    plot_interest_rates()
    plot_property_market_data() 
    plot_lending_requirements()
    
    print("\n" + "="*50)
    print("VISUALIZATION COMPLETE")
    print("="*50)
    print(f"All charts saved to: {create_output_directory().absolute()}")
    print("\nFiles created:")
    output_dir = create_output_directory()
    for file in output_dir.glob('*.png'):
        print(f"  📊 {file.name}")
    for file in output_dir.glob('*.csv'):
        print(f"  📋 {file.name}")

if __name__ == "__main__":
    main()