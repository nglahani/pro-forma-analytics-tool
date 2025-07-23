-- Economic Data Database Schema
-- Contains regional economic indicators and demographic data

-- =============================================================================
-- REGIONAL ECONOMIC INDICATORS TABLE
-- =============================================================================

-- Regional economic indicators (MSA/county specific)
CREATE TABLE IF NOT EXISTS regional_economic_indicators (
    date DATE NOT NULL,
    indicator_name TEXT NOT NULL,  -- 'unemployment_rate', 'employment_growth', etc.
    value REAL NOT NULL,
    geographic_code TEXT NOT NULL,  -- MSA code or county FIPS
    data_source TEXT NOT NULL,
    PRIMARY KEY(date, indicator_name, geographic_code)
);

-- =============================================================================
-- PROPERTY GROWTH TABLE
-- =============================================================================

-- Property value growth rates by region
CREATE TABLE IF NOT EXISTS property_growth (
    date DATE NOT NULL,
    property_growth REAL NOT NULL,  -- Annual property value growth rate
    geographic_code TEXT NOT NULL,
    data_source TEXT NOT NULL,
    PRIMARY KEY(date, geographic_code)
);

-- =============================================================================
-- LENDING REQUIREMENTS TABLE
-- =============================================================================

-- Lender reserve requirements and closing costs
CREATE TABLE IF NOT EXISTS lending_requirements (
    date DATE NOT NULL,
    metric_name TEXT NOT NULL,  -- 'ltv_ratio', 'closing_cost_pct', 'lender_reserves'
    value REAL NOT NULL,
    geographic_code TEXT NOT NULL,
    data_source TEXT NOT NULL,
    PRIMARY KEY(date, metric_name, geographic_code)
);


-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- Regional economic indicators indexes
CREATE INDEX IF NOT EXISTS idx_regional_econ_indicator ON regional_economic_indicators(indicator_name);
CREATE INDEX IF NOT EXISTS idx_regional_econ_geo ON regional_economic_indicators(geographic_code);

-- Property growth indexes
CREATE INDEX IF NOT EXISTS idx_property_growth_geo ON property_growth(geographic_code);

-- Lending requirements indexes
CREATE INDEX IF NOT EXISTS idx_lending_metric ON lending_requirements(metric_name);
CREATE INDEX IF NOT EXISTS idx_lending_geo ON lending_requirements(geographic_code);