"""
Database Manager for Pro Forma Analytics

Handles database connections, initialization, and basic operations
for all SQLite databases used in the system.
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import json
from datetime import datetime, date
import logging
from contextlib import contextmanager

from config.settings import settings

class DatabaseManager:
    """Manages SQLite database connections and operations."""
    
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.db_configs = {
            'market_data': settings.database.market_data_db,
            'property_data': settings.database.property_data_db,
            'economic_data': settings.database.economic_data_db,
            'forecast_cache': settings.database.forecast_cache_db
        }
        
        # Ensure database directory exists
        Path(settings.database.base_path).mkdir(parents=True, exist_ok=True)
    
    def get_db_path(self, db_name: str) -> Path:
        """Get the full path to a database file."""
        if db_name not in self.db_configs:
            raise ValueError(f"Unknown database: {db_name}")
        return Path(settings.database.base_path) / self.db_configs[db_name]
    
    @contextmanager
    def get_connection(self, db_name: str) -> Any:
        """Context manager for database connections."""
        db_path = self.get_db_path(db_name)
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        finally:
            conn.close()
    
    def initialize_databases(self) -> None:
        """Initialize all databases with their specialized schemas."""
        
        # Database-specific schema mapping
        schema_mapping = {
            'market_data': 'market_data_schema.sql',
            'property_data': 'property_data_schema.sql',
            'economic_data': 'economic_data_schema.sql',
            'forecast_cache': 'forecast_cache_schema.sql'
        }
        
        schema_dir = Path(__file__).parent / "schemas"
        
        # Initialize each database with its specific schema
        for db_name in self.db_configs.keys():
            try:
                schema_file = schema_mapping.get(db_name)
                if not schema_file:
                    self.logger.warning(f"No schema mapping found for {db_name}, skipping")
                    continue
                
                schema_path = schema_dir / schema_file
                if not schema_path.exists():
                    raise FileNotFoundError(f"Schema file not found: {schema_path}")
                
                # Read database-specific schema
                with open(schema_path, 'r') as f:
                    schema_sql = f.read()
                
                # Apply schema to specific database
                with self.get_connection(db_name) as conn:
                    conn.executescript(schema_sql)
                    conn.commit()
                
                self.logger.info(f"Initialized {db_name} with {schema_file}")
                
                
            except Exception as e:
                self.logger.error(f"Failed to initialize {db_name}: {e}")
                raise
    
    def insert_data(self, db_name: str, table: str, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> int:
        """
        Insert data into a table.
        
        Args:
            db_name: Database name
            table: Table name
            data: Single record (dict) or list of records
            
        Returns:
            Number of records inserted
        """
        if isinstance(data, dict):
            data = [data]
        
        if not data:
            return 0
        
        # Build INSERT OR REPLACE statement
        columns = list(data[0].keys())
        placeholders = ', '.join(['?' for _ in columns])
        column_names = ', '.join(columns)
        
        sql = f"INSERT OR REPLACE INTO {table} ({column_names}) VALUES ({placeholders})"
        
        try:
            with self.get_connection(db_name) as conn:
                values = [tuple(self._serialize_value(record[col]) for col in columns) 
                         for record in data]
                conn.executemany(sql, values)
                conn.commit()
                return len(data)
        except Exception as e:
            self.logger.error(f"Failed to insert data into {db_name}.{table}: {e}")
            raise
    
    def query_data(self, db_name: str, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results.
        
        Args:
            db_name: Database name
            query: SQL query
            params: Query parameters
            
        Returns:
            List of records as dictionaries
        """
        try:
            with self.get_connection(db_name) as conn:
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"Query failed on {db_name}: {e}")
            raise
    
    def get_parameter_data(self, parameter_name: str, geographic_code: str, 
                          start_date: Optional[date] = None, 
                          end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """
        Get historical data for a specific parameter and geography.
        
        Args:
            parameter_name: Parameter name (e.g., 'treasury_10y')
            geographic_code: Geographic identifier
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List of historical data points
        """
        # Map parameters to database locations based on our 11 ARIMA metrics
        param_config = {
            # Interest rates (national, from market_data.interest_rates)
            'treasury_10y': {'db': 'market_data', 'table': 'interest_rates', 'column': 'parameter_name'},
            'commercial_mortgage_rate': {'db': 'market_data', 'table': 'interest_rates', 'column': 'parameter_name'},
            'fed_funds_rate': {'db': 'market_data', 'table': 'interest_rates', 'column': 'parameter_name'},
            
            # Cap rates (MSA-specific, from market_data.cap_rates - use property_type = 'multifamily')
            'cap_rate': {'db': 'market_data', 'table': 'cap_rates', 'column': 'property_type', 'value': 'multifamily'},
            
            # Rental market (MSA-specific, from property_data.rental_market_data)
            'vacancy_rate': {'db': 'property_data', 'table': 'rental_market_data', 'column': 'metric_name'},
            'rent_growth': {'db': 'property_data', 'table': 'rental_market_data', 'column': 'metric_name'},
            
            # Operating expenses (MSA-specific, from property_data.operating_expenses)
            'expense_growth': {'db': 'property_data', 'table': 'operating_expenses', 'column': 'expense_growth', 'direct_column': True},
            
            # Lending requirements (MSA-specific, from economic_data.lending_requirements)
            'ltv_ratio': {'db': 'economic_data', 'table': 'lending_requirements', 'column': 'metric_name'},
            'closing_cost_pct': {'db': 'economic_data', 'table': 'lending_requirements', 'column': 'metric_name'},
            'lender_reserves': {'db': 'economic_data', 'table': 'lending_requirements', 'column': 'metric_name'},
            
            # Property growth (MSA-specific, from economic_data.property_growth)
            'property_growth': {'db': 'economic_data', 'table': 'property_growth', 'column': 'property_growth', 'direct_column': True}
        }
        
        if parameter_name not in param_config:
            raise ValueError(f"Unknown parameter: {parameter_name}. Supported parameters: {list(param_config.keys())}")
        
        config = param_config[parameter_name]
        db_name = config['db']
        table = config['table']
        column = config['column']
        
        # Build query based on configuration
        if config.get('direct_column'):
            # For tables like property_growth where the column IS the value
            query = f"""
                SELECT date, {column} as value, data_source
                FROM {table}
                WHERE geographic_code = ?
            """
            params = [geographic_code]
        elif 'value' in config:
            # For cap_rates where we filter by property_type = 'multifamily'
            query = f"""
                SELECT date, value, data_source
                FROM {table}
                WHERE {column} = ? AND geographic_code = ?
            """
            params = [config['value'], geographic_code]
        else:
            # Standard case with parameter/metric name filtering
            query = f"""
                SELECT date, value, data_source
                FROM {table}
                WHERE {column} = ? AND geographic_code = ?
            """
            params = [parameter_name, geographic_code]
        
        # Add date filters if provided
        if start_date:
            query += " AND date >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date.isoformat())
        
        query += " ORDER BY date"
        
        return self.query_data(db_name, query, tuple(params))
    
    def save_prophet_forecast(self, parameter_name: str, geographic_code: str,
                             forecast_horizon_years: int, forecast_values: List[float],
                             forecast_dates: List[str], lower_bound: List[float],
                             upper_bound: List[float], model_performance: Dict[str, Any],
                             trend_info: Dict[str, Any], historical_data_points: int) -> None:
        """Save Prophet forecast results to cache."""
        
        forecast_data = {
            'parameter_name': parameter_name,
            'geographic_code': geographic_code,
            'forecast_date': date.today().isoformat(),
            'forecast_horizon_years': forecast_horizon_years,
            'forecast_values': json.dumps(forecast_values),
            'forecast_dates': json.dumps(forecast_dates),
            'lower_bound': json.dumps(lower_bound),
            'upper_bound': json.dumps(upper_bound),
            'model_performance': json.dumps(model_performance),
            'trend_info': json.dumps(trend_info),
            'historical_data_points': historical_data_points
        }
        
        self.insert_data('forecast_cache', 'prophet_forecasts', forecast_data)
    
    def get_cached_prophet_forecast(self, parameter_name: str, geographic_code: str,
                                   forecast_horizon_years: int, 
                                   max_age_days: int = 30) -> Optional[Dict[str, Any]]:
        """Retrieve cached Prophet forecast if available and not too old."""
        
        query = """
            SELECT * FROM prophet_forecasts
            WHERE parameter_name = ? AND geographic_code = ? 
            AND forecast_horizon_years = ?
            AND DATE(forecast_date) >= DATE('now', '-{} days')
            ORDER BY forecast_date DESC
            LIMIT 1
        """.format(max_age_days)
        
        results = self.query_data('forecast_cache', query, 
                                (parameter_name, geographic_code, forecast_horizon_years))
        
        if results:
            return results[0]  # Return raw result - JSON parsing will be done by caller
        
        return None
    
    def save_correlations(self, geographic_code: str, correlation_window_years: int,
                         correlation_matrix: List[List[float]], parameter_names: List[str],
                         start_date: date, end_date: date) -> None:
        """Save parameter correlation matrix."""
        
        correlation_data = {
            'geographic_code': geographic_code,
            'correlation_window_years': correlation_window_years,
            'correlation_matrix': json.dumps(correlation_matrix),
            'parameter_names': json.dumps(parameter_names),
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        }
        
        self.insert_data('forecast_cache', 'parameter_correlations', correlation_data)
    
    def get_data_completeness(self, parameter_name: str, geographic_code: str,
                             start_date: date, end_date: date) -> float:
        """Calculate data completeness percentage for a parameter."""
        
        # Get actual data points
        data_points = self.get_parameter_data(parameter_name, geographic_code, start_date, end_date)
        
        # Calculate expected number of data points (annual data)
        expected_years = end_date.year - start_date.year + 1
        actual_years = len(data_points)
        
        return (actual_years / expected_years) * 100 if expected_years > 0 else 0
    
    def _serialize_value(self, value: Any) -> Any:
        """Serialize complex values for database storage."""
        if isinstance(value, (dict, list)):
            return json.dumps(value)
        elif isinstance(value, (date, datetime)):
            return value.isoformat()
        return value
    
    def backup_databases(self) -> List[str]:
        """Create backup copies of all databases."""
        backup_paths = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for db_name in self.db_configs.keys():
            source_path = self.get_db_path(db_name)
            if source_path.exists():
                backup_name = f"{source_path.stem}_backup_{timestamp}{source_path.suffix}"
                backup_path = source_path.parent / backup_name
                
                # Simple file copy for SQLite
                import shutil
                shutil.copy2(source_path, backup_path)
                backup_paths.append(str(backup_path))
        
        return backup_paths

# Global database manager instance
db_manager = DatabaseManager()