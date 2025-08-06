/**
 * FastAPI client types and response interfaces
 * Based on the REST API endpoints from src/presentation/api/
 */

import { 
  DCFAnalysisResult, 
  MonteCarloResult, 
  BatchAnalysisResult, 
  MarketData, 
  MarketForecast 
} from './analysis';
import { SimplifiedPropertyInput } from './property';

// API Response wrapper
export interface APIResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  errors?: string[];
  execution_time_ms?: number;
  timestamp: string;
}

// API Error Response
export interface APIError {
  success: false;
  error_code: string;
  error_message: string;
  error_details?: Record<string, unknown>;
  suggestions?: string[];
  timestamp: string;
}

// Authentication Types
export interface User {
  id: string;
  email: string;
  created_at: string;
  api_key: string;
}

export interface AuthResponse {
  user: User;
  session_token: string;
  expires_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  confirm_password: string;
}

// DCF Analysis Request/Response
export interface DCFAnalysisRequest {
  property_data: SimplifiedPropertyInput;
  options?: {
    include_monte_carlo?: boolean;
    monte_carlo_scenarios?: number;
    include_market_data?: boolean;
  };
}

export type DCFAnalysisResponse = APIResponse<DCFAnalysisResult>;

// Monte Carlo Simulation Request/Response
export interface MonteCarloRequest {
  property_data: SimplifiedPropertyInput;
  scenarios: number;
  options?: {
    correlation_matrix?: boolean;
    detailed_scenarios?: boolean;
  };
}

export type MonteCarloResponse = APIResponse<MonteCarloResult>;

// Batch Analysis Request/Response
export interface APIBatchAnalysisRequest {
  properties: SimplifiedPropertyInput[];
  options?: {
    monte_carlo_scenarios?: number;
    parallel_processing?: boolean;
    max_concurrent?: number;
  };
}

export type BatchAnalysisResponse = APIResponse<BatchAnalysisResult>;

// Market Data Request/Response
export interface MarketDataRequest {
  msa_code: string;
  parameters?: string[];
  date_range?: {
    start_date: string;
    end_date: string;
  };
}

export type MarketDataResponse = APIResponse<MarketData[]>;

// Market Forecast Request/Response
export interface MarketForecastRequest {
  parameter: string;
  msa_code: string;
  forecast_horizon?: number;
}

export type MarketForecastResponse = APIResponse<MarketForecast[]>;

// System Health Response
export interface HealthStatus {
  status: "healthy" | "degraded" | "unhealthy";
  timestamp: string;
  version: string;
  environment: string;
  uptime_seconds: number;
  dependencies: Record<string, string>;
}

export type HealthResponse = APIResponse<HealthStatus>;

// Configuration Response
export interface SystemConfig {
  api_version: string;
  supported_msas: string[];
  max_monte_carlo_scenarios: number;
  rate_limits: {
    requests_per_minute: number;
    concurrent_analyses: number;
  };
  features: {
    monte_carlo_enabled: boolean;
    batch_analysis_enabled: boolean;
    market_data_enabled: boolean;
  };
}

export type ConfigResponse = APIResponse<SystemConfig>;

// FastAPI Client Configuration
export interface APIClientConfig {
  baseURL: string;
  apiKey: string;
  timeout: number;
  retryAttempts: number;
  retryDelay: number;
}

// Request Options
export interface RequestOptions {
  timeout?: number;
  retries?: number;
  headers?: Record<string, string>;
  signal?: AbortSignal;
}

// Pagination (for future use)
export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

// WebSocket Types (for real-time updates)
export interface WebSocketMessage {
  type: 'analysis_progress' | 'analysis_complete' | 'error' | 'heartbeat';
  data: unknown;
  timestamp: string;
}

export interface AnalysisProgressMessage {
  analysis_id: string;
  progress_percent: number;
  current_step: string;
  estimated_completion_ms: number;
}

export interface AnalysisCompleteMessage {
  analysis_id: string;
  result: DCFAnalysisResult | MonteCarloResult;
}