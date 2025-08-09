# API Integration Guide: Pro Forma Analytics Tool

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Authentication and Security](#authentication-and-security)
4. [Core API Endpoints](#core-api-endpoints)
5. [Data Models and Schemas](#data-models-and-schemas)
6. [Integration Examples](#integration-examples)
7. [SDK and Client Libraries](#sdk-and-client-libraries)
8. [Error Handling](#error-handling)
9. [Rate Limiting and Performance](#rate-limiting-and-performance)
10. [Testing and Validation](#testing-and-validation)
11. [Production Deployment](#production-deployment)
12. [Troubleshooting](#troubleshooting)

## Overview

The Pro Forma Analytics Tool provides a comprehensive RESTful API for real estate investment analysis. The API enables integration with external systems, automated analysis workflows, and programmatic access to DCF calculations, Monte Carlo simulations, and market data.

### API Features

**🚀 Core Functionality**
- Complete DCF analysis workflow
- Monte Carlo simulation with 500+ scenarios
- Market data access across 5 major MSAs
- Property portfolio analysis and comparison

**📊 Advanced Analytics**
- Performance benchmarking and optimization
- Risk assessment and stress testing
- Custom scenario modeling
- Real-time market data integration

**🔧 Developer Tools**
- OpenAPI specification with interactive documentation
- Type-safe client libraries for Python and TypeScript
- Comprehensive testing utilities
- Performance monitoring and debugging tools

### API Architecture

```
┌─────────────────────────────────────────┐
│               Frontend                  │
│            (React/Next.js)              │
└─────────────────┬───────────────────────┘
                  │ HTTP/REST
┌─────────────────▼───────────────────────┐
│             API Gateway                 │
│            (FastAPI)                    │
├─────────────────────────────────────────┤
│          Application Layer              │
│      (DCF Services, Monte Carlo)        │
├─────────────────────────────────────────┤
│         Infrastructure Layer            │
│    (Database, Market Data, Cache)       │
└─────────────────────────────────────────┘
```

## Getting Started

### Prerequisites

- **Python 3.10+** for backend API server
- **FastAPI** framework with Pydantic validation
- **SQLite** databases with market and property data
- **HTTP client** for API consumption (curl, Postman, etc.)

### Quick Start

#### 1. Start the API Server

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize databases
python data_manager.py setup

# Start FastAPI development server
cd src/presentation/api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. Access API Documentation

- **Interactive Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative Documentation**: http://localhost:8000/redoc (ReDoc)
- **OpenAPI Schema**: http://localhost:8000/openapi.json

#### 3. Test API Connectivity

```bash
# Health check
curl -X GET "http://localhost:8000/health"

# Expected response:
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "2.0.0",
  "environment": "development"
}
```

### Base Configuration

```python
# API configuration
API_BASE_URL = "http://localhost:8000"
API_VERSION = "v1"
DEFAULT_TIMEOUT = 30  # seconds

# Common headers
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "ProFormaClient/2.0.0"
}
```

## Authentication and Security

### API Key Authentication

```bash
# Set API key (when authentication is enabled)
export PROFORMA_API_KEY="your_api_key_here"

# Include in requests
curl -X GET "http://localhost:8000/api/properties" \
  -H "Authorization: Bearer your_api_key_here"
```

### JWT Token Authentication

```python
import requests

# Login to get JWT token
login_response = requests.post(
    f"{API_BASE_URL}/auth/login",
    json={
        "username": "user@example.com", 
        "password": "password"
    }
)

token = login_response.json()["access_token"]

# Use token for subsequent requests
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{API_BASE_URL}/api/properties", headers=headers)
```

### Security Best Practices

**API Key Management:**
```bash
# Environment variables (recommended)
export PROFORMA_API_KEY="prod_api_key_here"
export PROFORMA_API_URL="https://api.proforma.example.com"

# Configuration file
echo '{"api_key": "your_key", "base_url": "https://api.example.com"}' > ~/.proforma-config.json
```

**Request Validation:**
```python
# Input validation and sanitization
def validate_property_input(data):
    required_fields = [
        'residential_units', 'renovation_time_months', 'commercial_units',
        'investor_equity_share_pct', 'residential_rent_per_unit',
        'commercial_rent_per_unit', 'self_cash_percentage'
    ]
    
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate ranges
    if not 0 <= data['investor_equity_share_pct'] <= 100:
        raise ValueError("Investor equity share must be between 0 and 100")
    
    return data
```

## Core API Endpoints

### Property Analysis

#### Submit Property for Analysis

```http
POST /api/properties/analyze
Content-Type: application/json

{
  "property_name": "Chicago Multifamily Investment",
  "residential_units": 24,
  "renovation_time_months": 6,
  "commercial_units": 0,
  "investor_equity_share_pct": 75.0,
  "residential_rent_per_unit": 2800,
  "commercial_rent_per_unit": 0,
  "self_cash_percentage": 30.0,
  "city": "Chicago",
  "state": "IL",
  "purchase_price": 3500000,
  "msa_code": "16980"
}
```

**Response:**
```json
{
  "analysis_id": "analysis_12345",
  "property_id": "prop_67890",
  "status": "completed",
  "timestamp": "2024-01-15T10:30:00Z",
  "results": {
    "financial_metrics": {
      "npv": 7847901,
      "irr": 0.648,
      "equity_multiple": 9.79,
      "payback_period": 3.2
    },
    "investment_recommendation": {
      "recommendation": "STRONG_BUY",
      "risk_level": "MODERATE",
      "confidence_score": 0.89
    },
    "cash_flows": [
      {"year": 0, "operating_cash_flow": -1050000, "distribution": 0},
      {"year": 1, "operating_cash_flow": 245000, "distribution": 183750},
      {"year": 2, "operating_cash_flow": 267000, "distribution": 200250},
      {"year": 3, "operating_cash_flow": 291000, "distribution": 218250},
      {"year": 4, "operating_cash_flow": 317000, "distribution": 237750},
      {"year": 5, "operating_cash_flow": 345000, "distribution": 258750}
    ],
    "terminal_value": {
      "sale_price": 4725000,
      "net_proceeds": 3892500,
      "investor_share": 2919375
    }
  }
}
```

#### Get Analysis Results

```http
GET /api/properties/{property_id}/analysis/{analysis_id}
```

**Response includes:**
- Complete financial metrics
- Cash flow projections
- Investment recommendations
- Risk assessment data
- Comparative market analysis

### Monte Carlo Simulation

#### Run Simulation

```http
POST /api/monte-carlo/simulate
Content-Type: application/json

{
  "property_id": "prop_67890",
  "scenarios": 1000,
  "confidence_level": 0.95,
  "custom_parameters": {
    "mortgage_rate_volatility": 0.15,
    "rent_growth_variance": 0.02,
    "cap_rate_stability": 0.85
  },
  "stress_testing": true
}
```

**Response:**
```json
{
  "simulation_id": "sim_45678",
  "scenarios_completed": 1000,
  "execution_time_seconds": 8.34,
  "results": {
    "npv_distribution": {
      "p10": 1250000,
      "p25": 3845000,
      "p50": 7847901,
      "p75": 12450000,
      "p90": 18250000,
      "mean": 8234567,
      "std_dev": 4567890
    },
    "irr_distribution": {
      "p10": 0.185,
      "p25": 0.425,
      "p50": 0.648,
      "p75": 0.892,
      "p90": 1.273,
      "mean": 0.684,
      "std_dev": 0.289
    },
    "risk_metrics": {
      "probability_of_loss": 0.021,
      "value_at_risk_95": -850000,
      "expected_shortfall": -1250000,
      "downside_deviation": 0.156
    },
    "scenario_classification": {
      "bull_market": 187,
      "bear_market": 156,
      "neutral": 312,
      "growth": 198,
      "stress": 147
    }
  }
}
```

### Market Data Access

#### Get MSA Market Data

```http
GET /api/market-data/msa/{msa_code}?parameters=rent_growth,cap_rate&years=6
```

**Supported MSA Codes:**
- `35620` - New York City
- `31080` - Los Angeles  
- `16980` - Chicago
- `47900` - Washington DC
- `33100` - Miami

**Response:**
```json
{
  "msa_code": "16980",
  "msa_name": "Chicago-Naperville-Elgin, IL-IN-WI",
  "data_updated": "2024-01-15T06:00:00Z",
  "forecast": {
    "rent_growth": [0.025, 0.028, 0.032, 0.029, 0.025, 0.022],
    "cap_rate": [0.065, 0.065, 0.066, 0.067, 0.068, 0.069],
    "vacancy_rate": [0.08, 0.075, 0.07, 0.065, 0.065, 0.06],
    "operating_expense_growth": [0.035, 0.038, 0.041, 0.037, 0.034, 0.032]
  },
  "confidence_intervals": {
    "rent_growth": {
      "lower_95": [0.015, 0.018, 0.022, 0.019, 0.015, 0.012],
      "upper_95": [0.035, 0.038, 0.042, 0.039, 0.035, 0.032]
    }
  },
  "historical_data": {
    "rent_growth": {
      "2019": 0.023,
      "2020": 0.012,
      "2021": 0.034,
      "2022": 0.028,
      "2023": 0.025
    }
  }
}
```

#### Get Economic Indicators

```http
GET /api/market-data/economic-indicators?indicators=mortgage_rate,treasury_10y&start_date=2024-01-01
```

**Response:**
```json
{
  "data_source": "FRED_API",
  "indicators": {
    "commercial_mortgage_rate": {
      "current": 0.075,
      "forecast": [0.077, 0.079, 0.081, 0.083, 0.085, 0.087],
      "historical_avg": 0.068,
      "volatility": 0.024
    },
    "treasury_10y": {
      "current": 0.042,
      "forecast": [0.044, 0.045, 0.047, 0.049, 0.048, 0.046],
      "historical_avg": 0.039,
      "volatility": 0.018
    }
  }
}
```

### Portfolio Analysis

#### Analyze Multiple Properties

```http
POST /api/portfolio/analyze
Content-Type: application/json

{
  "portfolio_name": "Chicago Investment Portfolio",
  "properties": [
    {
      "property_name": "Multifamily A",
      "residential_units": 24,
      "city": "Chicago",
      "purchase_price": 3500000
    },
    {
      "property_name": "Mixed-Use B", 
      "residential_units": 18,
      "commercial_units": 3,
      "city": "Chicago",
      "purchase_price": 2800000
    }
  ],
  "analysis_options": {
    "include_monte_carlo": true,
    "correlation_analysis": true,
    "diversification_metrics": true
  }
}
```

**Response:**
```json
{
  "portfolio_id": "portfolio_123",
  "total_investment": 6300000,
  "total_equity_required": 1890000,
  "weighted_metrics": {
    "portfolio_irr": 0.612,
    "portfolio_npv": 13245678,
    "combined_equity_multiple": 8.94
  },
  "diversification": {
    "geographic_concentration": 1.0,
    "property_type_concentration": 0.73,
    "diversification_score": 0.27
  },
  "correlation_analysis": {
    "property_correlations": 0.84,
    "risk_correlation": 0.78,
    "recommended_adjustments": [
      "Consider geographic diversification",
      "Evaluate different property types"
    ]
  },
  "properties": [
    {
      "property_id": "prop_001",
      "contribution_to_portfolio": 0.556,
      "individual_metrics": {...}
    },
    {
      "property_id": "prop_002", 
      "contribution_to_portfolio": 0.444,
      "individual_metrics": {...}
    }
  ]
}
```

## Data Models and Schemas

### Property Input Schema

```typescript
interface PropertyInput {
  // Required fields
  property_name: string;
  residential_units: number;           // 1-500
  renovation_time_months: number;      // 0-24
  commercial_units: number;            // 0-50
  investor_equity_share_pct: number;   // 0-100
  residential_rent_per_unit: number;   // Market validated
  commercial_rent_per_unit: number;    // Market validated  
  self_cash_percentage: number;        // 10-100

  // Optional fields
  purchase_price?: number;
  city?: string;
  state?: string;
  msa_code?: string;
  property_type?: 'multifamily' | 'mixed_use' | 'commercial';
  
  // Location details
  address?: string;
  zip_code?: string;
  
  // Financial details
  down_payment_pct?: number;
  current_gross_rent?: number;
  estimated_expenses?: number;
  
  // Physical characteristics
  total_square_feet?: number;
  year_built?: number;
  parking_spaces?: number;
  property_class?: 'class_a' | 'class_b' | 'class_c';
}
```

### Analysis Results Schema

```typescript
interface AnalysisResults {
  analysis_id: string;
  property_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  timestamp: string;
  execution_time_seconds?: number;
  
  results?: {
    // Core financial metrics
    financial_metrics: {
      npv: number;
      irr: number;
      equity_multiple: number;
      payback_period: number;
      cash_on_cash_return: number[];
      total_return: number;
    };
    
    // Investment recommendation
    investment_recommendation: {
      recommendation: 'STRONG_BUY' | 'BUY' | 'HOLD' | 'SELL' | 'STRONG_SELL';
      risk_level: 'LOW' | 'MODERATE' | 'HIGH' | 'VERY_HIGH';
      confidence_score: number;
      key_factors: string[];
    };
    
    // Cash flow projections
    cash_flows: Array<{
      year: number;
      operating_cash_flow: number;
      distribution: number;
      cumulative_distribution: number;
    }>;
    
    // Terminal value calculation
    terminal_value: {
      sale_price: number;
      transaction_costs: number;
      net_proceeds: number;
      investor_share: number;
      remaining_loan_balance: number;
    };
    
    // Market context
    market_analysis: {
      msa_code: string;
      market_conditions: 'bull' | 'bear' | 'neutral' | 'growth' | 'stress';
      rent_growth_outlook: number[];
      cap_rate_trend: number[];
      competition_level: 'low' | 'moderate' | 'high';
    };
  };
  
  error_message?: string;
}
```

### Monte Carlo Results Schema

```typescript
interface MonteCarloResults {
  simulation_id: string;
  scenarios_completed: number;
  execution_time_seconds: number;
  
  results: {
    // NPV distribution
    npv_distribution: {
      p10: number;
      p25: number; 
      p50: number;
      p75: number;
      p90: number;
      mean: number;
      std_dev: number;
    };
    
    // IRR distribution
    irr_distribution: {
      p10: number;
      p25: number;
      p50: number;
      p75: number;
      p90: number;
      mean: number;
      std_dev: number;
    };
    
    // Risk metrics
    risk_metrics: {
      probability_of_loss: number;
      value_at_risk_95: number;
      expected_shortfall: number;
      downside_deviation: number;
      upside_potential: number;
    };
    
    // Scenario classification
    scenario_classification: {
      bull_market: number;
      bear_market: number;
      neutral: number;
      growth: number;
      stress: number;
    };
    
    // Sensitivity analysis
    sensitivity_analysis: {
      rent_growth_sensitivity: number;
      cap_rate_sensitivity: number;
      interest_rate_sensitivity: number;
      renovation_cost_sensitivity: number;
    };
  };
}
```

## Integration Examples

### Python Integration

#### Basic Property Analysis

```python
import requests
import json
from typing import Dict, Any

class ProFormaClient:
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = None):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
    
    def analyze_property(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single property"""
        response = requests.post(
            f"{self.base_url}/api/properties/analyze",
            json=property_data,
            headers=self.headers,
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    
    def run_monte_carlo(self, property_id: str, scenarios: int = 1000) -> Dict[str, Any]:
        """Run Monte Carlo simulation"""
        simulation_data = {
            "property_id": property_id,
            "scenarios": scenarios,
            "confidence_level": 0.95
        }
        
        response = requests.post(
            f"{self.base_url}/api/monte-carlo/simulate",
            json=simulation_data,
            headers=self.headers,
            timeout=120
        )
        response.raise_for_status()
        return response.json()
    
    def get_market_data(self, msa_code: str, parameters: list = None) -> Dict[str, Any]:
        """Get market data for MSA"""
        params = {}
        if parameters:
            params['parameters'] = ','.join(parameters)
        
        response = requests.get(
            f"{self.base_url}/api/market-data/msa/{msa_code}",
            params=params,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

# Example usage
if __name__ == "__main__":
    client = ProFormaClient()
    
    # Define property
    property_data = {
        "property_name": "Chicago Investment Property",
        "residential_units": 24,
        "renovation_time_months": 6,
        "commercial_units": 0,
        "investor_equity_share_pct": 75.0,
        "residential_rent_per_unit": 2800,
        "commercial_rent_per_unit": 0,
        "self_cash_percentage": 30.0,
        "city": "Chicago",
        "state": "IL",
        "purchase_price": 3500000
    }
    
    # Run analysis
    analysis_result = client.analyze_property(property_data)
    print(f"NPV: ${analysis_result['results']['financial_metrics']['npv']:,.0f}")
    print(f"IRR: {analysis_result['results']['financial_metrics']['irr']:.1%}")
    print(f"Recommendation: {analysis_result['results']['investment_recommendation']['recommendation']}")
    
    # Run Monte Carlo simulation
    property_id = analysis_result['property_id']
    monte_carlo_result = client.run_monte_carlo(property_id, scenarios=500)
    
    npv_dist = monte_carlo_result['results']['npv_distribution']
    print(f"\nMonte Carlo Results (500 scenarios):")
    print(f"NPV P50: ${npv_dist['p50']:,.0f}")
    print(f"NPV P10: ${npv_dist['p10']:,.0f}")
    print(f"NPV P90: ${npv_dist['p90']:,.0f}")
```

#### Batch Analysis

```python
import concurrent.futures
import pandas as pd

def analyze_properties_batch(client: ProFormaClient, properties: list) -> pd.DataFrame:
    """Analyze multiple properties in parallel"""
    
    def analyze_single_property(prop_data):
        try:
            result = client.analyze_property(prop_data)
            return {
                'property_name': prop_data['property_name'],
                'npv': result['results']['financial_metrics']['npv'],
                'irr': result['results']['financial_metrics']['irr'],
                'equity_multiple': result['results']['financial_metrics']['equity_multiple'],
                'recommendation': result['results']['investment_recommendation']['recommendation'],
                'risk_level': result['results']['investment_recommendation']['risk_level'],
                'status': 'success'
            }
        except Exception as e:
            return {
                'property_name': prop_data['property_name'],
                'status': 'error',
                'error': str(e)
            }
    
    # Parallel execution
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(analyze_single_property, properties))
    
    return pd.DataFrame(results)

# Example usage
properties_to_analyze = [
    {
        "property_name": "Chicago Property 1",
        "residential_units": 24,
        "city": "Chicago",
        "purchase_price": 3500000,
        # ... other parameters
    },
    {
        "property_name": "Chicago Property 2", 
        "residential_units": 18,
        "city": "Chicago",
        "purchase_price": 2800000,
        # ... other parameters  
    }
]

client = ProFormaClient()
results_df = analyze_properties_batch(client, properties_to_analyze)
print(results_df.to_string())
```

### JavaScript/TypeScript Integration

#### React Component Integration

```typescript
import React, { useState, useEffect } from 'react';
import axios, { AxiosResponse } from 'axios';

interface PropertyAnalysisResult {
  analysis_id: string;
  results: {
    financial_metrics: {
      npv: number;
      irr: number;
      equity_multiple: number;
    };
    investment_recommendation: {
      recommendation: string;
      risk_level: string;
    };
  };
}

interface PropertyInput {
  property_name: string;
  residential_units: number;
  renovation_time_months: number;
  commercial_units: number;
  investor_equity_share_pct: number;
  residential_rent_per_unit: number;
  commercial_rent_per_unit: number;
  self_cash_percentage: number;
  city: string;
  state: string;
  purchase_price?: number;
}

const ProFormaAnalysis: React.FC = () => {
  const [propertyData, setPropertyData] = useState<PropertyInput>({
    property_name: '',
    residential_units: 0,
    renovation_time_months: 0,
    commercial_units: 0,
    investor_equity_share_pct: 0,
    residential_rent_per_unit: 0,
    commercial_rent_per_unit: 0,
    self_cash_percentage: 0,
    city: '',
    state: ''
  });
  
  const [analysisResult, setAnalysisResult] = useState<PropertyAnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

  const analyzeProperty = async (data: PropertyInput): Promise<void> => {
    setLoading(true);
    setError(null);
    
    try {
      const response: AxiosResponse<PropertyAnalysisResult> = await axios.post(
        `${API_BASE_URL}/api/properties/analyze`,
        data,
        {
          headers: {
            'Content-Type': 'application/json',
          },
          timeout: 60000, // 60 seconds
        }
      );
      
      setAnalysisResult(response.data);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail || err.message);
      } else {
        setError('An unexpected error occurred');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await analyzeProperty(propertyData);
  };

  return (
    <div className="proforma-analysis">
      <h2>Property Analysis</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="property_name">Property Name:</label>
          <input
            type="text"
            id="property_name"
            value={propertyData.property_name}
            onChange={(e) => setPropertyData({
              ...propertyData,
              property_name: e.target.value
            })}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="residential_units">Residential Units:</label>
          <input
            type="number"
            id="residential_units"
            value={propertyData.residential_units}
            onChange={(e) => setPropertyData({
              ...propertyData,
              residential_units: parseInt(e.target.value) || 0
            })}
            min="1"
            max="500"
            required
          />
        </div>
        
        {/* Additional form fields... */}
        
        <button type="submit" disabled={loading}>
          {loading ? 'Analyzing...' : 'Analyze Property'}
        </button>
      </form>
      
      {error && (
        <div className="error-message">
          <h3>Error:</h3>
          <p>{error}</p>
        </div>
      )}
      
      {analysisResult && (
        <div className="analysis-results">
          <h3>Analysis Results</h3>
          <div className="metrics">
            <p><strong>NPV:</strong> ${analysisResult.results.financial_metrics.npv.toLocaleString()}</p>
            <p><strong>IRR:</strong> {(analysisResult.results.financial_metrics.irr * 100).toFixed(1)}%</p>
            <p><strong>Equity Multiple:</strong> {analysisResult.results.financial_metrics.equity_multiple.toFixed(2)}x</p>
            <p><strong>Recommendation:</strong> {analysisResult.results.investment_recommendation.recommendation}</p>
            <p><strong>Risk Level:</strong> {analysisResult.results.investment_recommendation.risk_level}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProFormaAnalysis;
```

#### Node.js Service Integration

```typescript
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

interface ProFormaClientConfig {
  baseURL: string;
  apiKey?: string;
  timeout?: number;
}

class ProFormaAPIClient {
  private client: AxiosInstance;
  
  constructor(config: ProFormaClientConfig) {
    const axiosConfig: AxiosRequestConfig = {
      baseURL: config.baseURL,
      timeout: config.timeout || 30000,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      }
    };
    
    if (config.apiKey) {
      axiosConfig.headers!['Authorization'] = `Bearer ${config.apiKey}`;
    }
    
    this.client = axios.create(axiosConfig);
    
    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error.response?.data || error.message);
        throw error;
      }
    );
  }
  
  async analyzeProperty(propertyData: PropertyInput): Promise<PropertyAnalysisResult> {
    const response = await this.client.post('/api/properties/analyze', propertyData);
    return response.data;
  }
  
  async runMonteCarloSimulation(propertyId: string, scenarios: number = 1000): Promise<MonteCarloResults> {
    const response = await this.client.post('/api/monte-carlo/simulate', {
      property_id: propertyId,
      scenarios,
      confidence_level: 0.95
    });
    return response.data;
  }
  
  async getMarketData(msaCode: string, parameters?: string[]): Promise<any> {
    const params = parameters ? { parameters: parameters.join(',') } : {};
    const response = await this.client.get(`/api/market-data/msa/${msaCode}`, { params });
    return response.data;
  }
  
  async analyzePortfolio(properties: PropertyInput[]): Promise<any> {
    const response = await this.client.post('/api/portfolio/analyze', {
      portfolio_name: 'API Portfolio Analysis',
      properties,
      analysis_options: {
        include_monte_carlo: true,
        correlation_analysis: true,
        diversification_metrics: true
      }
    });
    return response.data;
  }
}

// Example usage in Express.js application
import express from 'express';

const app = express();
app.use(express.json());

const proformaClient = new ProFormaAPIClient({
  baseURL: 'http://localhost:8000',
  timeout: 60000
});

app.post('/analyze-property', async (req, res) => {
  try {
    const analysisResult = await proformaClient.analyzeProperty(req.body);
    res.json(analysisResult);
  } catch (error) {
    res.status(500).json({ error: 'Analysis failed', details: error.message });
  }
});

app.get('/market-data/:msaCode', async (req, res) => {
  try {
    const marketData = await proformaClient.getMarketData(req.params.msaCode);
    res.json(marketData);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch market data', details: error.message });
  }
});

app.listen(3001, () => {
  console.log('API integration service running on port 3001');
});
```

## SDK and Client Libraries

### Python SDK

```python
# pip install proforma-analytics-sdk

from proforma_analytics_sdk import ProFormaClient, PropertyInput, MonteCarloConfig
from proforma_analytics_sdk.exceptions import APIError, ValidationError

# Initialize client
client = ProFormaClient(
    base_url="https://api.proforma.example.com",
    api_key=os.getenv("PROFORMA_API_KEY")
)

# Type-safe property input
property_input = PropertyInput(
    property_name="Chicago Investment",
    residential_units=24,
    renovation_time_months=6,
    commercial_units=0,
    investor_equity_share_pct=75.0,
    residential_rent_per_unit=2800,
    commercial_rent_per_unit=0,
    self_cash_percentage=30.0,
    city="Chicago",
    state="IL",
    purchase_price=3500000
)

try:
    # Analyze property with automatic validation
    result = client.analyze_property(property_input)
    
    # Access typed results
    print(f"NPV: ${result.financial_metrics.npv:,.0f}")
    print(f"IRR: {result.financial_metrics.irr:.1%}")
    print(f"Recommendation: {result.investment_recommendation.recommendation}")
    
    # Run Monte Carlo with configuration
    monte_carlo_config = MonteCarloConfig(
        scenarios=1000,
        confidence_level=0.95,
        stress_testing=True
    )
    
    simulation_result = client.run_monte_carlo(result.property_id, monte_carlo_config)
    
    # Access distribution results
    print(f"NPV P50: ${simulation_result.npv_distribution.p50:,.0f}")
    print(f"Risk of Loss: {simulation_result.risk_metrics.probability_of_loss:.1%}")

except ValidationError as e:
    print(f"Validation error: {e.message}")
    print(f"Invalid fields: {e.invalid_fields}")

except APIError as e:
    print(f"API error: {e.message}")
    print(f"Status code: {e.status_code}")
```

### TypeScript SDK

```typescript
// npm install @proforma/analytics-sdk

import { ProFormaClient, PropertyInput, MonteCarloConfig } from '@proforma/analytics-sdk';

// Initialize with configuration
const client = new ProFormaClient({
  baseURL: 'https://api.proforma.example.com',
  apiKey: process.env.PROFORMA_API_KEY,
  timeout: 60000,
  retries: 3
});

// Type-safe analysis
const analyzeProperty = async (): Promise<void> => {
  const propertyInput: PropertyInput = {
    property_name: 'Chicago Investment',
    residential_units: 24,
    renovation_time_months: 6,
    commercial_units: 0,
    investor_equity_share_pct: 75.0,
    residential_rent_per_unit: 2800,
    commercial_rent_per_unit: 0,
    self_cash_percentage: 30.0,
    city: 'Chicago',
    state: 'IL',
    purchase_price: 3500000
  };

  try {
    // Analyze with automatic retries
    const analysisResult = await client.analyzeProperty(propertyInput);
    
    // Typed results
    console.log(`NPV: $${analysisResult.results.financial_metrics.npv.toLocaleString()}`);
    console.log(`IRR: ${(analysisResult.results.financial_metrics.irr * 100).toFixed(1)}%`);
    
    // Run Monte Carlo simulation
    const monteCarloConfig: MonteCarloConfig = {
      scenarios: 1000,
      confidence_level: 0.95,
      stress_testing: true
    };
    
    const simulationResult = await client.runMonteCarloSimulation(
      analysisResult.property_id,
      monteCarloConfig
    );
    
    // Access results with type safety
    const { npv_distribution, risk_metrics } = simulationResult.results;
    console.log(`NPV P50: $${npv_distribution.p50.toLocaleString()}`);
    console.log(`Risk of Loss: ${(risk_metrics.probability_of_loss * 100).toFixed(1)}%`);
    
  } catch (error) {
    if (error instanceof client.ValidationError) {
      console.error('Validation error:', error.message);
      console.error('Invalid fields:', error.invalidFields);
    } else if (error instanceof client.APIError) {
      console.error('API error:', error.message);
      console.error('Status:', error.statusCode);
    }
  }
};
```

## Error Handling

### Common Error Responses

#### Validation Errors (400)

```json
{
  "error": "ValidationError",
  "message": "Invalid property parameters",
  "details": {
    "residential_units": "Must be between 1 and 500",
    "investor_equity_share_pct": "Must be between 0 and 100",
    "city": "Required field missing"
  },
  "error_code": "VALIDATION_ERROR"
}
```

#### Not Found Errors (404)

```json
{
  "error": "NotFoundError",
  "message": "Property analysis not found",
  "details": {
    "property_id": "prop_12345",
    "analysis_id": "analysis_67890"
  },
  "error_code": "RESOURCE_NOT_FOUND"
}
```

#### Internal Server Errors (500)

```json
{
  "error": "InternalServerError",
  "message": "Analysis calculation failed",
  "details": {
    "error_type": "IRR_CALCULATION_ERROR",
    "cash_flows": "Invalid cash flow sequence"
  },
  "error_code": "CALCULATION_ERROR",
  "request_id": "req_abc123"
}
```

### Error Handling Best Practices

#### Python Error Handling

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time

class ProFormaClientWithRetry:
    def __init__(self, base_url: str, api_key: str = None):
        self.base_url = base_url
        self.session = requests.Session()
        
        # Configure retries
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS", "POST"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
    
    def analyze_property_with_retry(self, property_data: dict, max_attempts: int = 3) -> dict:
        """Analyze property with exponential backoff retry logic"""
        
        for attempt in range(max_attempts):
            try:
                response = self.session.post(
                    f"{self.base_url}/api/properties/analyze",
                    json=property_data,
                    timeout=60
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 400:
                    # Validation error - don't retry
                    error_data = response.json()
                    raise ValueError(f"Validation error: {error_data['message']}")
                elif response.status_code == 429:
                    # Rate limited - wait and retry
                    retry_after = int(response.headers.get('Retry-After', 60))
                    time.sleep(retry_after)
                    continue
                elif response.status_code >= 500:
                    # Server error - retry
                    if attempt == max_attempts - 1:
                        response.raise_for_status()
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    response.raise_for_status()
                    
            except requests.exceptions.Timeout:
                if attempt == max_attempts - 1:
                    raise TimeoutError("Analysis request timed out after multiple attempts")
                time.sleep(2 ** attempt)
                
            except requests.exceptions.ConnectionError:
                if attempt == max_attempts - 1:
                    raise ConnectionError("Unable to connect to API after multiple attempts")
                time.sleep(2 ** attempt)
        
        raise Exception("Maximum retry attempts exceeded")
```

#### TypeScript Error Handling

```typescript
import axios, { AxiosError, AxiosRequestConfig } from 'axios';

interface APIError {
  error: string;
  message: string;
  details?: any;
  error_code?: string;
  request_id?: string;
}

class ProFormaAPIError extends Error {
  public statusCode: number;
  public errorCode?: string;
  public details?: any;
  public requestId?: string;

  constructor(statusCode: number, apiError: APIError) {
    super(apiError.message);
    this.name = 'ProFormaAPIError';
    this.statusCode = statusCode;
    this.errorCode = apiError.error_code;
    this.details = apiError.details;
    this.requestId = apiError.request_id;
  }
}

class ResilientProFormaClient {
  private baseURL: string;
  private apiKey?: string;
  private maxRetries: number = 3;

  constructor(baseURL: string, apiKey?: string) {
    this.baseURL = baseURL;
    this.apiKey = apiKey;
  }

  private async makeRequest<T>(config: AxiosRequestConfig, retryCount: number = 0): Promise<T> {
    try {
      const response = await axios({
        ...config,
        baseURL: this.baseURL,
        timeout: 60000,
        headers: {
          'Content-Type': 'application/json',
          ...(this.apiKey && { Authorization: `Bearer ${this.apiKey}` }),
          ...config.headers
        }
      });

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError<APIError>;
        
        // Handle different error types
        if (axiosError.response) {
          const { status, data } = axiosError.response;
          
          // Rate limiting - retry after delay
          if (status === 429 && retryCount < this.maxRetries) {
            const retryAfter = parseInt(axiosError.response.headers['retry-after'] || '60');
            await this.delay(retryAfter * 1000);
            return this.makeRequest(config, retryCount + 1);
          }
          
          // Server errors - retry with exponential backoff
          if (status >= 500 && retryCount < this.maxRetries) {
            await this.delay(Math.pow(2, retryCount) * 1000);
            return this.makeRequest(config, retryCount + 1);
          }
          
          // Client errors - don't retry
          throw new ProFormaAPIError(status, data);
        } else if (axiosError.request) {
          // Network error - retry
          if (retryCount < this.maxRetries) {
            await this.delay(Math.pow(2, retryCount) * 1000);
            return this.makeRequest(config, retryCount + 1);
          }
          throw new Error('Network error: Unable to reach API');
        }
      }
      
      throw error;
    }
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async analyzeProperty(propertyData: PropertyInput): Promise<PropertyAnalysisResult> {
    return this.makeRequest<PropertyAnalysisResult>({
      method: 'POST',
      url: '/api/properties/analyze',
      data: propertyData
    });
  }
}
```

## Rate Limiting and Performance

### Rate Limiting

**Default Limits:**
- **Per IP**: 100 requests per minute
- **Per API Key**: 1000 requests per minute  
- **Analysis Operations**: 20 per minute (computationally intensive)
- **Monte Carlo Simulations**: 5 per minute (high resource usage)

**Rate Limit Headers:**
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
X-RateLimit-Retry-After: 60
```

### Performance Optimization

#### Request Optimization

```python
# Batch multiple properties efficiently
def analyze_properties_optimized(client, properties):
    # Group by similar parameters for caching benefits
    grouped_properties = group_by_location_and_type(properties)
    
    # Use connection pooling
    session = requests.Session()
    adapter = HTTPAdapter(
        pool_connections=10,
        pool_maxsize=10,
        max_retries=3
    )
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    results = []
    for group in grouped_properties:
        # Analyze similar properties together
        group_results = []
        for property_data in group:
            result = analyze_single_property(session, property_data)
            group_results.append(result)
        results.extend(group_results)
    
    return results
```

#### Caching Strategy

```typescript
// Client-side caching for market data
class CachedProFormaClient {
  private cache = new Map<string, { data: any; timestamp: number }>();
  private cacheTimeout = 5 * 60 * 1000; // 5 minutes

  async getMarketDataCached(msaCode: string): Promise<any> {
    const cacheKey = `market_data_${msaCode}`;
    const cached = this.cache.get(cacheKey);
    
    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      return cached.data;
    }
    
    const data = await this.getMarketData(msaCode);
    this.cache.set(cacheKey, { data, timestamp: Date.now() });
    
    return data;
  }
}
```

#### Performance Monitoring

```python
import time
from functools import wraps

def performance_monitor(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Log performance metrics
            print(f"{func.__name__} completed in {execution_time:.3f}s")
            
            # Alert on slow operations
            if execution_time > 30:  # 30 seconds threshold
                print(f"SLOW OPERATION: {func.__name__} took {execution_time:.1f}s")
            
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"{func.__name__} failed after {execution_time:.3f}s: {str(e)}")
            raise
    return wrapper

@performance_monitor  
def analyze_property_monitored(client, property_data):
    return client.analyze_property(property_data)
```

## Testing and Validation

### Integration Testing

```python
import unittest
from unittest.mock import Mock, patch
import json

class TestProFormaAPIIntegration(unittest.TestCase):
    def setUp(self):
        self.client = ProFormaClient("http://localhost:8000")
        self.sample_property = {
            "property_name": "Test Property",
            "residential_units": 24,
            "renovation_time_months": 6,
            "commercial_units": 0,
            "investor_equity_share_pct": 75.0,
            "residential_rent_per_unit": 2800,
            "commercial_rent_per_unit": 0,
            "self_cash_percentage": 30.0,
            "city": "Chicago",
            "state": "IL",
            "purchase_price": 3500000
        }

    def test_successful_property_analysis(self):
        """Test successful property analysis"""
        result = self.client.analyze_property(self.sample_property)
        
        # Validate response structure
        self.assertIn('analysis_id', result)
        self.assertIn('property_id', result) 
        self.assertIn('results', result)
        
        # Validate financial metrics
        metrics = result['results']['financial_metrics']
        self.assertIn('npv', metrics)
        self.assertIn('irr', metrics)
        self.assertIn('equity_multiple', metrics)
        
        # Validate reasonable values
        self.assertGreater(metrics['npv'], -10000000)  # NPV > -$10M
        self.assertGreater(metrics['irr'], -1)  # IRR > -100%
        self.assertGreater(metrics['equity_multiple'], 0)  # Positive multiple
        
        # Validate recommendation
        recommendation = result['results']['investment_recommendation']
        valid_recommendations = ['STRONG_BUY', 'BUY', 'HOLD', 'SELL', 'STRONG_SELL']
        self.assertIn(recommendation['recommendation'], valid_recommendations)

    def test_validation_error_handling(self):
        """Test API validation error handling"""
        invalid_property = self.sample_property.copy()
        invalid_property['residential_units'] = -5  # Invalid value
        
        with self.assertRaises(ValueError) as context:
            self.client.analyze_property(invalid_property)
        
        self.assertIn('validation', str(context.exception).lower())

    def test_monte_carlo_simulation(self):
        """Test Monte Carlo simulation"""
        # First analyze property
        analysis_result = self.client.analyze_property(self.sample_property)
        property_id = analysis_result['property_id']
        
        # Run Monte Carlo simulation
        simulation_result = self.client.run_monte_carlo(property_id, scenarios=100)
        
        # Validate simulation results
        self.assertEqual(simulation_result['scenarios_completed'], 100)
        self.assertIn('npv_distribution', simulation_result['results'])
        self.assertIn('irr_distribution', simulation_result['results'])
        
        # Validate distribution percentiles
        npv_dist = simulation_result['results']['npv_distribution']
        self.assertLessEqual(npv_dist['p10'], npv_dist['p50'])
        self.assertLessEqual(npv_dist['p50'], npv_dist['p90'])

    def test_market_data_access(self):
        """Test market data retrieval"""
        # Chicago MSA
        market_data = self.client.get_market_data('16980', ['rent_growth', 'cap_rate'])
        
        # Validate structure
        self.assertEqual(market_data['msa_code'], '16980')
        self.assertIn('forecast', market_data)
        self.assertIn('rent_growth', market_data['forecast'])
        self.assertIn('cap_rate', market_data['forecast'])
        
        # Validate forecast length (6 years)
        self.assertEqual(len(market_data['forecast']['rent_growth']), 6)

if __name__ == '__main__':
    unittest.main()
```

### Load Testing

```python
import asyncio
import aiohttp
import time
from concurrent.futures import ThreadPoolExecutor
import statistics

async def load_test_analysis(session, property_data, semaphore):
    """Single property analysis for load testing"""
    async with semaphore:
        start_time = time.time()
        try:
            async with session.post(
                'http://localhost:8000/api/properties/analyze',
                json=property_data,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                result = await response.json()
                execution_time = time.time() - start_time
                return {
                    'success': response.status == 200,
                    'execution_time': execution_time,
                    'status_code': response.status,
                    'response_size': len(str(result))
                }
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                'success': False,
                'execution_time': execution_time,
                'error': str(e)
            }

async def run_load_test(concurrent_users=10, requests_per_user=5):
    """Run concurrent load test"""
    semaphore = asyncio.Semaphore(concurrent_users)
    
    # Sample property data
    sample_property = {
        "property_name": f"Load Test Property",
        "residential_units": 24,
        "renovation_time_months": 6,
        "commercial_units": 0,
        "investor_equity_share_pct": 75.0,
        "residential_rent_per_unit": 2800,
        "commercial_rent_per_unit": 0,
        "self_cash_percentage": 30.0,
        "city": "Chicago",
        "state": "IL",
        "purchase_price": 3500000
    }
    
    async with aiohttp.ClientSession() as session:
        # Create tasks for concurrent execution
        tasks = []
        for user in range(concurrent_users):
            for request in range(requests_per_user):
                property_data = sample_property.copy()
                property_data['property_name'] = f"Load Test Property {user}-{request}"
                
                task = load_test_analysis(session, property_data, semaphore)
                tasks.append(task)
        
        # Execute all tasks concurrently
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # Analyze results
        successful_requests = [r for r in results if r['success']]
        failed_requests = [r for r in results if not r['success']]
        
        if successful_requests:
            execution_times = [r['execution_time'] for r in successful_requests]
            
            print(f"\nLoad Test Results:")
            print(f"Concurrent Users: {concurrent_users}")
            print(f"Requests per User: {requests_per_user}")
            print(f"Total Requests: {len(results)}")
            print(f"Successful Requests: {len(successful_requests)}")
            print(f"Failed Requests: {len(failed_requests)}")
            print(f"Success Rate: {len(successful_requests)/len(results)*100:.1f}%")
            print(f"Total Test Duration: {total_time:.2f}s")
            print(f"Requests per Second: {len(results)/total_time:.2f}")
            print(f"Average Response Time: {statistics.mean(execution_times):.2f}s")
            print(f"95th Percentile Response Time: {sorted(execution_times)[int(0.95*len(execution_times))]:.2f}s")
            
        if failed_requests:
            print(f"\nFailure Analysis:")
            error_types = {}
            for failure in failed_requests:
                error_key = failure.get('error', 'Unknown Error')
                error_types[error_key] = error_types.get(error_key, 0) + 1
            
            for error, count in error_types.items():
                print(f"  {error}: {count} occurrences")

# Run load test
if __name__ == "__main__":
    asyncio.run(run_load_test(concurrent_users=20, requests_per_user=5))
```

## Production Deployment

### Environment Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  proforma-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - API_KEY_REQUIRED=true
      - RATE_LIMITING_ENABLED=true
      - DATABASE_URL=sqlite:///data/proforma_production.db
      - REDIS_URL=redis://redis:6379
      - LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - proforma-api
    restart: unless-stopped

volumes:
  redis_data:
```

### API Gateway Configuration

```nginx
# nginx.conf
upstream proforma_api {
    server proforma-api:8000;
}

server {
    listen 80;
    server_name api.proforma.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.proforma.example.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;
    limit_req zone=api burst=20 nodelay;

    # API endpoints
    location /api/ {
        proxy_pass http://proforma_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts for long-running analysis
        proxy_read_timeout 300s;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
    }

    # Health check
    location /health {
        proxy_pass http://proforma_api;
        access_log off;
    }

    # Documentation
    location /docs {
        proxy_pass http://proforma_api;
    }
}
```

### Monitoring and Observability

```python
# monitoring.py
from prometheus_client import Counter, Histogram, start_http_server
import time
from functools import wraps

# Metrics
REQUEST_COUNT = Counter('proforma_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('proforma_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
ANALYSIS_COUNT = Counter('proforma_analysis_total', 'Total property analyses', ['status'])
MONTE_CARLO_COUNT = Counter('proforma_monte_carlo_total', 'Total Monte Carlo simulations', ['scenarios'])

def monitor_endpoint(endpoint_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            status = 'success'
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = 'error'
                raise
            finally:
                duration = time.time() - start_time
                REQUEST_DURATION.labels(method='POST', endpoint=endpoint_name).observe(duration)
                REQUEST_COUNT.labels(method='POST', endpoint=endpoint_name, status=status).inc()
                
                if endpoint_name == 'analyze_property':
                    ANALYSIS_COUNT.labels(status=status).inc()
        
        return wrapper
    return decorator

# Start Prometheus metrics server
start_http_server(8001)
```

### Deployment Script

```bash
#!/bin/bash
# deploy.sh

set -e

echo "🚀 Deploying Pro Forma Analytics API to Production"

# Environment check
if [ -z "$PROFORMA_API_KEY" ]; then
    echo "❌ Error: PROFORMA_API_KEY environment variable not set"
    exit 1
fi

# Build and test
echo "🔨 Building application..."
docker-compose build

echo "🧪 Running tests..."
docker-compose run --rm proforma-api python -m pytest tests/ -v

echo "🔍 Running security scan..."
docker run --rm -v $(pwd):/app pyupio/safety check

echo "📊 Running load test..."
docker-compose run --rm proforma-api python tests/load/load_test.py

# Deploy
echo "🎯 Deploying to production..."
docker-compose down
docker-compose up -d

# Health check
echo "🏥 Checking health..."
sleep 30

for i in {1..10}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ API is healthy"
        break
    else
        echo "⏳ Waiting for API to be ready... ($i/10)"
        sleep 10
    fi
    
    if [ $i -eq 10 ]; then
        echo "❌ API health check failed"
        docker-compose logs proforma-api
        exit 1
    fi
done

echo "✅ Deployment completed successfully"
echo "🌐 API available at: https://api.proforma.example.com"
echo "📖 Documentation: https://api.proforma.example.com/docs"
```

## Troubleshooting

### Common Issues

#### Connection Issues

```bash
# Check API server status
curl -I http://localhost:8000/health

# Expected: HTTP/1.1 200 OK

# Check for port conflicts
netstat -tuln | grep 8000

# Check Docker containers
docker-compose ps

# View API logs
docker-compose logs proforma-api
```

#### Performance Issues

```python
# Debug slow requests
import cProfile
import pstats

def profile_analysis():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Run analysis
    result = client.analyze_property(property_data)
    
    profiler.disable()
    
    # Print stats
    stats = pstats.Stats(profiler)
    stats.sort_stats('tottime')
    stats.print_stats(10)

profile_analysis()
```

#### Memory Issues

```python
# Monitor memory usage
import psutil
import os

def monitor_memory():
    process = psutil.Process(os.getpid())
    memory_usage = process.memory_info().rss / 1024 / 1024  # MB
    print(f"Memory usage: {memory_usage:.1f} MB")

# Check during analysis
monitor_memory()
result = client.analyze_property(property_data)
monitor_memory()
```

### Debug Mode

```python
# Enable detailed logging
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Enable API debugging
client = ProFormaClient(
    base_url="http://localhost:8000",
    debug=True,  # Enables request/response logging
    timeout=120  # Extended timeout for debugging
)
```

---

*This API Integration Guide provides comprehensive coverage of the Pro Forma Analytics Tool API. For specific implementation examples and advanced use cases, refer to the example code in the repository and the interactive API documentation.*