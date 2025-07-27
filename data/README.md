# Data Infrastructure

Historical market data, database schemas, and data management components.

## Structure

- **`databases/`** - SQLite database files and schema definitions
- **`api_sources/`** - External data source integrations (FRED API)

## Database Files

- **`market_data.db`** - Interest rates, cap rates, economic indicators
- **`property_data.db`** - Rental market data, operating expenses  
- **`economic_data.db`** - Regional indicators, lending requirements
- **`forecast_cache.db`** - Prophet forecasts and Monte Carlo results

## Data Coverage

688+ historical data points covering 11 pro forma metrics across 5 major MSAs with 15+ years of annual data (2010-2025).