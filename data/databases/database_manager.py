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
    
    def __init__(self):
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
    def get_connection(self, db_name: str):
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
        
        schema_dir = Path(__file__).parent
        
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
        # Determine which database and table to query based on parameter
        if 'rate' in parameter_name.lower() and any(x in parameter_name.lower() for x in ['treasury', 'mortgage', 'fed', 'funds']):
            db_name = 'market_data'
            table = 'interest_rates'
            param_column = 'parameter_name'
        elif 'rent' in parameter_name.lower() or 'vacancy' in parameter_name.lower():
            db_name = 'property_data'
            table = 'rental_market_data'
            param_column = 'metric_name'
        elif 'cap' in parameter_name.lower():
            db_name = 'market_data' 
            table = 'cap_rates'
            param_column = 'property_type'  # Different structure for cap rates
        elif 'tax' in parameter_name.lower():
            db_name = 'property_data'
            table = 'property_tax_data'
            param_column = None  # No parameter name column
        elif any(x in parameter_name.lower() for x in ['unemployment', 'employment', 'gdp', 'population', 'income', 'housing']):
            db_name = 'economic_data'
            table = 'regional_economic_indicators'
            param_column = 'indicator_name'
        else:
            # Default to market data economic indicators for national-level data
            db_name = 'market_data'
            table = 'economic_indicators'
            param_column = 'indicator_name'
        
        # Build query with optional date filters
        if param_column:
            query = f"""
                SELECT date, value, data_source, updated_at
                FROM {table}
                WHERE {param_column} = ? AND geographic_code = ?
            """
        else:
            query = f"""
                SELECT date, tax_rate as value, data_source, updated_at
                FROM {table}
                WHERE geographic_code = ?
            """
        if param_column:
            params = [parameter_name, geographic_code]
        else:
            params = [geographic_code]
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date.isoformat())
        
        query += " ORDER BY date"
        
        return self.query_data(db_name, query, tuple(params))
    
    def save_forecast(self, parameter_name: str, geographic_code: str,
                     forecast_horizon_years: int, model_order: str,
                     forecast_values: List[float], confidence_intervals: Dict[str, List[float]],
                     model_aic: Optional[float] = None,
                     model_performance: Optional[Dict[str, Any]] = None) -> None:
        """Save ARIMA forecast results to cache."""
        
        forecast_data = {
            'parameter_name': parameter_name,
            'geographic_code': geographic_code,
            'forecast_date': date.today().isoformat(),
            'forecast_horizon_years': forecast_horizon_years,
            'model_order': model_order,
            'forecast_values': json.dumps(forecast_values),
            'confidence_intervals': json.dumps(confidence_intervals),
            'model_aic': model_aic,
            'model_performance': json.dumps(model_performance) if model_performance else None
        }
        
        self.insert_data('forecast_cache', 'arima_forecasts', forecast_data)
    
    def get_cached_forecast(self, parameter_name: str, geographic_code: str,
                           forecast_horizon_years: int, 
                           max_age_days: int = 30) -> Optional[Dict[str, Any]]:
        """Retrieve cached forecast if available and not too old."""
        
        query = """
            SELECT * FROM arima_forecasts
            WHERE parameter_name = ? AND geographic_code = ? 
            AND forecast_horizon_years = ?
            AND DATE(forecast_date) >= DATE('now', '-{} days')
            ORDER BY forecast_date DESC
            LIMIT 1
        """.format(max_age_days)
        
        results = self.query_data('forecast_cache', query, 
                                (parameter_name, geographic_code, forecast_horizon_years))
        
        if results:
            result = results[0]
            # Deserialize JSON fields
            result['forecast_values'] = json.loads(result['forecast_values'])
            result['confidence_intervals'] = json.loads(result['confidence_intervals'])
            if result['model_performance']:
                result['model_performance'] = json.loads(result['model_performance'])
            return result
        
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