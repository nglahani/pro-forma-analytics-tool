# Configuration - v1.6

Comprehensive application configuration system with production-grade parameter definitions, geographic mappings, and environment-specific settings supporting the complete DCF analysis engine.

## Configuration Architecture

### Core Configuration Files

- **`dcf_constants.py`** - DCF calculation constants, financial assumptions, and business rule parameters
- **`geography.py`** - MSA codes, geographic mappings, and regional market identifiers
- **`parameters.py`** - Pro forma parameter definitions with validation rules and bounds
- **`settings.py`** - Global application settings, environment configuration, and feature flags

## DCF Constants (dcf_constants.py)

### Financial Calculation Parameters
```python
# Investment Analysis Constants
DEFAULT_HOLD_PERIOD = 6  # Years for DCF analysis
DEFAULT_DISCOUNT_RATE = 0.10  # 10% discount rate for NPV calculations
TERMINAL_CAP_RATE_ADJUSTMENT = 0.0025  # 25 basis point terminal adjustment

# Cash Flow Modeling
MONTHS_PER_YEAR = 12
DAYS_PER_YEAR = 365
WATERFALL_DISTRIBUTION_THRESHOLD = 0.08  # 8% preferred return threshold

# Investment Recommendation Thresholds
STRONG_BUY_IRR_THRESHOLD = 0.18  # 18% IRR minimum for STRONG_BUY
BUY_IRR_THRESHOLD = 0.15         # 15% IRR minimum for BUY
HOLD_IRR_THRESHOLD = 0.12        # 12% IRR minimum for HOLD
SELL_IRR_THRESHOLD = 0.10        # Below 10% IRR triggers SELL
```

### Risk Assessment Parameters
- **NPV Sensitivity Thresholds**: Risk-adjusted NPV evaluation criteria
- **Debt Service Coverage Ratios**: Minimum DSCR requirements for different scenarios
- **Stress Test Multipliers**: Economic downturn scenario adjustments
- **Break-even Analysis Constants**: Zero NPV and minimum IRR thresholds

## Geographic Configuration (geography.py)

### MSA Code Mappings
```python
MSA_CODES = {
    "16980": {
        "name": "Chicago-Naperville-Elgin, IL-IN-WI",
        "region": "Midwest",
        "market_tier": "Primary",
        "timezone": "America/Chicago"
    },
    "31080": {
        "name": "Los Angeles-Long Beach-Anaheim, CA",
        "region": "West",
        "market_tier": "Primary", 
        "timezone": "America/Los_Angeles"
    },
    "33100": {
        "name": "Miami-Fort Lauderdale-West Palm Beach, FL",
        "region": "Southeast",
        "market_tier": "Primary",
        "timezone": "America/New_York"
    },
    "35620": {
        "name": "New York-Newark-Jersey City, NY-NJ-PA",
        "region": "Northeast",
        "market_tier": "Gateway",
        "timezone": "America/New_York"
    },
    "47900": {
        "name": "Washington-Arlington-Alexandria, DC-VA-MD-WV",
        "region": "Mid-Atlantic",
        "market_tier": "Primary",
        "timezone": "America/New_York"
    }
}
```

### Regional Market Classifications
- **Gateway Markets**: Tier-1 markets with highest liquidity and institutional activity
- **Primary Markets**: Major metropolitan areas with strong fundamentals
- **Secondary Markets**: Mid-size markets with growth potential (future expansion)
- **Market Tier Adjustments**: Risk premium adjustments by market classification

## Parameter Definitions (parameters.py)

### Pro Forma Parameter Schema (11 Total Parameters)

#### Interest Rate Parameters
```python
INTEREST_RATE_PARAMETERS = {
    "treasury_10y": {
        "min_value": 0.01,      # 1% minimum
        "max_value": 0.08,      # 8% maximum  
        "default_value": 0.045,  # 4.5% default
        "validation_rules": ["positive", "reasonable_range"],
        "forecast_model": "prophet_with_seasonality"
    },
    "commercial_mortgage": {
        "min_value": 0.03,
        "max_value": 0.12,
        "default_value": 0.065,
        "correlation_with": ["treasury_10y", "fed_funds"],
        "spread_over_treasury": 0.02  # 200 basis points typical spread
    }
}
```

#### Market Condition Parameters
- **Cap Rate**: Property capitalization rates with MSA-specific adjustments
- **Vacancy Rate**: Market vacancy rates with seasonal and cyclical modeling
- **Rent Growth**: Annual rental appreciation with regional variations

#### Growth and Expense Parameters
- **Expense Growth**: Operating expense inflation with utility and tax adjustments
- **Property Growth**: Property value appreciation with market cycle modeling
- **Economic Indicators**: Employment, population, and GDP growth factors

#### Lending Requirement Parameters
- **LTV Ratios**: Loan-to-value requirements by property type and lender category
- **Closing Costs**: Transaction fees, title insurance, and legal expense ratios
- **Lender Reserves**: Required reserve funds as percentage of loan amount

### Parameter Validation Framework
```python
class ParameterValidator:
    """Comprehensive parameter validation with business rule enforcement"""
    
    def validate_parameter(self, param_name: str, value: float, context: dict) -> bool:
        """Validate parameter against defined rules and constraints"""
        rules = PARAMETER_DEFINITIONS[param_name]["validation_rules"]
        
        for rule in rules:
            if not self._apply_validation_rule(rule, value, context):
                raise ValidationError(f"Parameter {param_name} failed {rule} validation")
        
        return True
        
    def _apply_validation_rule(self, rule: str, value: float, context: dict) -> bool:
        """Apply specific validation rule with contextual information"""
        # Implementation includes range checking, correlation validation,
        # historical consistency checks, and business rule enforcement
```

## Application Settings (settings.py)

### Environment Configuration
```python
# Database Configuration
DATABASE_SETTINGS = {
    "sqlite_path": "data/databases/",
    "connection_timeout": 30,
    "query_cache_size": 1000,
    "enable_wal_mode": True  # Write-Ahead Logging for performance
}

# Forecasting Engine Settings
PROPHET_SETTINGS = {
    "forecast_horizon_years": 6,
    "seasonality_mode": "multiplicative",
    "uncertainty_samples": 1000,
    "changepoint_prior_scale": 0.05
}

# Monte Carlo Simulation Settings
MONTE_CARLO_SETTINGS = {
    "default_scenarios": 500,
    "max_scenarios": 10000,
    "correlation_threshold": 0.1,
    "random_seed": 42  # For reproducible results in testing
}
```

### Feature Flags and Toggles
- **Advanced Analytics**: Enable/disable complex financial metrics
- **Performance Optimizations**: Toggle query caching and batch processing
- **Debug Mode**: Enhanced logging and validation for development
- **A/B Testing**: Configuration for testing different calculation approaches

### Logging and Monitoring Configuration
```python
LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/application.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        }
    },
    "loggers": {
        "dcf_engine": {"level": "INFO"},
        "monte_carlo": {"level": "DEBUG"},
        "database": {"level": "WARNING"}
    }
}
```

## Configuration Management (v1.6)

### Environment-Specific Overrides
- **Development**: Enhanced debugging, mock data sources, relaxed validation
- **Testing**: Isolated databases, deterministic random seeds, fast execution
- **Staging**: Production-like data, performance monitoring, comprehensive logging
- **Production**: Optimized performance, strict validation, minimal logging

### Configuration Validation
```bash
# Validate all configuration files
python scripts/validate_configuration.py --env production

# Test parameter definitions
python scripts/test_parameter_validation.py --comprehensive

# Verify geographic mappings
python scripts/validate_geography.py --check-msa-codes
```

### Dynamic Configuration Updates
- **Hot Reloading**: Update parameters without application restart
- **Version Control**: Track configuration changes with git integration
- **Rollback Capability**: Quickly revert to previous configuration states
- **Audit Logging**: Complete history of configuration modifications

## Integration with Core Systems

### DCF Engine Integration
- **Parameter Injection**: Automatic parameter loading into calculation services
- **Validation Pipeline**: Pre-calculation parameter validation and bounds checking
- **Default Handling**: Intelligent defaults for missing or invalid parameters
- **Context Awareness**: Parameter adjustments based on property type and location

### Database Schema Alignment
- **Schema Validation**: Ensure parameter definitions match database constraints
- **Migration Support**: Automated schema updates when parameters change
- **Backward Compatibility**: Support for legacy parameter formats
- **Performance Optimization**: Index configuration based on parameter usage patterns