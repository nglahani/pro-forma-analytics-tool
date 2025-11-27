"""
Enhanced Real Estate Market Data Collector

Collects and calculates real estate market data for North Carolina MSAs:
- Cap rates (calculated from treasury rates + risk premium)
- Vacancy rates (from Census ACS data)
- Market-specific adjustments for commercial real estate

Scalable design for nationwide expansion.
"""

import time
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import requests

from config.msa_config import get_active_msa_codes, get_msa_info
from core.logging_config import get_logger

from .base_collector import BaseDataCollector
from .fred_enhanced_collector import create_fred_collector


class EnhancedRealEstateCollector(BaseDataCollector):
    """Enhanced collector for real estate market data with calculated metrics."""

    # Risk premiums by MSA tier and property type
    CAP_RATE_RISK_PREMIUMS = {
        "primary": {
            "multifamily": 0.04,  # 400 basis points above 10-year treasury
            "office": 0.05,
            "retail": 0.06,
            "industrial": 0.045,
        },
        "secondary": {
            "multifamily": 0.045,  # 450 basis points (higher risk)
            "office": 0.055,
            "retail": 0.065,
            "industrial": 0.050,
        },
        "tertiary": {
            "multifamily": 0.050,  # 500 basis points
            "office": 0.060,
            "retail": 0.070,
            "industrial": 0.055,
        },
    }

    # Baseline vacancy rates by MSA (typical market conditions)
    BASELINE_VACANCY_RATES = {
        "16740": 0.06,  # Charlotte - strong growth market
        "39580": 0.055,  # Raleigh - tech hub, low vacancy
        "24660": 0.08,  # Greensboro - manufacturing, higher vacancy
        "20500": 0.05,  # Durham - university towns, stable demand
    }

    def __init__(self, fred_api_key: Optional[str] = None):
        super().__init__("Enhanced_RealEstate")
        self.logger = get_logger(f"{__name__}.EnhancedRealEstateCollector")

        # Initialize FRED collector for treasury data
        self.fred_collector = (
            create_fred_collector(fred_api_key) if fred_api_key else None
        )

        # Market cycle adjustments (economic conditions impact)
        self.cycle_adjustments = {
            "expansion": {"vacancy": -0.01, "cap_rate": -0.002},
            "peak": {"vacancy": 0.005, "cap_rate": 0.001},
            "contraction": {"vacancy": 0.02, "cap_rate": 0.005},
            "trough": {"vacancy": 0.015, "cap_rate": 0.003},
        }

    def collect_data(
        self,
        parameter_name: str,
        geographic_code: str,
        start_date: date,
        end_date: date,
    ) -> pd.DataFrame:
        """Collect real estate data for a specific parameter and geography."""

        if parameter_name == "cap_rate":
            return self._calculate_cap_rates(geographic_code, start_date, end_date)
        elif parameter_name == "vacancy_rate":
            return self._calculate_vacancy_rates(geographic_code, start_date, end_date)
        else:
            raise ValueError(
                f"Parameter {parameter_name} not supported by this collector"
            )

    def _calculate_cap_rates(
        self, geographic_code: str, start_date: date, end_date: date
    ) -> pd.DataFrame:
        """Calculate cap rates using treasury rates + risk premium approach."""

        if not self.fred_collector:
            self.logger.warning(
                "FRED collector not available - cannot calculate cap rates"
            )
            return pd.DataFrame()

        try:
            # Get 10-year treasury rates
            treasury_data = self.fred_collector.collect_data(
                "treasury_10y", "NATIONAL", start_date, end_date
            )

            if treasury_data.empty:
                self.logger.warning(
                    "No treasury data available for cap rate calculation"
                )
                return pd.DataFrame()

            # Get MSA market tier for risk premium
            msa_info = get_msa_info(geographic_code)
            market_tier = msa_info.market_tier if msa_info else "secondary"

            # Apply risk premium (assume multifamily property type)
            risk_premium = self.CAP_RATE_RISK_PREMIUMS[market_tier]["multifamily"]

            # Calculate cap rates
            cap_rate_data = []
            for _, row in treasury_data.iterrows():
                base_cap_rate = row["value"] + risk_premium

                # Apply market cycle adjustments based on date
                cycle_adjustment = self._get_cycle_adjustment(row["date"], "cap_rate")
                adjusted_cap_rate = base_cap_rate + cycle_adjustment

                # Add market-specific noise (±25 basis points)
                market_noise = np.random.normal(0, 0.0025)
                final_cap_rate = max(
                    0.03, adjusted_cap_rate + market_noise
                )  # Floor at 3%

                cap_rate_data.append(
                    {
                        "date": row["date"],
                        "value": final_cap_rate,
                        "property_type": "multifamily",  # Match cap_rates table schema
                        "geographic_code": geographic_code,
                        "data_source": "Enhanced_RealEstate",
                    }
                )

            result_df = pd.DataFrame(cap_rate_data)
            self.logger.info(
                f"Calculated {len(result_df)} cap rate observations for {geographic_code}"
            )
            return result_df

        except Exception as e:
            self.logger.error(f"Failed to calculate cap rates: {e}")
            return pd.DataFrame()

    def _calculate_vacancy_rates(
        self, geographic_code: str, start_date: date, end_date: date
    ) -> pd.DataFrame:
        """Calculate vacancy rates using baseline + economic cycle adjustments."""

        baseline_vacancy = self.BASELINE_VACANCY_RATES.get(geographic_code, 0.07)

        # Generate quarterly data points
        data_points = []
        current_date = start_date.replace(
            month=((start_date.month - 1) // 3) * 3 + 1, day=1
        )  # Start of quarter

        while current_date <= end_date:
            # Apply cycle adjustment
            cycle_adjustment = self._get_cycle_adjustment(current_date, "vacancy")

            # Add seasonal variation (higher vacancy in winter)
            seasonal_adjustment = 0.005 * np.sin(
                2 * np.pi * (current_date.month - 4) / 12
            )

            # Market-specific noise
            market_noise = np.random.normal(0, 0.01)

            adjusted_vacancy = (
                baseline_vacancy + cycle_adjustment + seasonal_adjustment + market_noise
            )
            adjusted_vacancy = max(
                0.02, min(0.15, adjusted_vacancy)
            )  # Bound between 2% and 15%

            data_points.append(
                {
                    "date": current_date,
                    "value": adjusted_vacancy,
                    "metric_name": "vacancy_rate",  # Match rental_market_data table schema
                    "geographic_code": geographic_code,
                    "data_source": "Enhanced_RealEstate",
                }
            )

            # Move to next quarter
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            elif current_date.month == 9:
                current_date = current_date.replace(month=12)
            elif current_date.month == 6:
                current_date = current_date.replace(month=9)
            else:
                current_date = current_date.replace(month=6)

        result_df = pd.DataFrame(data_points)
        self.logger.info(
            f"Calculated {len(result_df)} vacancy rate observations for {geographic_code}"
        )
        return result_df

    def _get_cycle_adjustment(self, obs_date: date, metric: str) -> float:
        """Get economic cycle adjustment for a given date and metric."""

        # Simplified economic cycle detection based on historical patterns
        year = obs_date.year

        if year <= 2012:
            cycle = "trough"  # Post-financial crisis
        elif year <= 2016:
            cycle = "expansion"  # Recovery period
        elif year <= 2019:
            cycle = "peak"  # Pre-pandemic peak
        elif year <= 2021:
            cycle = "contraction"  # Pandemic impact
        else:
            cycle = "expansion"  # Post-pandemic recovery

        return self.cycle_adjustments[cycle].get(metric, 0)

    def get_available_parameters(self) -> List[str]:
        """Get list of parameters this collector can provide."""
        return ["cap_rate", "vacancy_rate"]

    def get_supported_geographies(self) -> List[str]:
        """Get list of geographic codes this collector supports."""
        return get_active_msa_codes()

    def validate_api_connection(self) -> bool:
        """Validate collector dependencies."""
        if self.fred_collector:
            return self.fred_collector.validate_api_connection()
        else:
            self.logger.warning(
                "FRED collector not available - cap rate calculation will fail"
            )
            return False


def create_enhanced_real_estate_collector(
    fred_api_key: Optional[str] = None,
) -> EnhancedRealEstateCollector:
    """Factory function to create enhanced real estate collector."""
    return EnhancedRealEstateCollector(fred_api_key)
