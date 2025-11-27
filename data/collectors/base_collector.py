"""
Base Data Collector

Abstract base class for all data collectors with common functionality
for validation, error handling, and database integration.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from core.exceptions import ValidationError
from data.databases.database_manager import db_manager


@dataclass
class DataQualityMetrics:
    """Data quality assessment metrics."""

    total_records: int
    missing_values: int
    completeness_pct: float
    date_range: Tuple[date, date]
    outliers_detected: int
    data_source: str
    collection_timestamp: datetime
    validation_errors: List[str]


class BaseDataCollector(ABC):
    """Base class for all data collectors."""

    def __init__(self, source_name: str):
        self.source_name = source_name
        self.logger = logging.getLogger(f"{__name__}.{source_name}")
        self.collection_stats = {}

    @abstractmethod
    def collect_data(
        self,
        parameter_name: str,
        geographic_code: str,
        start_date: date,
        end_date: date,
    ) -> pd.DataFrame:
        """
        Collect data for a specific parameter and geography.

        Returns:
            DataFrame with columns: date, value, parameter_name, geographic_code, data_source
        """
        pass

    @abstractmethod
    def get_available_parameters(self) -> List[str]:
        """Get list of parameters this collector can provide."""
        pass

    @abstractmethod
    def get_supported_geographies(self) -> List[str]:
        """Get list of geographic codes this collector supports."""
        pass

    def validate_data(
        self, data: pd.DataFrame, expected_range: Tuple[float, float]
    ) -> DataQualityMetrics:
        """Validate collected data quality."""

        if data.empty:
            return DataQualityMetrics(
                total_records=0,
                missing_values=0,
                completeness_pct=0.0,
                date_range=(date.min, date.min),
                outliers_detected=0,
                data_source=self.source_name,
                collection_timestamp=datetime.now(),
                validation_errors=["No data collected"],
            )

        # Basic metrics
        total_records = len(data)
        missing_values = data["value"].isna().sum()
        completeness_pct = ((total_records - missing_values) / total_records) * 100

        # Date range
        dates = pd.to_datetime(data["date"])
        date_range = (dates.min().date(), dates.max().date())

        # Outlier detection (values outside expected range)
        valid_data = data["value"].dropna()
        if len(valid_data) > 0:
            outliers = (
                (valid_data < expected_range[0]) | (valid_data > expected_range[1])
            ).sum()
        else:
            outliers = 0

        # Validation errors
        errors = []
        if completeness_pct < 80:
            errors.append(f"Low completeness: {completeness_pct:.1f}%")
        if outliers > total_records * 0.1:
            errors.append(f"High outlier rate: {outliers}/{total_records}")

        return DataQualityMetrics(
            total_records=total_records,
            missing_values=missing_values,
            completeness_pct=completeness_pct,
            date_range=date_range,
            outliers_detected=outliers,
            data_source=self.source_name,
            collection_timestamp=datetime.now(),
            validation_errors=errors,
        )

    def save_to_database(self, data: pd.DataFrame, table_info: Dict[str, str]) -> int:
        """
        Save collected data to appropriate database table.

        Args:
            data: DataFrame with collected data
            table_info: {'db_name': str, 'table_name': str}

        Returns:
            Number of records saved
        """
        if data.empty:
            self.logger.warning("No data to save")
            return 0

        try:
            # Convert DataFrame to list of dictionaries
            records = data.to_dict("records")

            # Convert datetime objects to ISO strings
            for record in records:
                if isinstance(record.get("date"), (pd.Timestamp, datetime)):
                    record["date"] = record["date"].strftime("%Y-%m-%d")

            # Save to database
            count = db_manager.insert_data(
                table_info["db_name"], table_info["table_name"], records
            )

            self.logger.info(
                f"Saved {count} records to {table_info['db_name']}.{table_info['table_name']}"
            )
            return count

        except Exception as e:
            self.logger.error(f"Failed to save data: {e}")
            raise

    def collect_and_validate(
        self,
        parameter_name: str,
        geographic_code: str,
        start_date: date,
        end_date: date,
        expected_range: Tuple[float, float],
        table_info: Dict[str, str],
    ) -> DataQualityMetrics:
        """
        Complete workflow: collect, validate, and save data.
        """
        try:
            # Collect data
            self.logger.info(f"Collecting {parameter_name} for {geographic_code}")
            data = self.collect_data(
                parameter_name, geographic_code, start_date, end_date
            )

            # Validate data quality
            metrics = self.validate_data(data, expected_range)

            # Save if quality is acceptable
            if not metrics.validation_errors:
                records_saved = self.save_to_database(data, table_info)
                self.logger.info(
                    f"Successfully processed {parameter_name}: {records_saved} records"
                )
            else:
                self.logger.warning(
                    f"Data quality issues for {parameter_name}: {metrics.validation_errors}"
                )

            # Update collection stats
            self.collection_stats[f"{parameter_name}_{geographic_code}"] = {
                "timestamp": datetime.now(),
                "records_collected": metrics.total_records,
                "quality_score": metrics.completeness_pct,
                "errors": metrics.validation_errors,
            }

            return metrics

        except Exception as e:
            self.logger.error(f"Collection failed for {parameter_name}: {e}")
            raise


class CollectorRegistry:
    """Registry for managing multiple data collectors."""

    def __init__(self):
        self.collectors: Dict[str, BaseDataCollector] = {}
        self.logger = logging.getLogger(__name__)

    def register_collector(self, collector: BaseDataCollector):
        """Register a data collector."""
        self.collectors[collector.source_name] = collector
        self.logger.info(f"Registered collector: {collector.source_name}")

    def get_collector(self, source_name: str) -> Optional[BaseDataCollector]:
        """Get collector by source name."""
        return self.collectors.get(source_name)

    def get_collectors_for_parameter(
        self, parameter_name: str
    ) -> List[BaseDataCollector]:
        """Get all collectors that can provide a specific parameter."""
        capable_collectors = []
        for collector in self.collectors.values():
            if parameter_name in collector.get_available_parameters():
                capable_collectors.append(collector)
        return capable_collectors

    def collect_all_sources(
        self,
        parameter_name: str,
        geographic_code: str,
        start_date: date,
        end_date: date,
    ) -> Dict[str, DataQualityMetrics]:
        """Collect data from all available sources for comparison."""
        results = {}

        collectors = self.get_collectors_for_parameter(parameter_name)
        if not collectors:
            self.logger.warning(f"No collectors available for {parameter_name}")
            return results

        for collector in collectors:
            try:
                # We'll need to define expected_range and table_info per parameter
                # For now, use defaults
                expected_range = (0.0, 1.0)  # Will be parameterized
                table_info = {"db_name": "market_data", "table_name": "interest_rates"}

                metrics = collector.collect_and_validate(
                    parameter_name,
                    geographic_code,
                    start_date,
                    end_date,
                    expected_range,
                    table_info,
                )
                results[collector.source_name] = metrics

            except Exception as e:
                self.logger.error(f"Collection failed for {collector.source_name}: {e}")

        return results


# Global registry instance
collector_registry = CollectorRegistry()
