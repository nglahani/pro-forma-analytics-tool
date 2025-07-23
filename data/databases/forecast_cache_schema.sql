-- Forecast Cache Database Schema
-- Contains ARIMA forecasts, correlations, and Monte Carlo simulation results

-- =============================================================================
-- ARIMA FORECASTS TABLE
-- =============================================================================

-- Cached ARIMA forecasts
CREATE TABLE IF NOT EXISTS arima_forecasts (
    parameter_name TEXT NOT NULL,
    geographic_code TEXT NOT NULL,
    forecast_date DATE NOT NULL,  -- Date forecast was generated
    forecast_horizon_years INTEGER NOT NULL,
    forecast_values TEXT NOT NULL,  -- JSON array of forecasted values
    confidence_intervals TEXT NOT NULL,  -- JSON object with confidence bands
    PRIMARY KEY(parameter_name, geographic_code, forecast_date, forecast_horizon_years)
);

-- =============================================================================
-- PARAMETER CORRELATIONS TABLE
-- =============================================================================

-- Parameter correlation matrices
CREATE TABLE IF NOT EXISTS parameter_correlations (
    geographic_code TEXT NOT NULL,
    correlation_matrix TEXT NOT NULL,  -- JSON correlation matrix
    parameter_names TEXT NOT NULL,  -- JSON array of parameter names
    calculation_date DATE NOT NULL,
    PRIMARY KEY(geographic_code, calculation_date)
);

-- =============================================================================
-- MONTE CARLO RESULTS TABLE
-- =============================================================================

-- Monte Carlo simulation results
CREATE TABLE IF NOT EXISTS monte_carlo_results (
    simulation_id TEXT PRIMARY KEY,  -- UUID for simulation run
    geographic_code TEXT NOT NULL,
    forecast_horizon_years INTEGER NOT NULL,
    result_statistics TEXT NOT NULL,  -- JSON with percentiles, mean, std
    simulation_date DATE NOT NULL
);


-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- Forecast indexes
CREATE INDEX IF NOT EXISTS idx_forecasts_param ON arima_forecasts(parameter_name);
CREATE INDEX IF NOT EXISTS idx_forecasts_geo ON arima_forecasts(geographic_code);

-- Correlation indexes
CREATE INDEX IF NOT EXISTS idx_correlations_geo ON parameter_correlations(geographic_code);

-- Monte Carlo indexes
CREATE INDEX IF NOT EXISTS idx_monte_carlo_geo ON monte_carlo_results(geographic_code);