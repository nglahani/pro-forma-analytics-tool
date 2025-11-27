"""
Enhanced FRED Data Collector

Improved version of FRED client with production-grade features:
- Comprehensive parameter coverage
- Better error handling and retry logic
- Data quality validation
- Automated database integration
"""

import time
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config.parameters import parameters
from core.logging_config import get_logger

from .base_collector import BaseDataCollector


class FredEnhancedCollector(BaseDataCollector):
    """Enhanced FRED API collector with production features."""

    # FRED series mapping for all our parameters
    FRED_SERIES_MAP = {
        # Interest rates (national)
        "treasury_10y": "GS10",  # 10-Year Treasury Constant Maturity Rate
        "treasury_5y": "GS5",  # 5-Year Treasury
        "treasury_2y": "GS2",  # 2-Year Treasury
        "fed_funds_rate": "FEDFUNDS",  # Federal Funds Rate
        "commercial_mortgage_rate": "MORTGAGE30US",  # Proxy using 30-year mortgage
        # Economic indicators (national)
        "cpi_housing": "CUUR0000SAH1",  # CPI Housing
        "cpi_all": "CPIAUCSL",  # Consumer Price Index - All Items
        "unemployment_rate": "UNRATE",  # Unemployment Rate
        "gdp_growth": "A191RL1A225NBEA",  # Real GDP Growth Rate
        # Property-related (national proxies)
        "house_price_index": "HPIPONM226S",  # House Price Index
        "housing_starts": "HOUST",  # Housing Starts
        "construction_costs": "WPUSI012011",  # PPI Construction Materials
    }

    def __init__(self, api_key: str):
        super().__init__("FRED_Enhanced")
        self.api_key = api_key
        self.base_url = "https://api.stlouisfed.org/fred"

        # Setup session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        self.logger = get_logger(f"{__name__}.FredEnhancedCollector")

        if not self.api_key:
            raise ValueError("FRED API key is required")

    def get_available_parameters(self) -> List[str]:
        """Get list of parameters this collector can provide."""
        return list(self.FRED_SERIES_MAP.keys())

    def get_supported_geographies(self) -> List[str]:
        """FRED provides national data only."""
        return ["NATIONAL"]

    def _make_request(self, endpoint: str, params: Dict[str, str]) -> Dict:
        """Make FRED API request with rate limiting and error handling."""

        # Add API key and format
        params.update({"api_key": self.api_key, "file_type": "json"})

        url = f"{self.base_url}/{endpoint}"

        try:
            # Rate limiting: FRED allows 120 requests per minute
            time.sleep(0.5)  # 2 requests per second = 120/minute

            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Check for FRED API errors
            if "error_code" in data:
                raise ValueError(
                    f"FRED API error {data['error_code']}: {data.get('error_message', 'Unknown error')}"
                )

            return data

        except requests.exceptions.RequestException as e:
            self.logger.error(f"FRED API request failed: {e}")
            raise

    def collect_data(
        self,
        parameter_name: str,
        geographic_code: str,
        start_date: date,
        end_date: date,
    ) -> pd.DataFrame:
        """Collect data from FRED for a specific parameter."""

        if parameter_name not in self.FRED_SERIES_MAP:
            raise ValueError(f"Parameter {parameter_name} not available from FRED")

        if geographic_code != "NATIONAL":
            raise ValueError(f"FRED only provides national data, not {geographic_code}")

        series_id = self.FRED_SERIES_MAP[parameter_name]

        # Get series observations with extended historical range
        endpoint = "series/observations"
        params = {
            "series_id": series_id,
            "observation_start": start_date.strftime("%Y-%m-%d"),
            "observation_end": end_date.strftime("%Y-%m-%d"),
            "frequency": "q",  # Quarterly frequency for better granularity
            "aggregation_method": "avg",  # Average for frequency conversion
        }

        response = self._make_request(endpoint, params)

        if "observations" not in response:
            self.logger.warning(f"No observations found for {series_id}")
            return pd.DataFrame()

        # Process observations
        data_records = []
        for obs in response["observations"]:
            try:
                # FRED uses '.' for missing values
                if obs["value"] == ".":
                    continue

                value = float(obs["value"])
                obs_date = pd.to_datetime(obs["date"]).date()

                # Convert percentage values to decimals if needed
                if parameter_name in [
                    "treasury_10y",
                    "fed_funds_rate",
                    "commercial_mortgage_rate",
                    "unemployment_rate",
                    "gdp_growth",
                ]:
                    value = value / 100.0  # Convert from percentage to decimal

                data_records.append(
                    {
                        "date": obs_date,
                        "value": value,
                        "parameter_name": parameter_name,
                        "geographic_code": geographic_code,
                        "data_source": "FRED",
                    }
                )

            except (ValueError, TypeError) as e:
                self.logger.warning(f"Skipping invalid observation: {obs}, error: {e}")
                continue

        if not data_records:
            self.logger.warning(f"No valid data found for {parameter_name}")
            return pd.DataFrame()

        df = pd.DataFrame(data_records)
        self.logger.info(
            f"Collected {len(df)} observations for {parameter_name} from {start_date} to {end_date}"
        )

        return df

    def get_series_metadata(self, series_id: str) -> Dict:
        """Get metadata for a FRED series."""
        endpoint = "series"
        params = {"series_id": series_id}

        response = self._make_request(endpoint, params)

        if "seriess" in response and len(response["seriess"]) > 0:
            return response["seriess"][0]
        else:
            raise ValueError(f"Series {series_id} not found")

    def collect_multiple_parameters(
        self, parameter_names: List[str], start_date: date, end_date: date
    ) -> Dict[str, pd.DataFrame]:
        """Collect data for multiple parameters efficiently."""
        results = {}

        for param_name in parameter_names:
            if param_name not in self.FRED_SERIES_MAP:
                self.logger.warning(f"Parameter {param_name} not available from FRED")
                continue

            try:
                data = self.collect_data(param_name, "NATIONAL", start_date, end_date)
                results[param_name] = data

                # Log success
                self.logger.info(
                    f"Successfully collected {len(data)} records for {param_name}"
                )

            except Exception as e:
                self.logger.error(f"Failed to collect {param_name}: {e}")
                results[param_name] = pd.DataFrame()

        return results

    def validate_api_connection(self) -> bool:
        """Test API connection and key validity."""
        try:
            # Try to get a simple series
            endpoint = "series"
            params = {"series_id": "GDP"}

            response = self._make_request(endpoint, params)

            if "seriess" in response:
                self.logger.info("FRED API connection validated successfully")
                return True
            else:
                self.logger.error("FRED API connection validation failed")
                return False

        except Exception as e:
            self.logger.error(f"FRED API connection validation failed: {e}")
            return False

    def get_data_coverage_report(self) -> Dict[str, Dict]:
        """Generate a report on data coverage for all supported parameters."""
        report = {}

        for param_name in self.get_available_parameters():
            try:
                series_id = self.FRED_SERIES_MAP[param_name]
                metadata = self.get_series_metadata(series_id)

                report[param_name] = {
                    "series_id": series_id,
                    "title": metadata.get("title"),
                    "units": metadata.get("units"),
                    "frequency": metadata.get("frequency"),
                    "observation_start": metadata.get("observation_start"),
                    "observation_end": metadata.get("observation_end"),
                    "last_updated": metadata.get("last_updated"),
                }

            except Exception as e:
                report[param_name] = {"error": str(e)}

        return report


def create_fred_collector(api_key: Optional[str] = None) -> FredEnhancedCollector:
    """Factory function to create FRED collector."""
    if not api_key:
        # Try to get from environment or settings
        import os

        api_key = os.getenv("FRED_API_KEY")

        if not api_key:
            try:
                from config.settings import settings

                api_key = settings.api.fred_api_key
            except:
                pass

    if not api_key:
        raise ValueError(
            "FRED API key must be provided or set in environment variable FRED_API_KEY"
        )

    return FredEnhancedCollector(api_key)
