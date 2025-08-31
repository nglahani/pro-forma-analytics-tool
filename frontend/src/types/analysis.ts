/**
 * DCF Analysis result types matching FastAPI backend responses
 * Based on the financial metrics and analysis services
 */

import { SimplifiedPropertyInput } from './property';

export interface DCFAssumptions {
  interest_rate: number;
  cap_rate: number;
  vacancy_rate: number;
  rent_growth_rate: number;
  expense_growth_rate: number;
  property_growth_rate: number;
  ltv_ratio: number;
  closing_costs_pct: number;
  lender_reserves_pct: number;
}

export interface InitialNumbers {
  property_id: string;
  scenario_id: string;
  calculation_date: string; // ISO date string
  
  // Purchase Details
  purchase_price: number;
  closing_cost_amount: number;
  renovation_capex: number;
  cost_basis: number;
  
  // Financing Calculations  
  loan_amount: number;
  annual_interest_expense: number;
  lender_reserves_amount: number;
  
  // Equity Requirements
  investor_cash_required: number;
  operator_cash_required: number;
  total_cash_required: number;
  
  // Valuation Metrics
  after_repair_value: number;
  initial_cap_rate: number;
  
  // Income Structure
  pre_renovation_annual_rent: number;
  post_renovation_annual_rent: number;
  year_1_rental_income: number;
  
  // Operating Expenses (Year 1 baseline)
  property_taxes: number;
  insurance: number;
  repairs_maintenance: number;
  property_management: number;
  admin_expenses: number;
  contracting: number;
  replacement_reserves: number;
  total_operating_expenses: number;
  
  // Investment Structure
  investor_equity_share: number;
  preferred_return_rate: number;
}

export interface CashFlowProjection {
  year: number;
  gross_rental_income: number;
  vacancy_loss: number;
  effective_gross_income: number;
  operating_expenses: number;
  net_operating_income: number;
  debt_service: number;
  net_cash_flow: number;
  cumulative_cash_flow: number;
}

export interface FinancialMetrics {
  npv: number;
  irr: number;
  equity_multiple: number;
  total_return: number;
  average_annual_return: number;
  payback_period: number;
  terminal_value: number;
  total_cash_invested: number;
  total_proceeds: number;
  risk_level: RiskLevel; // Updated to match backend field name
}

export enum InvestmentRecommendation {
  STRONG_BUY = "STRONG_BUY",
  BUY = "BUY", 
  HOLD = "HOLD",
  SELL = "SELL",
  STRONG_SELL = "STRONG_SELL"
}

export enum RiskLevel {
  LOW = "LOW",
  MODERATE = "MODERATE", 
  HIGH = "HIGH",
  VERY_HIGH = "VERY_HIGH"
}

// Keep RiskAssessment as alias for backward compatibility
export type RiskAssessment = RiskLevel;
export const RiskAssessment = RiskLevel;

export interface AnalysisMetadata {
  processing_time_seconds: number;
  dcf_engine_version: string;
  analysis_timestamp: string; // datetime from backend
  data_sources: Record<string, string>;
  assumptions_summary: Record<string, any>;
}

export interface DCFAnalysisResult {
  success: boolean;
  request_id: string;
  property_id: string;
  analysis_date: string; // datetime from backend
  financial_metrics: FinancialMetrics;
  cash_flows?: CashFlowProjection[]; // Optional from backend
  dcf_assumptions: DCFAssumptions;
  investment_recommendation: InvestmentRecommendation; // Direct field from backend
  metadata: AnalysisMetadata;
  monte_carlo_results?: any; // Optional additional results
}

// Monte Carlo Simulation Types
export interface MonteCarloScenario {
  scenario_id: number;
  npv: number;
  irr: number;
  market_classification: MarketClassification;
  growth_score: number;
  risk_score: number;
  assumptions: DCFAssumptions;
}

export enum MarketClassification {
  BULL = "BULL",
  BEAR = "BEAR", 
  NEUTRAL = "NEUTRAL",
  GROWTH = "GROWTH",
  STRESS = "STRESS"
}

export interface MonteCarloResult {
  simulation_id: string;
  property_id: string;
  total_scenarios: number;
  scenarios: MonteCarloScenario[];
  statistics: MonteCarloStatistics;
  execution_time_ms: number;
  success: boolean;
  // Additional fields for visualization
  percentiles: {
    npv: {
      p5: number;
      p25: number;
      median: number;
      p75: number;
      p95: number;
    };
    irr: {
      p5: number;
      p25: number;
      median: number;
      p75: number;
      p95: number;
    };
    total_cash_flow: {
      p5: number;
      p25: number;
      median: number;
      p75: number;
      p95: number;
    };
  };
  distribution: ScenarioDistribution[];
  risk_distribution: {
    low: number;
    moderate: number;
    high: number;
  };
  overall_risk_assessment: string;
}

export interface ScenarioDistribution {
  scenario_id: number;
  npv: number;
  irr: number;
  total_cash_flow: number;
  risk_score: number;
  market_classification: MarketClassification;
}

export interface MonteCarloStatistics {
  npv_stats: {
    mean: number;
    median: number;
    std_dev: number;
    min: number;
    max: number;
    percentile_5: number;
    percentile_25: number;
    percentile_75: number;
    percentile_95: number;
  };
  irr_stats: {
    mean: number;
    median: number;
    std_dev: number;
    min: number;
    max: number;
    percentile_5: number;
    percentile_25: number;
    percentile_75: number;
    percentile_95: number;
  };
  risk_metrics: {
    probability_of_loss: number;
    value_at_risk_5pct: number;
    expected_shortfall: number;
  };
}

// Market Data Types
export interface MarketData {
  msa_code: string;
  parameter_name: string;
  value: number;
  date: string;
  source: string;
  confidence_level?: number;
}

export interface MarketForecast {
  msa_code: string;
  parameter_name: string;
  forecast_date: string;
  forecast_value: number;
  confidence_interval_lower: number;
  confidence_interval_upper: number;
  trend: "increasing" | "decreasing" | "stable";
}

// Batch Analysis Types
export interface AnalysisBatchRequest {
  properties: SimplifiedPropertyInput[];
  monte_carlo_scenarios?: number;
  analysis_options?: {
    include_monte_carlo: boolean;
    include_market_data: boolean;
    parallel_processing: boolean;
  };
}

export interface BatchAnalysisResult {
  batch_id: string;
  total_properties: number;
  completed_analyses: DCFAnalysisResult[];
  failed_analyses: {
    property_id: string;
    error_message: string;
  }[];
  summary_statistics: {
    avg_npv: number;
    avg_irr: number;
    success_rate: number;
  };
  execution_time_ms: number;
}