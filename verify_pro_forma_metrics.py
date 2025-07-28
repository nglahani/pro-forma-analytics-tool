#!/usr/bin/env python3
"""
Pro Forma Metrics Verification Module

Verifies that all 11 required pro forma metrics have sufficient data
for DCF analysis across major MSAs.
"""

from typing import Dict, List, Tuple
from datetime import date, datetime
from data.databases.database_manager import db_manager


def verify_metric_coverage() -> bool:
    """
    Verify that all 11 pro forma metrics have adequate data coverage.
    
    Returns:
        bool: True if all metrics have sufficient data, False otherwise
    """
    print("Verifying Pro Forma Metric Coverage...")
    print("-" * 50)
    
    # Define the 11 required pro forma metrics
    required_metrics = [
        'treasury_10y',           # National interest rate
        'commercial_mortgage_rate', # National interest rate  
        'fed_funds_rate',         # National interest rate
        'cap_rate',              # MSA-specific
        'vacancy_rate',          # MSA-specific
        'rent_growth',           # MSA-specific
        'expense_growth',        # MSA-specific
        'ltv_ratio',             # MSA-specific lending
        'closing_cost_pct',      # MSA-specific lending
        'lender_reserves',       # MSA-specific lending
        'property_growth'        # MSA-specific
    ]
    
    # Major MSAs to verify
    major_msas = [
        '35620',  # New York-Newark-Jersey City
        '31080',  # Los Angeles-Long Beach-Anaheim
        '16980',  # Chicago-Naperville-Elgin
        '47900',  # Washington-Arlington-Alexandria
        '33100'   # Miami-Fort Lauderdale-West Palm Beach
    ]
    
    # National metrics only need one geographic code
    national_metrics = ['treasury_10y', 'commercial_mortgage_rate', 'fed_funds_rate']
    
    verification_results = []
    overall_success = True
    
    for metric in required_metrics:
        try:
            if metric in national_metrics:
                # Check national data (use 'US' as geographic code)
                coverage = check_metric_coverage(metric, 'US')
                verification_results.append((metric, 'US', coverage))
                if not coverage['sufficient']:
                    overall_success = False
            else:
                # Check MSA-specific data
                for msa in major_msas:
                    coverage = check_metric_coverage(metric, msa)
                    verification_results.append((metric, msa, coverage))
                    if not coverage['sufficient']:
                        overall_success = False
        except Exception as e:
            print(f"Error verifying {metric}: {e}")
            verification_results.append((metric, 'ERROR', {'sufficient': False, 'error': str(e)}))
            overall_success = False
    
    # Print detailed results
    print_verification_results(verification_results)
    
    return overall_success


def check_metric_coverage(metric_name: str, geographic_code: str) -> Dict:
    """
    Check data coverage for a specific metric and geography.
    
    Args:
        metric_name: Name of the pro forma metric
        geographic_code: Geographic identifier (MSA code or 'US')
        
    Returns:
        Dict with coverage information
    """
    # Define minimum data requirements
    min_years = 10  # Minimum 10 years of historical data
    min_completeness = 80.0  # At least 80% data completeness
    
    try:
        # Get data for the last 15 years
        end_date = date.today()
        start_date = date(end_date.year - 15, 1, 1)
        
        # Get historical data points
        data_points = db_manager.get_parameter_data(
            metric_name, geographic_code, start_date, end_date
        )
        
        # Calculate coverage metrics
        actual_years = len(data_points)
        expected_years = 15
        completeness_pct = (actual_years / expected_years) * 100 if expected_years > 0 else 0
        
        # Determine if coverage is sufficient
        sufficient = (actual_years >= min_years and completeness_pct >= min_completeness)
        
        return {
            'sufficient': sufficient,
            'actual_years': actual_years,
            'expected_years': expected_years,
            'completeness_pct': completeness_pct,
            'min_years_required': min_years,
            'min_completeness_required': min_completeness,
            'latest_date': data_points[-1]['date'] if data_points else None,
            'earliest_date': data_points[0]['date'] if data_points else None
        }
        
    except Exception as e:
        return {
            'sufficient': False,
            'error': str(e),
            'actual_years': 0,
            'completeness_pct': 0.0
        }


def print_verification_results(results: List[Tuple]) -> None:
    """Print formatted verification results."""
    
    print("\nMetric Coverage Verification Results:")
    print("=" * 80)
    
    # Group results by metric
    metrics_summary = {}
    
    for metric, geo, coverage in results:
        if metric not in metrics_summary:
            metrics_summary[metric] = []
        metrics_summary[metric].append((geo, coverage))
    
    # Print summary for each metric
    for metric, geo_results in metrics_summary.items():
        print(f"\n{metric.upper().replace('_', ' ')}:")
        print("-" * 40)
        
        for geo, coverage in geo_results:
            if 'error' in coverage:
                status = "❌ ERROR"
                details = f"Error: {coverage['error']}"
            elif coverage['sufficient']:
                status = "✅ SUFFICIENT"
                details = f"{coverage['actual_years']} years ({coverage['completeness_pct']:.1f}%)"
            else:
                status = "⚠️  INSUFFICIENT"
                details = f"{coverage['actual_years']} years ({coverage['completeness_pct']:.1f}%) - Need {coverage['min_years_required']}+ years"
            
            geo_name = "National" if geo == "US" else f"MSA {geo}"
            print(f"  {geo_name:20} {status:15} {details}")
    
    # Print overall summary
    total_checks = len(results)
    successful_checks = sum(1 for _, _, coverage in results if coverage.get('sufficient', False))
    
    print(f"\n" + "=" * 80)
    print(f"OVERALL SUMMARY: {successful_checks}/{total_checks} checks passed")
    
    if successful_checks == total_checks:
        print("✅ All pro forma metrics have sufficient data coverage for DCF analysis")
    else:
        failed_checks = total_checks - successful_checks
        print(f"⚠️  {failed_checks} metrics have insufficient data - DCF analysis may be limited")


def get_metric_summary() -> Dict:
    """
    Get a summary of all metric coverage for programmatic use.
    
    Returns:
        Dict with summary statistics
    """
    # This is a simplified version for programmatic access
    required_metrics = [
        'treasury_10y', 'commercial_mortgage_rate', 'fed_funds_rate',
        'cap_rate', 'vacancy_rate', 'rent_growth', 'expense_growth',
        'ltv_ratio', 'closing_cost_pct', 'lender_reserves', 'property_growth'
    ]
    
    summary = {
        'total_metrics': len(required_metrics),
        'metrics_with_data': 0,
        'metrics_missing_data': [],
        'overall_sufficient': False
    }
    
    try:
        # Quick check - just verify we have some data for each metric
        for metric in required_metrics:
            try:
                # Check with a major MSA or national code
                test_geo = 'US' if metric in ['treasury_10y', 'commercial_mortgage_rate', 'fed_funds_rate'] else '35620'
                data = db_manager.get_parameter_data(metric, test_geo)
                
                if data and len(data) >= 5:  # At least 5 years of data
                    summary['metrics_with_data'] += 1
                else:
                    summary['metrics_missing_data'].append(metric)
                    
            except Exception:
                summary['metrics_missing_data'].append(metric)
        
        # Determine overall sufficiency
        summary['overall_sufficient'] = len(summary['metrics_missing_data']) == 0
        
    except Exception as e:
        summary['error'] = str(e)
    
    return summary


if __name__ == "__main__":
    success = verify_metric_coverage()
    exit(0 if success else 1)