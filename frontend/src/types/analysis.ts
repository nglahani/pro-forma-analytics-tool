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
  purchase_price: number;
  renovation_cost: number;
  total_acquisition_cost: number;
  loan_amount: number;
  cash_required: number;
  lender_reserves: number;
  closing_costs: number;
  total_cash_investment: number;
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
  investment_recommendation: InvestmentRecommendation;
  risk_assessment: RiskAssessment;
}

export enum InvestmentRecommendation {
  STRONG_BUY = "STRONG_BUY",
  BUY = "BUY", 
  HOLD = "HOLD",
  SELL = "SELL",
  STRONG_SELL = "STRONG_SELL"
}

export enum RiskAssessment {
  LOW = "LOW",
  MODERATE = "MODERATE", 
  HIGH = "HIGH",
  VERY_HIGH = "VERY_HIGH"
}

export interface DCFAnalysisResult {
  property_id: string;
  analysis_id: string;
  analysis_date: string;
  assumptions: DCFAssumptions;
  initial_numbers: InitialNumbers;
  cash_flow_projections: CashFlowProjection[];
  financial_metrics: FinancialMetrics;
  execution_time_ms: number;
  success: boolean;
  errors?: string[];
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