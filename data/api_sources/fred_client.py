"""
FRED API Client for Economic Data Collection

Handles communication with the Federal Reserve Economic Data (FRED) API
to collect interest rates, economic indicators, and other financial time series.
"""

import logging
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import requests

from config.parameters import ParameterType, parameters
from config.settings import settings


@dataclass
class FredSeries:
    """Represents a FRED data series."""

    series_id: str
    title: str
    frequency: str
    units: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class FredAPIClient:
    """Client for interacting with the FRED API."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.api.fred_api_key
        self.base_url = settings.api.fred_base_url
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)

        if not self.api_key:
            raise ValueError(
                "FRED API key is required. Set FRED_API_KEY environment variable."
            )

    def _make_request(self, endpoint: str, params: Dict[str, str]) -> Dict:
        """Make an API request with rate limiting and error handling."""

        # Add API key and format to parameters
        params.update({"api_key": self.api_key, "file_type": "json"})

        url = f"{self.base_url}/{endpoint}"

        try:
            # Rate limiting
            time.sleep(60 / settings.api.rate_limit_requests_per_minute)

            response = self.session.get(
                url, params=params, timeout=settings.api.timeout_seconds
            )
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            self.logger.error(f"FRED API request failed: {e}")
            raise

    def get_series_info(self, series_id: str) -> FredSeries:
        """Get information about a FRED series."""

        endpoint = "series"
        params = {"series_id": series_id}

        response = self._make_request(endpoint, params)

        if "seriess" in response and len(response["seriess"]) > 0:
            series_data = response["seriess"][0]
            return FredSeries(
                series_id=series_data["id"],
                title=series_data["title"],
                frequency=series_data["frequency"],
                units=series_data["units"],
                start_date=series_data.get("observation_start"),
                end_date=series_data.get("observation_end"),
            )
        else:
            raise ValueError(f"Series {series_id} not found")

    def get_series_data(
        self,
        series_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> pd.DataFrame:
        """
        Get historical data for a FRED series.

        Args:
            series_id: FRED series identifier
            start_date: Start date for data (default: 10 years ago)
            end_date: End date for data (default: today)

        Returns:
            DataFrame with date and value columns
        """

        # Set default date range if not provided
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=365 * 10)  # 10 years

        endpoint = "series/observations"
        params = {
            "series_id": series_id,
            "observation_start": start_date.strftime("%Y-%m-%d"),
            "observation_end": end_date.strftime("%Y-%m-%d"),
            "frequency": "a",  # Annual frequency
            "aggregation_method": "avg",  # Average for frequency conversion
        }

        response = self._make_request(endpoint, params)

        if "observations" in response:
            observations = response["observations"]

            # Convert to DataFrame
            data = []
            for obs in observations:
                try:
                    value = float(obs["value"])
                    data.append({"date": pd.to_datetime(obs["date"]), "value": value})
                except (ValueError, TypeError):
                    # Skip invalid values (often marked as '.')
                    continue

            if data:
                df = pd.DataFrame(data)
                df = df.set_index("date").sort_index()
                return df
            else:
                self.logger.warning(f"No valid data found for series {series_id}")
                return pd.DataFrame()
        else:
            raise ValueError(f"No observations found for series {series_id}")

    def get_multiple_series(
        self,
        series_ids: List[str],
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict[str, pd.DataFrame]:
        """Get data for multiple FRED series."""

        results = {}

        for series_id in series_ids:
            try:
                data = self.get_series_data(series_id, start_date, end_date)
                results[series_id] = data
                self.logger.info(f"Retrieved {len(data)} observations for {series_id}")
            except Exception as e:
                self.logger.error(f"Failed to retrieve {series_id}: {e}")
                results[series_id] = pd.DataFrame()

        return results

    def search_series(self, search_text: str, limit: int = 10) -> List[FredSeries]:
        """Search for FRED series by keyword."""

        endpoint = "series/search"
        params = {
            "search_text": search_text,
            "limit": str(limit),
            "order_by": "popularity",
            "sort_order": "desc",
        }

        response = self._make_request(endpoint, params)

        results = []
        if "seriess" in response:
            for series_data in response["seriess"]:
                results.append(
                    FredSeries(
                        series_id=series_data["id"],
                        title=series_data["title"],
                        frequency=series_data["frequency"],
                        units=series_data["units"],
                        start_date=series_data.get("observation_start"),
                        end_date=series_data.get("observation_end"),
                    )
                )

        return results

    def get_interest_rate_data(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> Dict[str, pd.DataFrame]:
        """Get common interest rate series for real estate analysis."""

        # Key interest rate series for real estate
        interest_rate_series = {
            "treasury_10y": "GS10",  # 10-Year Treasury Constant Maturity Rate
            "treasury_5y": "GS5",  # 5-Year Treasury
            "treasury_2y": "GS2",  # 2-Year Treasury
            "mortgage_30y": "MORTGAGE30US",  # 30-Year Fixed Rate Mortgage Average
            "commercial_paper": "DCPN3M",  # 3-Month Commercial Paper Rate
            "fed_funds_rate": "FEDFUNDS",  # Federal Funds Rate
        }

        return self.get_multiple_series(
            list(interest_rate_series.values()), start_date, end_date
        )

    def get_economic_indicators(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> Dict[str, pd.DataFrame]:
        """Get economic indicators relevant to real estate."""

        economic_series = {
            "cpi_all": "CPIAUCSL",  # Consumer Price Index
            "cpi_housing": "CUUR0000SAH1",  # CPI Housing
            "unemployment": "UNRATE",  # Unemployment Rate
            "gdp_growth": "A191RL1A225NBEA",  # Real GDP Growth Rate
            "house_price_index": "HPIPONM226S",  # House Price Index
        }

        return self.get_multiple_series(
            list(economic_series.values()), start_date, end_date
        )


class FredDataCollector:
    """Orchestrates data collection from FRED for pro forma parameters."""

    def __init__(self, api_key: Optional[str] = None):
        self.client = FredAPIClient(api_key)
        self.logger = logging.getLogger(__name__)

    def collect_parameter_data(
        self,
        parameter_names: Optional[List[str]] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict[str, pd.DataFrame]:
        """
        Collect data for specific pro forma parameters.

        Args:
            parameter_names: List of parameter names to collect (default: all FRED parameters)
            start_date: Start date for data collection
            end_date: End date for data collection

        Returns:
            Dictionary mapping parameter names to DataFrames
        """

        if parameter_names is None:
            # Get all parameters that have FRED series
            fred_params = parameters.get_fred_parameters()
            parameter_names = [param.name for param in fred_params]

        results = {}

        for param_name in parameter_names:
            param_def = parameters.get_parameter(param_name)

            if param_def and param_def.fred_series:
                try:
                    data = self.client.get_series_data(
                        param_def.fred_series, start_date, end_date
                    )

                    if not data.empty:
                        # Add metadata
                        data["parameter_name"] = param_name
                        data["data_source"] = "FRED"
                        data["series_code"] = param_def.fred_series
                        data["geographic_code"] = "NATIONAL"
                        data["geographic_level"] = param_def.geographic_level

                        results[param_name] = data
                        self.logger.info(
                            f"Collected {len(data)} data points for {param_name}"
                        )

                except Exception as e:
                    self.logger.error(f"Failed to collect data for {param_name}: {e}")

        return results

    def validate_data_quality(
        self, data: pd.DataFrame, parameter_name: str
    ) -> Dict[str, Any]:
        """Validate data quality for a parameter."""

        param_def = parameters.get_parameter(parameter_name)

        quality_metrics = {
            "total_points": len(data),
            "missing_values": data["value"].isna().sum(),
            "completeness_pct": (1 - data["value"].isna().sum() / len(data)) * 100,
            "value_range": (data["value"].min(), data["value"].max()),
            "within_expected_range": True,
            "issues": [],
        }

        # Check if values are within expected range
        if param_def:
            min_val, max_val = param_def.typical_range
            out_of_range = ((data["value"] < min_val) | (data["value"] > max_val)).sum()

            if out_of_range > 0:
                quality_metrics["within_expected_range"] = False
                quality_metrics["issues"].append(
                    f"{out_of_range} values outside expected range [{min_val}, {max_val}]"
                )

        # Check for gaps in time series
        if len(data) > 1:
            data_sorted = data.sort_index()
            date_diff = data_sorted.index.to_series().diff()
            expected_freq = pd.DateOffset(years=1)  # Annual data

            large_gaps = (date_diff > expected_freq * 1.5).sum()
            if large_gaps > 0:
                quality_metrics["issues"].append(
                    f"{large_gaps} gaps larger than expected in time series"
                )

        return quality_metrics


# Convenience function for easy access
def get_fred_client(api_key: Optional[str] = None) -> FredAPIClient:
    """Get a FRED API client instance."""
    return FredAPIClient(api_key)
