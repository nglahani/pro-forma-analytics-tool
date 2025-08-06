/**
 * Centralized type exports for the Pro Forma Analytics frontend
 */

// Property types
export * from './property';

// Analysis types  
export * from './analysis';

// API types
export * from './api';

// Re-export commonly used types for convenience
export type {
  SimplifiedPropertyInput,
  PropertyTemplate,
  MSAInfo
} from './property';

export type {
  DCFAnalysisResult,
  MonteCarloResult,
  FinancialMetrics,
  InvestmentRecommendation,
  RiskAssessment
} from './analysis';

export type {
  APIResponse,
  APIError,
  User,
  DCFAnalysisResponse,
  MonteCarloResponse
} from './api';