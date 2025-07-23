# API Documentation

This document provides comprehensive documentation for the Pro-Forma Analytics Tool API endpoints, request/response formats, and integration guidelines.

## 🚀 API Overview

The Pro-Forma Analytics Tool provides a RESTful API for accessing financial data, performing calculations, and generating reports.

### Base URL
```
Development: http://localhost:8000
Production: https://api.proforma-analytics.com
```

### API Versioning
All endpoints are versioned using the URL path: `/api/v1/`

### Authentication
The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## 📊 Core Endpoints

### Market Data Endpoints

#### Get Interest Rates
```http
GET /api/v1/market/interest-rates
```

**Query Parameters:**
- `rate_type` (optional): Type of interest rate (e.g., "prime", "federal_funds")
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format
- `limit` (optional): Number of records to return (default: 100)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "date": "2024-01-15",
      "rate_type": "prime",
      "rate_value": 0.0825,
      "source": "Federal Reserve",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 100,
    "total": 150,
    "pages": 2
  }
}
```

#### Get Market Trends
```http
GET /api/v1/market/trends
```

**Query Parameters:**
- `market_area` (optional): Market area code
- `trend_type` (optional): Type of trend (e.g., "rent_growth", "occupancy")
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "date": "2024-01-15",
      "market_area": "NYC",
      "trend_type": "rent_growth",
      "trend_value": 0.045,
      "units": "percentage",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### Get Cap Rates
```http
GET /api/v1/market/cap-rates
```

**Query Parameters:**
- `property_type` (optional): Type of property
- `market_area` (optional): Market area code
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "date": "2024-01-15",
      "property_type": "multifamily",
      "market_area": "NYC",
      "cap_rate": 0.045,
      "source": "CBRE",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Property Data Endpoints

#### Get Properties
```http
GET /api/v1/properties
```

**Query Parameters:**
- `city` (optional): City name
- `state` (optional): State code
- `property_type` (optional): Type of property
- `limit` (optional): Number of records to return

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "property_name": "Sunset Apartments",
      "address": "123 Main St",
      "city": "New York",
      "state": "NY",
      "zip_code": "10001",
      "property_type": "multifamily",
      "total_units": 50,
      "year_built": 2010,
      "acquisition_date": "2023-01-15",
      "acquisition_price": 15000000.00,
      "current_value": 16500000.00,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### Get Property Details
```http
GET /api/v1/properties/{property_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "property_name": "Sunset Apartments",
    "address": "123 Main St",
    "city": "New York",
    "state": "NY",
    "zip_code": "10001",
    "property_type": "multifamily",
    "total_units": 50,
    "year_built": 2010,
    "acquisition_date": "2023-01-15",
    "acquisition_price": 15000000.00,
    "current_value": 16500000.00,
    "units": [
      {
        "id": 1,
        "unit_number": "101",
        "unit_type": "1BR",
        "square_feet": 750,
        "bedrooms": 1,
        "bathrooms": 1.0,
        "rent_amount": 2500.00,
        "occupied": true
      }
    ],
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

#### Create Property
```http
POST /api/v1/properties
```

**Request Body:**
```json
{
  "property_name": "New Property",
  "address": "456 Oak St",
  "city": "Los Angeles",
  "state": "CA",
  "zip_code": "90210",
  "property_type": "multifamily",
  "total_units": 25,
  "year_built": 2015,
  "acquisition_date": "2024-01-15",
  "acquisition_price": 8000000.00
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 2,
    "property_name": "New Property",
    "address": "456 Oak St",
    "city": "Los Angeles",
    "state": "CA",
    "zip_code": "90210",
    "property_type": "multifamily",
    "total_units": 25,
    "year_built": 2015,
    "acquisition_date": "2024-01-15",
    "acquisition_price": 8000000.00,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### Financial Analysis Endpoints

#### Calculate Pro-Forma
```http
POST /api/v1/analysis/pro-forma
```

**Request Body:**
```json
{
  "property_id": 1,
  "analysis_period": 10,
  "assumptions": {
    "rent_growth_rate": 0.03,
    "expense_growth_rate": 0.02,
    "vacancy_rate": 0.05,
    "cap_rate": 0.045,
    "discount_rate": 0.08
  },
  "scenarios": ["base", "optimistic", "pessimistic"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "property_id": 1,
    "analysis_period": 10,
    "scenarios": {
      "base": {
        "irr": 0.125,
        "roi": 0.085,
        "cash_flow": [
          {
            "year": 1,
            "revenue": 1500000.00,
            "expenses": 600000.00,
            "net_operating_income": 900000.00,
            "debt_service": 400000.00,
            "cash_flow": 500000.00
          }
        ],
        "exit_value": 20000000.00
      }
    },
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

#### Calculate IRR
```http
POST /api/v1/analysis/irr
```

**Request Body:**
```json
{
  "property_id": 1,
  "cash_flows": [
    {
      "date": "2024-01-15",
      "amount": -15000000.00,
      "type": "investment"
    },
    {
      "date": "2025-01-15",
      "amount": 500000.00,
      "type": "cash_flow"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "irr": 0.125,
    "calculation_date": "2024-01-15T10:30:00Z"
  }
}
```

### Economic Data Endpoints

#### Get GDP Data
```http
GET /api/v1/economic/gdp
```

**Query Parameters:**
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format
- `period_type` (optional): "quarterly" or "annual"

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "date": "2024-01-01",
      "gdp_value": 25000000000000.00,
      "growth_rate": 0.025,
      "period_type": "quarterly",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### Get Inflation Data
```http
GET /api/v1/economic/inflation
```

**Query Parameters:**
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "date": "2024-01-01",
      "cpi_value": 308.417,
      "inflation_rate": 0.031,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

## 📈 Forecasting Endpoints

#### Generate Forecast
```http
POST /api/v1/forecast/generate
```

**Request Body:**
```json
{
  "target_variable": "rent_growth",
  "market_area": "NYC",
  "forecast_period": 12,
  "model_type": "arima",
  "parameters": {
    "p": 1,
    "d": 1,
    "q": 1
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "forecast_id": "fc_123456",
    "target_variable": "rent_growth",
    "market_area": "NYC",
    "forecast_period": 12,
    "model_type": "arima",
    "predictions": [
      {
        "date": "2024-02-01",
        "predicted_value": 0.045,
        "confidence_interval_lower": 0.035,
        "confidence_interval_upper": 0.055
      }
    ],
    "model_accuracy": 0.85,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

#### Get Forecast
```http
GET /api/v1/forecast/{forecast_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "forecast_id": "fc_123456",
    "target_variable": "rent_growth",
    "market_area": "NYC",
    "forecast_period": 12,
    "model_type": "arima",
    "predictions": [
      {
        "date": "2024-02-01",
        "predicted_value": 0.045,
        "confidence_interval_lower": 0.035,
        "confidence_interval_upper": 0.055
      }
    ],
    "model_accuracy": 0.85,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

## 📊 Report Endpoints

#### Generate Property Report
```http
POST /api/v1/reports/property
```

**Request Body:**
```json
{
  "property_id": 1,
  "report_type": "comprehensive",
  "include_charts": true,
  "format": "pdf"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "report_id": "rep_123456",
    "property_id": 1,
    "report_type": "comprehensive",
    "download_url": "https://api.proforma-analytics.com/reports/rep_123456.pdf",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

#### Get Report Status
```http
GET /api/v1/reports/{report_id}/status
```

**Response:**
```json
{
  "success": true,
  "data": {
    "report_id": "rep_123456",
    "status": "completed",
    "progress": 100,
    "download_url": "https://api.proforma-analytics.com/reports/rep_123456.pdf",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

## 🔐 Authentication Endpoints

#### Login
```http
POST /api/v1/auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "name": "John Doe",
      "role": "analyst"
    },
    "expires_at": "2024-01-16T10:30:00Z"
  }
}
```

#### Refresh Token
```http
POST /api/v1/auth/refresh
```

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_at": "2024-01-16T10:30:00Z"
  }
}
```

## ⚠️ Error Handling

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "property_name",
        "message": "Property name is required"
      }
    ]
  }
}
```

### Common Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `VALIDATION_ERROR` | Invalid input data | 400 |
| `UNAUTHORIZED` | Authentication required | 401 |
| `FORBIDDEN` | Insufficient permissions | 403 |
| `NOT_FOUND` | Resource not found | 404 |
| `RATE_LIMIT_EXCEEDED` | Too many requests | 429 |
| `INTERNAL_ERROR` | Server error | 500 |

### Rate Limiting
- **Free Tier**: 100 requests/hour
- **Professional Tier**: 1000 requests/hour
- **Enterprise Tier**: 10000 requests/hour

## 📚 SDK Examples

### Python SDK
```python
from proforma_analytics import ProFormaAPI

# Initialize client
api = ProFormaAPI(api_key="your_api_key")

# Get market data
interest_rates = api.market.get_interest_rates(
    rate_type="prime",
    start_date="2024-01-01",
    end_date="2024-01-31"
)

# Calculate pro-forma
analysis = api.analysis.calculate_pro_forma(
    property_id=1,
    analysis_period=10,
    assumptions={
        "rent_growth_rate": 0.03,
        "expense_growth_rate": 0.02
    }
)
```

### JavaScript SDK
```javascript
import { ProFormaAPI } from '@proforma-analytics/sdk';

// Initialize client
const api = new ProFormaAPI({ apiKey: 'your_api_key' });

// Get market data
const interestRates = await api.market.getInterestRates({
  rateType: 'prime',
  startDate: '2024-01-01',
  endDate: '2024-01-31'
});

// Calculate pro-forma
const analysis = await api.analysis.calculateProForma({
  propertyId: 1,
  analysisPeriod: 10,
  assumptions: {
    rentGrowthRate: 0.03,
    expenseGrowthRate: 0.02
  }
});
```

## 🔧 Webhook Integration

### Webhook Events
- `property.created`: New property added
- `analysis.completed`: Analysis calculation completed
- `forecast.generated`: New forecast generated
- `report.ready`: Report generation completed

### Webhook Payload
```json
{
  "event": "analysis.completed",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "analysis_id": "ana_123456",
    "property_id": 1,
    "irr": 0.125,
    "roi": 0.085
  }
}
```

## 📈 API Usage Analytics

### Usage Metrics
- **Total Requests**: Number of API calls made
- **Response Time**: Average response time in milliseconds
- **Error Rate**: Percentage of failed requests
- **Popular Endpoints**: Most frequently used endpoints

### Usage Dashboard
Access your usage analytics at: `https://api.proforma-analytics.com/dashboard`

## 🔄 API Versioning

### Version Deprecation Policy
- **Deprecation Notice**: 12 months advance notice
- **Breaking Changes**: Only in major versions
- **Backward Compatibility**: Maintained for 24 months

### Migration Guide
When upgrading to a new API version:
1. Review the changelog
2. Update your SDK version
3. Test with the new version
4. Update your integration code

## 📞 Support

### Getting Help
- **Documentation**: https://docs.proforma-analytics.com
- **API Status**: https://status.proforma-analytics.com
- **Support Email**: api-support@proforma-analytics.com
- **Community Forum**: https://community.proforma-analytics.com

### API Status Codes
- **200**: Success
- **201**: Created
- **400**: Bad Request
- **401**: Unauthorized
- **403**: Forbidden
- **404**: Not Found
- **429**: Too Many Requests
- **500**: Internal Server Error