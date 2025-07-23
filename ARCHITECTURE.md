# Technical Architecture

This document provides detailed technical architecture for the Pro Forma Analytics Tool.

## 🏗️ System Architecture

### High-Level Design Principles

1. **Data-Driven**: All forecasts based on historical data, not subjective estimates
2. **Modular**: Clear separation between data, forecasting, and presentation layers  
3. **Scalable**: Designed to handle additional metrics and geographies
4. **Maintainable**: Simple, clean interfaces with comprehensive documentation
5. **Testable**: Each component can be validated independently

### Component Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           PRESENTATION LAYER                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │  Web Interface  │  │   CLI Tools     │  │  Report Engine  │    │
│  │                 │  │                 │  │                 │    │
│  │ • Dashboards    │  │ • data_manager  │  │ • PDF Export    │    │
│  │ • Scenario UI   │  │ • Verification  │  │ • Excel Export  │    │
│  │ • Charts/Graphs │  │ • Data Ops      │  │ • Custom Views  │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
└─────────────────┬─────────────┬─────────────────┬───────────────────┘
                  │             │                 │
┌─────────────────▼─────────────▼─────────────────▼───────────────────┐
│                          BUSINESS LOGIC LAYER                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │ ARIMA Forecasts │  │ Monte Carlo Sim │  │ Risk Analysis   │    │
│  │                 │  │                 │  │                 │    │
│  │ • Time Series   │  │ • Correlation   │  │ • Sensitivity   │    │
│  │ • Auto Selection│  │ • Scenarios     │  │ • Stress Tests  │    │
│  │ • Validation    │  │ • Percentiles   │  │ • Comparisons   │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
└─────────────────┬─────────────┬─────────────────┬───────────────────┘
                  │             │                 │
┌─────────────────▼─────────────▼─────────────────▼───────────────────┐
│                            DATA LAYER                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │ Database Manager│  │ Data Collection │  │ API Integration │    │
│  │                 │  │                 │  │                 │    │
│  │ • SQLite DBs    │  │ • Validation    │  │ • FRED API      │    │
│  │ • Schema Mgmt   │  │ • Transformation│  │ • Future APIs   │    │
│  │ • Query Engine  │  │ • Quality Check │  │ • Rate Limiting │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

## 💾 Data Architecture

### Database Design Philosophy

**Normalized by Function**: Each database serves a specific analytical purpose
- **market_data.db**: Financial market conditions
- **property_data.db**: Real estate specific metrics  
- **economic_data.db**: Regional economic indicators
- **forecast_cache.db**: Computed forecasts and simulations

### Entity Relationship Model

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   market_data   │     │  property_data  │     │  economic_data  │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ interest_rates  │────▶│rental_market_data│────▶│property_growth  │
│ cap_rates       │     │ operating_expenses│    │lending_requirements│
│ economic_indicators│   │ property_tax_data│    │regional_econ_indicators│
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │                       │
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────┐
                    │ forecast_cache  │
                    ├─────────────────┤
                    │ arima_forecasts │
                    │ parameter_correlations│
                    │ monte_carlo_results│
                    └─────────────────┘
```

### Schema Design Patterns

#### Temporal Data Pattern
All metric tables follow consistent temporal structure:
```sql
CREATE TABLE metric_table (
    date DATE NOT NULL,                    -- Annual data points
    [metric_specific_fields],              -- Varies by table
    value REAL NOT NULL,                   -- Standardized value field
    geographic_code TEXT NOT NULL,        -- MSA/FIPS code
    data_source TEXT NOT NULL,            -- Traceability
    PRIMARY KEY(date, [key_fields], geographic_code)
);
```

#### Geographic Normalization
- **MSA Codes**: 5-digit Census Bureau codes for metropolitan areas
- **FIPS Codes**: County-level Federal Information Processing Standards
- **Consistent Naming**: Standardized geographic identifiers across all tables

#### Data Quality Assurance
- **Primary Keys**: Prevent duplicate records
- **NOT NULL Constraints**: Ensure data completeness
- **Type Validation**: Proper data types for all fields
- **Source Tracking**: All data includes source attribution

## 🔄 Data Flow Architecture

### Collection Pipeline

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   External  │───▶│   Extract   │───▶│ Transform   │───▶│    Load     │
│   Sources   │    │             │    │             │    │             │
│             │    │ • API Calls │    │ • Validate  │    │ • Insert    │
│ • FRED API  │    │ • Mock Data │    │ • Convert   │    │ • Update    │
│ • Future    │    │ • Files     │    │ • Clean     │    │ • Verify    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### Processing Pipeline

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Historical  │───▶│    ARIMA    │───▶│ Monte Carlo │───▶│   Output    │
│    Data     │    │ Forecasting │    │ Simulation  │    │             │
│             │    │             │    │             │    │ • Reports   │
│ • Clean     │    │ • Model Fit │    │ • Scenarios │    │ • Charts    │
│ • Validated │    │ • Forecast  │    │ • Risk Calc │    │ • Export    │
│ • Complete  │    │ • Cache     │    │ • Cache     │    │ • API       │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## 🧩 Component Architecture

### Core Components

#### 1. Database Manager (`data/databases/database_manager.py`)
**Responsibility**: Database operations and connection management

```python
class DatabaseManager:
    # Connection management
    def get_connection(db_name: str) -> Connection
    def initialize_databases() -> None
    
    # Data operations  
    def insert_data(db_name: str, table: str, data: Union[Dict, List]) -> int
    def query_data(db_name: str, query: str, params: tuple) -> List[Dict]
    
    # Parameter-specific methods
    def get_parameter_data(parameter: str, geography: str) -> List[Dict]
    def save_forecast(parameter: str, geography: str, results: Dict) -> None
    def get_cached_forecast(parameter: str, geography: str) -> Optional[Dict]
```

#### 2. Data Collector (`collect_simplified_data.py`)
**Responsibility**: Historical data collection and validation

```python
class SimplifiedDataCollector:
    # Metric-specific collection
    def collect_interest_rates() -> Dict[str, Any]
    def collect_vacancy_rates() -> Dict[str, Any]
    def collect_rent_growth() -> Dict[str, Any]
    # ... other metrics
    
    # Orchestration
    def run_full_collection() -> Dict[str, Any]
    
    # Utilities
    def _generate_time_series(parameter: str, config: Dict) -> List[Dict]
```

#### 3. Configuration Management (`config/`)

**Geography Configuration** (`geography.py`):
```python
@dataclass
class GeographicRegion:
    name: str
    msa_code: Optional[str]
    fips_code: Optional[str]
    state: Optional[str]

class GeographyManager:
    def list_regions() -> List[str]
    def get_region(name: str) -> Optional[GeographicRegion]
```

**Parameter Configuration** (`parameters.py`):
```python
@dataclass
class ParameterDefinition:
    name: str
    parameter_type: ParameterType
    description: str
    unit: str
    typical_range: Tuple[float, float]
    data_sources: List[str]
    fred_series: Optional[str]
```

### Interface Contracts

#### Data Collection Interface
```python
def collect_metric(metric_name: str, geography: str) -> CollectionResult:
    """
    Standard interface for metric collection.
    
    Returns:
        CollectionResult with records_inserted, errors, metadata
    """
```

#### Forecasting Interface (Future)
```python
def generate_forecast(parameter: str, geography: str, 
                     horizon_years: int) -> ForecastResult:
    """
    Standard interface for ARIMA forecasting.
    
    Returns:
        ForecastResult with values, confidence_intervals, model_info
    """
```

#### Simulation Interface (Future)
```python
def run_monte_carlo(parameters: List[str], geography: str,
                   num_simulations: int) -> SimulationResult:
    """
    Standard interface for Monte Carlo simulation.
    
    Returns:
        SimulationResult with scenarios, statistics, risk_metrics
    """
```

## 🔧 Technology Stack

### Current Implementation
- **Language**: Python 3.8+
- **Database**: SQLite 3
- **Data Processing**: pandas, numpy
- **API Integration**: requests
- **Date/Time**: datetime, pandas date handling

### Future Additions (Phase 2+)
- **Time Series**: statsmodels (ARIMA), scipy
- **Simulation**: numpy.random, scipy.stats
- **Visualization**: plotly, matplotlib
- **Web Framework**: FastAPI or Flask
- **Testing**: pytest, unittest

## 📊 Performance Considerations

### Database Performance
- **Indexing Strategy**: Indexes on date, geographic_code, and metric identifiers
- **Query Optimization**: Parameterized queries with proper type handling
- **Connection Pooling**: Context managers for efficient connection handling

### Memory Management
- **Streaming**: Large datasets processed in chunks
- **Caching**: Computed forecasts cached to avoid recomputation
- **Lazy Loading**: Data loaded only when needed

### Scalability Design
- **Horizontal Scaling**: Each MSA can be processed independently
- **Vertical Scaling**: Additional metrics added without architectural changes
- **Caching Layer**: Forecast results cached for performance

## 🛡️ Security & Data Integrity

### Data Validation
- **Schema Enforcement**: Database constraints prevent invalid data
- **Range Validation**: Metric values validated against reasonable ranges
- **Source Verification**: All data includes source attribution
- **Completeness Checks**: Automated verification of data coverage

### Error Handling
- **Graceful Degradation**: System continues operating with partial data
- **Comprehensive Logging**: All operations logged for debugging
- **Rollback Capability**: Failed operations don't corrupt existing data
- **Validation Gates**: Multi-level validation prevents bad data propagation

### API Security (Future)
- **Rate Limiting**: Prevent API abuse
- **Authentication**: Secure access to forecasting endpoints
- **Input Sanitization**: Prevent injection attacks
- **Output Validation**: Ensure response data integrity

## 🔄 Development Patterns

### Configuration Management
- **Environment-Specific**: Different configs for dev/test/prod
- **Centralized**: All configuration in `config/` directory
- **Type-Safe**: Dataclasses with type hints for configuration
- **Validation**: Configuration validated at startup

### Error Handling Pattern
```python
try:
    result = operation()
    return {'success': True, 'data': result, 'errors': []}
except SpecificException as e:
    logger.error(f"Specific error in {operation}: {e}")
    return {'success': False, 'data': None, 'errors': [str(e)]}
except Exception as e:
    logger.error(f"Unexpected error in {operation}: {e}")
    return {'success': False, 'data': None, 'errors': [str(e)]}
```

### Testing Strategy
- **Unit Tests**: Individual function testing
- **Integration Tests**: Database and API integration
- **Data Validation Tests**: Data quality and completeness
- **End-to-End Tests**: Full workflow validation

This architecture provides a solid foundation for the current system and clear extension points for future development phases.