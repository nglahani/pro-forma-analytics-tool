#!/usr/bin/env python3
"""
Data Manager - Streamlined Data Operations

Consolidates key data operations:
- Database initialization
- Data collection for all 9 pro forma metrics
- Data verification
- Database status checks
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.databases.database_manager import db_manager
from collect_simplified_data import SimplifiedDataCollector
from verify_pro_forma_metrics import verify_metric_coverage

def initialize_system():
    """Initialize the database system."""
    print("INITIALIZING SYSTEM")
    print("=" * 40)
    
    try:
        db_manager.initialize_databases()
        print("SUCCESS: Databases initialized with simplified schemas")
        return True
    except Exception as e:
        print(f"ERROR: Failed to initialize databases: {e}")
        return False

def collect_all_data():
    """Collect data for all 9 pro forma metrics."""
    print("\nCOLLECTING DATA")
    print("=" * 40)
    
    collector = SimplifiedDataCollector()
    results = collector.run_full_collection()
    
    if results['success']:
        print(f"SUCCESS: Collected {results['total_records']} records across all metrics")
        return True
    else:
        print(f"PARTIAL SUCCESS: Collected {results['total_records']} records with {len(results['errors'])} errors")
        return False

def verify_system():
    """Verify all 9 pro forma metrics have data."""
    print("\nVERIFYING SYSTEM")
    print("=" * 40)
    
    return verify_metric_coverage()

def get_system_status():
    """Get current system status."""
    print("\nSYSTEM STATUS")
    print("=" * 40)
    
    # Check database files exist
    db_files = ['market_data.db', 'property_data.db', 'economic_data.db', 'forecast_cache.db']
    
    for db_file in db_files:
        db_path = db_manager.get_db_path(db_file.replace('.db', ''))
        exists = db_path.exists()
        print(f"{db_file}: {'EXISTS' if exists else 'MISSING'}")
    
    # Check total records
    total_records = 0
    try:
        # Count records across all main tables
        queries = [
            ("market_data", "SELECT COUNT(*) as count FROM interest_rates"),
            ("market_data", "SELECT COUNT(*) as count FROM cap_rates"),
            ("property_data", "SELECT COUNT(*) as count FROM rental_market_data"),
            ("property_data", "SELECT COUNT(*) as count FROM operating_expenses"),
            ("economic_data", "SELECT COUNT(*) as count FROM property_growth"),
            ("economic_data", "SELECT COUNT(*) as count FROM lending_requirements")
        ]
        
        for db_name, query in queries:
            results = db_manager.query_data(db_name, query)
            if results:
                total_records += results[0]['count']
        
        print(f"Total Records: {total_records}")
        
    except Exception as e:
        print(f"Error counting records: {e}")

def full_system_setup():
    """Complete system setup from scratch."""
    print("FULL SYSTEM SETUP")
    print("=" * 50)
    
    # Step 1: Initialize
    if not initialize_system():
        return False
    
    # Step 2: Collect data
    if not collect_all_data():
        print("Warning: Data collection had issues, but continuing...")
    
    # Step 3: Verify
    if verify_system():
        print("\nSUCCESS: System fully operational with all 9 pro forma metrics")
        return True
    else:
        print("\nWARNING: System setup completed but some metrics may be missing")
        return False

def main():
    """Main function with menu options."""
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'init':
            return 0 if initialize_system() else 1
        elif command == 'collect':
            return 0 if collect_all_data() else 1
        elif command == 'verify':
            return 0 if verify_system() else 1
        elif command == 'status':
            get_system_status()
            return 0
        elif command == 'setup':
            return 0 if full_system_setup() else 1
        else:
            print("Usage: python data_manager.py [init|collect|verify|status|setup]")
            return 1
    else:
        # Default: show status
        get_system_status()
        return 0

if __name__ == "__main__":
    exit(main())