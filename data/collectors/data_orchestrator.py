"""
Data Collection Orchestrator

Coordinates multiple data collectors to replace mock data with real market data.
Handles the complete workflow of data collection, validation, and database updates.
"""

import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from config.parameters import parameters
from core.logging_config import get_logger
from data.databases.database_manager import db_manager

from .base_collector import BaseDataCollector, DataQualityMetrics, collector_registry
from .bls_collector import BLSDataCollector, create_bls_collector
from .enhanced_real_estate_collector import (
    EnhancedRealEstateCollector,
    create_enhanced_real_estate_collector,
)
from .fhfa_collector import FHFACollector, create_fhfa_collector
from .fred_enhanced_collector import FredEnhancedCollector, create_fred_collector
from .lending_collector import LendingRequirementsCollector


@dataclass
class CollectionJob:
    """Represents a data collection job."""

    parameter_name: str
    geographic_code: str
    start_date: date
    end_date: date
    collector_name: str
    database_info: Dict[str, str]
    expected_range: Tuple[float, float]


@dataclass
class CollectionResult:
    """Results from a data collection job."""

    job: CollectionJob
    success: bool
    records_collected: int
    quality_metrics: Optional[DataQualityMetrics] = None
    error_message: Optional[str] = None


class DataOrchestrator:
    """Orchestrates data collection from multiple sources."""

    # Database table mapping for each parameter
    PARAMETER_DB_MAPPING = {
        # Interest rates -> market_data.interest_rates
        "treasury_10y": {"db_name": "market_data", "table_name": "interest_rates"},
        "fed_funds_rate": {"db_name": "market_data", "table_name": "interest_rates"},
        "commercial_mortgage_rate": {
            "db_name": "market_data",
            "table_name": "interest_rates",
        },
        # Cap rates -> market_data.cap_rates
        "cap_rate": {"db_name": "market_data", "table_name": "cap_rates"},
        # Rental market -> property_data.rental_market_data
        "vacancy_rate": {
            "db_name": "property_data",
            "table_name": "rental_market_data",
        },
        "rent_growth": {"db_name": "property_data", "table_name": "rental_market_data"},
        # Operating expenses -> property_data.operating_expenses
        "expense_growth": {
            "db_name": "property_data",
            "table_name": "operating_expenses",
        },
        # Property growth -> economic_data.property_growth
        "property_growth": {
            "db_name": "economic_data",
            "table_name": "property_growth",
        },
        # Lending requirements -> economic_data.lending_requirements
        "ltv_ratio": {"db_name": "economic_data", "table_name": "lending_requirements"},
        "closing_cost_pct": {
            "db_name": "economic_data",
            "table_name": "lending_requirements",
        },
        "lender_reserves": {
            "db_name": "economic_data",
            "table_name": "lending_requirements",
        },
    }

    def __init__(self, fred_api_key: Optional[str] = None):
        self.logger = get_logger(__name__)
        self.collectors: Dict[str, BaseDataCollector] = {}
        self.collection_history: List[CollectionResult] = []

        # Initialize collectors
        self._setup_collectors(fred_api_key)

    def _setup_collectors(self, fred_api_key: Optional[str]):
        """Initialize and register all data collectors."""

        try:
            # FRED collector for interest rates and economic data
            if not fred_api_key:
                fred_api_key = os.getenv("FRED_API_KEY")

            # Also try loading from settings if still not found
            if not fred_api_key:
                try:
                    from config.settings import settings

                    # External API keys are exposed via settings.external_apis
                    fred_api_key = settings.external_apis.fred_api_key
                except Exception:
                    fred_api_key = None

            if fred_api_key:
                fred_collector = create_fred_collector(fred_api_key)
                self.collectors["FRED"] = fred_collector
                collector_registry.register_collector(fred_collector)
                self.logger.info("Registered FRED collector")
            else:
                self.logger.warning(
                    "FRED API key not available - skipping FRED collector"
                )

            # BLS collector for economic data
            bls_collector = create_bls_collector()
            self.collectors["BLS"] = bls_collector
            collector_registry.register_collector(bls_collector)
            self.logger.info("Registered BLS collector")

            # FHFA collector for property growth
            fhfa_collector = create_fhfa_collector()
            self.collectors["FHFA"] = fhfa_collector
            collector_registry.register_collector(fhfa_collector)
            self.logger.info("Registered FHFA collector")

            # Enhanced real estate collector
            enhanced_re_collector = create_enhanced_real_estate_collector(fred_api_key)
            self.collectors["Enhanced_RealEstate"] = enhanced_re_collector
            collector_registry.register_collector(enhanced_re_collector)
            self.logger.info("Registered Enhanced Real Estate collector")

            # Lending collector
            lending_collector = LendingRequirementsCollector()
            self.collectors["Lending"] = lending_collector
            collector_registry.register_collector(lending_collector)
            self.logger.info("Registered Lending collector")

        except Exception as e:
            self.logger.error(f"Failed to setup collectors: {e}")
            raise

    def get_collection_plan(
        self, start_date: date, end_date: date, msas: Optional[List[str]] = None
    ) -> List[CollectionJob]:
        """
        Generate a comprehensive data collection plan.

        Args:
            start_date: Start date for data collection
            end_date: End date for data collection
            msas: List of MSA codes (default: all supported MSAs)

        Returns:
            List of collection jobs to execute
        """
        if msas is None:
            from config.msa_config import get_active_msa_codes

            msas = get_active_msa_codes()  # Use active North Carolina MSAs

        jobs = []

        # FRED parameters (national only)
        fred_params = ["treasury_10y", "fed_funds_rate", "commercial_mortgage_rate"]
        for param in fred_params:
            if "FRED" in self.collectors:
                param_def = parameters.get_parameter(param)
                expected_range = param_def.typical_range if param_def else (0.0, 1.0)

                jobs.append(
                    CollectionJob(
                        parameter_name=param,
                        geographic_code="NATIONAL",
                        start_date=start_date,
                        end_date=end_date,
                        collector_name="FRED",
                        database_info=self.PARAMETER_DB_MAPPING[param],
                        expected_range=expected_range,
                    )
                )

        # Enhanced real estate parameters (cap_rate, vacancy_rate)
        enhanced_re_params = ["cap_rate", "vacancy_rate"]
        for param in enhanced_re_params:
            param_def = parameters.get_parameter(param)
            expected_range = param_def.typical_range if param_def else (0.0, 1.0)

            for msa in msas:
                if "Enhanced_RealEstate" in self.collectors:
                    jobs.append(
                        CollectionJob(
                            parameter_name=param,
                            geographic_code=msa,
                            start_date=start_date,
                            end_date=end_date,
                            collector_name="Enhanced_RealEstate",
                            database_info=self.PARAMETER_DB_MAPPING.get(
                                param,
                                {"db_name": "market_data", "table_name": "cap_rates"},
                            ),
                            expected_range=expected_range,
                        )
                    )

        # BLS parameters (rent_growth, expense_growth)
        bls_params = ["rent_growth", "expense_growth"]
        for param in bls_params:
            param_def = parameters.get_parameter(param)
            expected_range = param_def.typical_range if param_def else (0.0, 1.0)

            for msa in msas:
                if "BLS" in self.collectors:
                    jobs.append(
                        CollectionJob(
                            parameter_name=param,
                            geographic_code=msa,
                            start_date=start_date,
                            end_date=end_date,
                            collector_name="BLS",
                            database_info=self.PARAMETER_DB_MAPPING.get(
                                param,
                                {
                                    "db_name": "property_data",
                                    "table_name": "rental_market_data",
                                },
                            ),
                            expected_range=expected_range,
                        )
                    )

        # FHFA parameters (property_growth)
        fhfa_params = ["property_growth"]
        for param in fhfa_params:
            param_def = parameters.get_parameter(param)
            expected_range = param_def.typical_range if param_def else (0.0, 1.0)

            for msa in msas:
                if "FHFA" in self.collectors:
                    jobs.append(
                        CollectionJob(
                            parameter_name=param,
                            geographic_code=msa,
                            start_date=start_date,
                            end_date=end_date,
                            collector_name="FHFA",
                            database_info=self.PARAMETER_DB_MAPPING.get(
                                param,
                                {
                                    "db_name": "economic_data",
                                    "table_name": "property_growth",
                                },
                            ),
                            expected_range=expected_range,
                        )
                    )

        # Lending parameters (MSA-specific)
        lending_params = ["ltv_ratio", "closing_cost_pct", "lender_reserves"]
        for param in lending_params:
            param_def = parameters.get_parameter(param)
            expected_range = param_def.typical_range if param_def else (0.0, 1.0)

            for msa in msas:
                jobs.append(
                    CollectionJob(
                        parameter_name=param,
                        geographic_code=msa,
                        start_date=start_date,
                        end_date=end_date,
                        collector_name="Lending",
                        database_info=self.PARAMETER_DB_MAPPING[param],
                        expected_range=expected_range,
                    )
                )

        self.logger.info(f"Generated {len(jobs)} collection jobs")
        return jobs

    def execute_collection_job(self, job: CollectionJob) -> CollectionResult:
        """Execute a single data collection job."""

        collector = self.collectors.get(job.collector_name)
        if not collector:
            return CollectionResult(
                job=job,
                success=False,
                records_collected=0,
                error_message=f"Collector {job.collector_name} not available",
            )

        try:
            self.logger.info(
                f"Executing job: {job.parameter_name} for {job.geographic_code}"
            )

            # Collect data
            quality_metrics = collector.collect_and_validate(
                job.parameter_name,
                job.geographic_code,
                job.start_date,
                job.end_date,
                job.expected_range,
                job.database_info,
            )

            return CollectionResult(
                job=job,
                success=True,
                records_collected=quality_metrics.total_records,
                quality_metrics=quality_metrics,
            )

        except Exception as e:
            self.logger.error(
                f"Job failed: {job.parameter_name} for {job.geographic_code}: {e}"
            )
            return CollectionResult(
                job=job, success=False, records_collected=0, error_message=str(e)
            )

    def execute_collection_plan(
        self, jobs: List[CollectionJob], max_workers: int = 4
    ) -> List[CollectionResult]:
        """
        Execute multiple collection jobs in parallel.

        Args:
            jobs: List of collection jobs
            max_workers: Maximum number of parallel workers

        Returns:
            List of collection results
        """
        results = []

        self.logger.info(
            f"Executing {len(jobs)} collection jobs with {max_workers} workers"
        )

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all jobs
            future_to_job = {
                executor.submit(self.execute_collection_job, job): job for job in jobs
            }

            # Collect results as they complete
            for future in as_completed(future_to_job):
                try:
                    result = future.result()
                    results.append(result)

                    if result.success:
                        self.logger.info(
                            f"SUCCESS {result.job.parameter_name} ({result.job.geographic_code}): {result.records_collected} records"
                        )
                    else:
                        self.logger.error(
                            f"FAILED {result.job.parameter_name} ({result.job.geographic_code}): {result.error_message}"
                        )

                except Exception as e:
                    job = future_to_job[future]
                    self.logger.error(
                        f"Job execution failed: {job.parameter_name}: {e}"
                    )
                    results.append(
                        CollectionResult(
                            job=job,
                            success=False,
                            records_collected=0,
                            error_message=str(e),
                        )
                    )

        # Store results for analysis
        self.collection_history.extend(results)

        return results

    def replace_all_mock_data(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Complete workflow to replace all mock data with real market data.

        Args:
            start_date: Start date (default: 2010-01-01)
            end_date: End date (default: current year)

        Returns:
            Summary of collection results
        """
        if start_date is None:
            start_date = date(2010, 1, 1)
        if end_date is None:
            end_date = date(datetime.now().year, 1, 1)

        self.logger.info(
            f"Starting complete mock data replacement from {start_date} to {end_date}"
        )

        # Step 1: Backup existing databases
        try:
            backup_paths = db_manager.backup_databases()
            self.logger.info(f"Created database backups: {len(backup_paths)} files")
        except Exception as e:
            self.logger.warning(f"Failed to create backups: {e}")
            backup_paths = []

        # Step 2: Generate collection plan
        jobs = self.get_collection_plan(start_date, end_date)

        # Step 3: Execute collection
        results = self.execute_collection_plan(
            jobs, max_workers=3
        )  # Conservative parallelism

        # Step 4: Generate summary
        summary = self._generate_collection_summary(results, backup_paths)

        self.logger.info(
            f"Mock data replacement completed. Success rate: {summary['success_rate']:.1%}"
        )

        return summary

    def _generate_collection_summary(
        self, results: List[CollectionResult], backup_paths: List[str]
    ) -> Dict[str, Any]:
        """Generate summary of collection results."""

        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]

        total_records = sum(r.records_collected for r in successful)

        # Group by parameter
        parameter_summary = {}
        for result in results:
            param = result.job.parameter_name
            if param not in parameter_summary:
                parameter_summary[param] = {"success": 0, "failed": 0, "records": 0}

            if result.success:
                parameter_summary[param]["success"] += 1
                parameter_summary[param]["records"] += result.records_collected
            else:
                parameter_summary[param]["failed"] += 1

        return {
            "total_jobs": len(results),
            "successful_jobs": len(successful),
            "failed_jobs": len(failed),
            "success_rate": len(successful) / len(results) if results else 0,
            "total_records_collected": total_records,
            "parameter_summary": parameter_summary,
            "backup_files": backup_paths,
            "collection_timestamp": datetime.now(),
            "errors": [r.error_message for r in failed if r.error_message],
        }

    def get_data_status_report(self) -> Dict[str, Any]:
        """Generate a comprehensive data status report."""

        report = {
            "collectors_available": list(self.collectors.keys()),
            "total_collections": len(self.collection_history),
            "database_status": {},
            "parameter_coverage": {},
        }

        # Check database status
        for param, db_info in self.PARAMETER_DB_MAPPING.items():
            try:
                # Count records in database
                if param in [
                    "treasury_10y",
                    "fed_funds_rate",
                    "commercial_mortgage_rate",
                ]:
                    query = f"SELECT COUNT(*) as count FROM interest_rates WHERE parameter_name = '{param}'"
                    result = db_manager.query_data(db_info["db_name"], query)
                elif param == "cap_rate":
                    query = "SELECT COUNT(*) as count FROM cap_rates WHERE property_type = 'multifamily'"
                    result = db_manager.query_data(db_info["db_name"], query)
                else:
                    # Use the parameter mapping logic from database_manager
                    data_points = db_manager.get_parameter_data(
                        param, "35620"
                    )  # Sample MSA
                    result = [{"count": len(data_points)}]

                if result:
                    report["database_status"][param] = result[0]["count"]
                else:
                    report["database_status"][param] = 0

            except Exception as e:
                report["database_status"][param] = f"Error: {e}"

        return report


# Convenience functions
def create_orchestrator(fred_api_key: Optional[str] = None) -> DataOrchestrator:
    """Create a data orchestrator instance."""
    return DataOrchestrator(fred_api_key)


def replace_mock_data_quick_start(fred_api_key: Optional[str] = None) -> Dict[str, Any]:
    """Quick start function to replace all mock data."""
    orchestrator = create_orchestrator(fred_api_key)
    return orchestrator.replace_all_mock_data()


if __name__ == "__main__":
    # Demo usage
    print("=== DATA ORCHESTRATOR DEMO ===")

    # You'll need to provide your FRED API key
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        print("Please set FRED_API_KEY environment variable")
        exit(1)

    orchestrator = create_orchestrator(api_key)

    # Generate collection plan
    jobs = orchestrator.get_collection_plan(date(2020, 1, 1), date(2024, 1, 1))
    print(f"Generated {len(jobs)} collection jobs")

    # Execute a few jobs as test
    test_jobs = jobs[:5]  # First 5 jobs
    results = orchestrator.execute_collection_plan(test_jobs)

    # Show results
    for result in results:
        status = "✓" if result.success else "✗"
        print(
            f"{status} {result.job.parameter_name} ({result.job.geographic_code}): {result.records_collected} records"
        )
