"""
API Documentation Examples

Comprehensive example objects for OpenAPI documentation and interactive testing.
These examples provide realistic data that demonstrates proper API usage.
"""

from datetime import date, datetime
from typing import Any, Dict

# =============================================================================
# PROPERTY REQUEST EXAMPLES
# =============================================================================

EXAMPLE_PROPERTY_REQUEST_BASIC = {
    "property_data": {
        "property_id": "NYC_BASIC_001",
        "property_name": "Manhattan Multifamily Property",
        "analysis_date": "2025-07-31",
        "residential_units": {
            "total_units": 12,
            "average_rent_per_unit": 2800,
            "unit_types": "Mix: 6x1BR ($2,400), 6x2BR ($3,200)",
        },
        "renovation_info": {"status": "not_needed", "anticipated_duration_months": 0},
        "equity_structure": {
            "investor_equity_share_pct": 75.0,
            "self_cash_percentage": 30.0,
            "number_of_investors": 2,
        },
        "city": "New York",
        "state": "NY",
        "purchase_price": 2500000.0,
    },
    "options": {
        "monte_carlo_simulations": 1000,
        "forecast_horizon_years": 6,
        "include_scenarios": False,
        "confidence_level": 0.95,
        "detailed_cash_flows": False,
    },
}

EXAMPLE_PROPERTY_REQUEST_COMPREHENSIVE = {
    "property_data": {
        "property_id": "BKN_RENO_001",
        "property_name": "Brooklyn Heights Value-Add Opportunity",
        "analysis_date": "2025-07-31",
        "residential_units": {
            "total_units": 24,
            "average_rent_per_unit": 3200,
            "unit_types": "Mix: 12x1BR ($2,800), 12x2BR ($3,600)",
        },
        "renovation_info": {
            "status": "major_renovation",
            "anticipated_duration_months": 8,
        },
        "equity_structure": {
            "investor_equity_share_pct": 80.0,
            "self_cash_percentage": 25.0,
            "number_of_investors": 3,
        },
        "commercial_units": {
            "total_units": 2,
            "average_rent_per_unit": 4500,
            "unit_types": "Ground floor retail spaces",
        },
        "city": "Brooklyn",
        "state": "NY",
        "msa_code": "35620",
        "purchase_price": 4500000.0,
        "property_address": "123 Atlantic Avenue, Brooklyn Heights, NY 11201",
    },
    "options": {
        "monte_carlo_simulations": 5000,
        "forecast_horizon_years": 6,
        "include_scenarios": True,
        "confidence_level": 0.95,
        "detailed_cash_flows": True,
    },
    "request_id": "comprehensive_analysis_001",
}

EXAMPLE_PROPERTY_REQUEST_MINIMAL = {
    "property_data": {
        "property_id": "CHI_MIN_001",
        "property_name": "Chicago Minimal Example",
        "analysis_date": "2025-07-31",
        "residential_units": {"total_units": 8, "average_rent_per_unit": 1800},
        "renovation_info": {"status": "not_needed"},
        "equity_structure": {
            "investor_equity_share_pct": 70.0,
            "self_cash_percentage": 35.0,
        },
        "city": "Chicago",
        "state": "IL",
        "purchase_price": 1200000.0,
    }
}

# =============================================================================
# BATCH REQUEST EXAMPLES
# =============================================================================

EXAMPLE_BATCH_REQUEST = {
    "properties": [
        EXAMPLE_PROPERTY_REQUEST_BASIC,
        {
            "property_data": {
                "property_id": "LA_PROP_002",
                "property_name": "Los Angeles Investment Property",
                "analysis_date": "2025-07-31",
                "residential_units": {"total_units": 16, "average_rent_per_unit": 2400},
                "renovation_info": {
                    "status": "minor_renovation",
                    "anticipated_duration_months": 4,
                },
                "equity_structure": {
                    "investor_equity_share_pct": 80.0,
                    "self_cash_percentage": 20.0,
                },
                "city": "Los Angeles",
                "state": "CA",
                "purchase_price": 3200000.0,
            }
        },
    ],
    "parallel_processing": True,
    "max_concurrent": 5,
    "batch_id": "portfolio_analysis_batch_001",
}

# =============================================================================
# MONTE CARLO REQUEST EXAMPLES
# =============================================================================

EXAMPLE_MONTE_CARLO_REQUEST_BASIC = {
    "property_id": "NYC_MC_001",
    "msa_code": "35620",
    "num_scenarios": 1000,
    "horizon_years": 6,
    "use_correlations": True,
    "confidence_level": 0.95,
}

EXAMPLE_MONTE_CARLO_REQUEST_ADVANCED = {
    "property_id": "LA_MC_ADVANCED_001",
    "msa_code": "31080",
    "num_scenarios": 10000,
    "horizon_years": 8,
    "use_correlations": True,
    "confidence_level": 0.99,
    "request_id": "advanced_monte_carlo_simulation",
}

# =============================================================================
# RESPONSE EXAMPLES
# =============================================================================

EXAMPLE_DCF_RESPONSE = {
    "request_id": "comprehensive_analysis_001",
    "property_id": "BKN_RENO_001",
    "analysis_date": "2025-07-31T18:30:00Z",
    "financial_metrics": {
        "net_present_value": 2847901.0,
        "internal_rate_return": 0.324,
        "equity_multiple": 4.82,
        "payback_period_years": 4.2,
        "total_return": 0.892,
        "annualized_return": 0.324,
        "cash_on_cash_return": 0.156,
    },
    "cash_flows": {
        "property_id": "BKN_RENO_001",
        "total_investment": 1125000.0,
        "annual_cash_flows": [
            {
                "year": 1,
                "gross_rental_income": 0.0,
                "operating_expenses": 85000.0,
                "net_operating_income": -85000.0,
                "debt_service": 180000.0,
                "before_tax_cash_flow": -265000.0,
                "investor_distribution": -212000.0,
            },
            {
                "year": 2,
                "gross_rental_income": 864000.0,
                "operating_expenses": 229000.0,
                "net_operating_income": 635000.0,
                "debt_service": 180000.0,
                "before_tax_cash_flow": 455000.0,
                "investor_distribution": 364000.0,
            },
        ],
        "terminal_value": {
            "gross_sale_price": 7200000.0,
            "sale_costs": 432000.0,
            "net_sale_proceeds": 6768000.0,
            "remaining_debt": 2850000.0,
            "net_proceeds_to_equity": 3918000.0,
            "investor_proceeds": 3134400.0,
        },
    },
    "dcf_assumptions": {
        "interest_rates": {
            "treasury_10y": 0.045,
            "commercial_mortgage_rate": 0.072,
            "fed_funds_rate": 0.0525,
        },
        "market_assumptions": {
            "cap_rate": 0.065,
            "vacancy_rate": 0.05,
            "rent_growth_rate": 0.03,
            "expense_growth_rate": 0.025,
            "property_appreciation_rate": 0.032,
        },
        "financing_assumptions": {
            "ltv_ratio": 0.75,
            "loan_term_years": 30,
            "interest_rate": 0.072,
            "closing_costs_pct": 0.03,
        },
    },
    "investment_recommendation": {
        "recommendation": "STRONG_BUY",
        "confidence_level": "HIGH",
        "risk_assessment": "MODERATE",
        "key_strengths": [
            "Strong positive NPV ($2,847,901)",
            "Excellent IRR (32.4%)",
            "Strong equity multiple (4.82x)",
            "Attractive location in Brooklyn Heights",
        ],
        "key_risks": [
            "Extended renovation period with no income",
            "Market timing risk for value-add strategy",
            "Interest rate sensitivity",
        ],
        "investment_summary": "Attractive value-add opportunity with strong fundamentals and excellent location. The 8-month renovation period presents initial cash flow challenges but the projected returns justify the investment.",
    },
    "metadata": {
        "processing_time_seconds": 0.847,
        "dcf_engine_version": "1.5.0",
        "analysis_timestamp": "2025-07-31T18:30:00Z",
        "data_sources": {
            "market_data": "Historical Database",
            "forecasts": "Prophet Engine",
            "assumptions": "Monte Carlo Simulation",
        },
        "assumptions_summary": {
            "scenarios_analyzed": 5000,
            "forecast_horizon_years": 6,
            "confidence_level": 0.95,
        },
    },
}

EXAMPLE_MONTE_CARLO_RESPONSE = {
    "request_id": "advanced_monte_carlo_simulation",
    "property_id": "LA_MC_ADVANCED_001",
    "simulation_date": "2025-07-31T18:45:00Z",
    "num_scenarios": 10000,
    "horizon_years": 8,
    "statistical_summary": {
        "cap_rate": {
            "mean": 0.058,
            "std": 0.012,
            "p5": 0.042,
            "p25": 0.051,
            "p50": 0.058,
            "p75": 0.065,
            "p95": 0.078,
        },
        "rent_growth": {
            "mean": 0.035,
            "std": 0.018,
            "p5": 0.008,
            "p25": 0.024,
            "p50": 0.035,
            "p75": 0.046,
            "p95": 0.068,
        },
        "property_growth": {
            "mean": 0.028,
            "std": 0.015,
            "p5": 0.005,
            "p25": 0.019,
            "p50": 0.028,
            "p75": 0.037,
            "p95": 0.055,
        },
    },
    "scenario_distribution": {
        "bull_market": 1847,
        "bear_market": 1203,
        "neutral_market": 3456,
        "growth_market": 2518,
        "stress_market": 976,
    },
    "confidence_intervals": {
        "95": {
            "cap_rate": [0.042, 0.078],
            "rent_growth": [0.008, 0.068],
            "property_growth": [0.005, 0.055],
        },
        "99": {
            "cap_rate": [0.038, 0.085],
            "rent_growth": [0.002, 0.078],
            "property_growth": [0.001, 0.062],
        },
    },
    "risk_metrics": {
        "value_at_risk_5": -0.18,
        "expected_shortfall_5": -0.27,
        "maximum_drawdown": -0.42,
        "volatility": 0.21,
        "sharpe_ratio": 1.34,
    },
    "metadata": {
        "processing_time_seconds": 2.341,
        "simulation_timestamp": "2025-07-31T18:45:00Z",
        "correlation_matrix_used": True,
        "confidence_level": 0.99,
        "engine_status": "production",
        "data_sources": {
            "forecasting": "Prophet Engine",
            "historical_data": "SQLite Database",
            "correlations": "Economic Parameter Correlations",
        },
    },
}

# =============================================================================
# ERROR RESPONSE EXAMPLES
# =============================================================================

EXAMPLE_VALIDATION_ERROR = {
    "error_code": "validation_error",
    "message": "Invalid property data provided",
    "details": {"http_status": 422},
    "field_errors": {
        "property_data.residential_units.total_units": [
            "Total units must be greater than 0"
        ],
        "property_data.purchase_price": ["Purchase price must be a positive number"],
    },
    "invalid_fields": [
        "property_data.residential_units.total_units",
        "property_data.purchase_price",
    ],
    "suggestions": [
        "Check required fields are provided",
        "Verify data types match API specification",
        "Review field validation rules in documentation",
    ],
    "documentation_url": "http://localhost:8000/api/v1/docs#/analysis/dcf_analysis",
    "example_valid_request": EXAMPLE_PROPERTY_REQUEST_BASIC,
    "timestamp": "2025-07-31T18:50:00Z",
    "request_id": "req_1753998250000_validation_error",
    "path": "/api/v1/analysis/dcf",
}

EXAMPLE_AUTHENTICATION_ERROR = {
    "error_code": "authentication_failed",
    "message": "API key required for access",
    "details": {"http_status": 401, "auth_method": "API-Key"},
    "suggestions": [
        "Ensure X-API-Key header is included",
        "Verify API key is valid and active",
        "Check API key has sufficient permissions",
    ],
    "documentation_url": "http://localhost:8000/api/v1/docs#section/Authentication",
    "timestamp": "2025-07-31T18:52:00Z",
    "request_id": "req_1753998252000_auth_error",
    "path": "/api/v1/analysis/dcf",
}

EXAMPLE_CALCULATION_ERROR = {
    "error_code": "calculation_error",
    "message": "Monte Carlo simulation failed: Expected 11 forecasts, found 0 for MSA 35620",
    "details": {"http_status": 500, "calculation_phase": "monte_carlo_simulation"},
    "parameter_issues": ["simulation_parameters", "forecasting_data"],
    "suggestions": [
        "Verify property data values are realistic",
        "Check MSA code is supported (35620, 31080, 16980, 47900, 33100)",
        "Ensure all required financial parameters are provided",
        "Reduce number of scenarios if performance issues",
    ],
    "documentation_url": "http://localhost:8000/api/v1/docs#/simulation/monte_carlo_simulation",
    "timestamp": "2025-07-31T18:55:00Z",
    "request_id": "req_1753998255000_calc_error",
    "path": "/api/v1/simulation/monte-carlo",
}

EXAMPLE_RATE_LIMIT_ERROR = {
    "error_code": "rate_limit_exceeded",
    "message": "Too many requests. Rate limit exceeded.",
    "details": {
        "http_status": 429,
        "limit": 100,
        "window_seconds": 60,
        "current_usage": 101,
    },
    "retry_after_seconds": 45,
    "suggestions": [
        "Wait before making additional requests",
        "Implement exponential backoff in your client",
        "Consider upgrading to higher rate limit tier",
        "Use batch endpoints for multiple properties",
    ],
    "documentation_url": "http://localhost:8000/api/v1/docs#section/Rate-Limiting",
    "timestamp": "2025-07-31T18:58:00Z",
    "request_id": "req_1753998258000_rate_limit",
    "path": "/api/v1/analysis/dcf",
}

# =============================================================================
# MARKET DATA EXAMPLES
# =============================================================================

EXAMPLE_MARKET_DATA_RESPONSE = {
    "msa": "New York-Newark-Jersey City, NY-NJ-PA",
    "parameter": "cap_rate",
    "data_points": [
        {
            "date": "2023-01-01T00:00:00Z",
            "value": 0.065,
            "source": "Historical Database",
        },
        {
            "date": "2023-02-01T00:00:00Z",
            "value": 0.066,
            "source": "Historical Database",
        },
        {
            "date": "2023-03-01T00:00:00Z",
            "value": 0.064,
            "source": "Historical Database",
        },
    ],
    "current_value": 0.064,
    "last_updated": "2025-07-31T18:00:00Z",
    "data_coverage": {
        "historical_years": 15,
        "parameters_available": 11,
        "data_quality": "high",
        "update_frequency": "monthly",
    },
}

EXAMPLE_FORECAST_RESPONSE = {
    "parameter": "rent_growth",
    "msa": "Los Angeles-Long Beach-Anaheim, CA",
    "forecast_horizon_years": 6,
    "confidence_level": 0.95,
    "forecast_points": [
        {
            "date": "2025-08-01T00:00:00Z",
            "predicted_value": 0.032,
            "lower_bound": 0.027,
            "upper_bound": 0.037,
        },
        {
            "date": "2025-09-01T00:00:00Z",
            "predicted_value": 0.033,
            "lower_bound": 0.028,
            "upper_bound": 0.038,
        },
    ],
    "historical_data": None,
    "model_info": {
        "model_type": "Prophet",
        "training_period_years": 15,
        "cross_validation_score": 0.89,
        "seasonal_components": ["yearly", "monthly"],
        "external_regressors": ["economic_indicators", "market_trends"],
        "model_accuracy": "high",
    },
    "forecast_timestamp": "2025-07-31T19:00:00Z",
}

# =============================================================================
# HEALTH AND CONFIG EXAMPLES
# =============================================================================

EXAMPLE_HEALTH_RESPONSE = {
    "status": "healthy",
    "timestamp": "2025-07-31T19:05:00Z",
    "version": "1.5.0",
    "environment": "development",
    "uptime_seconds": 3600.5,
    "dependencies": {
        "market_data": "healthy",
        "property_data": "healthy",
        "economic_data": "healthy",
        "forecast_cache": "healthy",
        "core_services": "healthy",
        "api_middleware": "healthy",
        "logging_system": "healthy",
    },
}

EXAMPLE_CONFIG_RESPONSE = {
    "supported_msas": ["35620", "31080", "16980", "47900", "33100"],
    "supported_parameters": [
        "commercial_mortgage_rate",
        "treasury_10y",
        "fed_funds_rate",
        "cap_rate",
        "rent_growth",
        "expense_growth",
        "property_growth",
        "vacancy_rate",
        "ltv_ratio",
        "closing_cost_pct",
        "lender_reserves",
    ],
    "analysis_limits": {
        "max_monte_carlo_scenarios": 50000,
        "min_monte_carlo_scenarios": 500,
        "max_forecast_horizon_years": 10,
        "min_forecast_horizon_years": 3,
        "max_batch_properties": 50,
        "max_concurrent_batch": 10,
        "request_timeout_seconds": 300,
    },
    "dcf_methodology": {
        "phases": "4-Phase DCF Workflow",
        "phase_1": "DCF Assumptions from Monte Carlo",
        "phase_2": "Initial Numbers & Acquisition Costs",
        "phase_3": "Cash Flow Projections (6 years)",
        "phase_4": "Financial Metrics & Investment Analysis",
        "forecasting_engine": "Prophet Time Series",
        "simulation_engine": "Custom Monte Carlo with Correlations",
        "discount_rate_default": "10%",
        "confidence_level_default": "95%",
    },
    "api_version": "1.5.0",
    "last_updated": "2025-07-31T19:10:00Z",
}
