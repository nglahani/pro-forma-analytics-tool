# Core Infrastructure - v1.6

Production-grade shared infrastructure components and utilities providing foundational services across the DCF analysis platform, including comprehensive error handling, structured logging, and legacy compatibility layers.

## Infrastructure Components

### Core Files

- **`exceptions.py`** - Comprehensive custom exception hierarchy with detailed error context
- **`logging_config.py`** - Production-ready centralized logging with rotation and filtering
- **`property_inputs.py`** - Legacy property input definitions with backward compatibility support

## Exception Handling System (exceptions.py)

### Custom Exception Hierarchy

```python
class DCFAnalysisError(Exception):
    """Base exception for all DCF analysis errors with structured context"""
    
class ValidationError(DCFAnalysisError):
    """Parameter validation failures with detailed constraint information"""
    
class CalculationError(DCFAnalysisError):
    """Financial calculation errors with intermediate result context"""
    
class DataError(DCFAnalysisError):
    """Data access and integrity errors with source attribution"""
    
class ConfigurationError(DCFAnalysisError):
    """Configuration and environment setup errors"""
```

### Error Context and Reporting
- **Structured Error Messages**: Consistent error formatting with actionable information
- **Error Classification**: Categorized exceptions for targeted error handling
- **Context Preservation**: Full error context including parameter values and calculation state
- **Debug Information**: Enhanced debugging support with stack trace analysis
- **User-Friendly Messages**: Clear error descriptions for end-user presentation

### Production Error Handling
```python
try:
    dcf_result = financial_metrics_service.calculate_metrics(property_input)
except ValidationError as e:
    logger.error(f"Parameter validation failed: {e.context}")
    # Handle validation errors with specific parameter guidance
except CalculationError as e:
    logger.error(f"Financial calculation error: {e.intermediate_results}")
    # Handle calculation errors with diagnostic information
```

## Logging Configuration (logging_config.py)

### Production Logging Framework

#### Log Level Hierarchy
- **DEBUG**: Detailed diagnostic information for development and troubleshooting
- **INFO**: General application flow and business process tracking
- **WARNING**: Potential issues that don't prevent operation
- **ERROR**: Error conditions that affect specific operations
- **CRITICAL**: Severe errors that may cause application failure

#### Structured Logging Configuration
```python
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "json": {
            "format": '{"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "message": "%(message)s", "module": "%(module)s"}',
            "datefmt": "%Y-%m-%dT%H:%M:%S"
        }
    },
    "handlers": {
        "file_rotating": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/application.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 10,
            "formatter": "detailed"
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/errors.log",
            "maxBytes": 5242880,  # 5MB
            "backupCount": 5,
            "level": "ERROR",
            "formatter": "json"
        },
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "detailed",
            "stream": "ext://sys.stdout"
        }
    },
    "loggers": {
        "dcf_engine": {
            "level": "INFO",
            "handlers": ["file_rotating", "console"],
            "propagate": False
        },
        "monte_carlo": {
            "level": "DEBUG",
            "handlers": ["file_rotating"],
            "propagate": False
        },
        "database": {
            "level": "WARNING",
            "handlers": ["file_rotating", "error_file"],
            "propagate": False
        },
        "performance": {
            "level": "INFO",
            "handlers": ["file_rotating"],
            "propagate": False
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["file_rotating", "console"]
    }
}
```

### Logging Features (v1.6)
- **Automatic Log Rotation**: Prevents log files from consuming excessive disk space
- **Multi-Handler Support**: Simultaneous logging to files, console, and error streams
- **JSON Formatting**: Structured logging for automated log analysis and monitoring
- **Performance Tracking**: Dedicated performance logger for optimization analysis
- **Error Aggregation**: Separate error log for critical issue monitoring
- **Environment-Specific Configuration**: Different log levels for dev/staging/production

### Logger Usage Patterns
```python
import logging
from core.logging_config import setup_logging

# Initialize logging system
setup_logging()
logger = logging.getLogger('dcf_engine')

# Structured logging with context
logger.info("Starting DCF calculation", extra={
    "property_id": property_input.property_id,
    "msa_code": property_input.msa_code,
    "analysis_date": datetime.now().isoformat()
})

# Performance logging
perf_logger = logging.getLogger('performance')
with performance_timer() as timer:
    result = calculate_irr(cash_flows)
perf_logger.info(f"IRR calculation completed in {timer.elapsed:.3f}s")
```

## Legacy Compatibility (property_inputs.py)

### Backward Compatibility Support

#### Legacy Property Input Definitions
- **PropertyInputData**: Original property input class for backward compatibility
- **Field Mapping**: Automatic mapping between legacy and current field names
- **Validation Bridge**: Legacy validation rules mapped to current validation framework
- **Migration Utilities**: Tools for converting legacy property definitions

#### Compatibility Layer Functions
```python
def convert_legacy_property_input(legacy_input: PropertyInputData) -> SimplifiedPropertyInput:
    """Convert legacy property input to current format with validation"""
    
def validate_legacy_constraints(legacy_input: PropertyInputData) -> List[ValidationError]:
    """Apply legacy validation rules for backward compatibility"""
    
def migrate_property_data(legacy_data: dict) -> dict:
    """Migrate legacy property data structure to current schema"""
```

### Migration Support
- **Automatic Detection**: Identify legacy property input formats
- **Seamless Conversion**: Transparent conversion to current property input format
- **Validation Preservation**: Maintain original validation behavior for legacy inputs
- **Deprecation Warnings**: Inform users about legacy usage with migration guidance

## Core Infrastructure Integration

### Application Bootstrap
```python
from core.logging_config import setup_logging
from core.exceptions import DCFAnalysisError

# Initialize core infrastructure
def initialize_application():
    """Bootstrap core infrastructure components"""
    setup_logging()
    configure_exception_handlers()
    validate_environment_configuration()
    
    logger = logging.getLogger('dcf_engine')
    logger.info("DCF Analysis Platform v1.6 initialized successfully")
```

### Error Handling Integration
- **Global Exception Handler**: Centralized error handling with logging integration
- **Graceful Degradation**: Fallback behaviors for non-critical errors
- **Error Recovery**: Automatic retry mechanisms for transient failures
- **User Notification**: Clear error messages with suggested resolutions

### Performance Monitoring
- **Execution Timing**: Automatic timing for critical operations
- **Memory Usage Tracking**: Monitor memory consumption during calculations
- **Resource Utilization**: Database connection and query performance monitoring
- **Alert Thresholds**: Configurable performance alerts for regression detection

## Development and Testing Support

### Testing Infrastructure
- **Mock Logging**: Test-friendly logging configuration with suppression options
- **Exception Testing**: Utilities for testing error conditions and recovery
- **Log Analysis**: Tools for analyzing log output during test execution
- **Performance Benchmarking**: Infrastructure for performance regression testing

### Debug and Development Features
- **Enhanced Debug Logging**: Detailed diagnostic information for development
- **Interactive Error Handling**: Debug-friendly error presentation
- **Configuration Validation**: Startup validation of core infrastructure configuration
- **Health Checks**: Runtime validation of core infrastructure components