"""
Data Scheduler Management Script

Command-line interface for managing the automated data update scheduler.
Provides easy start/stop/status control and configuration management.
"""

import os
import sys
import argparse
from datetime import datetime, date
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data.scheduler.data_scheduler import create_scheduler, UpdateFrequency
from core.logging_config import get_logger


def main():
    parser = argparse.ArgumentParser(description='Manage the automated data update scheduler')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start the scheduler')
    start_parser.add_argument('--fred-key', help='FRED API key (optional)')
    
    # Stop command
    stop_parser = subparsers.add_parser('stop', help='Stop the scheduler')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show scheduler status')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Execute immediate updates')
    update_parser.add_argument('parameter', nargs='?', help='Specific parameter to update (optional)')
    update_parser.add_argument('--all', action='store_true', help='Update all parameters')
    update_parser.add_argument('--type', choices=['all', 'interest_rates', 'real_estate', 'lending_requirements'], 
                               help='Update specific parameter category')
    update_parser.add_argument('--action', help='Action to perform (for CI/CD integration)')
    update_parser.add_argument('--fred-key', help='FRED API key')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Manage scheduler configuration')
    config_subparsers = config_parser.add_subparsers(dest='config_action')
    
    # Config add
    add_parser = config_subparsers.add_parser('add', help='Add scheduled update')
    add_parser.add_argument('parameter', help='Parameter name')
    add_parser.add_argument('--frequency', choices=['daily', 'weekly', 'monthly', 'quarterly'], 
                           default='monthly', help='Update frequency')
    add_parser.add_argument('--time', default='02:00', help='Time of day (HH:MM)')
    add_parser.add_argument('--geo-codes', nargs='+', help='Geographic codes')
    
    # Config remove
    remove_parser = config_subparsers.add_parser('remove', help='Remove scheduled update')
    remove_parser.add_argument('parameter', help='Parameter name')
    
    # Config enable/disable
    enable_parser = config_subparsers.add_parser('enable', help='Enable scheduled update')
    enable_parser.add_argument('parameter', help='Parameter name')
    
    disable_parser = config_subparsers.add_parser('disable', help='Disable scheduled update')
    disable_parser.add_argument('parameter', help='Parameter name')
    
    # Config list
    list_parser = config_subparsers.add_parser('list', help='List all scheduled updates')
    
    # Freshness command
    freshness_parser = subparsers.add_parser('freshness', help='Check data freshness')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    logger = get_logger(__name__)
    
    try:
        # Get FRED API key
        fred_api_key = args.fred_key if hasattr(args, 'fred_key') else os.getenv('FRED_API_KEY')
        
        if args.command == 'start':
            return start_scheduler(fred_api_key, logger)
        
        elif args.command == 'stop':
            return stop_scheduler(logger)
        
        elif args.command == 'status':
            return show_status(fred_api_key, logger)
        
        elif args.command == 'update':
            return execute_updates(fred_api_key, args, logger)
        
        elif args.command == 'config':
            return manage_config(fred_api_key, args, logger)
        
        elif args.command == 'freshness':
            return check_freshness(fred_api_key, logger)
        
        else:
            logger.error(f"Unknown command: {args.command}")
            return 1
            
    except Exception as e:
        logger.error(f"Command failed: {e}")
        return 1


def start_scheduler(fred_api_key: str, logger) -> int:
    """Start the scheduler."""
    
    logger.info("Starting data update scheduler...")
    
    scheduler = create_scheduler(fred_api_key)
    scheduler.start_scheduler()
    
    print("Data update scheduler started successfully!")
    print(f"Configured updates: {len(scheduler.scheduled_updates)}")
    print(f"Enabled updates: {len([u for u in scheduler.scheduled_updates.values() if u.enabled])}")
    print("\nScheduler is now running in the background.")
    print("Use 'python scripts/manage_scheduler.py status' to check status")
    print("Use 'python scripts/manage_scheduler.py stop' to stop the scheduler")
    
    # Keep the script running to maintain the scheduler
    try:
        while scheduler.is_running:
            import time
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, stopping scheduler...")
        scheduler.stop_scheduler()
        print("\nScheduler stopped.")
    
    return 0


def stop_scheduler(logger) -> int:
    """Stop the scheduler."""
    
    logger.info("Stopping scheduler...")
    
    # This is a simplified version - in production you'd want proper process management
    print("To stop the scheduler, use Ctrl+C on the running process.")
    print("For production deployment, use a process manager like systemd or supervisord.")
    
    return 0


def show_status(fred_api_key: str, logger) -> int:
    """Show scheduler status."""
    
    scheduler = create_scheduler(fred_api_key)
    status = scheduler.get_scheduler_status()
    
    print("\n" + "="*60)
    print("DATA SCHEDULER STATUS")
    print("="*60)
    print(f"Running: {'YES' if status['is_running'] else 'NO'}")
    print(f"Total scheduled updates: {status['total_scheduled_updates']}")
    print(f"Enabled updates: {status['enabled_updates']}")
    print(f"Stale parameters: {status['stale_parameters_count']}")
    print(f"Last health check: {status['last_health_check']}")
    print(f"Total update history: {status['total_update_history']}")
    
    if status['recent_updates']:
        print(f"\nRecent Updates:")
        for update in status['recent_updates']:
            timestamp = update.get('execution_time', 'Unknown')
            param = update.get('parameter_name', 'Unknown')
            success = 'SUCCESS' if update.get('success') else 'FAILED'
            print(f"  {timestamp}: {param} - {success}")
    
    print(f"\nNext Scheduled Jobs:")
    for job in status['next_scheduled_jobs']:
        print(f"  {job['parameter_name']}: {job['frequency']} at {job['time_of_day']}")
    
    return 0


def execute_updates(fred_api_key: str, args, logger) -> int:
    """Execute immediate updates."""
    
    scheduler = create_scheduler(fred_api_key)
    
    if args.all:
        logger.info("Executing updates for all parameters...")
        print("Executing immediate updates for all parameters...")
        
        result = scheduler.execute_all_updates()
        
        print(f"\nUpdate Summary:")
        print(f"Parameters updated: {result['parameters_updated']}")
        print(f"Successful: {result['successful_updates']}")
        print(f"Failed: {result['failed_updates']}")
        
        if result['failed_updates'] > 0:
            print(f"\nFailed updates:")
            for param, param_result in result['results'].items():
                if not param_result['success']:
                    print(f"  {param}: {param_result.get('error', 'Unknown error')}")
    
    elif args.parameter:
        logger.info(f"Executing update for {args.parameter}...")
        print(f"Executing immediate update for {args.parameter}...")
        
        result = scheduler.execute_immediate_update(args.parameter)
        
        if result['success']:
            print(f"SUCCESS: {result['records_collected']} records collected")
            print(f"Jobs: {result['jobs_successful']}/{result['jobs_total']} successful")
        else:
            print(f"FAILED: {result.get('error', 'Unknown error')}")
            return 1
    
    else:
        print("Please specify --all or a specific parameter name")
        return 1
    
    return 0


def manage_config(fred_api_key: str, args, logger) -> int:
    """Manage scheduler configuration."""
    
    scheduler = create_scheduler(fred_api_key)
    
    if args.config_action == 'list':
        print("\n" + "="*60)
        print("SCHEDULED UPDATES CONFIGURATION")
        print("="*60)
        
        for param_name, update in scheduler.scheduled_updates.items():
            status = "ENABLED" if update.enabled else "DISABLED"
            print(f"{param_name}: {update.frequency.value} at {update.time_of_day} ({status})")
            print(f"  Geographic codes: {', '.join(update.geographic_codes)}")
            print(f"  Updates: {update.update_count}, Errors: {update.error_count}")
            if update.last_update:
                print(f"  Last update: {update.last_update}")
            print()
    
    elif args.config_action == 'add':
        geo_codes = args.geo_codes or ['35620']  # Default to NYC
        frequency = UpdateFrequency(args.frequency)
        
        success = scheduler.add_scheduled_update(
            args.parameter, geo_codes, frequency, args.time
        )
        
        if success:
            print(f"Added scheduled update for {args.parameter}")
        else:
            print(f"Failed to add scheduled update for {args.parameter}")
            return 1
    
    elif args.config_action == 'remove':
        success = scheduler.remove_scheduled_update(args.parameter)
        
        if success:
            print(f"Removed scheduled update for {args.parameter}")
        else:
            print(f"Failed to remove scheduled update for {args.parameter}")
            return 1
    
    elif args.config_action == 'enable':
        success = scheduler.enable_update(args.parameter, True)
        
        if success:
            print(f"Enabled scheduled update for {args.parameter}")
        else:
            print(f"Failed to enable scheduled update for {args.parameter}")
            return 1
    
    elif args.config_action == 'disable':
        success = scheduler.enable_update(args.parameter, False)
        
        if success:
            print(f"Disabled scheduled update for {args.parameter}")
        else:
            print(f"Failed to disable scheduled update for {args.parameter}")
            return 1
    
    else:
        print("Please specify a config action: add, remove, enable, disable, or list")
        return 1
    
    return 0


def check_freshness(fred_api_key: str, logger) -> int:
    """Check data freshness."""
    
    scheduler = create_scheduler(fred_api_key)
    freshness_report = scheduler.get_data_freshness_report()
    
    print("\n" + "="*80)
    print("DATA FRESHNESS REPORT")
    print("="*80)
    
    # Group by staleness
    fresh_data = [r for r in freshness_report if not r.is_stale]
    stale_data = [r for r in freshness_report if r.is_stale]
    
    print(f"Fresh parameters: {len(fresh_data)}")
    print(f"Stale parameters: {len(stale_data)}")
    
    if stale_data:
        print(f"\nSTALE DATA (needs update):")
        print(f"{'Parameter':<20} {'Geography':<10} {'Days Old':<10} {'Action'}")
        print("-" * 80)
        
        for report in sorted(stale_data, key=lambda x: x.days_since_update, reverse=True):
            print(f"{report.parameter_name:<20} {report.geographic_code:<10} {report.days_since_update:<10} {report.recommended_action}")
    
    if fresh_data:
        print(f"\nFRESH DATA:")
        print(f"{'Parameter':<20} {'Geography':<10} {'Days Old':<10} {'Last Update'}")
        print("-" * 80)
        
        for report in sorted(fresh_data, key=lambda x: x.days_since_update):
            print(f"{report.parameter_name:<20} {report.geographic_code:<10} {report.days_since_update:<10} {report.last_data_date}")
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)