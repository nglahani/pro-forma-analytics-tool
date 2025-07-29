"""
Federal Housing Finance Agency (FHFA) House Price Index Collector

Collects property value growth data using FHFA House Price Index:
- MSA-level house price indices (quarterly data back to 1991)
- Used as proxy for commercial property value growth
- Free public API with no authentication required

Logic: Residential price growth correlates 0.7-0.9 with commercial property values
"""

import pandas as pd
import requests
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date, timedelta
import xml.etree.ElementTree as ET

from .base_collector import BaseDataCollector
from config.msa_config import get_active_msa_codes, get_msa_info
from core.logging_config import get_logger


class FHFACollector(BaseDataCollector):
    """FHFA House Price Index collector for property growth data."""
    
    # FHFA MSA codes for North Carolina metros
    FHFA_MSA_CODES = {
        '16740': '16740',  # Charlotte-Concord-Gastonia, NC-SC
        '39580': '39580',  # Raleigh-Cary, NC  
        '24660': '24660',  # Greensboro-High Point, NC
        '20500': '20500',  # Durham-Chapel Hill, NC
    }
    
    def __init__(self):
        super().__init__("FHFA_PropertyGrowth")
        self.base_url = "https://www.fhfa.gov/DataTools/Downloads/Pages/House-Price-Index-Datasets.aspx"
        # FHFA provides CSV downloads rather than API
        self.csv_url = "https://www.fhfa.gov/DataTools/Downloads/Documents/HPI/HPI_master.csv"
        self.session = requests.Session()
        
        # Rate limiting (be respectful to FHFA servers)
        self.request_delay = 2.0
        self.last_request_time = 0
        
    def _make_request(self, url: str) -> pd.DataFrame:
        """Make rate-limited request to FHFA for CSV data."""
        
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.request_delay:
            time.sleep(self.request_delay - time_since_last)
        
        try:
            response = self.session.get(url, timeout=60)
            response.raise_for_status()
            
            self.last_request_time = time.time()
            
            # Parse CSV data
            from io import StringIO
            csv_data = StringIO(response.text)
            df = pd.read_csv(csv_data)
            
            return df
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"FHFA request failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"FHFA CSV parsing failed: {e}")
            raise
    
    def collect_data(self, parameter_name: str, geographic_code: str,
                    start_date: date, end_date: date) -> pd.DataFrame:
        """Collect FHFA house price data for property growth calculation."""
        
        if parameter_name != 'property_growth':
            raise ValueError(f"Parameter {parameter_name} not available from FHFA")
        
        # Check if we have this MSA
        fhfa_code = self.FHFA_MSA_CODES.get(geographic_code)
        if not fhfa_code:
            self.logger.warning(f"FHFA data not available for MSA {geographic_code}")
            return pd.DataFrame()
        
        try:
            # Download the master HPI dataset
            self.logger.info("Downloading FHFA House Price Index data...")
            df = self._make_request(self.csv_url)
            
            # Filter for our MSA and date range
            # FHFA CSV structure: columns include 'msa', 'yr', 'qtr', 'index_sa' (seasonally adjusted)
            msa_data = df[df['msa'] == fhfa_code].copy()
            
            if msa_data.empty:
                self.logger.warning(f"No FHFA data found for MSA {fhfa_code}")
                return pd.DataFrame()
            
            # Convert year/quarter to date
            msa_data['date'] = pd.to_datetime(
                msa_data['yr'].astype(str) + '-Q' + msa_data['qtr'].astype(str)
            ).dt.to_period('Q').dt.start_time.dt.date
            
            # Filter date range
            msa_data = msa_data[
                (msa_data['date'] >= start_date) & 
                (msa_data['date'] <= end_date)
            ]
            
            if msa_data.empty:
                self.logger.warning(f"No FHFA data in date range {start_date} to {end_date}")
                return pd.DataFrame()
            
            # Calculate year-over-year growth rate from index
            msa_data = msa_data.sort_values('date')
            msa_data['prev_year_index'] = msa_data['index_sa'].shift(4)  # 4 quarters ago
            msa_data['growth_rate'] = (
                (msa_data['index_sa'] - msa_data['prev_year_index']) / 
                msa_data['prev_year_index']
            )
            
            # Apply commercial property adjustment factor (commercial typically 1.2x residential volatility)
            commercial_multiplier = 1.2
            msa_data['commercial_growth'] = msa_data['growth_rate'] * commercial_multiplier
            
            # Format for our database schema
            data_records = []
            for _, row in msa_data.dropna(subset=['commercial_growth']).iterrows():
                data_records.append({
                    'date': row['date'],
                    'value': row['commercial_growth'],
                    'parameter_name': parameter_name,
                    'geographic_code': geographic_code,
                    'data_source': 'FHFA'
                })
            
            result_df = pd.DataFrame(data_records)
            
            self.logger.info(f"Collected {len(result_df)} property growth observations from FHFA")
            return result_df
            
        except Exception as e:
            self.logger.error(f"Failed to collect FHFA data: {e}")
            return pd.DataFrame()
    
    def get_available_parameters(self) -> List[str]:
        """Get list of parameters this collector can provide."""
        return ['property_growth']
    
    def get_supported_geographies(self) -> List[str]:
        """Get list of geographic codes this collector supports."""
        return list(self.FHFA_MSA_CODES.keys())
    
    def validate_api_connection(self) -> bool:
        """Test FHFA data connection."""
        try:
            # Test downloading a small sample of the CSV
            response = self.session.head(self.csv_url, timeout=30)
            
            if response.status_code == 200:
                self.logger.info("FHFA data connection successful")
                return True
            else:
                self.logger.error(f"FHFA connection failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"FHFA connection test failed: {e}")
            return False


def create_fhfa_collector() -> FHFACollector:
    """Factory function to create FHFA collector."""
    return FHFACollector()