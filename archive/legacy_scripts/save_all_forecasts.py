#!/usr/bin/env python3
"""
Save All Prophet Forecasts to Database

Generates and saves all 11 Prophet forecasts to the forecast_cache database.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from forecasting.prophet_engine import ProphetForecaster
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

def save_forecast(parameter_name: str, geographic_code: str):
    """Generate and save forecast for a single metric."""
    
    print(f"Saving forecast: {parameter_name} ({geographic_code})")
    
    try:
        # Create forecaster
        forecaster = ProphetForecaster(parameter_name, geographic_code)
        
        # Generate forecast (without plot to save time)
        forecast_result = forecaster.run_complete_forecast(horizon_years=5, create_plot=False)
        
        print(f"   Saved to database: {parameter_name}")
        return True
        
    except Exception as e:
        print(f"   ERROR: {str(e)}")
        return False

def main():
    """Save all 11 Prophet forecasts to database."""
    
    print("SAVING ALL PROPHET FORECASTS TO DATABASE")
    print("=" * 50)
    
    # Define all 11 metrics
    metrics_to_save = [
        # National metrics (3)
        ('treasury_10y', 'NATIONAL'),
        ('commercial_mortgage_rate', 'NATIONAL'), 
        ('fed_funds_rate', 'NATIONAL'),
        
        # MSA-specific metrics (8) - NYC MSA
        ('cap_rate', '35620'),
        ('vacancy_rate', '35620'),
        ('rent_growth', '35620'),
        ('expense_growth', '35620'),
        ('ltv_ratio', '35620'),
        ('closing_cost_pct', '35620'),
        ('lender_reserves', '35620'),
        ('property_growth', '35620')
    ]
    
    # Track results
    successful = 0
    
    for parameter_name, geographic_code in metrics_to_save:
        if save_forecast(parameter_name, geographic_code):
            successful += 1
    
    # Summary
    print(f"\n{'='*50}")
    print("DATABASE SAVE COMPLETE")
    print(f"{'='*50}")
    print(f"Successfully saved: {successful}/11 forecasts")
    
    # Verify database contents
    try:
        from data.databases.database_manager import db_manager
        forecasts = db_manager.query_data('forecast_cache', 'SELECT COUNT(*) as count FROM prophet_forecasts')[0]['count']
        print(f"Total forecasts in database: {forecasts}")
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    main()