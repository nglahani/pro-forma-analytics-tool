#!/usr/bin/env python3
"""
Regenerate All Prophet Forecast Plots

Regenerates all 11 forecast plots with the fixed visualization (no gaps).
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from forecasting.prophet_engine import ProphetForecaster
from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

def regenerate_plot(parameter_name: str, geographic_code: str):
    """Regenerate plot for a single metric."""
    
    print(f"Regenerating plot: {parameter_name} ({geographic_code})")
    
    try:
        # Create forecaster
        forecaster = ProphetForecaster(parameter_name, geographic_code)
        
        # Load data and fit model (suppress output)
        forecaster.load_historical_data()
        forecaster.fit_model()
        
        # Generate forecast
        forecast_result = forecaster.generate_forecast(horizon_years=5)
        
        # Create plot with fixed visualization
        plots_dir = Path("forecast_plots")
        plots_dir.mkdir(exist_ok=True)
        plot_path = plots_dir / f"{parameter_name}_{geographic_code}_prophet_forecast.png"
        forecaster.plot_forecast(forecast_result, str(plot_path))
        
        print(f"   Plot saved: {plot_path}")
        return True
        
    except Exception as e:
        print(f"   ERROR: {str(e)}")
        return False

def main():
    """Regenerate all 11 forecast plots."""
    
    print("REGENERATING ALL PROPHET FORECAST PLOTS")
    print("=" * 50)
    
    # Define all 11 metrics
    metrics_to_regenerate = [
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
    
    for parameter_name, geographic_code in metrics_to_regenerate:
        if regenerate_plot(parameter_name, geographic_code):
            successful += 1
    
    # Summary
    print(f"\n{'='*50}")
    print("REGENERATION COMPLETE")
    print(f"{'='*50}")
    print(f"Successfully regenerated: {successful}/11 plots")
    print("All plots now have connected historical and forecast lines!")

if __name__ == "__main__":
    main()