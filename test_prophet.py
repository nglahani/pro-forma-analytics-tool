#!/usr/bin/env python3
"""
Test Prophet Forecasting Engine

Tests all 11 Prophet metrics and generates forecast plots.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from forecasting.prophet_engine import ProphetForecaster
from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for faster plotting

def test_single_metric(parameter_name: str, geographic_code: str):
    """Test a single metric with Prophet forecasting."""
    
    print(f"\n{'='*80}")
    print(f"Testing: {parameter_name} ({geographic_code})")
    print(f"{'='*80}")
    
    try:
        # Create forecaster
        forecaster = ProphetForecaster(parameter_name, geographic_code)
        
        # Run complete forecast
        forecast_result = forecaster.run_complete_forecast(horizon_years=5)
        
        print(f"SUCCESS: {parameter_name}")
        print(f"   MAPE: {forecast_result.model_performance['mape']:.2f}%")
        print(f"   Trend: {forecast_result.trend_info['overall_trend']}")
        print(f"   Data Points: {forecast_result.historical_data_points}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {parameter_name} - {str(e)}")
        return False

def main():
    """Test all 11 Prophet metrics."""
    
    print("PROPHET FORECASTING TEST - ALL 11 METRICS")
    print("="*80)
    
    # Define all 11 metrics
    metrics_to_test = [
        # National metrics (3)
        ('treasury_10y', 'NATIONAL'),
        ('commercial_mortgage_rate', 'NATIONAL'), 
        ('fed_funds_rate', 'NATIONAL'),
        
        # MSA-specific metrics (8) - test with NYC MSA
        ('cap_rate', '35620'),  # NYC MSA
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
    failed = 0
    
    for parameter_name, geographic_code in metrics_to_test:
        if test_single_metric(parameter_name, geographic_code):
            successful += 1
        else:
            failed += 1
    
    # Summary
    print(f"\n{'='*80}")
    print("FINAL SUMMARY")
    print(f"{'='*80}")
    print(f"Successful forecasts: {successful}/11")
    print(f"Failed forecasts: {failed}/11")
    
    if successful == 11:
        print("ALL METRICS SUCCESSFULLY FORECASTED WITH PROPHET!")
        print("Check the 'forecast_plots' directory for visualizations")
    else:
        print(f"{failed} metrics failed - check errors above")

if __name__ == "__main__":
    main()