"""
Live Data Update Scheduler

Provides automated, scheduled updates for market data with configurable
frequencies, data freshness monitoring, and intelligent incremental updates.
"""

import schedule
import time
import threading
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path

from data.collectors.data_orchestrator import create_orchestrator, CollectionJob, CollectionResult
from data.databases.database_manager import db_manager
from config.parameters import parameters
from core.logging_config import get_logger


class UpdateFrequency(Enum):
    """Update frequency options."""
    DAILY = "daily"
    WEEKLY = "weekly"  
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


@dataclass
class ScheduledUpdate:
    """Configuration for a scheduled data update."""
    parameter_name: str
    geographic_codes: List[str]
    frequency: UpdateFrequency
    time_of_day: str = "02:00"  # Default to 2 AM
    enabled: bool = True
    last_update: Optional[datetime] = None
    next_update: Optional[datetime] = None
    update_count: int = 0
    error_count: int = 0
    last_error: Optional[str] = None


@dataclass
class DataFreshnessReport:
    """Report on data freshness status."""
    parameter_name: str
    geographic_code: str
    last_data_date: date
    days_since_update: int
    is_stale: bool
    recommended_action: str


class LiveDataScheduler:
    """Automated scheduler for live data updates."""
    
    def __init__(self, fred_api_key: Optional[str] = None, 
                 config_file: Optional[str] = None):
        self.logger = get_logger(__name__)
        self.orchestrator = create_orchestrator(fred_api_key)
        self.config_file = config_file or "data/scheduler/schedule_config.json"
        
        # Scheduling configuration
        self.scheduled_updates: Dict[str, ScheduledUpdate] = {}
        self.is_running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        
        # Monitoring
        self.update_history: List[Dict[str, Any]] = []
        self.last_health_check: Optional[datetime] = None
        
        # Load configuration
        self._load_configuration()
        
        # Setup default schedules
        self._setup_default_schedules()
    
    def _load_configuration(self):
        """Load scheduler configuration from file."""
        config_path = Path(self.config_file)
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                
                # Convert to ScheduledUpdate objects
                for param_name, config in config_data.get('scheduled_updates', {}).items():
                    self.scheduled_updates[param_name] = ScheduledUpdate(
                        parameter_name=param_name,
                        geographic_codes=config['geographic_codes'],
                        frequency=UpdateFrequency(config['frequency']),
                        time_of_day=config.get('time_of_day', '02:00'),
                        enabled=config.get('enabled', True),
                        last_update=datetime.fromisoformat(config['last_update']) if config.get('last_update') else None,
                        update_count=config.get('update_count', 0),
                        error_count=config.get('error_count', 0),
                        last_error=config.get('last_error')
                    )
                
                self.logger.info(f"Loaded {len(self.scheduled_updates)} scheduled updates from {config_path}")
                
            except Exception as e:
                self.logger.error(f"Failed to load configuration: {e}")
        else:
            self.logger.info("No existing configuration found, will create default")
    
    def _save_configuration(self):
        """Save current configuration to file."""
        config_path = Path(self.config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to serializable format
        config_data = {
            'scheduled_updates': {}
        }
        
        for param_name, update in self.scheduled_updates.items():
            config_data['scheduled_updates'][param_name] = {
                'geographic_codes': update.geographic_codes,
                'frequency': update.frequency.value,
                'time_of_day': update.time_of_day,
                'enabled': update.enabled,
                'last_update': update.last_update.isoformat() if update.last_update else None,
                'update_count': update.update_count,
                'error_count': update.error_count,
                'last_error': update.last_error
            }
        
        try:
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            self.logger.info(f"Saved configuration to {config_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
    
    def _setup_default_schedules(self):
        """Setup default update schedules for all parameters."""
        
        # Define recommended update frequencies by parameter type
        frequency_map = {
            # Interest rates - weekly (volatile)
            'treasury_10y': UpdateFrequency.WEEKLY,
            'fed_funds_rate': UpdateFrequency.WEEKLY,
            'commercial_mortgage_rate': UpdateFrequency.WEEKLY,
            
            # Real estate market data - monthly (slower moving)
            'cap_rate': UpdateFrequency.MONTHLY,
            'vacancy_rate': UpdateFrequency.MONTHLY,
            'rent_growth': UpdateFrequency.MONTHLY,
            'property_growth': UpdateFrequency.MONTHLY,
            'expense_growth': UpdateFrequency.MONTHLY,
            
            # Lending requirements - quarterly (stable)
            'ltv_ratio': UpdateFrequency.QUARTERLY,
            'closing_cost_pct': UpdateFrequency.QUARTERLY,
            'lender_reserves': UpdateFrequency.QUARTERLY
        }
        
        # Import active MSA configuration
        from config.msa_config import get_active_msa_codes
        msa_codes = get_active_msa_codes()
        national_codes = ['NATIONAL']
        
        for param_name, frequency in frequency_map.items():
            if param_name not in self.scheduled_updates:
                # Determine geographic scope
                if param_name in ['treasury_10y', 'fed_funds_rate', 'commercial_mortgage_rate']:
                    geo_codes = national_codes
                else:
                    geo_codes = msa_codes
                
                self.scheduled_updates[param_name] = ScheduledUpdate(
                    parameter_name=param_name,
                    geographic_codes=geo_codes,
                    frequency=frequency,
                    time_of_day="02:00",  # 2 AM for minimal system impact
                    enabled=True
                )
        
        # Save default configuration
        self._save_configuration()
        self.logger.info(f"Setup {len(self.scheduled_updates)} default scheduled updates")
    
    def add_scheduled_update(self, parameter_name: str, geographic_codes: List[str],
                           frequency: UpdateFrequency, time_of_day: str = "02:00",
                           enabled: bool = True) -> bool:
        """Add or update a scheduled parameter update."""
        
        try:
            self.scheduled_updates[parameter_name] = ScheduledUpdate(
                parameter_name=parameter_name,
                geographic_codes=geographic_codes,
                frequency=frequency,
                time_of_day=time_of_day,
                enabled=enabled
            )
            
            self._save_configuration()
            self.logger.info(f"Added scheduled update for {parameter_name}: {frequency.value} at {time_of_day}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add scheduled update for {parameter_name}: {e}")
            return False
    
    def remove_scheduled_update(self, parameter_name: str) -> bool:
        """Remove a scheduled update."""
        
        if parameter_name in self.scheduled_updates:
            del self.scheduled_updates[parameter_name]
            self._save_configuration()
            self.logger.info(f"Removed scheduled update for {parameter_name}")
            return True
        else:
            self.logger.warning(f"No scheduled update found for {parameter_name}")
            return False
    
    def enable_update(self, parameter_name: str, enabled: bool = True) -> bool:
        """Enable or disable a scheduled update."""
        
        if parameter_name in self.scheduled_updates:
            self.scheduled_updates[parameter_name].enabled = enabled
            self._save_configuration()
            status = "enabled" if enabled else "disabled"
            self.logger.info(f"Update for {parameter_name} {status}")
            return True
        else:
            self.logger.warning(f"No scheduled update found for {parameter_name}")
            return False
    
    def _execute_parameter_update(self, parameter_name: str) -> Dict[str, Any]:
        """Execute update for a specific parameter."""
        
        if parameter_name not in self.scheduled_updates:
            return {'success': False, 'error': 'Parameter not scheduled'}
        
        update_config = self.scheduled_updates[parameter_name]
        
        if not update_config.enabled:
            return {'success': False, 'error': 'Update disabled'}
        
        self.logger.info(f"Executing scheduled update for {parameter_name}")
        
        try:
            # Create collection jobs for this parameter
            param_def = parameters.get_parameter(parameter_name)
            expected_range = param_def.typical_range if param_def else (0.0, 1.0)
            
            # Get database mapping
            db_mapping = self.orchestrator.PARAMETER_DB_MAPPING.get(parameter_name)
            if not db_mapping:
                raise ValueError(f"No database mapping for {parameter_name}")
            
            jobs = []
            for geo_code in update_config.geographic_codes:
                # Only collect recent data (last 2 years for incremental updates)
                start_date = date.today() - timedelta(days=730)
                end_date = date.today()
                
                # Determine appropriate collector
                # Map parameters to appropriate collectors
                if parameter_name in ['treasury_10y', 'fed_funds_rate', 'commercial_mortgage_rate']:
                    collector_name = 'FRED'
                elif parameter_name in ['cap_rate', 'vacancy_rate']:
                    collector_name = 'Enhanced_RealEstate'
                elif parameter_name in ['rent_growth', 'expense_growth']:
                    collector_name = 'BLS'
                elif parameter_name in ['property_growth']:
                    collector_name = 'FHFA'
                else:
                    collector_name = 'Lending'
                
                jobs.append(CollectionJob(
                    parameter_name=parameter_name,
                    geographic_code=geo_code,
                    start_date=start_date,
                    end_date=end_date,
                    collector_name=collector_name,
                    database_info=db_mapping,
                    expected_range=expected_range
                ))
            
            # Execute collection
            results = self.orchestrator.execute_collection_plan(jobs, max_workers=2)
            
            # Process results
            successful_jobs = [r for r in results if r.success]
            failed_jobs = [r for r in results if not r.success]
            total_records = sum(r.records_collected for r in successful_jobs)
            
            # Update configuration
            update_config.last_update = datetime.now()
            update_config.update_count += 1
            
            if failed_jobs:
                update_config.error_count += len(failed_jobs)
                update_config.last_error = f"{len(failed_jobs)} of {len(jobs)} jobs failed"
            else:
                update_config.last_error = None
            
            self._save_configuration()
            
            result = {
                'success': True,
                'parameter_name': parameter_name,
                'jobs_total': len(jobs),
                'jobs_successful': len(successful_jobs),
                'jobs_failed': len(failed_jobs),
                'records_collected': total_records,
                'execution_time': datetime.now(),
                'errors': [r.error_message for r in failed_jobs if r.error_message]
            }
            
            self.logger.info(f"Completed update for {parameter_name}: {len(successful_jobs)}/{len(jobs)} jobs successful, {total_records} records")
            
            return result
            
        except Exception as e:
            update_config.error_count += 1
            update_config.last_error = str(e)
            self._save_configuration()
            
            self.logger.error(f"Failed to execute update for {parameter_name}: {e}")
            return {
                'success': False,
                'parameter_name': parameter_name,
                'error': str(e),
                'execution_time': datetime.now()
            }
    
    def execute_immediate_update(self, parameter_name: str) -> Dict[str, Any]:
        """Execute an immediate update for a parameter (outside of schedule)."""
        self.logger.info(f"Executing immediate update for {parameter_name}")
        
        result = self._execute_parameter_update(parameter_name)
        self.update_history.append(result)
        
        return result
    
    def execute_all_updates(self) -> Dict[str, Any]:
        """Execute immediate updates for all enabled parameters."""
        self.logger.info("Executing immediate updates for all parameters")
        
        results = {}
        total_successful = 0
        total_failed = 0
        
        for param_name, update_config in self.scheduled_updates.items():
            if update_config.enabled:
                result = self._execute_parameter_update(param_name)
                results[param_name] = result
                self.update_history.append(result)
                
                if result['success']:
                    total_successful += 1
                else:
                    total_failed += 1
        
        summary = {
            'execution_time': datetime.now(),
            'parameters_updated': len(results),
            'successful_updates': total_successful,
            'failed_updates': total_failed,
            'results': results
        }
        
        self.logger.info(f"Completed all updates: {total_successful} successful, {total_failed} failed")
        
        return summary
    
    def start_scheduler(self):
        """Start the automated scheduler."""
        
        if self.is_running:
            self.logger.warning("Scheduler is already running")
            return
        
        self.logger.info("Starting data update scheduler")
        
        # Clear any existing schedules
        schedule.clear()
        
        # Setup schedules for each parameter
        for param_name, update_config in self.scheduled_updates.items():
            if not update_config.enabled:
                continue
            
            # Create update function for this parameter
            def create_update_func(param):
                def update_func():
                    try:
                        result = self._execute_parameter_update(param)
                        self.update_history.append(result)
                    except Exception as e:
                        self.logger.error(f"Scheduled update failed for {param}: {e}")
                return update_func
            
            update_func = create_update_func(param_name)
            
            # Schedule based on frequency
            if update_config.frequency == UpdateFrequency.DAILY:
                schedule.every().day.at(update_config.time_of_day).do(update_func)
            elif update_config.frequency == UpdateFrequency.WEEKLY:
                schedule.every().monday.at(update_config.time_of_day).do(update_func)  # Monday updates
            elif update_config.frequency == UpdateFrequency.MONTHLY:
                schedule.every().month.do(update_func)  # First of month
            elif update_config.frequency == UpdateFrequency.QUARTERLY:
                # Schedule for first day of each quarter (Jan, Apr, Jul, Oct)
                schedule.every().month.do(update_func)  # Will need custom logic for quarterly
        
        # Add health check schedule (daily)
        schedule.every().day.at("01:00").do(self._health_check)
        
        # Start scheduler thread
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        self.logger.info(f"Scheduler started with {len(self.scheduled_updates)} configured updates")
    
    def stop_scheduler(self):
        """Stop the automated scheduler."""
        
        if not self.is_running:
            self.logger.warning("Scheduler is not running")
            return
        
        self.logger.info("Stopping data update scheduler")
        
        self.is_running = False
        schedule.clear()
        
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        self.logger.info("Scheduler stopped")
    
    def _run_scheduler(self):
        """Main scheduler loop (runs in separate thread)."""
        
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Scheduler error: {e}")
                time.sleep(300)  # Wait 5 minutes before retrying
    
    def _health_check(self):
        """Perform health check on data freshness and system status."""
        
        self.logger.info("Performing data freshness health check")
        
        try:
            freshness_report = self.get_data_freshness_report()
            stale_parameters = [r for r in freshness_report if r.is_stale]
            
            if stale_parameters:
                self.logger.warning(f"Found {len(stale_parameters)} stale parameters:")
                for param_report in stale_parameters:
                    self.logger.warning(f"  {param_report.parameter_name} ({param_report.geographic_code}): {param_report.days_since_update} days old")
            else:
                self.logger.info("All data is fresh")
            
            self.last_health_check = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
    
    def get_data_freshness_report(self) -> List[DataFreshnessReport]:
        """Generate a report on data freshness for all parameters."""
        
        freshness_reports = []
        today = date.today()
        
        # Define staleness thresholds by frequency
        staleness_thresholds = {
            UpdateFrequency.DAILY: 3,      # 3 days
            UpdateFrequency.WEEKLY: 10,    # 10 days  
            UpdateFrequency.MONTHLY: 40,   # 40 days
            UpdateFrequency.QUARTERLY: 100 # 100 days
        }
        
        for param_name, update_config in self.scheduled_updates.items():
            for geo_code in update_config.geographic_codes:
                try:
                    # Get most recent data point
                    data_points = db_manager.get_parameter_data(param_name, geo_code)
                    
                    if data_points:
                        # Find most recent date
                        most_recent = max(data_points, key=lambda x: x['date'])
                        last_data_date = date.fromisoformat(most_recent['date'])
                        days_since_update = (today - last_data_date).days
                    else:
                        last_data_date = date.min
                        days_since_update = 9999  # Very stale
                    
                    # Determine if stale
                    threshold = staleness_thresholds.get(update_config.frequency, 30)
                    is_stale = days_since_update > threshold
                    
                    # Recommended action
                    if is_stale:
                        if days_since_update > threshold * 2:
                            recommended_action = "URGENT: Execute immediate update"
                        else:
                            recommended_action = "Schedule update soon"
                    else:
                        recommended_action = "No action needed"
                    
                    freshness_reports.append(DataFreshnessReport(
                        parameter_name=param_name,
                        geographic_code=geo_code,
                        last_data_date=last_data_date,
                        days_since_update=days_since_update,
                        is_stale=is_stale,
                        recommended_action=recommended_action
                    ))
                    
                except Exception as e:
                    self.logger.error(f"Failed to check freshness for {param_name} ({geo_code}): {e}")
        
        return freshness_reports
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get comprehensive scheduler status report."""
        
        freshness_report = self.get_data_freshness_report()
        stale_count = len([r for r in freshness_report if r.is_stale])
        
        return {
            'is_running': self.is_running,
            'total_scheduled_updates': len(self.scheduled_updates),
            'enabled_updates': len([u for u in self.scheduled_updates.values() if u.enabled]),
            'last_health_check': self.last_health_check,
            'total_update_history': len(self.update_history),
            'recent_updates': self.update_history[-5:] if self.update_history else [],
            'stale_parameters_count': stale_count,
            'configuration_file': self.config_file,
            'next_scheduled_jobs': self._get_next_scheduled_jobs()
        }
    
    def _get_next_scheduled_jobs(self) -> List[Dict[str, Any]]:
        """Get list of next scheduled jobs."""
        # This would require more complex scheduling logic
        # For now, return a simple summary
        next_jobs = []
        
        for param_name, update_config in self.scheduled_updates.items():
            if update_config.enabled:
                next_jobs.append({
                    'parameter_name': param_name,
                    'frequency': update_config.frequency.value,
                    'time_of_day': update_config.time_of_day,
                    'last_update': update_config.last_update.isoformat() if update_config.last_update else None
                })
        
        return next_jobs


# Convenience functions
def create_scheduler(fred_api_key: Optional[str] = None,
                    config_file: Optional[str] = None) -> LiveDataScheduler:
    """Create a live data scheduler instance."""
    return LiveDataScheduler(fred_api_key, config_file)


def setup_default_schedule(fred_api_key: Optional[str] = None) -> LiveDataScheduler:
    """Setup scheduler with recommended default schedule."""
    scheduler = create_scheduler(fred_api_key)
    
    # Start the scheduler
    scheduler.start_scheduler()
    
    return scheduler