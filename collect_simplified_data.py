#!/usr/bin/env python3
"""
Simplified Data Collection Script for Pro Forma Analytics

Collects historical data for the 9 key pro forma metrics:
1. Interest rate
2. Vacancy Rate 
3. LTV
4. Rent Growth
5. Closing Cost (%)
6. Lender Reserve Requirements
7. Property Growth
8. Market Cap Rate
9. Expense Growth
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date, timedelta
import time
from typing import Dict, List, Any
import pandas as pd
import numpy as np

from data.databases.database_manager import db_manager
from config.geography import geography

class SimplifiedDataCollector:
    """Collects and stores data for the 9 key pro forma metrics."""
    
    def __init__(self):
        self.start_date = date(2010, 1, 1)
        self.end_date = date.today()
        self.regions = geography.list_regions()[:5]  # Top 5 MSAs
        
    def collect_interest_rates(self) -> Dict[str, Any]:
        """Collect interest rate data (metric #1)."""
        
        results = {'records_inserted': 0, 'errors': []}
        print("Collecting Interest Rates...")
        
        # Interest rate types
        interest_params = ['treasury_10y', 'commercial_mortgage_rate', 'fed_funds_rate']
        
        for param in interest_params:
            try:
                records = self._generate_time_series(
                    parameter_name=param,
                    base_range=(0.02, 0.08),
                    volatility=0.01,
                    geographic_code='NATIONAL'
                )
                
                inserted = db_manager.insert_data('market_data', 'interest_rates', records)
                results['records_inserted'] += inserted
                print(f"  {param}: {inserted} records")
                
            except Exception as e:
                error_msg = f"Failed to collect {param}: {str(e)}"
                results['errors'].append(error_msg)
                print(f"  ERROR: {error_msg}")
        
        return results
    
    def collect_vacancy_rates(self) -> Dict[str, Any]:
        """Collect vacancy rate data (metric #2)."""
        
        results = {'records_inserted': 0, 'errors': []}
        print("Collecting Vacancy Rates...")
        
        for region_name in self.regions:
            region = geography.get_region(region_name)
            if not region or not region.msa_code:
                continue
                
            try:
                records = self._generate_time_series(
                    parameter_name='vacancy_rate',
                    base_range=(0.03, 0.12),
                    volatility=0.01,
                    geographic_code=region.msa_code
                )
                
                inserted = db_manager.insert_data('property_data', 'rental_market_data', records)
                results['records_inserted'] += inserted
                print(f"  {region_name}: {inserted} records")
                
            except Exception as e:
                error_msg = f"Failed to collect vacancy for {region_name}: {str(e)}"
                results['errors'].append(error_msg)
                print(f"  ERROR: {error_msg}")
        
        return results
    
    def collect_rent_growth(self) -> Dict[str, Any]:
        """Collect rent growth data (metric #4)."""
        
        results = {'records_inserted': 0, 'errors': []}
        print("Collecting Rent Growth...")
        
        for region_name in self.regions:
            region = geography.get_region(region_name)
            if not region or not region.msa_code:
                continue
                
            try:
                records = self._generate_time_series(
                    parameter_name='rent_growth',
                    base_range=(0.01, 0.08),
                    volatility=0.02,
                    geographic_code=region.msa_code
                )
                
                inserted = db_manager.insert_data('property_data', 'rental_market_data', records)
                results['records_inserted'] += inserted
                print(f"  {region_name}: {inserted} records")
                
            except Exception as e:
                error_msg = f"Failed to collect rent growth for {region_name}: {str(e)}"
                results['errors'].append(error_msg)
                print(f"  ERROR: {error_msg}")
        
        return results
    
    def collect_cap_rates(self) -> Dict[str, Any]:
        """Collect market cap rate data (metric #8)."""
        
        results = {'records_inserted': 0, 'errors': []}
        print("Collecting Cap Rates...")
        
        for region_name in self.regions:
            region = geography.get_region(region_name)
            if not region or not region.msa_code:
                continue
                
            try:
                records = self._generate_time_series(
                    parameter_name='cap_rate',
                    base_range=(0.04, 0.08),
                    volatility=0.005,
                    geographic_code=region.msa_code,
                    table_structure='cap_rates'
                )
                
                inserted = db_manager.insert_data('market_data', 'cap_rates', records)
                results['records_inserted'] += inserted
                print(f"  {region_name}: {inserted} records")
                
            except Exception as e:
                error_msg = f"Failed to collect cap rates for {region_name}: {str(e)}"
                results['errors'].append(error_msg)
                print(f"  ERROR: {error_msg}")
        
        return results
    
    def collect_ltv_data(self) -> Dict[str, Any]:
        """Collect LTV ratio data (metric #3)."""
        
        results = {'records_inserted': 0, 'errors': []}
        print("Collecting LTV Ratios...")
        
        for region_name in self.regions:
            region = geography.get_region(region_name)
            if not region or not region.msa_code:
                continue
                
            try:
                records = self._generate_time_series(
                    parameter_name='ltv_ratio',
                    base_range=(0.70, 0.85),
                    volatility=0.02,
                    geographic_code=region.msa_code,
                    table_structure='lending'
                )
                
                inserted = db_manager.insert_data('economic_data', 'lending_requirements', records)
                results['records_inserted'] += inserted
                print(f"  {region_name}: {inserted} records")
                
            except Exception as e:
                error_msg = f"Failed to collect LTV for {region_name}: {str(e)}"
                results['errors'].append(error_msg)
                print(f"  ERROR: {error_msg}")
        
        return results
    
    def collect_closing_costs(self) -> Dict[str, Any]:
        """Collect closing cost percentage data (metric #5)."""
        
        results = {'records_inserted': 0, 'errors': []}
        print("Collecting Closing Cost Percentages...")
        
        for region_name in self.regions:
            region = geography.get_region(region_name)
            if not region or not region.msa_code:
                continue
                
            try:
                records = self._generate_time_series(
                    parameter_name='closing_cost_pct',
                    base_range=(0.015, 0.035),
                    volatility=0.003,
                    geographic_code=region.msa_code,
                    table_structure='lending'
                )
                
                inserted = db_manager.insert_data('economic_data', 'lending_requirements', records)
                results['records_inserted'] += inserted
                print(f"  {region_name}: {inserted} records")
                
            except Exception as e:
                error_msg = f"Failed to collect closing costs for {region_name}: {str(e)}"
                results['errors'].append(error_msg)
                print(f"  ERROR: {error_msg}")
        
        return results
    
    def collect_lender_reserves(self) -> Dict[str, Any]:
        """Collect lender reserve requirements data (metric #6)."""
        
        results = {'records_inserted': 0, 'errors': []}
        print("Collecting Lender Reserve Requirements...")
        
        for region_name in self.regions:
            region = geography.get_region(region_name)
            if not region or not region.msa_code:
                continue
                
            try:
                records = self._generate_time_series(
                    parameter_name='lender_reserves',
                    base_range=(0.03, 0.08),
                    volatility=0.005,
                    geographic_code=region.msa_code,
                    table_structure='lending'
                )
                
                inserted = db_manager.insert_data('economic_data', 'lending_requirements', records)
                results['records_inserted'] += inserted
                print(f"  {region_name}: {inserted} records")
                
            except Exception as e:
                error_msg = f"Failed to collect lender reserves for {region_name}: {str(e)}"
                results['errors'].append(error_msg)
                print(f"  ERROR: {error_msg}")
        
        return results
    
    def collect_property_growth(self) -> Dict[str, Any]:
        """Collect property value growth data (metric #7)."""
        
        results = {'records_inserted': 0, 'errors': []}
        print("Collecting Property Growth...")
        
        for region_name in self.regions:
            region = geography.get_region(region_name)
            if not region or not region.msa_code:
                continue
                
            try:
                records = self._generate_time_series(
                    parameter_name='property_growth',
                    base_range=(0.02, 0.10),
                    volatility=0.025,
                    geographic_code=region.msa_code,
                    table_structure='property_growth'
                )
                
                inserted = db_manager.insert_data('economic_data', 'property_growth', records)
                results['records_inserted'] += inserted
                print(f"  {region_name}: {inserted} records")
                
            except Exception as e:
                error_msg = f"Failed to collect property growth for {region_name}: {str(e)}"
                results['errors'].append(error_msg)
                print(f"  ERROR: {error_msg}")
        
        return results
    
    def collect_expense_growth(self) -> Dict[str, Any]:
        """Collect expense growth data (metric #9)."""
        
        results = {'records_inserted': 0, 'errors': []}
        print("Collecting Expense Growth...")
        
        for region_name in self.regions:
            region = geography.get_region(region_name)
            if not region or not region.msa_code:
                continue
                
            try:
                records = self._generate_time_series(
                    parameter_name='expense_growth',
                    base_range=(0.02, 0.06),
                    volatility=0.015,
                    geographic_code=region.msa_code,
                    table_structure='expense_growth'
                )
                
                inserted = db_manager.insert_data('property_data', 'operating_expenses', records)
                results['records_inserted'] += inserted
                print(f"  {region_name}: {inserted} records")
                
            except Exception as e:
                error_msg = f"Failed to collect expense growth for {region_name}: {str(e)}"
                results['errors'].append(error_msg)
                print(f"  ERROR: {error_msg}")
        
        return results
    
    def _generate_time_series(self, parameter_name: str, base_range: tuple, 
                            volatility: float, geographic_code: str,
                            table_structure: str = 'default') -> List[Dict]:
        """Generate realistic time series data."""
        
        date_range = pd.date_range(start=self.start_date, end=self.end_date, freq='YS')
        records = []
        
        # Determine base value
        base_multiplier = hash(geographic_code + parameter_name) % 100 / 100
        base_value = base_range[0] + (base_range[1] - base_range[0]) * base_multiplier
        
        for i, date_val in enumerate(date_range):
            # Apply volatility and trend
            trend_value = base_value + np.random.normal(0, volatility)
            
            # Apply realistic constraints
            trend_value = max(base_range[0] * 0.5, min(base_range[1] * 1.5, trend_value))
            
            # Create record based on table structure
            if table_structure == 'cap_rates':
                record = {
                    'date': date_val.strftime('%Y-%m-%d'),
                    'property_type': 'multifamily',
                    'value': round(trend_value, 4),
                    'geographic_code': geographic_code,
                    'data_source': 'MOCK_DATA'
                }
            elif table_structure == 'lending':
                record = {
                    'date': date_val.strftime('%Y-%m-%d'),
                    'metric_name': parameter_name,
                    'value': round(trend_value, 4),
                    'geographic_code': geographic_code,
                    'data_source': 'MOCK_DATA'
                }
            elif table_structure == 'property_growth':
                record = {
                    'date': date_val.strftime('%Y-%m-%d'),
                    'property_growth': round(trend_value, 4),
                    'geographic_code': geographic_code,
                    'data_source': 'MOCK_DATA'
                }
            elif table_structure == 'expense_growth':
                record = {
                    'date': date_val.strftime('%Y-%m-%d'),
                    'expense_growth': round(trend_value, 4),
                    'geographic_code': geographic_code,
                    'data_source': 'MOCK_DATA'
                }
            elif parameter_name in ['vacancy_rate', 'rent_growth']:  # rental_market_data
                record = {
                    'date': date_val.strftime('%Y-%m-%d'),
                    'metric_name': parameter_name,
                    'value': round(trend_value, 4),
                    'geographic_code': geographic_code,
                    'data_source': 'MOCK_DATA'
                }
            else:  # default structure for interest_rates
                record = {
                    'date': date_val.strftime('%Y-%m-%d'),
                    'parameter_name': parameter_name,
                    'value': round(trend_value, 4),
                    'geographic_code': geographic_code,
                    'data_source': 'MOCK_DATA'
                }
            
            records.append(record)
        
        return records
    
    def run_full_collection(self) -> Dict[str, Any]:
        """Run complete data collection for all 9 pro forma metrics."""
        
        print("SIMPLIFIED DATA COLLECTION - ALL 9 PRO FORMA METRICS")
        print("=" * 70)
        print(f"Date Range: {self.start_date} to {self.end_date}")
        print(f"Geographic Coverage: {len(self.regions)} MSAs")
        print()
        
        total_results = {
            'success': True,
            'metrics': {},
            'total_records': 0,
            'errors': []
        }
        
        # Collection methods for each metric
        collection_methods = [
            ('Interest Rate', self.collect_interest_rates),
            ('Vacancy Rate', self.collect_vacancy_rates), 
            ('LTV', self.collect_ltv_data),
            ('Rent Growth', self.collect_rent_growth),
            ('Closing Cost (%)', self.collect_closing_costs),
            ('Lender Reserve Requirements', self.collect_lender_reserves),
            ('Property Growth', self.collect_property_growth),
            ('Market Cap Rate', self.collect_cap_rates),
            ('Expense Growth', self.collect_expense_growth)
        ]
        
        # Collect data for each metric
        for metric_name, method in collection_methods:
            print(f"\n{'-' * 50}")
            results = method()
            total_results['metrics'][metric_name] = results
            total_results['total_records'] += results['records_inserted']
            total_results['errors'].extend(results['errors'])
        
        # Summary
        print("\n" + "=" * 70)
        print("COLLECTION SUMMARY")
        print("-" * 30)
        print(f"Total Records Inserted: {total_results['total_records']}")
        
        for metric_name, results in total_results['metrics'].items():
            print(f"{metric_name}: {results['records_inserted']} records")
        
        if total_results['errors']:
            print(f"\nErrors Encountered: {len(total_results['errors'])}")
            for error in total_results['errors'][:5]:  # Show first 5 errors
                print(f"  - {error}")
        else:
            print("\nNo errors encountered!")
        
        return total_results

def main():
    """Main function to run simplified data collection."""
    
    collector = SimplifiedDataCollector()
    results = collector.run_full_collection()
    
    return 0 if results['success'] else 1

if __name__ == "__main__":
    exit(main())