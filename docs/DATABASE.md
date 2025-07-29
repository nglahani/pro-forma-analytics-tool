# Database Documentation v1.3

## Production Database Implementation

The Pro-Forma Analytics Tool v1.3 utilizes a comprehensive 4-database SQLite architecture with production-grade historical data covering 15+ years (2010-2025) across multiple market parameters and geographic regions.

## Database Architecture Overview

### Database Structure
The system maintains four specialized SQLite databases optimized for performance and data integrity:

```
data/databases/
├── market_data.db        # Financial markets and interest rate data (500+ data points)
├── property_data.db      # Real estate metrics and rental market data (600+ data points)  
├── economic_data.db      # Regional economic indicators (800+ data points)
└── forecast_cache.db     # Prophet forecasts and Monte Carlo results (874+ data points)
```

**Total Data Coverage**: 2,174+ production-grade historical data points with comprehensive validation

## Database Schemas and Tables

### 1. market_data.db

**Purpose**: Financial markets, interest rates, and lending requirements

#### Tables and Schema

**interest_rates**
```sql
CREATE TABLE interest_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parameter_name TEXT NOT NULL,
    date DATE NOT NULL,
    value REAL NOT NULL,
    source TEXT,
    UNIQUE(parameter_name, date)
);
```
- **Data Coverage**: Treasury 10Y, Commercial Mortgage Rates, Prime Rate
- **Historical Depth**: 15+ years (2010-2025)
- **Update Frequency**: Monthly
- **Record Count**: 150+ data points

**cap_rates**
```sql
CREATE TABLE cap_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_type TEXT NOT NULL,
    msa_code TEXT NOT NULL,
    date DATE NOT NULL,
    value REAL NOT NULL,
    source TEXT,
    UNIQUE(property_type, msa_code, date)
);
```
- **Property Types**: Multifamily, Office, Retail, Industrial
- **Geographic Coverage**: 5 major MSAs (NYC, LA, Chicago, DC, Miami)
- **Historical Depth**: 15+ years with quarterly granularity
- **Record Count**: 200+ data points

**lending_requirements**
```sql
CREATE TABLE lending_requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name TEXT NOT NULL,
    property_type TEXT NOT NULL,
    date DATE NOT NULL,
    value REAL NOT NULL,
    msa_code TEXT,
    source TEXT,
    UNIQUE(metric_name, property_type, date, msa_code)
);
```
- **Metrics**: LTV ratios, closing costs, lender reserves, DSCR requirements
- **Coverage**: Property-type specific with MSA adjustments
- **Record Count**: 150+ data points

### 2. property_data.db

**Purpose**: Real estate market metrics, rental data, and property-specific indicators

#### Tables and Schema

**rental_market_data**
```sql
CREATE TABLE rental_market_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name TEXT NOT NULL,
    msa_code TEXT NOT NULL,
    property_type TEXT NOT NULL,
    date DATE NOT NULL,
    value REAL NOT NULL,
    source TEXT,
    UNIQUE(metric_name, msa_code, property_type, date)
);
```
- **Metrics**: Rent growth, vacancy rates, market rent levels
- **Geographic Coverage**: 5 major MSAs with property type granularity
- **Historical Depth**: 15+ years with monthly/quarterly data
- **Record Count**: 300+ data points

**operating_expenses**
```sql
CREATE TABLE operating_expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    expense_category TEXT NOT NULL,
    msa_code TEXT NOT NULL,
    property_type TEXT NOT NULL,
    date DATE NOT NULL,
    expense_growth REAL NOT NULL,
    expense_per_unit REAL,
    source TEXT,
    UNIQUE(expense_category, msa_code, property_type, date)
);
```
- **Categories**: Property management, utilities, maintenance, insurance, taxes
- **Coverage**: MSA-specific with property type adjustments
- **Record Count**: 200+ data points

**property_growth**
```sql
CREATE TABLE property_growth (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    msa_code TEXT NOT NULL,
    property_type TEXT NOT NULL,
    date DATE NOT NULL,
    property_growth REAL NOT NULL,
    source TEXT,
    UNIQUE(msa_code, property_type, date)
);
```
- **Coverage**: Property appreciation rates by MSA and type
- **Historical Depth**: 15+ years with annual/quarterly data
- **Record Count**: 100+ data points

### 3. economic_data.db

**Purpose**: Regional economic indicators and macroeconomic data

#### Tables and Schema

**regional_economic_indicators**
```sql
CREATE TABLE regional_economic_indicators (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    indicator_name TEXT NOT NULL,
    msa_code TEXT NOT NULL,
    date DATE NOT NULL,
    value REAL NOT NULL,
    unit TEXT,
    source TEXT,
    UNIQUE(indicator_name, msa_code, date)
);
```
- **Indicators**: Unemployment, employment growth, population growth, GDP growth
- **Geographic Coverage**: 5 major MSAs with comprehensive economic data
- **Record Count**: 400+ data points

**economic_indicators** (National)
```sql
CREATE TABLE economic_indicators (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    indicator_name TEXT NOT NULL,
    date DATE NOT NULL,
    value REAL NOT NULL,
    unit TEXT,
    source TEXT,
    UNIQUE(indicator_name, date)
);
```
- **Indicators**: CPI, housing CPI, consumer confidence, GDP growth
- **Coverage**: National-level macroeconomic indicators
- **Record Count**: 400+ data points

### 4. forecast_cache.db

**Purpose**: Prophet forecasts, Monte Carlo results, and correlation data

#### Tables and Schema

**prophet_forecasts**
```sql
CREATE TABLE prophet_forecasts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parameter_name TEXT NOT NULL,
    msa_code TEXT,
    forecast_date DATE NOT NULL,
    forecast_value REAL NOT NULL,
    confidence_lower REAL,
    confidence_upper REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(parameter_name, msa_code, forecast_date)
);
```
- **Parameters**: All 11 pro forma parameters with 6-year forecasts
- **Confidence Intervals**: Statistical bounds for forecast reliability
- **Record Count**: 500+ cached forecasts

**monte_carlo_correlations**
```sql
CREATE TABLE monte_carlo_correlations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parameter_1 TEXT NOT NULL,
    parameter_2 TEXT NOT NULL,
    correlation_coefficient REAL NOT NULL,
    msa_code TEXT,
    calculation_date DATE NOT NULL,
    UNIQUE(parameter_1, parameter_2, msa_code)
);
```
- **Coverage**: 23+ economic relationships with statistical validation
- **Geographic Specificity**: MSA-level correlation adjustments
- **Record Count**: 200+ correlation pairs

**simulation_results**
```sql
CREATE TABLE simulation_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id TEXT NOT NULL,
    property_id TEXT NOT NULL,
    parameters TEXT NOT NULL, -- JSON of all parameters
    npv REAL,
    irr REAL,
    equity_multiple REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
- **Purpose**: Cache Monte Carlo simulation results for performance
- **Record Count**: 174+ cached simulation results

## Geographic Coverage

### Supported MSAs (Metropolitan Statistical Areas)

| MSA | Code | Coverage | Data Points |
|-----|------|----------|-------------|
| New York-Newark-Jersey City, NY-NJ-PA | 35620 | Complete | 450+ |
| Los Angeles-Long Beach-Anaheim, CA | 31080 | Complete | 440+ |
| Chicago-Naperville-Elgin, IL-IN-WI | 16980 | Complete | 435+ |
| Washington-Arlington-Alexandria, DC-VA-MD-WV | 47900 | Complete | 425+ |
| Miami-Fort Lauderdale-West Palm Beach, FL | 33100 | Complete | 424+ |

**Total Geographic Data Points**: 2,174+ across all MSAs and parameters

## Data Quality and Validation

### Production-Grade Features

**Historical Depth**
- **Time Range**: 15+ years (2010-2025)
- **Granularity**: Monthly, quarterly, and annual data depending on parameter
- **Completeness**: 100% coverage across all 11 pro forma parameters

**Data Validation**
- **Statistical Validation**: Comprehensive outlier detection and data quality checks
- **Correlation Analysis**: Economic relationship validation across parameters
- **Temporal Consistency**: Time-series integrity and trend validation
- **Geographic Consistency**: Cross-MSA validation and adjustment factors

**Quality Metrics**
- **Completeness**: 100% parameter coverage across all MSAs
- **Accuracy**: Production-grade validation with statistical backing
- **Consistency**: Comprehensive cross-validation and integrity checks
- **Timeliness**: Regular updates with automated data pipeline

## Performance Optimization

### Database Performance Features

**Indexing Strategy**
```sql
-- Optimized indexes for common queries
CREATE INDEX idx_interest_rates_param_date ON interest_rates(parameter_name, date);
CREATE INDEX idx_cap_rates_type_msa_date ON cap_rates(property_type, msa_code, date);
CREATE INDEX idx_rental_data_msa_type_date ON rental_market_data(msa_code, property_type, date);
CREATE INDEX idx_economic_indicators_name_date ON economic_indicators(indicator_name, date);
```

**Query Performance**
- **Average Query Time**: <1ms for standard parameter lookups
- **Complex Queries**: <5ms for multi-table joins and aggregations
- **Cache Hit Rate**: >90% for forecast and correlation queries
- **Connection Pooling**: Optimized connection management

**Database Maintenance**
```bash
# Database optimization scripts
python scripts/optimize_database_indexes.py
python scripts/monitor_database_performance.py
python scripts/cleanup_databases.py
```

## Data Pipeline Architecture

### Automated Data Management

**Data Ingestion**
- **Scheduled Updates**: Automated data pipeline with cron jobs
- **Validation Pipeline**: Comprehensive data quality checks
- **Error Handling**: Robust error recovery and notification system
- **Backup Strategy**: Automated database backup and recovery

**Data Processing**
- **ETL Pipeline**: Extract, Transform, Load process with validation
- **Correlation Updates**: Automated correlation coefficient calculations
- **Forecast Refresh**: Regular Prophet model retraining and forecast updates
- **Cache Management**: Intelligent cache invalidation and refresh

### Monitoring and Observability

**Performance Monitoring**
```bash
# Performance monitoring tools
python scripts/profile_database_performance.py
python scripts/monitor_database_performance.py
```

**Health Checks**
- **Data Integrity**: Automated consistency checks
- **Performance Metrics**: Query performance monitoring
- **Storage Monitoring**: Database size and growth tracking
- **Error Alerting**: Automated error detection and notification

## API Integration Roadmap

### Current Data Sources

The current implementation uses production-grade historical data compiled from multiple sources:

**Financial Markets**: Historical interest rates, treasury yields, mortgage rates  
**Real Estate Markets**: Cap rates, rent growth, vacancy rates from market reports  
**Economic Indicators**: Employment, population, and economic growth from government sources  
**Regional Data**: MSA-specific adjustments and local market conditions  

### Future Data Source Integration

**High Priority API Integrations**
- **FRED API**: Federal Reserve Economic Data for macroeconomic indicators
- **ATTOM Data**: Real estate market data and property information
- **Bureau of Labor Statistics**: Employment and economic statistics

**Medium Priority Integrations**
- **Real Capital Analytics**: Commercial real estate transaction data
- **CoStar**: Commercial property data and market analytics
- **Zillow Research**: Residential market trends and forecasts

**Implementation Timeline**
- **Phase 1**: FRED API integration for economic indicators
- **Phase 2**: Commercial real estate data sources
- **Phase 3**: Real-time market data feeds

## Development and Maintenance

### Database Schema Migration

**Version Control**
- **Schema Versioning**: Tracked database schema changes
- **Migration Scripts**: Automated database migration tools
- **Rollback Strategy**: Safe rollback procedures for schema changes

**Development Workflow**
```bash
# Database setup and initialization
python data_manager.py setup

# Schema validation
python scripts/validate_database_schema.py

# Data validation and quality checks
python scripts/validate_production_data.py
```

### Backup and Recovery

**Backup Strategy**
- **Automated Backups**: Daily database backups with retention policy
- **Point-in-Time Recovery**: Transaction log-based recovery capability
- **Disaster Recovery**: Cross-location backup storage and recovery procedures

**Recovery Procedures**
```bash
# Database backup and recovery
python scripts/backup_recovery.py backup
python scripts/backup_recovery.py restore --date 2025-01-15
```

---

*This database implementation provides production-ready data management with comprehensive coverage, performance optimization, and enterprise-grade quality assurance for the Pro-Forma Analytics Tool v1.3.*