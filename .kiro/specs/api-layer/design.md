# API Layer Design Documentation

## Architecture Overview

The API layer implements a **Presentation Layer** over the existing Clean Architecture, exposing DCF analysis capabilities through REST endpoints while maintaining strict separation of concerns and preserving existing business logic.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (New)                         │
├─────────────────────────────────────────────────────────────┤
│  FastAPI Router  │  Middleware  │  Response Models         │
│  Controllers     │  Auth        │  Input Validation        │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│              Application Layer (Existing)                  │
├─────────────────────────────────────────────────────────────┤
│  Service Factory │  DCF Services │  Business Logic         │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│               Domain Layer (Existing)                      │
├─────────────────────────────────────────────────────────────┤
│  Entities        │  Repositories │  Business Rules         │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│            Infrastructure Layer (Existing)                 │
├─────────────────────────────────────────────────────────────┤
│  Databases       │  External APIs │  Data Access           │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Core Framework Selection

**FastAPI Framework**
- **Rationale**: Already included in requirements.txt, automatic OpenAPI documentation, excellent performance, native async support
- **Version**: 0.104.0+ (compatible with existing Python 3.8+ requirement)
- **Benefits**: Type-safe request/response handling, built-in validation, automatic API documentation

**Supporting Technologies**
- **Pydantic 2.5.0+**: Data validation and serialization (already included)
- **Uvicorn**: ASGI server for production deployment
- **Python 3.8+**: Maintain existing compatibility requirements

### Integration with Existing Infrastructure

**Service Factory Integration**
- Leverage existing `src/application/factories/service_factory.py`
- No modifications required to existing DCF services
- Maintain singleton pattern for service instances

**Configuration Management**
- Extend existing `config/settings.py` APISettings class
- Use existing environment-based configuration system
- Maintain production/development/testing environment support

## API Design

### URL Structure and Versioning

**Base URL Pattern**: `https://api.proforma-analytics.com/api/v1`

**Versioning Strategy**:
- Path-based versioning (`/api/v1/`, `/api/v2/`)
- Major version changes for breaking API modifications
- Backward compatibility maintained for one major version

### Endpoint Architecture

#### Core Analysis Endpoints

**POST /api/v1/analysis/dcf**
```
Purpose: Single property DCF analysis
Input: PropertyAnalysisRequest (SimplifiedPropertyInput + options)
Output: DCFAnalysisResponse (NPV, IRR, metrics, recommendation)
Processing: Complete 4-phase DCF workflow
```

**POST /api/v1/analysis/batch**
```
Purpose: Multiple property analysis
Input: BatchAnalysisRequest (array of PropertyAnalysisRequest)
Output: BatchAnalysisResponse (array of results with request IDs)
Processing: Concurrent execution up to 50 properties
```

**POST /api/v1/simulation/monte-carlo**
```
Purpose: Monte Carlo scenario analysis
Input: MonteCarloRequest (property + simulation parameters)
Output: MonteCarloResponse (distributions, risk metrics, scenarios)
Processing: Configurable simulation count (500-10000)
```

#### Data Access Endpoints

**GET /api/v1/data/markets/{msa}**
```
Purpose: Market data for specific MSA
Parameters: msa (NYC, LA, Chicago, DC, Miami)
Query Params: parameters, start_date, end_date
Output: MarketDataResponse (historical + current data)
```

**GET /api/v1/forecasts/{parameter}/{msa}**
```
Purpose: Prophet forecasts for specific parameter/MSA
Parameters: parameter (rent_growth, cap_rate, etc.), msa
Query Params: horizon_years, confidence_level
Output: ForecastResponse (predictions + confidence intervals)
```

#### System Endpoints

**GET /api/v1/health**
```
Purpose: Service health monitoring
Output: HealthResponse (status, uptime, dependencies)
Processing: Database connectivity, external API availability
```

**GET /api/v1/config**
```
Purpose: System configuration information
Output: ConfigResponse (supported MSAs, parameters, limits)
Authentication: Required for sensitive configuration
```

## Data Models

### Request/Response Schema Design

**Request Models** (Pydantic BaseModel extensions):

```python
class PropertyAnalysisRequest(BaseModel):
    property_data: SimplifiedPropertyInput  # Reuse existing domain entity
    options: Optional[AnalysisOptions] = None
    
class AnalysisOptions(BaseModel):
    monte_carlo_simulations: int = 10000
    forecast_horizon_years: int = 6
    include_scenarios: bool = True
    confidence_level: float = 0.95

class BatchAnalysisRequest(BaseModel):
    properties: List[PropertyAnalysisRequest]
    parallel_processing: bool = True
    max_concurrent: int = 50
```

**Response Models**:

```python
class DCFAnalysisResponse(BaseModel):
    request_id: str
    property_id: str
    analysis_date: datetime
    dcf_results: FinancialMetrics  # Use existing domain entity
    cash_flows: CashFlowProjection  # Use existing domain entity
    recommendation: InvestmentRecommendation
    metadata: AnalysisMetadata

class AnalysisMetadata(BaseModel):
    processing_time_seconds: float
    dcf_engine_version: str
    assumptions_used: DCFAssumptions
    data_sources: Dict[str, str]
```

### Domain Entity Mapping

**Direct Entity Reuse**:
- `SimplifiedPropertyInput` → API request body
- `FinancialMetrics` → API response section
- `CashFlowProjection` → API response section
- `DCFAssumptions` → API response metadata

**API-Specific Models**:
- Request/Response wrappers with metadata
- Error response structures
- Batch processing containers
- Health check responses

## Error Handling Strategy

### HTTP Status Code Usage

**Success Responses**:
- `200 OK`: Successful analysis completion
- `201 Created`: Batch analysis initiated (async)
- `202 Accepted`: Long-running operation accepted

**Client Error Responses**:
- `400 Bad Request`: Invalid input data or parameters
- `401 Unauthorized`: Missing or invalid API key
- `403 Forbidden`: Insufficient permissions for endpoint
- `422 Unprocessable Entity`: Valid JSON but business logic errors
- `429 Too Many Requests`: Rate limit exceeded

**Server Error Responses**:
- `500 Internal Server Error`: Unexpected system error
- `503 Service Unavailable`: External dependency failure
- `504 Gateway Timeout`: Analysis timeout exceeded

### Error Response Structure

```python
class APIError(BaseModel):
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime
    request_id: str

class ValidationError(APIError):
    field_errors: Dict[str, List[str]]
    
class BusinessLogicError(APIError):
    business_rule: str
    suggested_action: str
```

### Exception Mapping

**Domain Exceptions → HTTP Responses**:
- `ValidationError` → HTTP 422 + detailed field errors
- `ConfigurationError` → HTTP 500 + generic error message
- `DataNotFoundError` → HTTP 404 + resource identification
- Generic exceptions → HTTP 500 + sanitized error information

## Authentication & Security

### API Key Authentication

**Implementation Strategy**:
- Header-based authentication: `X-API-Key: {api_key}`
- API key validation against secure storage
- Rate limiting per API key
- Request logging with API key identification

**API Key Management**:
- 32-character alphanumeric keys
- Environment variable storage
- Role-based permissions (read-only vs full access)
- Key rotation support for security

### Security Middleware Stack

**Request Processing Pipeline**:
1. **HTTPS Enforcement**: Redirect HTTP to HTTPS in production
2. **CORS Policy**: Configurable allowed origins from settings
3. **Rate Limiting**: Token bucket algorithm per API key
4. **Input Sanitization**: SQL injection and XSS prevention
5. **Request Logging**: Comprehensive audit trail
6. **Authentication**: API key validation
7. **Authorization**: Endpoint permission checking

### Data Protection

**Input Validation**:
- Pydantic model validation for all requests
- Range checking for numerical inputs
- String length limits and pattern validation
- Business rule validation before processing

**Output Sanitization**:
- Remove internal system information from responses
- Exclude sensitive configuration from public endpoints
- Standardized error messages without system details

## Performance Design

### Response Time Optimization

**Target Performance**:
- Single DCF analysis: ≤ 30 seconds (95th percentile)
- Market data queries: ≤ 5 seconds
- Health checks: ≤ 2 seconds
- Batch processing: ≤ 60 seconds for 10 properties

**Optimization Strategies**:
1. **Connection Pooling**: Reuse database connections
2. **Service Instance Caching**: Singleton service factory pattern
3. **Forecast Caching**: Leverage existing forecast_cache.db
4. **Concurrent Processing**: Async batch analysis execution
5. **Response Compression**: Gzip encoding for large responses

### Scalability Architecture

**Horizontal Scaling Support**:
- Stateless API design for load balancer compatibility
- Shared database access across multiple API instances
- Environment-based configuration for multi-instance deployment
- Health checks for load balancer monitoring

**Resource Management**:
- Request timeout configuration
- Memory usage monitoring
- Connection pool size limits
- Graceful shutdown handling

## Integration Points

### Service Layer Integration

**Service Factory Pattern**:
```python
# src/presentation/api/dependencies.py
from src.application.factories.service_factory import get_service_factory

def get_dcf_services():
    factory = get_service_factory()
    return {
        'dcf_assumptions': factory.create_dcf_assumptions_service(),
        'initial_numbers': factory.create_initial_numbers_service(),
        'cash_flow_projection': factory.create_cash_flow_projection_service(),
        'financial_metrics': factory.create_financial_metrics_service()
    }
```

**Workflow Integration**:
- Maintain existing 4-phase DCF workflow
- Use existing service orchestration patterns
- Preserve error handling and validation logic
- Leverage existing logging configuration

### Database Integration

**Existing Database Usage**:
- Read-only access to market_data.db, property_data.db, economic_data.db
- Read/write access to forecast_cache.db for caching
- No new database schemas required
- Maintain existing backup and maintenance procedures

**External API Integration**:
- Continue using existing FRED API client
- Preserve rate limiting and caching mechanisms
- Maintain existing error handling for external dependencies

## Project Structure

### New API Components

```
src/
├── presentation/
│   └── api/                     # New API layer
│       ├── __init__.py
│       ├── main.py              # FastAPI application
│       ├── routers/             # Endpoint routing
│       │   ├── __init__.py
│       │   ├── analysis.py      # DCF analysis endpoints
│       │   ├── simulation.py    # Monte Carlo endpoints
│       │   ├── data.py          # Market data endpoints
│       │   └── system.py        # Health/config endpoints
│       ├── models/              # API-specific Pydantic models
│       │   ├── __init__.py
│       │   ├── requests.py      # Request models
│       │   ├── responses.py     # Response models
│       │   └── errors.py        # Error models
│       ├── middleware/          # Custom middleware
│       │   ├── __init__.py
│       │   ├── auth.py          # Authentication middleware
│       │   ├── rate_limit.py    # Rate limiting
│       │   └── logging.py       # Request/response logging
│       ├── dependencies.py      # FastAPI dependencies
│       └── exceptions.py        # API exception handlers
```

### Integration with Existing Structure

**No Changes Required**:
- `src/application/` - Existing services used as-is
- `src/domain/` - Domain entities reused in API models
- `src/infrastructure/` - Database access unchanged
- `config/settings.py` - Extended for API configuration
- `tests/` - New API tests added alongside existing tests

## Testing Strategy

### Test Categories

**Unit Tests** (`tests/unit/presentation/api/`):
- Router endpoint testing with mock services
- Pydantic model validation testing  
- Middleware functionality testing
- Error handling and exception mapping

**Integration Tests** (`tests/integration/api/`):
- End-to-end API workflow testing
- Database integration via API endpoints
- External API interaction through endpoints
- Authentication and authorization flows

**Performance Tests** (`tests/performance/api/`):
- Load testing for concurrent requests
- Response time validation under load
- Memory usage profiling during batch processing
- Rate limiting effectiveness testing

### Test Implementation Approach

**FastAPI Test Client**:
```python
from fastapi.testclient import TestClient
from src.presentation.api.main import app

client = TestClient(app)

def test_dcf_analysis_endpoint():
    response = client.post(
        "/api/v1/analysis/dcf",
        json=test_property_data,
        headers={"X-API-Key": "test_api_key"}
    )
    assert response.status_code == 200
    assert "npv" in response.json()
```

**Mock Service Integration**:
- Mock application services for unit tests
- Use existing test fixtures for domain entities
- Preserve existing test data and scenarios

## Deployment Configuration

### Environment-Specific Settings

**Development Environment**:
```python
# Loaded from config/settings.py
API_HOST = "127.0.0.1"
API_PORT = 8000
API_DEBUG = True
API_RELOAD = True
RATE_LIMIT_REQUESTS = 60  # Lower for development
```

**Production Environment**:
```python
API_HOST = "0.0.0.0"
API_PORT = 8000
API_DEBUG = False
API_WORKERS = 4  # Multi-worker deployment
RATE_LIMIT_REQUESTS = 100
SECRET_KEY = os.getenv("SECRET_KEY")  # Required
```

### Server Configuration

**Uvicorn Server Setup**:
```python
# src/presentation/api/main.py
if __name__ == "__main__":
    import uvicorn
    from config.settings import get_settings
    
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.api.reload,
        workers=settings.api.workers
    )
```

**Production Deployment**:
- Docker container support using existing Dockerfile patterns
- Environment variable configuration
- Health check endpoint for load balancer integration
- Graceful shutdown handling for rolling deployments

## Monitoring and Observability

### Logging Strategy

**Request/Response Logging**:
- Structured JSON logging for production
- Request ID correlation across components
- Performance timing for all endpoints
- Error details with sanitized information

**Integration with Existing Logging**:
- Use existing `core/logging_config.py`
- Maintain consistent log format across application
- Preserve existing log file rotation and management

### Health Monitoring

**Health Check Implementation**:
```python
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "dependencies": {
            "database": check_database_connection(),
            "fred_api": check_external_api_availability()
        },
        "uptime_seconds": get_uptime()
    }
```

### Performance Metrics

**Key Metrics Collection**:
- Request count by endpoint
- Response time percentiles
- Error rate by status code
- Authentication success/failure rates
- Rate limiting trigger frequency

## Documentation Strategy

### API Documentation

**OpenAPI/Swagger Integration**:
- Automatic documentation generation via FastAPI
- Interactive API explorer at `/docs` endpoint
- Downloadable OpenAPI specification
- Code examples in multiple languages

**Developer Documentation**:
- Integration guides for common use cases
- Authentication setup procedures
- Error handling best practices
- Performance optimization recommendations

### Maintenance Documentation

**Operational Procedures**:
- API key management workflows
- Rate limiting configuration
- Monitoring and alerting setup
- Troubleshooting common issues

## Migration and Rollout Strategy

### Phased Implementation

**Phase 1**: Core DCF Analysis API
- Single property analysis endpoint
- Basic authentication and error handling
- Health check and configuration endpoints

**Phase 2**: Enhanced Features
- Batch analysis capabilities
- Market data access endpoints
- Monte Carlo simulation endpoints

**Phase 3**: Production Optimization
- Advanced rate limiting and caching
- Comprehensive monitoring and logging
- Performance optimization and load testing

### Backward Compatibility

**Library Interface Preservation**:
- Existing Python library functionality unchanged
- Demo workflow continues to work identically
- All existing tests remain valid
- No breaking changes to core business logic

**API Evolution Strategy**:
- Version endpoints for future breaking changes
- Deprecation notices for endpoint modifications
- Migration guides for API consumers
- Sunset timeline communication for deprecated features