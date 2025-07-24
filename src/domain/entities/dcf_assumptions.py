"""
DCF Assumptions Domain Entity

Represents market assumptions extracted from Monte Carlo scenarios for DCF calculations.
Maps Monte Carlo forecasted parameters to Excel pro forma assumptions.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import date

from core.exceptions import ValidationError


@dataclass
class DCFAssumptions:
    """
    Market assumptions extracted from Monte Carlo scenarios.
    Maps Monte Carlo forecasted parameters to Excel pro forma assumptions.
    """
    scenario_id: str
    msa_code: str
    property_id: str
    created_date: date = field(default_factory=date.today)
    
    # Interest and Financing Parameters (6-year forecasts: Years 0-5)
    commercial_mortgage_rate: List[float] = field(default_factory=list)
    treasury_10y_rate: List[float] = field(default_factory=list)
    fed_funds_rate: List[float] = field(default_factory=list)
    
    # Property Market Parameters (6-year forecasts: Years 0-5)
    cap_rate: List[float] = field(default_factory=list)
    rent_growth_rate: List[float] = field(default_factory=list)
    expense_growth_rate: List[float] = field(default_factory=list)
    property_growth_rate: List[float] = field(default_factory=list)
    vacancy_rate: List[float] = field(default_factory=list)
    
    # Financing and Transaction Parameters (static values)
    ltv_ratio: float = 0.0
    closing_cost_pct: float = 0.0
    lender_reserves_months: float = 0.0
    
    # Investment Structure (from property inputs)
    investor_equity_share: float = 0.0
    preferred_return_rate: float = 0.06  # Default 6%
    self_cash_percentage: float = 0.0
    
    def __post_init__(self):
        """Validate DCF assumptions after initialization."""
        self._validate_identifiers()
        self._validate_forecast_parameters()
        self._validate_static_parameters()
        self._validate_investment_structure()
    
    def _validate_identifiers(self):
        """Validate required identifiers."""
        if not self.scenario_id:
            raise ValidationError("Scenario ID is required")
        if not self.msa_code:
            raise ValidationError("MSA code is required")
        if not self.property_id:
            raise ValidationError("Property ID is required")
    
    def _validate_forecast_parameters(self):
        """Validate forecasted parameter arrays."""
        forecast_params = [
            ('commercial_mortgage_rate', self.commercial_mortgage_rate),
            ('treasury_10y_rate', self.treasury_10y_rate),
            ('fed_funds_rate', self.fed_funds_rate),
            ('cap_rate', self.cap_rate),
            ('rent_growth_rate', self.rent_growth_rate),
            ('expense_growth_rate', self.expense_growth_rate),
            ('property_growth_rate', self.property_growth_rate),
            ('vacancy_rate', self.vacancy_rate)
        ]
        
        for param_name, param_values in forecast_params:
            if not param_values:
                raise ValidationError(f"{param_name} cannot be empty")
            if len(param_values) != 6:
                raise ValidationError(f"{param_name} must have 6 years of data (Years 0-5)")
            
            # Validate reasonable ranges
            self._validate_parameter_ranges(param_name, param_values)
    
    def _validate_parameter_ranges(self, param_name: str, values: List[float]):
        """Validate parameter values are within reasonable ranges."""
        range_checks = {
            'commercial_mortgage_rate': (0.01, 0.20),  # 1% to 20%
            'treasury_10y_rate': (0.005, 0.15),       # 0.5% to 15%
            'fed_funds_rate': (0.0, 0.12),            # 0% to 12%
            'cap_rate': (0.03, 0.15),                 # 3% to 15%
            'rent_growth_rate': (-0.10, 0.20),        # -10% to 20%
            'expense_growth_rate': (-0.05, 0.15),     # -5% to 15%
            'property_growth_rate': (-0.20, 0.30),    # -20% to 30%
            'vacancy_rate': (0.0, 0.50)               # 0% to 50%
        }
        
        if param_name in range_checks:
            min_val, max_val = range_checks[param_name]
            for i, value in enumerate(values):
                if not (min_val <= value <= max_val):
                    raise ValidationError(
                        f"{param_name}[{i}] = {value:.4f} is outside reasonable range "
                        f"[{min_val:.4f}, {max_val:.4f}]"
                    )
    
    def _validate_static_parameters(self):
        """Validate static parameters."""
        if not (0.5 <= self.ltv_ratio <= 0.95):
            raise ValidationError("LTV ratio must be between 50% and 95%")
        if not (0.01 <= self.closing_cost_pct <= 0.15):
            raise ValidationError("Closing cost percentage must be between 1% and 15%")
        if not (1.0 <= self.lender_reserves_months <= 12.0):
            raise ValidationError("Lender reserves must be between 1 and 12 months")
    
    def _validate_investment_structure(self):
        """Validate investment structure parameters."""
        if not (0.0 <= self.investor_equity_share <= 1.0):
            raise ValidationError("Investor equity share must be between 0% and 100%")
        if not (0.0 <= self.preferred_return_rate <= 0.20):
            raise ValidationError("Preferred return rate must be between 0% and 20%")
        if not (0.0 <= self.self_cash_percentage <= 1.0):
            raise ValidationError("Self cash percentage must be between 0% and 100%")
    
    def get_year_assumptions(self, year: int) -> Dict[str, float]:
        """Get all assumptions for a specific year (0-5)."""
        if not (0 <= year <= 5):
            raise ValidationError("Year must be between 0 and 5")
        
        return {
            'commercial_mortgage_rate': self.commercial_mortgage_rate[year],
            'treasury_10y_rate': self.treasury_10y_rate[year],
            'fed_funds_rate': self.fed_funds_rate[year],
            'cap_rate': self.cap_rate[year],
            'rent_growth_rate': self.rent_growth_rate[year],
            'expense_growth_rate': self.expense_growth_rate[year],
            'property_growth_rate': self.property_growth_rate[year],
            'vacancy_rate': self.vacancy_rate[year]
        }
    
    def get_terminal_assumptions(self) -> Dict[str, float]:
        """Get Year 5 (terminal) assumptions for exit calculations."""
        return self.get_year_assumptions(5)
    
    def calculate_loan_amount(self, purchase_price: float) -> float:
        """Calculate loan amount based on purchase price and LTV."""
        return purchase_price * self.ltv_ratio
    
    def calculate_closing_costs(self, purchase_price: float) -> float:
        """Calculate closing costs based on purchase price."""
        return purchase_price * self.closing_cost_pct
    
    def calculate_lender_reserves(self, annual_debt_service: float) -> float:
        """Calculate required lender reserves."""
        return annual_debt_service * (self.lender_reserves_months / 12)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'scenario_id': self.scenario_id,
            'msa_code': self.msa_code,
            'property_id': self.property_id,
            'created_date': self.created_date.isoformat(),
            
            # Forecast parameters
            'commercial_mortgage_rate': self.commercial_mortgage_rate,
            'treasury_10y_rate': self.treasury_10y_rate,
            'fed_funds_rate': self.fed_funds_rate,
            'cap_rate': self.cap_rate,
            'rent_growth_rate': self.rent_growth_rate,
            'expense_growth_rate': self.expense_growth_rate,
            'property_growth_rate': self.property_growth_rate,
            'vacancy_rate': self.vacancy_rate,
            
            # Static parameters
            'ltv_ratio': self.ltv_ratio,
            'closing_cost_pct': self.closing_cost_pct,
            'lender_reserves_months': self.lender_reserves_months,
            
            # Investment structure
            'investor_equity_share': self.investor_equity_share,
            'preferred_return_rate': self.preferred_return_rate,
            'self_cash_percentage': self.self_cash_percentage
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DCFAssumptions':
        """Create from dictionary (deserialization)."""
        # Parse date
        created_date = date.fromisoformat(data['created_date']) if 'created_date' in data else date.today()
        
        return cls(
            scenario_id=data['scenario_id'],
            msa_code=data['msa_code'],
            property_id=data['property_id'],
            created_date=created_date,
            
            # Forecast parameters
            commercial_mortgage_rate=data['commercial_mortgage_rate'],
            treasury_10y_rate=data['treasury_10y_rate'],
            fed_funds_rate=data['fed_funds_rate'],
            cap_rate=data['cap_rate'],
            rent_growth_rate=data['rent_growth_rate'],
            expense_growth_rate=data['expense_growth_rate'],
            property_growth_rate=data['property_growth_rate'],
            vacancy_rate=data['vacancy_rate'],
            
            # Static parameters
            ltv_ratio=data['ltv_ratio'],
            closing_cost_pct=data['closing_cost_pct'],
            lender_reserves_months=data['lender_reserves_months'],
            
            # Investment structure
            investor_equity_share=data['investor_equity_share'],
            preferred_return_rate=data['preferred_return_rate'],
            self_cash_percentage=data['self_cash_percentage']
        )
    
    def __str__(self) -> str:
        """String representation for debugging."""
        return (f"DCFAssumptions(scenario={self.scenario_id}, "
                f"property={self.property_id}, msa={self.msa_code}, "
                f"ltv={self.ltv_ratio:.1%}, equity_share={self.investor_equity_share:.1%})")


# Monte Carlo Parameter Mapping Constants
MONTE_CARLO_PARAMETER_MAPPING = {
    # Excel Assumption ← Monte Carlo Parameter
    'commercial_mortgage_rate': 'commercial_mortgage_rate',
    'cap_rate': 'cap_rate',
    'rent_growth_rate': 'rent_growth',
    'expense_growth_rate': 'expense_growth',
    'property_growth_rate': 'property_growth',
    'vacancy_rate': 'vacancy_rate',
    'ltv_ratio': 'ltv_ratio',
    'closing_cost_pct': 'closing_cost_pct',
    'lender_reserves': 'lender_reserves',
    
    # Reference parameters
    'treasury_10y_rate': 'treasury_10y',
    'fed_funds_rate': 'fed_funds_rate'
}


def validate_monte_carlo_parameters(forecasted_parameters: Dict[str, List[float]]) -> List[str]:
    """Validate Monte Carlo scenario has all required parameters."""
    required_params = list(MONTE_CARLO_PARAMETER_MAPPING.values())
    
    issues = []
    for param in required_params:
        if param not in forecasted_parameters:
            issues.append(f"Missing parameter: {param}")
        elif len(forecasted_parameters[param]) != 6:
            issues.append(f"Parameter {param} should have 6 years of data, got {len(forecasted_parameters[param])}")
    
    return issues