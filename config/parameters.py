"""
Investment Parameter Configuration

Defines the investment parameters that will be forecasted using ARIMA models
and their data source mappings.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ParameterType(Enum):
    """Types of investment parameters."""
    INTEREST_RATE = "interest_rate"
    RENT_GROWTH = "rent_growth" 
    EXPENSE_GROWTH = "expense_growth"
    VACANCY_RATE = "vacancy_rate"
    CAP_RATE = "cap_rate"
    PROPERTY_GROWTH = "property_growth"

class DataFrequency(Enum):
    """Data update frequencies."""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"

@dataclass
class ParameterDefinition:
    """Definition of an investment parameter."""
    name: str
    parameter_type: ParameterType
    description: str
    unit: str  # e.g., "percentage", "basis_points", "decimal"
    typical_range: Tuple[float, float]  # (min, max) for validation
    data_sources: List[str]
    update_frequency: DataFrequency
    geographic_level: str  # "national", "msa", "county"
    fred_series: Optional[str] = None  # FRED API series code if applicable
    
    def validate_value(self, value: float) -> bool:
        """Validate if a value is within typical range."""
        return self.typical_range[0] <= value <= self.typical_range[1]

class ParameterManager:
    """Manages investment parameter definitions and configurations."""
    
    def __init__(self) -> None:
        self.parameters: Dict[str, ParameterDefinition] = {}
        self._load_default_parameters()
    
    def _load_default_parameters(self) -> None:
        """Load default investment parameter definitions."""
        
        # Interest Rate Parameters
        self.parameters["treasury_10y"] = ParameterDefinition(
            name="10-Year Treasury Rate",
            parameter_type=ParameterType.INTEREST_RATE,
            description="10-Year Treasury Constant Maturity Rate",
            unit="percentage",
            typical_range=(1.0, 8.0),
            data_sources=["FRED"],
            update_frequency=DataFrequency.MONTHLY,
            geographic_level="national",
            fred_series="GS10"
        )
        
        self.parameters["commercial_mortgage_rate"] = ParameterDefinition(
            name="Commercial Mortgage Rate",
            parameter_type=ParameterType.INTEREST_RATE,
            description="Commercial real estate mortgage rates",
            unit="percentage", 
            typical_range=(3.0, 12.0),
            data_sources=["FRED", "Commercial Lenders"],
            update_frequency=DataFrequency.MONTHLY,
            geographic_level="national",
            fred_series="MORTG"  # Placeholder - may need composite rate
        )
        
        # Rent Growth Parameters
        self.parameters["rent_growth"] = ParameterDefinition(
            name="MSA Rent Growth Rate",
            parameter_type=ParameterType.RENT_GROWTH,
            description="Annual rental rate growth by MSA",
            unit="percentage",
            typical_range=(-5.0, 15.0),
            data_sources=["Census ACS", "Apartment List", "RentData"],
            update_frequency=DataFrequency.ANNUALLY,
            geographic_level="msa"
        )
        
        # Expense Growth Parameters  
        self.parameters["cpi_housing"] = ParameterDefinition(
            name="CPI Housing",
            parameter_type=ParameterType.EXPENSE_GROWTH,
            description="Consumer Price Index for Housing by MSA",
            unit="percentage",
            typical_range=(0.0, 10.0),
            data_sources=["BLS"],
            update_frequency=DataFrequency.MONTHLY,
            geographic_level="msa",
            fred_series="CUUR0000SAH1"  # National, need MSA-specific
        )
        
        self.parameters["property_tax_growth"] = ParameterDefinition(
            name="Property Tax Growth",
            parameter_type=ParameterType.EXPENSE_GROWTH,
            description="Annual property tax assessment growth",
            unit="percentage",
            typical_range=(1.0, 8.0),
            data_sources=["County Assessors", "Census"],
            update_frequency=DataFrequency.ANNUALLY,
            geographic_level="county"
        )
        
        # Vacancy Rate Parameters
        self.parameters["vacancy_rate"] = ParameterDefinition(
            name="Rental Vacancy Rate",
            parameter_type=ParameterType.VACANCY_RATE,
            description="Rental housing vacancy rate by MSA",
            unit="percentage",
            typical_range=(2.0, 20.0),
            data_sources=["Census Housing Vacancy Survey"],
            update_frequency=DataFrequency.QUARTERLY,
            geographic_level="msa"
        )
        
        # Cap Rate Parameters
        self.parameters["cap_rate"] = ParameterDefinition(
            name="Multifamily Cap Rate",
            parameter_type=ParameterType.CAP_RATE,
            description="Multifamily investment cap rates by MSA",
            unit="percentage",
            typical_range=(3.0, 12.0),
            data_sources=["RCA", "CoStar", "CBRE Research"],
            update_frequency=DataFrequency.QUARTERLY,
            geographic_level="msa"
        )
        
        # Property Value Growth
        self.parameters["property_growth"] = ParameterDefinition(
            name="Property Value Growth",
            parameter_type=ParameterType.PROPERTY_GROWTH,
            description="Annual property value growth by MSA",
            unit="percentage",
            typical_range=(-10.0, 20.0),
            data_sources=["FHFA", "Local Assessors"],
            update_frequency=DataFrequency.ANNUALLY,
            geographic_level="msa"
        )
        
        # Expense Growth (operating expenses)
        self.parameters["expense_growth"] = ParameterDefinition(
            name="Operating Expense Growth",
            parameter_type=ParameterType.EXPENSE_GROWTH,
            description="Annual operating expense growth rate",
            unit="percentage",
            typical_range=(1.0, 8.0),
            data_sources=["CPI", "Property Management Data"],
            update_frequency=DataFrequency.ANNUALLY,
            geographic_level="msa"
        )
        
        # Federal funds rate
        self.parameters["fed_funds_rate"] = ParameterDefinition(
            name="Federal Funds Rate",
            parameter_type=ParameterType.INTEREST_RATE,
            description="Federal funds effective rate",
            unit="percentage",
            typical_range=(0.0, 8.0),
            data_sources=["FRED"],
            update_frequency=DataFrequency.MONTHLY,
            geographic_level="national",
            fred_series="FEDFUNDS"
        )
        
        # Additional Pro Forma Parameters (typically fixed inputs, not forecasted)
        self.parameters["ltv_ratio"] = ParameterDefinition(
            name="Loan-to-Value Ratio",
            parameter_type=ParameterType.INTEREST_RATE,  # Financing related
            description="Maximum loan-to-value ratio for financing",
            unit="decimal",
            typical_range=(0.5, 0.9),
            data_sources=["Lender Guidelines", "Market Standards"],
            update_frequency=DataFrequency.QUARTERLY,
            geographic_level="msa"
        )
        
        self.parameters["closing_cost_pct"] = ParameterDefinition(
            name="Closing Cost Percentage",
            parameter_type=ParameterType.EXPENSE_GROWTH,
            description="Closing costs as percentage of purchase price",
            unit="decimal",
            typical_range=(0.02, 0.08),
            data_sources=["Market Standards", "Title Companies"],
            update_frequency=DataFrequency.ANNUALLY,
            geographic_level="msa"
        )
        
        self.parameters["lender_reserves"] = ParameterDefinition(
            name="Lender Reserve Requirements",
            parameter_type=ParameterType.EXPENSE_GROWTH,
            description="Lender required reserves as percentage of loan amount",
            unit="decimal",
            typical_range=(0.02, 0.1),
            data_sources=["Lender Requirements"],
            update_frequency=DataFrequency.ANNUALLY,
            geographic_level="msa"
        )
    
    def get_parameter(self, name: str) -> Optional[ParameterDefinition]:
        """Get parameter definition by name."""
        return self.parameters.get(name)
    
    def get_parameters_by_type(self, param_type: ParameterType) -> List[ParameterDefinition]:
        """Get all parameters of a specific type."""
        return [param for param in self.parameters.values() 
                if param.parameter_type == param_type]
    
    def get_fred_parameters(self) -> List[ParameterDefinition]:
        """Get all parameters that have FRED series codes."""
        return [param for param in self.parameters.values() 
                if param.fred_series is not None]
    
    def list_parameters(self) -> List[str]:
        """List all parameter names."""
        return list(self.parameters.keys())
    
    def add_parameter(self, name: str, definition: ParameterDefinition) -> None:
        """Add a new parameter definition."""
        self.parameters[name] = definition

# Global instance
parameters = ParameterManager()

# Parameter mapping for pro forma Excel sections
PRO_FORMA_PARAMETER_MAPPING = {
    # From Excel Assumptions Section (matches our 11 Prophet metrics)
    "treasury_10y": "treasury_10y",
    "commercial_mortgage_rate": "commercial_mortgage_rate",
    "fed_funds_rate": "fed_funds_rate",
    "cap_rate": "cap_rate",
    "vacancy_rate": "vacancy_rate", 
    "rent_growth": "rent_growth",
    "expense_growth": "expense_growth",
    "ltv_ratio": "ltv_ratio",
    "closing_cost_pct": "closing_cost_pct",
    "lender_reserves": "lender_reserves",
    "property_growth": "property_growth"
}

def get_pro_forma_parameters() -> Dict[str, ParameterDefinition]:
    """Get parameter definitions mapped to pro forma assumptions."""
    result = {}
    for excel_name, param_name in PRO_FORMA_PARAMETER_MAPPING.items():
        param = parameters.get_parameter(param_name)
        if param is not None:
            result[excel_name] = param
    return result