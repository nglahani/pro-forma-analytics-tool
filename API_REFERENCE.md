# API Reference

Complete documentation for all classes, functions, and modules in the Pro Forma Analytics Tool.

## 📚 Module Overview

| Module | Purpose | Key Classes |
|--------|---------|-------------|
| `data_manager.py` | Main operations hub | - |
| `collect_simplified_data.py` | Data collection | `SimplifiedDataCollector` |
| `verify_pro_forma_metrics.py` | Data verification | - |
| `data.databases.database_manager.py` | Database operations | `DatabaseManager` |
| `config.geography.py` | Geographic mapping | `GeographicRegion`, `GeographyManager` |
| `config.parameters.py` | Parameter definitions | `ParameterDefinition`, `ParameterType` |
| `config.settings.py` | System configuration | `Settings` classes |

## 🔧 Core Operations (`data_manager.py`)

### Functions

#### `initialize_system() -> bool`
Initialize the database system with clean schemas.

**Returns:**
- `bool`: True if initialization successful, False otherwise

**Example:**
```python
from data_manager import initialize_system
success = initialize_system()
```

#### `collect_all_data() -> bool`
Collect data for all 9 pro forma metrics across all MSAs.

**Returns:**
- `bool`: True if collection successful, False if errors occurred

**Example:**
```python
from data_manager import collect_all_data
success = collect_all_data()
```

#### `verify_system() -> bool`
Verify all 9 pro forma metrics have complete data coverage.

**Returns:**
- `bool`: True if all metrics verified, False if missing data

#### `get_system_status() -> None`
Print current system status including database files and record counts.

#### `full_system_setup() -> bool`
Complete system setup from scratch (init + collect + verify).

**Returns:**
- `bool`: True if full setup successful

### Command Line Interface

```bash
python data_manager.py [command]
```

**Commands:**
- `init` - Initialize databases
- `collect` - Collect all data  
- `verify` - Verify data coverage
- `status` - Show system status
- `setup` - Full system setup

## 💾 Database Operations (`data.databases.database_manager.py`)

### DatabaseManager Class

Primary interface for all database operations.

#### Methods

##### `__init__()`
Initialize database manager with configuration from settings.

##### `get_db_path(db_name: str) -> Path`
Get the full path to a database file.

**Parameters:**
- `db_name` (str): Database name ('market_data', 'property_data', 'economic_data', 'forecast_cache')

**Returns:**
- `Path`: Full path to database file

**Raises:**
- `ValueError`: If unknown database name

##### `get_connection(db_name: str) -> ContextManager[sqlite3.Connection]`
Context manager for database connections.

**Parameters:**
- `db_name` (str): Database name

**Returns:**
- `ContextManager`: SQLite connection context manager

**Example:**
```python
with db_manager.get_connection('market_data') as conn:
    cursor = conn.execute("SELECT * FROM interest_rates LIMIT 5")
    results = cursor.fetchall()
```

##### `initialize_databases() -> None`
Initialize all databases with their specialized schemas.

**Raises:**
- `FileNotFoundError`: If schema files not found
- `Exception`: If database initialization fails

##### `insert_data(db_name: str, table: str, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> int`
Insert data into a table.

**Parameters:**
- `db_name` (str): Database name
- `table` (str): Table name
- `data` (Union[Dict, List[Dict]]): Single record or list of records

**Returns:**
- `int`: Number of records inserted

**Example:**
```python
record = {
    'date': '2024-01-01',
    'parameter_name': 'treasury_10y',
    'value': 0.045,
    'geographic_code': 'NATIONAL',
    'data_source': 'FRED'
}
count = db_manager.insert_data('market_data', 'interest_rates', record)
```

##### `query_data(db_name: str, query: str, params: tuple = ()) -> List[Dict[str, Any]]`
Execute a SELECT query and return results.

**Parameters:**
- `db_name` (str): Database name
- `query` (str): SQL query
- `params` (tuple): Query parameters

**Returns:**
- `List[Dict]`: Query results as list of dictionaries

**Example:**
```python
results = db_manager.query_data(
    'market_data',
    'SELECT * FROM interest_rates WHERE parameter_name = ? LIMIT 5',
    ('treasury_10y',)
)
```

##### `get_parameter_data(parameter_name: str, geographic_code: str, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]`
Get historical data for a specific parameter and geography.

**Parameters:**
- `parameter_name` (str): Parameter name (e.g., 'treasury_10y')
- `geographic_code` (str): Geographic identifier
- `start_date` (Optional[date]): Start date filter
- `end_date` (Optional[date]): End date filter

**Returns:**
- `List[Dict]`: Historical data points

**Example:**
```python
from datetime import date
data = db_manager.get_parameter_data(
    'vacancy_rate',
    '35620',  # NYC MSA
    start_date=date(2020, 1, 1)
)
```

##### `save_forecast(parameter_name: str, geographic_code: str, forecast_horizon_years: int, model_order: str, forecast_values: List[float], confidence_intervals: Dict[str, List[float]], model_aic: Optional[float] = None, model_performance: Optional[Dict[str, Any]] = None) -> None`
Save ARIMA forecast results to cache.

**Parameters:**
- `parameter_name` (str): Parameter being forecasted
- `geographic_code` (str): Geographic identifier
- `forecast_horizon_years` (int): Forecast horizon
- `model_order` (str): ARIMA model order (e.g., 'ARIMA(1,1,1)')
- `forecast_values` (List[float]): Forecasted values
- `confidence_intervals` (Dict[str, List[float]]): Confidence bands
- `model_aic` (Optional[float]): Model AIC score
- `model_performance` (Optional[Dict]): Model performance metrics

##### `get_cached_forecast(parameter_name: str, geographic_code: str, forecast_horizon_years: int, max_age_days: int = 30) -> Optional[Dict[str, Any]]`
Retrieve cached forecast if available and not too old.

**Parameters:**
- `parameter_name` (str): Parameter name
- `geographic_code` (str): Geographic identifier  
- `forecast_horizon_years` (int): Forecast horizon
- `max_age_days` (int): Maximum age in days (default: 30)

**Returns:**
- `Optional[Dict]`: Cached forecast or None if not found/expired

##### `get_data_completeness(parameter_name: str, geographic_code: str, start_date: date, end_date: date) -> float`
Calculate data completeness percentage for a parameter.

**Returns:**
- `float`: Completeness percentage (0-100)

### Global Instance

```python
from data.databases.database_manager import db_manager
# Use db_manager instance for all database operations
```

## 📊 Data Collection (`collect_simplified_data.py`)

### SimplifiedDataCollector Class

Handles collection of all 9 pro forma metrics with mock historical data.

#### Methods

##### `__init__()`
Initialize collector with date range and geographic regions.

**Attributes:**
- `start_date`: date(2010, 1, 1)
- `end_date`: date.today()
- `regions`: Top 5 MSAs from geography configuration

##### `collect_interest_rates() -> Dict[str, Any]`
Collect interest rate data (metric #1).

**Returns:**
- `Dict`: Collection results with records_inserted, errors

**Collects:**
- Treasury 10-year rates
- Commercial mortgage rates  
- Federal funds rates

##### `collect_vacancy_rates() -> Dict[str, Any]`
Collect vacancy rate data (metric #2) by MSA.

##### `collect_ltv_data() -> Dict[str, Any]`
Collect LTV ratio data (metric #3) by MSA.

##### `collect_rent_growth() -> Dict[str, Any]`
Collect rent growth data (metric #4) by MSA.

##### `collect_closing_costs() -> Dict[str, Any]`
Collect closing cost percentage data (metric #5) by MSA.

##### `collect_lender_reserves() -> Dict[str, Any]`
Collect lender reserve requirements data (metric #6) by MSA.

##### `collect_property_growth() -> Dict[str, Any]`
Collect property value growth data (metric #7) by MSA.

##### `collect_cap_rates() -> Dict[str, Any]`
Collect market cap rate data (metric #8) by MSA.

##### `collect_expense_growth() -> Dict[str, Any]`
Collect expense growth data (metric #9) by MSA.

##### `run_full_collection() -> Dict[str, Any]`
Run complete data collection for all 9 pro forma metrics.

**Returns:**
- `Dict`: Comprehensive results including:
  - `success` (bool): Overall success status
  - `metrics` (Dict): Results for each metric
  - `total_records` (int): Total records inserted
  - `errors` (List[str]): Any errors encountered

**Example:**
```python
collector = SimplifiedDataCollector()
results = collector.run_full_collection()
print(f"Collected {results['total_records']} records")
```

##### `_generate_time_series(parameter_name: str, base_range: tuple, volatility: float, geographic_code: str, table_structure: str = 'default') -> List[Dict]`
Generate realistic time series data for a parameter.

**Parameters:**
- `parameter_name` (str): Name of parameter
- `base_range` (tuple): (min, max) value range
- `volatility` (float): Volatility factor
- `geographic_code` (str): Geographic identifier
- `table_structure` (str): Table structure type

**Returns:**
- `List[Dict]`: Generated time series records

## 🌍 Geographic Configuration (`config.geography.py`)

### GeographicRegion Class

```python
@dataclass
class GeographicRegion:
    name: str
    msa_code: Optional[str] = None
    fips_code: Optional[str] = None  
    state: Optional[str] = None
```

Data class representing a geographic region.

**Attributes:**
- `name` (str): Human-readable region name
- `msa_code` (Optional[str]): MSA code for metropolitan areas
- `fips_code` (Optional[str]): FIPS code for counties
- `state` (Optional[str]): State abbreviation

### GeographyManager Class

#### Methods

##### `list_regions() -> List[str]`
Get list of all available region names.

**Returns:**
- `List[str]`: Region names

##### `get_region(name: str) -> Optional[GeographicRegion]`
Get region details by name.

**Parameters:**
- `name` (str): Region name

**Returns:**
- `Optional[GeographicRegion]`: Region object or None if not found

**Example:**
```python
from config.geography import geography
regions = geography.list_regions()
nyc = geography.get_region("New York-Newark-Jersey City")
print(f"NYC MSA Code: {nyc.msa_code}")
```

### Global Instance

```python
from config.geography import geography
# Use geography instance for all geographic operations
```

## ⚙️ Parameter Configuration (`config.parameters.py`)

### ParameterType Enum

```python
class ParameterType(Enum):
    INTEREST_RATE = "interest_rate"
    GROWTH_RATE = "growth_rate"  
    PERCENTAGE = "percentage"
    RATIO = "ratio"
    CURRENCY = "currency"
```

### ParameterDefinition Class

```python
@dataclass
class ParameterDefinition:
    name: str
    parameter_type: ParameterType
    description: str
    unit: str
    typical_range: Tuple[float, float]
    data_sources: List[str]
    fred_series: Optional[str] = None
```

**Attributes:**
- `name` (str): Parameter identifier
- `parameter_type` (ParameterType): Type classification
- `description` (str): Human-readable description
- `unit` (str): Unit of measurement
- `typical_range` (Tuple[float, float]): Expected value range
- `data_sources` (List[str]): Available data sources
- `fred_series` (Optional[str]): FRED API series code

### ParameterManager Class

#### Methods

##### `get_parameter(name: str) -> Optional[ParameterDefinition]`
Get parameter definition by name.

##### `list_parameters() -> List[str]`
Get list of all parameter names.

##### `get_parameters_by_type(param_type: ParameterType) -> List[ParameterDefinition]`
Get all parameters of a specific type.

**Example:**
```python
from config.parameters import parameters, ParameterType
treasury_param = parameters.get_parameter('treasury_10y')
rates = parameters.get_parameters_by_type(ParameterType.INTEREST_RATE)
```

## 🔍 Data Verification (`verify_pro_forma_metrics.py`)

### Functions

#### `verify_metric_coverage() -> bool`
Verify we have data for all 9 pro forma metrics.

**Returns:**
- `bool`: True if all metrics have data, False otherwise

**Output:**
Prints detailed verification results for each metric including:
- Record counts
- Date ranges
- Success/failure status

**Example:**
```python
from verify_pro_forma_metrics import verify_metric_coverage
all_good = verify_metric_coverage()
```

## 🔧 Excel Analysis (`excel_analysis_consolidated.py`)

### ExcelAnalyzer Class

Tools for analyzing the reference Excel pro forma.

#### Methods

##### `__init__(excel_path: str)`
Initialize analyzer with Excel file path.

##### `read_excel_structure() -> Dict[str, Any]`
Read and analyze Excel file structure.

**Returns:**
- `Dict`: Structure analysis including sheets, columns, data samples

##### `extract_pro_forma_parameters() -> Dict[str, Any]`
Extract key pro forma parameters from Excel.

**Returns:**
- `Dict`: Extracted parameter values

#### Functions

##### `analyze_reference_excel() -> None`
Analyze the reference Excel file and print results.

**Example:**
```python
from excel_analysis_consolidated import analyze_reference_excel
analyze_reference_excel()
```

## 🏗️ Configuration System (`config.settings.py`)

### Settings Classes

Hierarchical configuration system with separate classes for different components.

#### DatabaseSettings

```python
@dataclass  
class DatabaseSettings:
    base_path: str
    market_data_db: str
    property_data_db: str
    economic_data_db: str
    forecast_cache_db: str
```

#### ForecastSettings

```python
@dataclass
class ForecastSettings:
    default_horizon_years: int
    max_horizon_years: int
    min_horizon_years: int
    confidence_levels: List[float]
```

#### MonteCarloSettings

```python
@dataclass
class MonteCarloSettings:
    default_simulations: int
    max_simulations: int
    correlation_window_years: int
```

#### Settings (Root)

```python
@dataclass
class Settings:
    database: DatabaseSettings
    forecast: ForecastSettings
    monte_carlo: MonteCarloSettings
    fred_api: FredApiSettings
```

### Global Instance

```python
from config.settings import settings
# Use settings instance for all configuration access
db_path = settings.database.base_path
```

## ⚠️ Error Handling Patterns

### Standard Result Format

Most functions return results in this format:

```python
{
    'success': bool,           # Overall operation success
    'data': Any,              # Result data (if applicable)
    'records_inserted': int,   # Number of records (for data operations)
    'errors': List[str],      # List of error messages
    'metadata': Dict          # Additional metadata (optional)
}
```

### Exception Handling

```python
try:
    result = operation()
    if result['success']:
        print(f"Success: {result['records_inserted']} records")
    else:
        print(f"Errors: {result['errors']}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## 🔗 Usage Examples

### Complete Workflow Example

```python
# Initialize system
from data_manager import full_system_setup
success = full_system_setup()

# Query specific data
from data.databases.database_manager import db_manager
nyc_vacancy = db_manager.get_parameter_data('vacancy_rate', '35620')

# Verify system
from verify_pro_forma_metrics import verify_metric_coverage
all_metrics_present = verify_metric_coverage()
```

### Custom Data Query Example

```python
from data.databases.database_manager import db_manager

# Get recent interest rate data
recent_rates = db_manager.query_data(
    'market_data',
    '''SELECT date, parameter_name, value 
       FROM interest_rates 
       WHERE date >= '2020-01-01' 
       ORDER BY date DESC''')

# Calculate average vacancy rate for NYC
avg_vacancy = db_manager.query_data(
    'property_data',
    '''SELECT AVG(value) as avg_vacancy 
       FROM rental_market_data 
       WHERE metric_name = 'vacancy_rate' 
       AND geographic_code = '35620' ''')
```

This API reference provides complete documentation for all current functionality and serves as a foundation for future development.