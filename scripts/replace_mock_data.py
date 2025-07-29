"""
Replace Mock Data Script

Executable script to replace all mock data with real market data from various sources.
This script coordinates the complete data collection process.
"""

import os
import sys
from datetime import date, datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data.collectors.data_orchestrator import create_orchestrator
from core.logging_config import get_logger


def main():
    """Main execution function."""
    
    logger = get_logger(__name__)
    logger.info("Starting mock data replacement process")
    
    # Check for FRED API key
    fred_api_key = os.getenv('FRED_API_KEY')
    if not fred_api_key:
        logger.warning("FRED_API_KEY not found in environment variables")
        logger.info("FRED data collection will be skipped")
        logger.info("You can get a free API key at: https://fred.stlouisfed.org/docs/api/api_key.html")
        logger.info("Continuing with non-FRED data sources...")
        # Auto-continue for non-interactive execution
    
    try:
        # Create orchestrator
        logger.info("Initializing data orchestrator...")
        orchestrator = create_orchestrator(fred_api_key)
        
        # Set date range for data collection
        start_date = date(2010, 1, 1)
        end_date = date(datetime.now().year, 1, 1)
        
        logger.info(f"Data collection period: {start_date} to {end_date}")
        
        # Execute complete mock data replacement
        logger.info("Starting complete mock data replacement...")
        summary = orchestrator.replace_all_mock_data(start_date, end_date)
        
        # Display results
        print("\n" + "="*60)
        print("MOCK DATA REPLACEMENT SUMMARY")
        print("="*60)
        print(f"Total jobs executed: {summary['total_jobs']}")
        print(f"Successful jobs: {summary['successful_jobs']}")
        print(f"Failed jobs: {summary['failed_jobs']}")
        print(f"Success rate: {summary['success_rate']:.1%}")
        print(f"Total records collected: {summary['total_records_collected']:,}")
        
        print(f"\nBackup files created: {len(summary['backup_files'])}")
        for backup in summary['backup_files']:
            print(f"  - {backup}")
        
        print(f"\nPer-parameter results:")
        for param, stats in summary['parameter_summary'].items():
            print(f"  {param}: {stats['success']} success, {stats['failed']} failed, {stats['records']} records")
        
        if summary['errors']:
            print(f"\nErrors encountered:")
            for error in summary['errors'][:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(summary['errors']) > 5:
                print(f"  ... and {len(summary['errors']) - 5} more errors")
        
        print("\n" + "="*60)
        
        if summary['success_rate'] > 0.8:
            print("SUCCESS: Mock data replacement completed successfully!")
            logger.info("Mock data replacement completed with high success rate")
        elif summary['success_rate'] > 0.5:
            print("WARNING: Mock data replacement completed with some issues")
            logger.warning("Mock data replacement completed with moderate success rate")
        else:
            print("ERROR: Mock data replacement had significant issues")
            logger.error("Mock data replacement had low success rate")
        
        # Generate data status report
        print("\nGenerating final data status report...")
        status_report = orchestrator.get_data_status_report()
        
        print(f"\nDATA STATUS REPORT")
        print(f"Available collectors: {', '.join(status_report['collectors_available'])}")
        print(f"Total collections performed: {status_report['total_collections']}")
        
        print(f"\nDatabase record counts:")
        for param, count in status_report['database_status'].items():
            print(f"  {param}: {count}")
        
    except Exception as e:
        logger.error(f"Mock data replacement failed: {e}")
        print(f"\nERROR: {e}")
        print("Check the logs for more details.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)