/**
 * Property-related TypeScript definitions matching FastAPI backend
 * Based on SimplifiedPropertyInput from src/domain/entities/property_data.py
 */

export enum RenovationStatus {
  NOT_NEEDED = "not_needed",
  PLANNED = "planned",
  IN_PROGRESS = "in_progress",
  COMPLETED = "completed"
}

export enum PropertyType {
  MULTIFAMILY = "multifamily",
  OFFICE = "office", 
  RETAIL = "retail",
  INDUSTRIAL = "industrial",
  MIXED_USE = "mixed_use"
}

export interface ResidentialUnits {
  total_units: number;
  average_rent_per_unit: number;
  unit_types?: string;
  average_square_feet_per_unit?: number;
}

export interface CommercialUnits {
  total_units: number;
  average_rent_per_unit: number;
  unit_types?: string;
  average_square_feet_per_unit?: number;
}

export interface RenovationInfo {
  status: RenovationStatus;
  anticipated_duration_months?: number;
  start_date?: string;
  completion_date?: string;
  estimated_cost?: number;
  description?: string;
}

export interface InvestorEquityStructure {
  investor_equity_share_pct: number;
  self_cash_percentage: number;
  number_of_investors?: number;
  investment_structure?: string;
}

export interface PropertyAddress {
  street: string;
  city: string;
  state: string;
  zip_code: string;
  msa_code?: string; // Auto-resolved from city/state
}

export interface LoanTerms {
  interest_rate?: number; // Optional - can use market data
  loan_term_years: number;
  loan_to_value_ratio?: number;
}

export interface PropertyFinancials {
  purchase_price: number;
  down_payment_percentage: number;
  loan_terms: LoanTerms;
  monthly_rent_per_unit: number;
  other_monthly_income: number;
  vacancy_rate?: number; // Optional - can use market data
  monthly_operating_expenses: number;
  annual_property_taxes: number;
  annual_insurance: number;
  capex_percentage: number;
}

export interface AnalysisParameters {
  analysis_period_years: number; // Default 6
  exit_cap_rate?: number; // Optional - can use market data
}

export interface SimplifiedPropertyInput {
  property_id: string;
  property_name: string;
  property_type: PropertyType;
  address: PropertyAddress;
  
  // Property Details
  residential_units: ResidentialUnits;
  commercial_units?: CommercialUnits;
  total_square_feet: number;
  year_built: number;
  renovation_info: RenovationInfo;
  equity_structure: InvestorEquityStructure;
  
  // Financial Data
  financials: PropertyFinancials;
  
  // Analysis Configuration
  analysis_parameters: AnalysisParameters;
  analysis_date: string;
  notes?: string;
}

export interface PropertyMetrics {
  total_units: number;
  monthly_gross_rent: number;
  annual_gross_rent: number;
  property_type: string;
  is_mixed_use: boolean;
  purchase_price?: number;
  price_per_unit?: number;
  total_cash_required?: number;
  gross_cap_rate?: number;
}

// Property Templates for the UI
export interface PropertyTemplate {
  id: string;
  name: string;
  description: string;
  icon: string;
  defaults: Partial<SimplifiedPropertyInput>;
  requiredFields: string[];
  helpText: Record<string, string>;
}

// MSA Information
export interface MSAInfo {
  msa_code: string;
  name: string;
  state: string;
  major_cities: string[];
  population?: number;
  market_tier: "primary" | "secondary" | "tertiary";
  notes?: string;
}

// Form Validation Types
export interface PropertyValidationErrors {
  property_name?: string;
  address?: {
    street?: string;
    city?: string;
    state?: string;
    zip_code?: string;
  };
  residential_units?: {
    total_units?: string;
    average_rent_per_unit?: string;
  };
  financials?: {
    purchase_price?: string;
    down_payment_percentage?: string;
    loan_terms?: {
      loan_term_years?: string;
    };
    monthly_operating_expenses?: string;
    annual_property_taxes?: string;
    annual_insurance?: string;
  };
  [key: string]: any;
}

// Backend-Compatible Simplified Property Input (matches backend exactly)
export interface SimplifiedPropertyInputBackend {
  property_id: string;
  property_name: string;
  analysis_date: string; // ISO date string
  residential_units: ResidentialUnits;
  renovation_info: RenovationInfo;
  equity_structure: InvestorEquityStructure;
  commercial_units?: CommercialUnits;
  
  // Optional fields for enhanced analysis (matches backend exactly)
  city?: string;
  state?: string;
  msa_code?: string;
  purchase_price?: number;
  property_address?: string;
  notes?: string;
}

// Form Step Types for Multi-step Wizard
export interface PropertyFormStep {
  id: string;
  title: string;
  description: string;
  fields: string[];
  isValid: boolean;
  isComplete: boolean;
}

// Market Data Defaults
export interface MarketDataDefaults {
  interest_rate: number;
  cap_rate: number;
  vacancy_rate: number;
  rent_growth_rate: number;
  expense_growth_rate: number;
  property_growth_rate: number;
  ltv_ratio: number;
  management_fee_pct: number;
  closing_cost_pct: number;
  lender_reserves_months: number;
  maintenance_reserve_per_unit: number;
  last_updated: string;
}

// Address Validation
export interface AddressValidationResult {
  isValid: boolean;
  suggestions?: PropertyAddress[];
  msa_info?: MSAInfo;
  market_data?: MarketDataDefaults;
  error?: string;
}