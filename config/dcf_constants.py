"""
DCF Engine Configuration Constants

Centralized configuration for all magic numbers and constants used
throughout the DCF calculation engine. This enables easy adjustment
of business rules and calculation parameters.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class FinancialCalculationConstants:
    """Constants for financial calculations and assumptions."""
    
    # Renovation and CapEx
    RENOVATION_COST_PER_UNIT: float = 10000.0  # Cost per unit for renovation CapEx estimation
    POST_RENOVATION_RENT_MULTIPLIER: float = 1.125  # 12.5% rent increase after renovation
    
    # Operating Assumptions
    DEFAULT_EXPENSE_RATIO: float = 0.25  # 25% expense ratio assumption
    ANNUAL_PRINCIPAL_PAYDOWN_RATE: float = 0.02  # 2% annual principal paydown
    DEFAULT_SELLING_COSTS_RATE: float = 0.03  # 3% selling costs on disposition
    
    # IRR Calculation
    INITIAL_IRR_GUESS: float = 0.10  # 10% initial guess for Newton-Raphson
    IRR_MAX_ITERATIONS: int = 1000
    IRR_PRECISION: float = 1e-6
    IRR_MIN_BOUND: float = -0.99
    IRR_MAX_BOUND: float = 10.0
    
    # Default Rates
    DEFAULT_PREFERRED_RETURN_RATE: float = 0.06  # 6% preferred return
    DEFAULT_DISCOUNT_RATE: float = 0.10  # 10% discount rate for NPV


@dataclass(frozen=True)
class RiskAssessmentThresholds:
    """Thresholds for risk level assessment."""
    
    # IRR Risk Thresholds
    LOW_IRR_THRESHOLD: float = 0.08  # Below 8% IRR increases risk
    HIGH_IRR_THRESHOLD: float = 0.20  # Above 20% IRR may indicate high risk
    
    # Equity Multiple Risk Thresholds
    LOW_EQUITY_MULTIPLE_THRESHOLD: float = 1.2  # Below 1.2x is concerning
    MODERATE_EQUITY_MULTIPLE_THRESHOLD: float = 1.5  # Below 1.5x is moderate risk
    STRONG_EQUITY_MULTIPLE_THRESHOLD: float = 2.0  # Above 2.0x is strong
    
    # Debt Coverage Thresholds
    TIGHT_DSCR_THRESHOLD: float = 1.2  # Below 1.2x is tight coverage
    MODERATE_DSCR_THRESHOLD: float = 1.5  # Below 1.5x is moderate risk
    STRONG_DSCR_THRESHOLD: float = 2.0  # Above 2.0x is strong coverage
    
    # LTV Risk Thresholds
    MODERATE_LTV_THRESHOLD: float = 0.75  # Above 75% LTV increases risk
    HIGH_LTV_THRESHOLD: float = 0.85  # Above 85% LTV is high risk
    
    # Risk Scoring Weights
    HIGH_RISK_SCORE_WEIGHT: int = 2
    MODERATE_RISK_SCORE_WEIGHT: int = 1
    
    # Risk Level Boundaries
    VERY_HIGH_RISK_SCORE: int = 6
    HIGH_RISK_SCORE: int = 4
    MODERATE_RISK_SCORE: int = 2


@dataclass(frozen=True)
class InvestmentRecommendationThresholds:
    """Thresholds for investment recommendation scoring."""
    
    # NPV Thresholds
    STRONG_POSITIVE_NPV_THRESHOLD: float = 500000.0  # $500k+ is strong positive
    POSITIVE_NPV_THRESHOLD: float = 100000.0  # $100k+ is positive
    NEGATIVE_NPV_THRESHOLD: float = -100000.0  # -$100k is concerning
    
    # IRR Thresholds for Recommendations
    EXCELLENT_IRR_THRESHOLD: float = 0.18  # 18%+ is excellent
    GOOD_IRR_THRESHOLD: float = 0.12  # 12%+ is good
    LOW_IRR_THRESHOLD: float = 0.08  # Below 8% is low
    
    # Payback Period Thresholds
    QUICK_PAYBACK_THRESHOLD: float = 3.0  # Under 3 years is quick
    LONG_PAYBACK_THRESHOLD: float = 6.0  # Over 6 years is long
    
    # Recommendation Score Boundaries
    STRONG_BUY_SCORE: int = 5
    BUY_SCORE: int = 2
    HOLD_SCORE: int = -1
    SELL_SCORE: int = -3
    
    # Scoring Weights
    NPV_SCORE_WEIGHT: int = 2
    IRR_SCORE_WEIGHT: int = 2
    EQUITY_MULTIPLE_SCORE_WEIGHT: int = 2
    PAYBACK_SCORE_WEIGHT: int = 1
    RISK_SCORE_WEIGHT: int = 1


@dataclass(frozen=True)
class ValidationConstants:
    """Constants for validation and business rules."""
    
    # Monte Carlo Parameters
    EXPECTED_PARAMETER_COUNT: int = 11  # All pro forma parameters
    PARAMETER_COMPLETENESS_THRESHOLD: float = 0.9  # 90% parameter completeness
    
    # Time Periods
    MAX_INVESTMENT_HORIZON_YEARS: int = 15
    MIN_INVESTMENT_HORIZON_YEARS: int = 1
    STANDARD_PROJECTION_YEARS: int = 5  # Years 1-5 for cash flow projections
    
    # Rate Bounds
    MIN_DISCOUNT_RATE: float = 0.03  # 3%
    MAX_DISCOUNT_RATE: float = 0.25  # 25%
    MIN_CAP_RATE: float = 0.02  # 2%
    MAX_CAP_RATE: float = 0.15  # 15%
    
    # Calculation Tolerances
    FLOATING_POINT_TOLERANCE: float = 0.01  # For waterfall distribution validation
    PERCENTAGE_TOLERANCE: float = 1e-6  # For percentage calculations


# Global constants instance
FINANCIAL_CONSTANTS = FinancialCalculationConstants()
RISK_THRESHOLDS = RiskAssessmentThresholds()
INVESTMENT_THRESHOLDS = InvestmentRecommendationThresholds()
VALIDATION_CONSTANTS = ValidationConstants()


def get_all_constants() -> Dict[str, Any]:
    """Get all constants as a dictionary for configuration management."""
    return {
        'financial': FINANCIAL_CONSTANTS.__dict__,
        'risk': RISK_THRESHOLDS.__dict__,
        'investment': INVESTMENT_THRESHOLDS.__dict__,
        'validation': VALIDATION_CONSTANTS.__dict__
    }


def validate_constants() -> bool:
    """Validate that all constants are within reasonable ranges."""
    try:
        # Validate financial constants
        assert 0 < FINANCIAL_CONSTANTS.RENOVATION_COST_PER_UNIT < 100000
        assert 1.0 < FINANCIAL_CONSTANTS.POST_RENOVATION_RENT_MULTIPLIER < 2.0
        assert 0.1 < FINANCIAL_CONSTANTS.DEFAULT_EXPENSE_RATIO < 0.6
        assert 0.01 < FINANCIAL_CONSTANTS.ANNUAL_PRINCIPAL_PAYDOWN_RATE < 0.1
        
        # Validate risk thresholds
        assert RISK_THRESHOLDS.LOW_IRR_THRESHOLD < RISK_THRESHOLDS.HIGH_IRR_THRESHOLD
        assert RISK_THRESHOLDS.LOW_EQUITY_MULTIPLE_THRESHOLD < RISK_THRESHOLDS.STRONG_EQUITY_MULTIPLE_THRESHOLD
        assert RISK_THRESHOLDS.TIGHT_DSCR_THRESHOLD < RISK_THRESHOLDS.STRONG_DSCR_THRESHOLD
        
        # Validate investment thresholds
        assert INVESTMENT_THRESHOLDS.NEGATIVE_NPV_THRESHOLD < INVESTMENT_THRESHOLDS.POSITIVE_NPV_THRESHOLD
        assert INVESTMENT_THRESHOLDS.LOW_IRR_THRESHOLD < INVESTMENT_THRESHOLDS.EXCELLENT_IRR_THRESHOLD
        
        return True
        
    except AssertionError:
        return False


if __name__ == "__main__":
    # Validate constants on module load
    if validate_constants():
        print("[SUCCESS] All DCF constants validated successfully")
    else:
        print("[ERROR] DCF constants validation failed")
        
    # Display configuration summary
    print("\nDCF Engine Configuration Summary:")
    print(f"Renovation Cost per Unit: ${FINANCIAL_CONSTANTS.RENOVATION_COST_PER_UNIT:,.0f}")
    print(f"Post-Renovation Rent Increase: {(FINANCIAL_CONSTANTS.POST_RENOVATION_RENT_MULTIPLIER - 1) * 100:.1f}%")
    print(f"Default Expense Ratio: {FINANCIAL_CONSTANTS.DEFAULT_EXPENSE_RATIO:.1%}")
    print(f"Annual Principal Paydown: {FINANCIAL_CONSTANTS.ANNUAL_PRINCIPAL_PAYDOWN_RATE:.1%}")
    print(f"Low IRR Threshold: {RISK_THRESHOLDS.LOW_IRR_THRESHOLD:.1%}")
    print(f"Strong Buy NPV Threshold: ${INVESTMENT_THRESHOLDS.STRONG_POSITIVE_NPV_THRESHOLD:,.0f}")