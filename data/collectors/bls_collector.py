"""
Bureau of Labor Statistics (BLS) Data Collector

Collects regional economic data including:
- Consumer Price Index (CPI) for housing costs
- Regional price variations by MSA
- Expense growth proxies

Uses BLS Public API (no key required, rate limited to 25 requests/day for unregistered users)
"""

import pandas as pd
import requests
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date, timedelta
import json

from .base_collector import BaseDataCollector
from config.msa_config import get_active_msa_codes, get_msa_info
from core.logging_config import get_logger


class BLSDataCollector(BaseDataCollector):
    """BLS API collector for regional economic data."""
    
    # BLS Series mapping for housing-related CPI data
    BLS_SERIES_MAP = {
        # National housing CPI (available for all regions)
        'expense_growth': {
            'national': 'CUUR0000SAH1',  # CPI Housing - All Urban Consumers
            'description': 'Consumer Price Index - Housing'
        },
        'rent_growth': {
            'national': 'CUUR0000SEHA',  # CPI Rent of Primary Residence
            'description': 'Consumer Price Index - Rent of Primary Residence'
        },
        
        # Regional CPI series (major metros only)
        'regional_cpi': {
            # Southeast region codes
            '16740': 'CURS49CSAH1',    # Charlotte CPI Housing (if available)
            '39580': 'CURS49ASAH1',    # Raleigh area (Southeast urban)
            'southeast': 'CURS49CSAH1', # Southeast Urban CPI Housing
            'description': 'Regional CPI Housing by Metro Area'
        }
    }
    
    # BLS area codes for North Carolina MSAs (when available)
    MSA_TO_BLS_AREA = {
        '16740': 'S49C',  # Charlotte (Southeast region proxy)
        '39580': 'S49A',  # Raleigh (Southeast region proxy) 
        '24660': 'S49C',  # Greensboro (use Charlotte proxy)
        '20500': 'S49A',  # Durham (use Raleigh proxy)
    }
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("BLS_Economic")
        self.api_key = api_key  # Optional - public API allows 25 requests/day without key
        self.base_url = "https://api.bls.gov/publicAPI/v2/timeseries/data"
        self.session = requests.Session()
        
        # Rate limiting for public API
        self.request_delay = 1.0  # 1 second between requests
        self.last_request_time = 0
        
    def _make_request(self, series_ids: List[str], start_year: int, end_year: int) -> Dict:
        """Make rate-limited request to BLS API."""
        
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.request_delay:
            time.sleep(self.request_delay - time_since_last)
        
        # Prepare request data
        data = {
            'seriesid': series_ids,
            'startyear': str(start_year),
            'endyear': str(end_year),
            'registrationkey': self.api_key if self.api_key else None
        }
        
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}
        
        try:
            response = self.session.post(
                self.base_url,
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            response.raise_for_status()
            
            self.last_request_time = time.time()
            result = response.json()
            
            # Check for BLS API errors
            if result.get('status') != 'REQUEST_SUCCEEDED':
                error_msg = result.get('message', [])
                raise ValueError(f"BLS API error: {error_msg}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"BLS API request failed: {e}")
            raise
    
    def collect_data(self, parameter_name: str, geographic_code: str,
                    start_date: date, end_date: date) -> pd.DataFrame:
        """Collect BLS data for a specific parameter and geography."""
        
        if parameter_name not in ['expense_growth', 'rent_growth']:
            raise ValueError(f"Parameter {parameter_name} not available from BLS")
        
        # Determine appropriate series ID
        series_id = self._get_series_id(parameter_name, geographic_code)
        if not series_id:
            self.logger.warning(f"No BLS series available for {parameter_name} in {geographic_code}")
            return pd.DataFrame()
        
        # BLS API works with years
        start_year = start_date.year
        end_year = end_date.year
        
        # BLS limits to 20 years per request for unregistered users
        if not self.api_key and (end_year - start_year) > 19:
            start_year = end_year - 19
            self.logger.warning(f"Limited to {start_year}-{end_year} for unregistered BLS API")
        
        response = self._make_request([series_id], start_year, end_year)
        
        if not response.get('Results', {}).get('series'):
            self.logger.warning(f"No data returned for {series_id}")
            return pd.DataFrame()
        
        # Process BLS response
        series_data = response['Results']['series'][0]
        data_records = []
        
        for item in series_data.get('data', []):
            try:
                # BLS returns data as: {'year': '2023', 'period': 'Q01', 'value': '100.5'}
                year = int(item['year'])
                period = item['period']
                value = float(item['value'])
                
                # Convert period to date
                if period.startswith('Q'):
                    quarter = int(period[2:])
                    month = (quarter - 1) * 3 + 1
                    obs_date = date(year, month, 1)
                elif period.startswith('M'):
                    month = int(period[1:])
                    obs_date = date(year, month, 1)
                else:
                    # Annual data
                    obs_date = date(year, 1, 1)
                
                # Convert CPI to growth rate (year-over-year change)
                # Note: This requires calculating growth rates from index values
                data_records.append({
                    'date': obs_date,
                    'value': value,  # CPI index value
                    'parameter_name': parameter_name,
                    'geographic_code': geographic_code,
                    'data_source': 'BLS'
                })
                
            except (ValueError, KeyError) as e:
                self.logger.warning(f"Skipping invalid BLS observation: {item}, error: {e}")
                continue
        
        if not data_records:
            self.logger.warning(f"No valid data found for {parameter_name}")
            return pd.DataFrame()
        
        df = pd.DataFrame(data_records)
        
        # Convert CPI index values to growth rates
        df = self._calculate_growth_rates(df)
        
        # Filter to requested date range
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        
        self.logger.info(f"Collected {len(df)} observations for {parameter_name} from BLS")
        return df
    
    def _get_series_id(self, parameter_name: str, geographic_code: str) -> Optional[str]:
        """Get appropriate BLS series ID for parameter and geography."""
        
        if geographic_code == 'NATIONAL':
            return self.BLS_SERIES_MAP[parameter_name]['national']
        
        # For regional data, try MSA-specific first, then regional proxy
        msa_info = get_msa_info(geographic_code)
        if not msa_info:
            return self.BLS_SERIES_MAP[parameter_name]['national']
        
        # Check if we have MSA-specific data
        regional_series = self.BLS_SERIES_MAP.get('regional_cpi', {})
        if geographic_code in regional_series:
            return regional_series[geographic_code]
        
        # Fall back to regional proxy
        if 'NC' in msa_info.state:
            return regional_series.get('southeast', self.BLS_SERIES_MAP[parameter_name]['national'])
        
        # Default to national
        return self.BLS_SERIES_MAP[parameter_name]['national']
    
    def _calculate_growth_rates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert CPI index values to year-over-year growth rates."""
        
        if df.empty:
            return df
        
        # Sort by date
        df = df.sort_values('date').copy()
        
        # Calculate year-over-year growth rate
        df['prev_year_value'] = df['value'].shift(4)  # 4 quarters ago
        df['growth_rate'] = ((df['value'] - df['prev_year_value']) / df['prev_year_value'])
        
        # Replace value with growth rate, remove first year (no prior data)
        df['value'] = df['growth_rate']
        df = df.dropna(subset=['value'])
        df = df.drop(['prev_year_value', 'growth_rate'], axis=1)
        
        return df
    
    def get_available_parameters(self) -> List[str]:
        """Get list of parameters this collector can provide."""
        return ['expense_growth', 'rent_growth']
    
    def get_supported_geographies(self) -> List[str]:
        """Get list of geographic codes this collector supports."""
        return ['NATIONAL'] + list(get_active_msa_codes())
    
    def validate_api_connection(self) -> bool:
        """Test BLS API connection."""
        try:
            # Test with a simple national CPI request
            test_series = ['CUUR0000SA0']  # All items CPI
            current_year = datetime.now().year
            
            response = self._make_request(test_series, current_year - 1, current_year)
            
            if response.get('status') == 'REQUEST_SUCCEEDED':
                self.logger.info("BLS API connection successful")
                return True
            else:
                self.logger.error(f"BLS API test failed: {response.get('message')}")
                return False
                
        except Exception as e:
            self.logger.error(f"BLS API connection test failed: {e}")
            return False


def create_bls_collector(api_key: Optional[str] = None) -> BLSDataCollector:
    """Factory function to create BLS collector."""
    return BLSDataCollector(api_key)