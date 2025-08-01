# API Layer Requirements Specification

## Overview

Transform the pro-forma-analytics-tool from a Python library into a production-ready REST API service, enabling external systems and applications to access DCF analysis capabilities through standardized HTTP endpoints.

## User Stories

### Primary Users

**Real Estate Investment Firms**
- As an investment analyst, I want to submit property data via API calls so that I can integrate DCF analysis into our existing investment workflows
- As a portfolio manager, I want to analyze multiple properties programmatically so that I can efficiently evaluate large deal pipelines
- As a developer, I want to integrate DCF calculations into our proprietary investment platform so that analysts can access sophisticated financial modeling without switching tools

**Third-Party Applications**
- As a PropTech application developer, I want to access DCF analysis via REST API so that I can offer advanced financial modeling to my users
- As a CRE platform, I want to integrate pro forma analysis so that property listings can include investment projections
- As a financial modeling SaaS, I want to call external DCF services so that I can enhance my product offering with specialized real estate calculations

**Internal Operations**
- As a system administrator, I want API monitoring and logging so that I can ensure service reliability and performance
- As a data scientist, I want programmatic access to bulk analysis so that I can conduct market research and model validation
- As a business stakeholder, I want usage analytics so that I can understand API adoption and plan capacity

## Functional Requirements

### Core DCF Analysis Endpoints

**FR-1: Property Analysis Endpoint**
- WHEN a user submits property data via POST /api/v1/analysis/dcf
- THEN the system SHALL execute the complete 4-phase DCF workflow
- AND return NPV, IRR, financial metrics, and investment recommendation
- AND process the request within 30 seconds for standard property inputs

**FR-2: Batch Analysis Endpoint**
- WHEN a user submits multiple properties via POST /api/v1/analysis/batch
- THEN the system SHALL process up to 50 properties concurrently
- AND return results for each property with unique request IDs
- AND support asynchronous processing with status tracking

**FR-3: Monte Carlo Simulation Endpoint**
- WHEN a user requests scenario analysis via POST /api/v1/simulation/monte-carlo
- THEN the system SHALL generate 500-10000 scenarios based on input parameters
- AND return statistical distributions, risk metrics, and scenario classifications
- AND support configurable simulation parameters

### Data Management Endpoints

**FR-4: Market Data Access**
- WHEN a user requests market data via GET /api/v1/data/markets/{msa}
- THEN the system SHALL return current and historical market parameters
- AND include data sources, last update timestamps, and coverage periods
- AND support filtering by parameter type and date ranges

**FR-5: Forecast Data Endpoint**
- WHEN a user requests forecasts via GET /api/v1/forecasts/{parameter}/{msa}
- THEN the system SHALL return Prophet-generated forecasts with confidence intervals
- AND include forecast methodology, assumptions, and validation metrics
- AND support horizon specification (3-10 years)

### Configuration and Status Endpoints

**FR-6: Health Check Endpoint**
- WHEN a user accesses GET /api/v1/health
- THEN the system SHALL return service status, database connectivity, and system metrics
- AND complete the check within 5 seconds
- AND include dependency status (databases, external APIs)

**FR-7: Configuration Endpoint**
- WHEN an authenticated user accesses GET /api/v1/config
- THEN the system SHALL return non-sensitive configuration parameters
- AND include supported MSAs, parameter definitions, and calculation methodologies
- AND exclude API keys, secrets, and internal settings

## Technical Requirements

### Performance Requirements

**TR-1: Response Time**
- Single property DCF analysis: ≤ 30 seconds (95th percentile)
- Batch analysis (10 properties): ≤ 60 seconds
- Market data queries: ≤ 5 seconds
- Health checks: ≤ 2 seconds

**TR-2: Throughput**
- Support 100 concurrent single-property analyses
- Handle 10 concurrent batch requests
- Process 1000 API requests/hour during peak usage
- Scale horizontally to meet demand

**TR-3: Data Validation**
- Validate all input parameters against business rules
- Return detailed error messages for invalid inputs
- Support partial validation for draft submissions
- Maintain data integrity across all operations

### Security Requirements

**TR-4: Authentication & Authorization**
- Implement API key-based authentication via X-API-Key header
- Support role-based access control (read-only vs full access)
- Rate limit requests per API key (100 requests/minute default)
- Log all API access attempts with user identification

**TR-5: Data Protection**
- Encrypt all API communications via HTTPS/TLS 1.3
- Sanitize input data to prevent injection attacks
- Implement request/response logging without exposing sensitive data
- Support data retention policies for compliance

### Integration Requirements

**TR-6: Standards Compliance**
- Follow OpenAPI 3.0 specification for all endpoints
- Support JSON request/response formats
- Implement standard HTTP status codes and error responses
- Provide comprehensive API documentation via Swagger UI

**TR-7: External Dependencies**
- Maintain existing FRED API integration for market data updates
- Support graceful degradation when external services are unavailable
- Implement caching to reduce dependency on external APIs
- Ensure backward compatibility with existing DCF engine

## API Design Constraints

### Data Format Requirements

**Input Data Structure**
- Accept SimplifiedPropertyInput format as defined in domain entities
- Support MSA-based location specification (NYC, LA, Chicago, DC, Miami)
- Validate investor equity structures and renovation information
- Handle optional parameters with sensible defaults

**Output Data Structure**
- Return structured JSON responses matching domain entity schemas
- Include calculation metadata (timestamps, versions, assumptions)
- Provide detailed error responses with field-level validation messages
- Support multiple response formats (summary vs detailed)

### Business Logic Constraints

**DCF Calculation Integrity**
- Maintain existing 4-phase DCF workflow without modification
- Preserve Monte Carlo correlation models and statistical validation
- Use existing Prophet forecasting engine without changes
- Ensure API results match library results exactly

## Acceptance Criteria

### Core Functionality

**AC-1: DCF Analysis Integration**
- GIVEN a valid property input via API
- WHEN the DCF analysis endpoint is called
- THEN the response matches demo_end_to_end_workflow.py output
- AND includes NPV, IRR, cash flows, and investment recommendation

**AC-2: Error Handling**
- GIVEN invalid property input data
- WHEN any API endpoint is called
- THEN the system returns HTTP 400 with detailed validation errors
- AND includes field-specific error messages and suggested corrections

**AC-3: Performance Compliance**
- GIVEN standard property input
- WHEN DCF analysis is requested
- THEN the response is returned within 30 seconds
- AND system resource usage remains within acceptable limits

### Operational Requirements

**AC-4: Service Monitoring**
- GIVEN the API service is running
- WHEN health check endpoint is accessed
- THEN response includes service status, uptime, and dependency health
- AND provides actionable information for troubleshooting

**AC-5: Documentation Completeness**
- GIVEN the API service is deployed
- WHEN developer accesses API documentation
- THEN all endpoints are documented with examples, schemas, and error codes
- AND documentation is accessible via Swagger UI interface

## Out of Scope

### Phase 1 Exclusions

The following features are explicitly excluded from the initial API layer implementation:

- **User Management System**: No user registration, password management, or session handling
- **Data Persistence**: No storage of analysis results or user-generated content
- **Advanced Security**: No OAuth2, JWT tokens, or enterprise authentication integration
- **Websocket Support**: No real-time updates or streaming data capabilities
- **File Upload/Download**: No support for Excel import/export or PDF report generation
- **Advanced Analytics**: No portfolio optimization or machine learning enhancements
- **Caching Layer**: No Redis or advanced caching beyond existing forecast cache
- **Multi-tenant Architecture**: No customer isolation or tenant-specific configurations

### Future Considerations

These features may be considered for future API versions:

- GraphQL endpoint for flexible data querying
- Webhook support for asynchronous result delivery
- Advanced rate limiting with tiered access levels
- Integration with external CRM/ERP systems
- Support for custom calculation parameters and overrides

## Success Metrics

### Technical Metrics

- **API Uptime**: ≥ 99.5% availability during business hours
- **Response Time**: 95th percentile under performance requirements
- **Error Rate**: < 1% of requests result in server errors (5xx)
- **Test Coverage**: ≥ 95% code coverage for API layer components

### Business Metrics

- **Integration Success**: External systems successfully integrate within 2 weeks
- **Analysis Accuracy**: API results match existing library calculations 100%
- **Developer Experience**: API documentation completeness score ≥ 90%
- **Performance Scalability**: Support 10x current usage without degradation

## Dependencies

### Technical Dependencies

- **FastAPI Framework**: Primary web framework for API implementation
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for production deployment
- **Existing DCF Engine**: No modifications to core business logic
- **SQLite Databases**: Continue using existing data infrastructure

### Infrastructure Dependencies

- **Environment Configuration**: Leverage existing config/settings.py
- **Clean Architecture**: Maintain domain/application/infrastructure separation
- **Testing Framework**: Extend existing pytest-based testing approach
- **CI/CD Pipeline**: Integrate API testing into existing GitHub Actions workflow

### Business Dependencies

- **API Key Management**: Define API key generation and distribution process
- **Rate Limiting Policy**: Establish usage limits and upgrade tiers
- **Support Documentation**: Create user guides for API integration
- **Service Level Agreements**: Define uptime and performance commitments