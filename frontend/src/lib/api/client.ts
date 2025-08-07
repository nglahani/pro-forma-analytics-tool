/**
 * FastAPI Client
 * HTTP client for communicating with the Pro Forma Analytics FastAPI backend
 */

import { SimplifiedPropertyInput } from '@/types/property';
import { MonteCarloResult, MarketData, MarketForecast } from '@/types/analysis';

// API Response types matching FastAPI backend
export interface DCFAnalysisResponse {
  property_id: string;
  analysis_id: string;
  npv: number;
  irr: number;
  equity_multiple: number;
  total_return: number;
  investment_recommendation: 'STRONG_BUY' | 'BUY' | 'HOLD' | 'SELL' | 'STRONG_SELL';
  analysis_date: string;
  terminal_value: number;
  total_cash_flow: number;
  risk_assessment: {
    risk_score: number;
    growth_score: number;
    market_classification: string;
  };
}

export interface MonteCarloResponse {
  simulation_id: string;
  property_id: string;
  total_scenarios: number;
  successful_scenarios: number;
  average_npv: number;
  average_irr: number;
  npv_percentiles: {
    p5: number;
    p25: number;
    p50: number;
    p75: number;
    p95: number;
  };
  irr_percentiles: {
    p5: number;
    p25: number;
    p50: number;
    p75: number;
    p95: number;
  };
  risk_metrics: {
    value_at_risk_5: number;
    expected_shortfall: number;
    probability_of_loss: number;
    sharpe_ratio: number;
  };
  scenario_classification: {
    bull_market: number;
    bear_market: number;
    neutral_market: number;
    growth_market: number;
    stress_market: number;
  };
}

export interface MarketDataResponse {
  msa_code: string;
  msa_name: string;
  data_points: Array<{
    parameter: string;
    value: number;
    date: string;
    forecast_confidence?: number;
  }>;
  last_updated: string;
}

export interface HealthCheckResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  version: string;
  environment: string;
  uptime_seconds: number;
  dependencies: Record<string, string>;
}

class APIClient {
  private baseURL: string;
  private apiKey: string;

  constructor() {
    // Use environment variable or fallback to localhost for development
    this.baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    this.apiKey = '';
  }

  setApiKey(apiKey: string) {
    this.apiKey = apiKey;
  }

  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const config: RequestInit = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': this.apiKey,
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(
          errorData?.detail || 
          errorData?.message || 
          `HTTP ${response.status}: ${response.statusText}`
        );
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('An unexpected error occurred');
    }
  }

  // Health Check
  async healthCheck(): Promise<HealthCheckResponse> {
    return this.makeRequest<HealthCheckResponse>('/api/v1/health');
  }

  // DCF Analysis
  async runDCFAnalysis(propertyData: SimplifiedPropertyInput): Promise<DCFAnalysisResponse> {
    return this.makeRequest<DCFAnalysisResponse>('/api/v1/analysis/dcf', {
      method: 'POST',
      body: JSON.stringify(propertyData),
    });
  }

  // Get Analysis History
  async getAnalysisHistory(limit?: number): Promise<DCFAnalysisResponse[]> {
    const queryParams = new URLSearchParams();
    if (limit) {
      queryParams.append('limit', limit.toString());
    }
    
    const endpoint = `/api/v1/analysis/history${
      queryParams.toString() ? `?${queryParams.toString()}` : ''
    }`;
    
    return this.makeRequest<DCFAnalysisResponse[]>(endpoint);
  }

  // Get Single Analysis
  async getAnalysis(analysisId: string): Promise<DCFAnalysisResponse> {
    return this.makeRequest<DCFAnalysisResponse>(`/api/v1/analysis/${analysisId}`);
  }

  // Batch DCF Analysis
  async runBatchDCFAnalysis(properties: SimplifiedPropertyInput[]): Promise<DCFAnalysisResponse[]> {
    return this.makeRequest<DCFAnalysisResponse[]>('/api/v1/analysis/batch', {
      method: 'POST',
      body: JSON.stringify({ properties }),
    });
  }

  // Get Batch Analysis Status
  async getBatchAnalysisStatus(batchId: string): Promise<{
    batch_id: string;
    status: 'pending' | 'processing' | 'completed' | 'failed';
    completed_count: number;
    total_count: number;
    results?: DCFAnalysisResponse[];
  }> {
    return this.makeRequest(`/api/v1/analysis/batch/${batchId}/status`);
  }

  // Monte Carlo Simulation
  async runMonteCarloSimulation(
    propertyData: SimplifiedPropertyInput,
    options: {
      numScenarios?: number;
      includeCorrelations?: boolean;
      includeMarketCycles?: boolean;
      randomSeed?: number;
      confidenceLevel?: number;
    } = {}
  ): Promise<MonteCarloResult> {
    const {
      numScenarios = 1000,
      includeCorrelations = true,
      includeMarketCycles = true,
      randomSeed,
      confidenceLevel = 95,
    } = options;

    return this.makeRequest<MonteCarloResult>('/api/v1/simulation/monte-carlo', {
      method: 'POST',
      body: JSON.stringify({
        property_data: propertyData,
        num_scenarios: numScenarios,
        include_correlations: includeCorrelations,
        include_market_cycles: includeMarketCycles,
        random_seed: randomSeed,
        confidence_level: confidenceLevel,
      }),
    });
  }

  // Get Monte Carlo Simulation Status (for progress tracking)
  async getMonteCarloStatus(simulationId: string): Promise<{
    simulation_id: string;
    status: 'initializing' | 'running' | 'analyzing' | 'complete' | 'error';
    progress: number;
    current_scenario: number;
    total_scenarios: number;
    estimated_time_remaining: number;
    message: string;
    results?: MonteCarloResult;
  }> {
    return this.makeRequest(`/api/v1/simulation/monte-carlo/${simulationId}/status`);
  }

  // Start Monte Carlo Simulation (async with progress tracking)
  async startMonteCarloSimulation(
    propertyData: SimplifiedPropertyInput,
    options: {
      numScenarios?: number;
      includeCorrelations?: boolean;
      includeMarketCycles?: boolean;
      randomSeed?: number;
      confidenceLevel?: number;
    } = {}
  ): Promise<{ simulation_id: string }> {
    const {
      numScenarios = 1000,
      includeCorrelations = true,
      includeMarketCycles = true,
      randomSeed,
      confidenceLevel = 95,
    } = options;

    return this.makeRequest<{ simulation_id: string }>('/api/v1/simulation/monte-carlo/start', {
      method: 'POST',
      body: JSON.stringify({
        property_data: propertyData,
        num_scenarios: numScenarios,
        include_correlations: includeCorrelations,
        include_market_cycles: includeMarketCycles,
        random_seed: randomSeed,
        confidence_level: confidenceLevel,
      }),
    });
  }

  // Stop Monte Carlo Simulation
  async stopMonteCarloSimulation(simulationId: string): Promise<{ success: boolean }> {
    return this.makeRequest(`/api/v1/simulation/monte-carlo/${simulationId}/stop`, {
      method: 'POST',
    });
  }

  // Market Data
  async getMarketData(
    msaCode: string, 
    options: {
      parameters?: string[];
      startDate?: string;
      endDate?: string;
      includeForecasts?: boolean;
    } = {}
  ): Promise<MarketData> {
    const { parameters, startDate, endDate, includeForecasts } = options;
    const queryParams = new URLSearchParams();
    
    if (parameters && parameters.length > 0) {
      queryParams.append('parameters', parameters.join(','));
    }
    if (startDate) {
      queryParams.append('start_date', startDate);
    }
    if (endDate) {
      queryParams.append('end_date', endDate);
    }
    if (includeForecasts) {
      queryParams.append('include_forecasts', 'true');
    }
    
    const endpoint = `/api/v1/data/markets/${msaCode}${
      queryParams.toString() ? `?${queryParams.toString()}` : ''
    }`;
    
    return this.makeRequest<MarketData>(endpoint);
  }

  // Get All Available MSAs
  async getAvailableMSAs(): Promise<Array<{
    msa_code: string;
    name: string;
    state: string;
    data_availability: {
      parameters: string[];
      date_range: {
        start: string;
        end: string;
      };
    };
  }>> {
    return this.makeRequest('/api/v1/data/markets');
  }

  // Get Market Data for Multiple MSAs (comparison)
  async compareMarketData(
    msaCodes: string[],
    parameters: string[],
    options: {
      startDate?: string;
      endDate?: string;
    } = {}
  ): Promise<{
    comparison_id: string;
    msas: Array<{
      msa_code: string;
      name: string;
      data: MarketData;
    }>;
  }> {
    const { startDate, endDate } = options;
    
    return this.makeRequest('/api/v1/data/markets/compare', {
      method: 'POST',
      body: JSON.stringify({
        msa_codes: msaCodes,
        parameters,
        start_date: startDate,
        end_date: endDate,
      }),
    });
  }

  // Forecast Data
  async getForecastData(
    parameter: string,
    msaCode: string,
    options: {
      horizonMonths?: number;
      confidenceLevel?: number;
      includeHistorical?: boolean;
    } = {}
  ): Promise<MarketForecast> {
    const { horizonMonths, confidenceLevel, includeHistorical } = options;
    const queryParams = new URLSearchParams();
    
    if (horizonMonths) {
      queryParams.append('horizon_months', horizonMonths.toString());
    }
    if (confidenceLevel) {
      queryParams.append('confidence_level', confidenceLevel.toString());
    }
    if (includeHistorical) {
      queryParams.append('include_historical', 'true');
    }
    
    const endpoint = `/api/v1/data/forecasts/${parameter}/${msaCode}${
      queryParams.toString() ? `?${queryParams.toString()}` : ''
    }`;
    
    return this.makeRequest<MarketForecast>(endpoint);
  }

  // Get Forecasts for Multiple Parameters
  async getMultiParameterForecast(
    parameters: string[],
    msaCode: string,
    options: {
      horizonMonths?: number;
      confidenceLevel?: number;
    } = {}
  ): Promise<{
    msa_code: string;
    forecasts: MarketForecast[];
  }> {
    const { horizonMonths, confidenceLevel } = options;
    
    return this.makeRequest('/api/v1/data/forecasts/multi', {
      method: 'POST',
      body: JSON.stringify({
        parameters,
        msa_code: msaCode,
        horizon_months: horizonMonths,
        confidence_level: confidenceLevel,
      }),
    });
  }

  // Address Validation and MSA Detection
  async validateAddress(address: {
    street: string;
    city: string;
    state: string;
    zip_code?: string;
  }): Promise<{
    isValid: boolean;
    suggestions?: Array<{
      street: string;
      city: string;
      state: string;
      zip_code: string;
      msa_code?: string;
    }>;
    msa_info?: {
      msa_code: string;
      name: string;
      state: string;
    };
    error?: string;
  }> {
    return this.makeRequest('/api/v1/data/validate-address', {
      method: 'POST',
      body: JSON.stringify(address),
    });
  }

  // Get Market Data Defaults for Property Form
  async getMarketDataDefaults(msaCode: string): Promise<{
    interest_rate: number;
    cap_rate: number;
    vacancy_rate: number;
    rent_growth_rate: number;
    expense_growth_rate: number;
    property_growth_rate: number;
    last_updated: string;
  }> {
    return this.makeRequest(`/api/v1/data/market-defaults/${msaCode}`);
  }

  // Export Analysis Results
  async exportAnalysis(
    analysisId: string, 
    format: 'pdf' | 'excel'
  ): Promise<Blob> {
    const response = await fetch(`${this.baseURL}/api/v1/analysis/${analysisId}/export/${format}`, {
      method: 'GET',
      headers: {
        'X-API-Key': this.apiKey,
      },
    });

    if (!response.ok) {
      throw new Error(`Export failed: ${response.statusText}`);
    }

    return await response.blob();
  }

  // Export Batch Analysis Results
  async exportBatchAnalysis(
    batchId: string,
    format: 'pdf' | 'excel'
  ): Promise<Blob> {
    const response = await fetch(`${this.baseURL}/api/v1/analysis/batch/${batchId}/export/${format}`, {
      method: 'GET',
      headers: {
        'X-API-Key': this.apiKey,
      },
    });

    if (!response.ok) {
      throw new Error(`Batch export failed: ${response.statusText}`);
    }

    return await response.blob();
  }

  // System Configuration (Admin only)
  async getSystemConfig(): Promise<{
    database_info: Record<string, unknown>;
    api_settings: Record<string, unknown>;
    forecast_settings: Record<string, unknown>;
  }> {
    return this.makeRequest('/api/v1/config');
  }
}

// Export singleton instance
export const apiClient = new APIClient();

// Export class for testing
export { APIClient };