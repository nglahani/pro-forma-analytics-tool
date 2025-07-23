#!/usr/bin/env python3
"""
Verify Pro Forma Metrics Data Coverage

Checks that we have historical data for all 9 key pro forma metrics:
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

from data.databases.database_manager import db_manager

def verify_metric_coverage():
    """Verify we have data for all 9 pro forma metrics."""
    
    print("VERIFYING PRO FORMA METRICS DATA COVERAGE")
    print("=" * 60)
    
    metrics_status = {}
    
    # 1. Interest Rate
    print("\n1. Interest Rate:")
    query = "SELECT COUNT(*) as count, MIN(date) as start_date, MAX(date) as end_date FROM interest_rates"
    results = db_manager.query_data('market_data', query)
    if results and results[0]['count'] > 0:
        print(f"   SUCCESS: {results[0]['count']} records from {results[0]['start_date']} to {results[0]['end_date']}")
        metrics_status['Interest Rate'] = True
    else:
        print("   NO DATA FOUND")
        metrics_status['Interest Rate'] = False
    
    # 2. Vacancy Rate
    print("\n2. Vacancy Rate:")
    query = "SELECT COUNT(*) as count, MIN(date) as start_date, MAX(date) as end_date FROM rental_market_data WHERE metric_name = 'vacancy_rate'"
    results = db_manager.query_data('property_data', query)
    if results and results[0]['count'] > 0:
        print(f"   SUCCESS: {results[0]['count']} records from {results[0]['start_date']} to {results[0]['end_date']}")
        metrics_status['Vacancy Rate'] = True
    else:
        print("   NO DATA FOUND")
        metrics_status['Vacancy Rate'] = False
    
    # 3. LTV
    print("\n3. LTV:")
    query = "SELECT COUNT(*) as count, MIN(date) as start_date, MAX(date) as end_date FROM lending_requirements WHERE metric_name = 'ltv_ratio'"
    results = db_manager.query_data('economic_data', query)
    if results and results[0]['count'] > 0:
        print(f"   SUCCESS: {results[0]['count']} records from {results[0]['start_date']} to {results[0]['end_date']}")
        metrics_status['LTV'] = True
    else:
        print("   NO DATA: No data found")
        metrics_status['LTV'] = False
    
    # 4. Rent Growth
    print("\n4. Rent Growth:")
    query = "SELECT COUNT(*) as count, MIN(date) as start_date, MAX(date) as end_date FROM rental_market_data WHERE metric_name = 'rent_growth'"
    results = db_manager.query_data('property_data', query)
    if results and results[0]['count'] > 0:
        print(f"   SUCCESS: {results[0]['count']} records from {results[0]['start_date']} to {results[0]['end_date']}")
        metrics_status['Rent Growth'] = True
    else:
        print("   NO DATA: No data found")
        metrics_status['Rent Growth'] = False
    
    # 5. Closing Cost (%)
    print("\n5. Closing Cost (%):")
    query = "SELECT COUNT(*) as count, MIN(date) as start_date, MAX(date) as end_date FROM lending_requirements WHERE metric_name = 'closing_cost_pct'"
    results = db_manager.query_data('economic_data', query)
    if results and results[0]['count'] > 0:
        print(f"   SUCCESS: {results[0]['count']} records from {results[0]['start_date']} to {results[0]['end_date']}")
        metrics_status['Closing Cost (%)'] = True
    else:
        print("   NO DATA: No data found")
        metrics_status['Closing Cost (%)'] = False
    
    # 6. Lender Reserve Requirements
    print("\n6. Lender Reserve Requirements:")
    query = "SELECT COUNT(*) as count, MIN(date) as start_date, MAX(date) as end_date FROM lending_requirements WHERE metric_name = 'lender_reserves'"
    results = db_manager.query_data('economic_data', query)
    if results and results[0]['count'] > 0:
        print(f"   SUCCESS: {results[0]['count']} records from {results[0]['start_date']} to {results[0]['end_date']}")
        metrics_status['Lender Reserve Requirements'] = True
    else:
        print("   NO DATA: No data found")
        metrics_status['Lender Reserve Requirements'] = False
    
    # 7. Property Growth
    print("\n7. Property Growth:")
    query = "SELECT COUNT(*) as count, MIN(date) as start_date, MAX(date) as end_date FROM property_growth"
    results = db_manager.query_data('economic_data', query)
    if results and results[0]['count'] > 0:
        print(f"   SUCCESS: {results[0]['count']} records from {results[0]['start_date']} to {results[0]['end_date']}")
        metrics_status['Property Growth'] = True
    else:
        print("   NO DATA: No data found")
        metrics_status['Property Growth'] = False
    
    # 8. Market Cap Rate
    print("\n8. Market Cap Rate:")
    query = "SELECT COUNT(*) as count, MIN(date) as start_date, MAX(date) as end_date FROM cap_rates"
    results = db_manager.query_data('market_data', query)
    if results and results[0]['count'] > 0:
        print(f"   SUCCESS: {results[0]['count']} records from {results[0]['start_date']} to {results[0]['end_date']}")
        metrics_status['Market Cap Rate'] = True
    else:
        print("   NO DATA: No data found")
        metrics_status['Market Cap Rate'] = False
    
    # 9. Expense Growth
    print("\n9. Expense Growth:")
    query = "SELECT COUNT(*) as count, MIN(date) as start_date, MAX(date) as end_date FROM operating_expenses"
    results = db_manager.query_data('property_data', query)
    if results and results[0]['count'] > 0:
        print(f"   SUCCESS: {results[0]['count']} records from {results[0]['start_date']} to {results[0]['end_date']}")
        metrics_status['Expense Growth'] = True
    else:
        print("   NO DATA: No data found")
        metrics_status['Expense Growth'] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("-" * 30)
    
    metrics_with_data = sum(metrics_status.values())
    total_metrics = len(metrics_status)
    
    print(f"Metrics with Data: {metrics_with_data}/{total_metrics}")
    
    if metrics_with_data == total_metrics:
        print("SUCCESS: ALL PRO FORMA METRICS HAVE HISTORICAL DATA")
        return True
    else:
        print("MISSING DATA FOR SOME METRICS")
        print("\nMissing data for:")
        for metric, has_data in metrics_status.items():
            if not has_data:
                print(f"  - {metric}")
        return False

def main():
    """Main function."""
    success = verify_metric_coverage()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())