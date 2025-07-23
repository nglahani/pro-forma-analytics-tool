-- Property Data Database Schema
-- Contains real estate specific data and property market metrics

-- =============================================================================
-- RENTAL MARKET DATA TABLE
-- =============================================================================

-- Rental market data (rents, vacancy rates)
CREATE TABLE IF NOT EXISTS rental_market_data (
    date DATE NOT NULL,
    metric_name TEXT NOT NULL,  -- 'rent_growth', 'vacancy_rate'
    value REAL NOT NULL,
    geographic_code TEXT NOT NULL,  -- MSA or county code
    data_source TEXT NOT NULL,  -- 'ACS', 'ApartmentList', 'RentData', etc.
    PRIMARY KEY(date, metric_name, geographic_code)
);

-- =============================================================================
-- PROPERTY TAX DATA TABLE
-- =============================================================================

-- Property tax and assessment data
CREATE TABLE IF NOT EXISTS property_tax_data (
    date DATE NOT NULL,
    tax_rate REAL NOT NULL,  -- Effective tax rate as decimal
    geographic_code TEXT NOT NULL,  -- County FIPS code
    data_source TEXT NOT NULL,
    PRIMARY KEY(date, geographic_code)
);

-- =============================================================================
-- OPERATING EXPENSES TABLE
-- =============================================================================

-- Operating expense growth rates
CREATE TABLE IF NOT EXISTS operating_expenses (
    date DATE NOT NULL,
    expense_growth REAL NOT NULL,  -- Annual expense growth rate as decimal
    geographic_code TEXT NOT NULL,
    data_source TEXT NOT NULL,
    PRIMARY KEY(date, geographic_code)
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- Rental market indexes
CREATE INDEX IF NOT EXISTS idx_rental_metric ON rental_market_data(metric_name);
CREATE INDEX IF NOT EXISTS idx_rental_geo ON rental_market_data(geographic_code);

-- Property tax indexes
CREATE INDEX IF NOT EXISTS idx_property_tax_geo ON property_tax_data(geographic_code);

-- Operating expenses indexes
CREATE INDEX IF NOT EXISTS idx_operating_exp_geo ON operating_expenses(geographic_code);