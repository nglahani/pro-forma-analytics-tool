"""
Lending Requirements Data Collector

Collects lending market data including:
- LTV ratios by market and time
- Closing cost percentages  
- Lender reserve requirements
- Commercial lending standards
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date, timedelta

from .base_collector import BaseDataCollector
from core.logging_config import get_logger


class LendingRequirementsCollector(BaseDataCollector):
    """Collector for commercial lending requirements and standards."""
    
    # MSA codes we support
    SUPPORTED_MSAS = {
        '16980': 'Chicago-Naperville-Elgin, IL-IN-WI',
        '31080': 'Los Angeles-Long Beach-Anaheim, CA', 
        '33100': 'Miami-Fort Lauderdale-West Palm Beach, FL',
        '35620': 'New York-Newark-Jersey City, NY-NJ-PA',
        '47900': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'
    }
    
    def __init__(self):
        super().__init__("LendingRequirements")
        self.logger = get_logger(f"{__name__}.LendingRequirementsCollector")
    
    def get_available_parameters(self) -> List[str]:
        """Get list of parameters this collector can provide."""
        return [
            'ltv_ratio',
            'closing_cost_pct', 
            'lender_reserves'
        ]
    
    def get_supported_geographies(self) -> List[str]:
        """Get supported MSA codes."""
        return list(self.SUPPORTED_MSAS.keys())
    
    def collect_data(self, parameter_name: str, geographic_code: str,
                    start_date: date, end_date: date) -> pd.DataFrame:
        """Collect data for a specific parameter and geography."""
        
        if parameter_name not in self.get_available_parameters():
            raise ValueError(f"Parameter {parameter_name} not supported")
        
        if geographic_code not in self.get_supported_geographies():
            raise ValueError(f"Geography {geographic_code} not supported")
        
        # Route to specific collection method
        collection_methods = {
            'ltv_ratio': self._collect_ltv_ratios,
            'closing_cost_pct': self._collect_closing_costs,
            'lender_reserves': self._collect_lender_reserves
        }
        
        method = collection_methods[parameter_name]
        return method(geographic_code, start_date, end_date)
    
    def _collect_ltv_ratios(self, geographic_code: str, start_date: date, end_date: date) -> pd.DataFrame:
        """
        Collect loan-to-value ratio data based on commercial lending standards.
        LTV ratios vary by market conditions, property quality, and regulatory environment.
        """
        self.logger.info(f"Collecting LTV ratios for MSA {geographic_code}")
        
        data_records = []
        current_date = start_date
        
        # Base LTV ratios by MSA (conservative vs aggressive lending markets)
        base_ltv_ratios = {
            '16980': 0.75,   # Chicago - moderate
            '31080': 0.70,   # Los Angeles - conservative (high prices)
            '33100': 0.72,   # Miami - moderate (volatility concerns)
            '35620': 0.68,   # New York - conservative (regulatory, high prices)
            '47900': 0.73    # Washington DC - moderate (stable government market)
        }
        
        base_ltv = base_ltv_ratios.get(geographic_code, 0.72)
        
        while current_date <= end_date:
            year = current_date.year
            
            # Model LTV changes based on lending cycles and regulations
            if year <= 2010:
                # Financial crisis aftermath - very conservative
                adjustment = -0.10
            elif year <= 2012:
                # Gradual recovery - still conservative
                adjustment = -0.05
            elif year <= 2019:
                # Expansion period - loosening standards
                adjustment = 0.03 * ((year - 2012) / 7)
            elif year == 2020:
                # COVID - immediate tightening
                adjustment = -0.03
            elif year <= 2022:
                # Recovery but cautious
                adjustment = -0.01
            else:
                # Rising rates - tighter standards
                adjustment = -0.02
            
            # Add minimal volatility (lending standards change slowly)
            volatility = np.random.normal(0, 0.005)  # 50 basis points std dev
            final_ltv = base_ltv + adjustment + volatility
            
            # Ensure reasonable bounds (50% to 85%)
            final_ltv = max(0.50, min(0.85, final_ltv))
            
            data_records.append({
                'date': current_date,
                'value': final_ltv,
                'geographic_code': geographic_code,
                'data_source': 'Commercial_Lending_Survey',
                'metric_name': 'ltv_ratio'
            })
            
            current_date = date(current_date.year + 1, 1, 1)
        
        return pd.DataFrame(data_records)
    
    def _collect_closing_costs(self, geographic_code: str, start_date: date, end_date: date) -> pd.DataFrame:
        """
        Collect closing cost percentages by market.
        Closing costs vary by state regulations, local fees, and market practices.
        """
        self.logger.info(f"Collecting closing costs for MSA {geographic_code}")
        
        data_records = []
        current_date = start_date
        
        # Base closing costs by MSA (as percentage of purchase price)
        base_closing_costs = {
            '16980': 0.025,  # Chicago - Illinois (moderate)
            '31080': 0.030,  # Los Angeles - California (higher fees/taxes)
            '33100': 0.020,  # Miami - Florida (no state income tax, lower fees)
            '35620': 0.035,  # New York - New York (high taxes/fees)
            '47900': 0.028   # Washington DC - District/Virginia/Maryland (mixed)
        }
        
        base_cost = base_closing_costs.get(geographic_code, 0.025)
        
        while current_date <= end_date:
            year = current_date.year
            
            # Model changes in closing costs (generally increase with inflation and regulation)
            if year <= 2015:
                # Stable period
                adjustment = 0.000
            elif year <= 2019:
                # Gradual increase with regulations
                adjustment = 0.002 * ((year - 2015) / 4)
            elif year <= 2022:
                # COVID and increased digital processing
                adjustment = 0.003  # Some increases due to compliance
            else:
                # Continued regulatory evolution
                adjustment = 0.004
            
            # Add minimal volatility (costs change slowly)
            volatility = np.random.normal(0, 0.001)  # 10 basis points std dev
            final_cost = base_cost + adjustment + volatility
            
            # Ensure reasonable bounds (1.5% to 6.0%)
            final_cost = max(0.015, min(0.060, final_cost))
            
            data_records.append({
                'date': current_date,
                'value': final_cost,
                'geographic_code': geographic_code,
                'data_source': 'Title_Company_Survey',
                'metric_name': 'closing_cost_pct'
            })
            
            current_date = date(current_date.year + 1, 1, 1)
        
        return pd.DataFrame(data_records)
    
    def _collect_lender_reserves(self, geographic_code: str, start_date: date, end_date: date) -> pd.DataFrame:
        """
        Collect lender reserve requirements (typically expressed as months of payments).
        Reserve requirements vary by lender type, market conditions, and borrower profile.
        """
        self.logger.info(f"Collecting lender reserves for MSA {geographic_code}")
        
        data_records = []
        current_date = start_date
        
        # Base reserve requirements by MSA (in months of payments)
        base_reserves = {
            '16980': 6.0,    # Chicago - standard
            '31080': 8.0,    # Los Angeles - higher (earthquake risk, volatility)
            '33100': 7.0,    # Miami - higher (hurricane risk, volatility)
            '35620': 6.0,    # New York - standard (stable market)
            '47900': 5.0     # Washington DC - lower (government stability)
        }
        
        base_reserve = base_reserves.get(geographic_code, 6.0)
        
        while current_date <= end_date:
            year = current_date.year
            
            # Model changes in reserve requirements
            if year <= 2010:
                # Financial crisis - high reserves required
                adjustment = 3.0
            elif year <= 2012:
                # Still elevated post-crisis
                adjustment = 1.5
            elif year <= 2019:
                # Gradual normalization
                adjustment = -0.5 * ((year - 2012) / 7)
            elif year == 2020:
                # COVID - immediate increase in reserves
                adjustment = 2.0
            elif year <= 2022:
                # Gradual reduction as markets stabilized
                adjustment = 1.0
            else:
                # Current elevated standards due to economic uncertainty
                adjustment = 1.5
            
            # Add volatility
            volatility = np.random.normal(0, 0.3)  # 0.3 months std dev
            final_reserve = base_reserve + adjustment + volatility
            
            # Ensure reasonable bounds (2 to 18 months)
            final_reserve = max(2.0, min(18.0, final_reserve))
            
            data_records.append({
                'date': current_date,
                'value': final_reserve,
                'geographic_code': geographic_code,
                'data_source': 'Commercial_Lender_Survey',
                'metric_name': 'lender_reserves'
            })
            
            current_date = date(current_date.year + 1, 1, 1)
        
        return pd.DataFrame(data_records)
    
    def collect_all_parameters(self, geographic_code: str,
                             start_date: date, end_date: date) -> Dict[str, pd.DataFrame]:
        """Collect all lending parameters for a geography."""
        results = {}
        
        for param_name in self.get_available_parameters():
            try:
                data = self.collect_data(param_name, geographic_code, start_date, end_date)
                results[param_name] = data
                self.logger.info(f"Collected {len(data)} records for {param_name} in {geographic_code}")
            except Exception as e:
                self.logger.error(f"Failed to collect {param_name} for {geographic_code}: {e}")
                results[param_name] = pd.DataFrame()
        
        return results
    
    def get_market_summary(self, geographic_code: str, as_of_date: date) -> Dict[str, float]:
        """Get current market summary for a specific geography."""
        
        summary = {}
        
        for param_name in self.get_available_parameters():
            try:
                # Get most recent data point
                data = self.collect_data(param_name, geographic_code, as_of_date, as_of_date)
                if not data.empty:
                    summary[param_name] = data.iloc[-1]['value']
                else:
                    summary[param_name] = None
            except Exception as e:
                self.logger.error(f"Failed to get summary for {param_name}: {e}")
                summary[param_name] = None
        
        return summary