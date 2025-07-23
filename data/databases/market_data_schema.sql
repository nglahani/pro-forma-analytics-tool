-- Market Data Database Schema
-- Contains financial markets and macroeconomic data

-- =============================================================================
-- INTEREST RATES TABLE
-- =============================================================================

-- Interest rate data from FRED and other sources
CREATE TABLE IF NOT EXISTS interest_rates (
    date DATE NOT NULL,
    parameter_name TEXT NOT NULL,  -- e.g., 'treasury_10y', 'commercial_mortgage_rate'
    value REAL NOT NULL,  -- Interest rate as decimal (e.g., 0.05 for 5%)
    geographic_code TEXT NOT NULL,  -- MSA code, 'NATIONAL', etc.
    data_source TEXT NOT NULL,  -- 'FRED', 'BLS', 'Custom'
    PRIMARY KEY(date, parameter_name, geographic_code)
);

-- =============================================================================
-- CAP RATES TABLE
-- =============================================================================

-- Cap rates for different property types and geographies
CREATE TABLE IF NOT EXISTS cap_rates (
    date DATE NOT NULL,
    property_type TEXT NOT NULL,  -- 'multifamily', 'office', 'retail', etc.
    value REAL NOT NULL,  -- Cap rate as decimal
    geographic_code TEXT NOT NULL,  -- MSA code or county FIPS
    data_source TEXT NOT NULL,
    PRIMARY KEY(date, property_type, geographic_code)
);

-- =============================================================================
-- ECONOMIC INDICATORS TABLE
-- =============================================================================

-- General economic indicators (national level)
CREATE TABLE IF NOT EXISTS economic_indicators (
    date DATE NOT NULL,
    indicator_name TEXT NOT NULL,  -- 'cpi_housing', 'unemployment_rate', etc.
    value REAL NOT NULL,
    geographic_code TEXT NOT NULL,
    data_source TEXT NOT NULL,
    PRIMARY KEY(date, indicator_name, geographic_code)
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- Interest rates indexes
CREATE INDEX IF NOT EXISTS idx_interest_rates_param ON interest_rates(parameter_name);
CREATE INDEX IF NOT EXISTS idx_interest_rates_geo ON interest_rates(geographic_code);

-- Cap rates indexes  
CREATE INDEX IF NOT EXISTS idx_cap_rates_type ON cap_rates(property_type);
CREATE INDEX IF NOT EXISTS idx_cap_rates_geo ON cap_rates(geographic_code);

-- Economic indicators indexes
CREATE INDEX IF NOT EXISTS idx_economic_indicator ON economic_indicators(indicator_name);
CREATE INDEX IF NOT EXISTS idx_economic_geo ON economic_indicators(geographic_code);