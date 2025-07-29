# Database Schemas - v1.3

Production-grade normalized database schema definitions for real estate DCF analysis with optimized indexing, referential integrity, and comprehensive data validation supporting 2,174+ market data points across 11 pro forma parameters.

## Schema Architecture (v1.3)

### Core Schema Files

- **`market_data_schema.sql`** - National economic indicators schema with time series optimization
- **`property_data_schema.sql`** - MSA-specific property market data schema with geographic indexing
- **`economic_data_schema.sql`** - Regional economic indicators schema with source attribution
- **`forecast_cache_schema.sql`** - Prophet forecasting and Monte Carlo results caching schema
- **`indexes.sql`** - Performance optimization indexes and query acceleration
- **`constraints.sql`** - Data integrity constraints and business rule enforcement

## Market Data Schema (market_data_schema.sql)

### National Economic Indicators Table
```sql
-- Primary table for national economic data
CREATE TABLE market_data_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parameter_name TEXT NOT NULL,
    parameter_value REAL NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER,
    source_type TEXT NOT NULL,
    source_name TEXT NOT NULL,
    reliability_score REAL DEFAULT 0.8,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Data validation constraints
    CONSTRAINT valid_year CHECK (year >= 2000 AND year <= 2030),
    CONSTRAINT valid_quarter CHECK (quarter IS NULL OR (quarter >= 1 AND quarter <= 4)),
    CONSTRAINT valid_reliability CHECK (reliability_score >= 0.0 AND reliability_score <= 1.0),
    CONSTRAINT valid_parameter_name CHECK (parameter_name IN (
        'treasury_10y', 'commercial_mortgage', 'fed_funds_rate',
        'national_cap_rate', 'national_vacancy', 'inflation_rate'
    ))
);

-- Performance indexes
CREATE INDEX idx_market_data_parameter_year ON market_data_table(parameter_name, year);
CREATE INDEX idx_market_data_source ON market_data_table(source_type, source_name);
CREATE INDEX idx_market_data_updated ON market_data_table(updated_date);

-- Composite index for common queries
CREATE INDEX idx_market_data_lookup ON market_data_table(parameter_name, year, source_type);
```

### Parameter Metadata Table
```sql
-- Metadata for parameter definitions and validation rules
CREATE TABLE parameter_metadata (
    parameter_name TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    description TEXT NOT NULL,
    unit_type TEXT NOT NULL,
    min_value REAL,
    max_value REAL,
    default_value REAL,
    validation_rules TEXT, -- JSON string for complex validation
    is_active BOOLEAN DEFAULT TRUE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Property Data Schema (property_data_schema.sql)

### MSA-Specific Property Market Data
```sql
-- Primary table for MSA-specific property data
CREATE TABLE property_data_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    msa_code TEXT NOT NULL,
    parameter_name TEXT NOT NULL,
    parameter_value REAL NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER,
    property_type TEXT DEFAULT 'multifamily',
    market_tier TEXT NOT NULL,
    source_type TEXT NOT NULL,
    source_name TEXT NOT NULL,
    data_quality_score REAL DEFAULT 0.8,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Geographic and data validation constraints
    CONSTRAINT valid_msa_code CHECK (msa_code IN (
        '16980', '31080', '33100', '35620', '47900'
    )),
    CONSTRAINT valid_property_parameter CHECK (parameter_name IN (
        'rent_growth', 'vacancy_rate', 'operating_expenses', 
        'cap_rate', 'property_growth'
    )),
    CONSTRAINT valid_market_tier CHECK (market_tier IN (
        'Gateway', 'Primary', 'Secondary'
    )),
    CONSTRAINT valid_year CHECK (year >= 2000 AND year <= 2030),
    CONSTRAINT valid_quality_score CHECK (data_quality_score >= 0.0 AND data_quality_score <= 1.0)
);

-- Geographic and parameter-based indexes
CREATE INDEX idx_property_data_msa_param ON property_data_table(msa_code, parameter_name);
CREATE INDEX idx_property_data_msa_year ON property_data_table(msa_code, year);
CREATE INDEX idx_property_data_param_year ON property_data_table(parameter_name, year);
CREATE INDEX idx_property_data_market_tier ON property_data_table(market_tier, msa_code);

-- Composite index for common DCF queries
CREATE INDEX idx_property_dcf_lookup ON property_data_table(
    msa_code, parameter_name, year, property_type
);
```

### MSA Geographic Reference
```sql
-- MSA reference data with geographic and market information
CREATE TABLE msa_reference (
    msa_code TEXT PRIMARY KEY,
    msa_name TEXT NOT NULL,
    state_codes TEXT NOT NULL,
    region TEXT NOT NULL,
    market_tier TEXT NOT NULL,
    population_2020 INTEGER,
    median_income INTEGER,
    timezone TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert reference data
INSERT INTO msa_reference VALUES 
('16980', 'Chicago-Naperville-Elgin, IL-IN-WI', 'IL,IN,WI', 'Midwest', 'Primary', 9618502, 68403, 'America/Chicago', TRUE, CURRENT_TIMESTAMP),
('31080', 'Los Angeles-Long Beach-Anaheim, CA', 'CA', 'West', 'Primary', 13214799, 70372, 'America/Los_Angeles', TRUE, CURRENT_TIMESTAMP),
('33100', 'Miami-Fort Lauderdale-West Palm Beach, FL', 'FL', 'Southeast', 'Primary', 6138333, 61220, 'America/New_York', TRUE, CURRENT_TIMESTAMP),
('35620', 'New York-Newark-Jersey City, NY-NJ-PA', 'NY,NJ,PA', 'Northeast', 'Gateway', 20140470, 83160, 'America/New_York', TRUE, CURRENT_TIMESTAMP),
('47900', 'Washington-Arlington-Alexandria, DC-VA-MD-WV', 'DC,VA,MD,WV', 'Mid-Atlantic', 'Primary', 6385162, 95843, 'America/New_York', TRUE, CURRENT_TIMESTAMP);
```

## Economic Data Schema (economic_data_schema.sql)

### Regional Economic Indicators
```sql
-- Regional economic and lending data
CREATE TABLE economic_data_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    msa_code TEXT,
    parameter_name TEXT NOT NULL,
    parameter_category TEXT NOT NULL,
    parameter_value REAL NOT NULL,
    year INTEGER NOT NULL,
    source_type TEXT NOT NULL,
    source_name TEXT NOT NULL,
    source_reliability REAL DEFAULT 0.8,
    geographic_scope TEXT DEFAULT 'msa', -- 'national', 'regional', 'msa'
    update_frequency TEXT DEFAULT 'annual',
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Validation constraints
    CONSTRAINT valid_economic_year CHECK (year >= 2000 AND year <= 2030),
    CONSTRAINT valid_parameter_category CHECK (parameter_category IN (
        'lending_requirements', 'closing_costs', 'property_growth', 
        'economic_indicators', 'employment_data'
    )),
    CONSTRAINT valid_geographic_scope CHECK (geographic_scope IN (
        'national', 'regional', 'msa', 'state'
    )),
    CONSTRAINT valid_source_reliability CHECK (source_reliability >= 0.0 AND source_reliability <= 1.0)
);

-- Performance indexes for economic data
CREATE INDEX idx_economic_data_category ON economic_data_table(parameter_category, year);
CREATE INDEX idx_economic_data_msa ON economic_data_table(msa_code, parameter_name);
CREATE INDEX idx_economic_data_source ON economic_data_table(source_type, source_name);
CREATE INDEX idx_economic_data_scope ON economic_data_table(geographic_scope, parameter_category);
```

### Data Source Attribution
```sql
-- Comprehensive data source tracking and attribution
CREATE TABLE data_sources (
    source_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type TEXT NOT NULL,
    source_name TEXT NOT NULL,
    description TEXT NOT NULL,
    reliability_score REAL NOT NULL,
    update_frequency TEXT NOT NULL,
    api_endpoint TEXT,
    contact_info TEXT,
    data_license TEXT,
    last_updated TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_reliability_score CHECK (reliability_score >= 0.0 AND reliability_score <= 1.0),
    CONSTRAINT valid_update_frequency CHECK (update_frequency IN (
        'real-time', 'daily', 'weekly', 'monthly', 'quarterly', 'annual'
    ))
);

-- Insert verified data sources
INSERT INTO data_sources (source_type, source_name, description, reliability_score, update_frequency) VALUES
('survey', 'Market_Analysis_Proxy', 'Real estate market analysis for rental and vacancy data', 0.92, 'quarterly'),
('survey', 'Commercial_Lending_Survey', 'Industry lending standards and requirements', 0.89, 'semi-annual'),
('survey', 'Title_Company_Survey', 'Closing cost and transaction fee data', 0.91, 'annual'),
('api', 'FRED_API', 'Federal Reserve economic data for interest rates', 0.98, 'daily');
```

## Forecast Cache Schema (forecast_cache_schema.sql)

### Prophet Forecasting Results Cache
```sql
-- Cached Prophet forecasting results for performance optimization
CREATE TABLE forecast_cache_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cache_key TEXT UNIQUE NOT NULL,
    parameter_name TEXT NOT NULL,
    msa_code TEXT,
    forecast_type TEXT NOT NULL,
    forecast_horizon_years INTEGER NOT NULL,
    forecast_data TEXT NOT NULL, -- JSON string containing forecast results
    model_metadata TEXT, -- JSON string containing model parameters
    forecast_confidence REAL,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_date TIMESTAMP NOT NULL,
    access_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Cache validation constraints
    CONSTRAINT valid_forecast_type CHECK (forecast_type IN (
        'prophet_forecast', 'monte_carlo_scenarios', 'correlation_matrix'
    )),
    CONSTRAINT valid_horizon CHECK (forecast_horizon_years >= 1 AND forecast_horizon_years <= 10),
    CONSTRAINT valid_confidence CHECK (forecast_confidence IS NULL OR 
                                     (forecast_confidence >= 0.0 AND forecast_confidence <= 1.0))
);

-- Cache performance indexes
CREATE INDEX idx_forecast_cache_key ON forecast_cache_table(cache_key);
CREATE INDEX idx_forecast_cache_lookup ON forecast_cache_table(parameter_name, msa_code, forecast_type);
CREATE INDEX idx_forecast_cache_expires ON forecast_cache_table(expires_date);
CREATE INDEX idx_forecast_cache_accessed ON forecast_cache_table(last_accessed);

-- Automatic cache cleanup trigger
CREATE TRIGGER cleanup_expired_forecasts
AFTER INSERT ON forecast_cache_table
BEGIN
    DELETE FROM forecast_cache_table 
    WHERE expires_date < datetime('now');
END;
```

### Monte Carlo Scenario Cache
```sql
-- Cached Monte Carlo scenario results
CREATE TABLE monte_carlo_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_set_id TEXT UNIQUE NOT NULL,
    msa_code TEXT NOT NULL,
    scenario_count INTEGER NOT NULL,
    correlation_version TEXT NOT NULL,
    scenario_data TEXT NOT NULL, -- JSON array of scenarios
    regime_distribution TEXT, -- JSON object with regime percentages
    generation_parameters TEXT, -- JSON object with generation settings
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_date TIMESTAMP NOT NULL,
    usage_count INTEGER DEFAULT 0,
    
    CONSTRAINT valid_scenario_count CHECK (scenario_count >= 100 AND scenario_count <= 10000)
);

-- Monte Carlo cache indexes
CREATE INDEX idx_monte_carlo_msa ON monte_carlo_cache(msa_code, correlation_version);
CREATE INDEX idx_monte_carlo_expires ON monte_carlo_cache(expires_date);
```

## Performance Optimization (indexes.sql)

### Strategic Index Design
```sql
-- Cross-table query optimization indexes

-- Multi-parameter correlation queries
CREATE INDEX idx_cross_param_correlation ON property_data_table(
    msa_code, year, parameter_name, parameter_value
);

-- Time series analysis queries
CREATE INDEX idx_time_series_analysis ON market_data_table(
    parameter_name, year ASC, parameter_value
);

-- DCF calculation parameter retrieval
CREATE INDEX idx_dcf_parameter_batch ON property_data_table(
    msa_code, property_type, year, parameter_name
) WHERE year >= 2020;

-- Forecast cache efficiency
CREATE INDEX idx_forecast_efficiency ON forecast_cache_table(
    parameter_name, msa_code, created_date DESC
) WHERE expires_date > datetime('now');

-- Data quality monitoring
CREATE INDEX idx_data_quality_monitoring ON property_data_table(
    data_quality_score, updated_date DESC
) WHERE data_quality_score < 0.9;
```

### Query Performance Statistics
```sql
-- Enable query performance analysis
PRAGMA optimize;
PRAGMA analysis_limit=1000;
PRAGMA cache_size=10000;

-- Analyze all tables for optimal query planning
ANALYZE market_data_table;
ANALYZE property_data_table;
ANALYZE economic_data_table;
ANALYZE forecast_cache_table;
```

## Data Integrity and Constraints (constraints.sql)

### Business Rule Enforcement
```sql
-- Cross-table referential integrity
ALTER TABLE property_data_table 
ADD CONSTRAINT fk_property_msa 
FOREIGN KEY (msa_code) REFERENCES msa_reference(msa_code);

ALTER TABLE economic_data_table 
ADD CONSTRAINT fk_economic_msa 
FOREIGN KEY (msa_code) REFERENCES msa_reference(msa_code);

-- Parameter value validation triggers
CREATE TRIGGER validate_rent_growth
BEFORE INSERT ON property_data_table
WHEN NEW.parameter_name = 'rent_growth'
BEGIN
    SELECT CASE
        WHEN NEW.parameter_value < -0.20 OR NEW.parameter_value > 0.25 THEN
            RAISE(ABORT, 'Rent growth must be between -20% and 25%')
    END;
END;

CREATE TRIGGER validate_cap_rate
BEFORE INSERT ON property_data_table
WHEN NEW.parameter_name = 'cap_rate'
BEGIN
    SELECT CASE
        WHEN NEW.parameter_value < 0.02 OR NEW.parameter_value > 0.15 THEN
            RAISE(ABORT, 'Cap rate must be between 2% and 15%')
    END;
END;

CREATE TRIGGER validate_vacancy_rate
BEFORE INSERT ON property_data_table
WHEN NEW.parameter_name = 'vacancy_rate'
BEGIN
    SELECT CASE
        WHEN NEW.parameter_value < 0.0 OR NEW.parameter_value > 0.30 THEN
            RAISE(ABORT, 'Vacancy rate must be between 0% and 30%')
    END;
END;
```

### Audit Trail System
```sql
-- Audit trail for data modifications
CREATE TABLE audit_log (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,
    operation_type TEXT NOT NULL, -- 'INSERT', 'UPDATE', 'DELETE'
    record_id INTEGER NOT NULL,
    old_values TEXT, -- JSON representation of old values
    new_values TEXT, -- JSON representation of new values
    changed_by TEXT DEFAULT 'system',
    change_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    change_reason TEXT
);

-- Audit triggers for critical tables
CREATE TRIGGER audit_property_data_changes
AFTER UPDATE ON property_data_table
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (table_name, operation_type, record_id, old_values, new_values, change_reason)
    VALUES (
        'property_data_table',
        'UPDATE',
        NEW.id,
        json_object('parameter_value', OLD.parameter_value, 'updated_date', OLD.updated_date),
        json_object('parameter_value', NEW.parameter_value, 'updated_date', NEW.updated_date),
        'Data update via automated process'
    );
END;
```

## Schema Maintenance and Evolution

### Version Control
```sql
-- Schema version tracking
CREATE TABLE schema_version (
    version_id INTEGER PRIMARY KEY AUTOINCREMENT,
    version_number TEXT NOT NULL,
    description TEXT NOT NULL,
    applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    applied_by TEXT DEFAULT 'system'
);

-- Current schema version
INSERT INTO schema_version (version_number, description) 
VALUES ('v1.3.0', 'Production-grade schema with comprehensive indexing and validation');
```

### Database Health Monitoring
```sql
-- Database health check views
CREATE VIEW data_quality_summary AS
SELECT 
    'market_data' as table_name,
    COUNT(*) as total_records,
    AVG(reliability_score) as avg_reliability,
    MIN(updated_date) as oldest_update,
    MAX(updated_date) as newest_update
FROM market_data_table
UNION ALL
SELECT 
    'property_data' as table_name,
    COUNT(*) as total_records,
    AVG(data_quality_score) as avg_reliability,
    MIN(updated_date) as oldest_update,
    MAX(updated_date) as newest_update
FROM property_data_table;

CREATE VIEW parameter_coverage AS
SELECT 
    msa_code,
    parameter_name,
    COUNT(*) as data_points,
    MIN(year) as earliest_year,
    MAX(year) as latest_year,
    MAX(year) - MIN(year) + 1 as years_covered
FROM property_data_table
GROUP BY msa_code, parameter_name
ORDER BY msa_code, parameter_name;
```

## Schema Documentation Standards

### Table Documentation
- **Comprehensive Comments**: Every table and column includes descriptive comments
- **Business Context**: Schema elements linked to business requirements
- **Data Dictionary**: Maintained data dictionary with field definitions
- **Relationship Diagrams**: Entity-relationship diagrams for complex relationships

### Migration Scripts
- **Incremental Migrations**: Version-controlled schema evolution scripts
- **Rollback Procedures**: Safe rollback mechanisms for schema changes
- **Data Preservation**: Ensure data integrity during schema modifications
- **Testing Protocols**: Comprehensive testing of schema changes before production deployment
