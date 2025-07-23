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
    
    def __init__(self):
        self.parameters: Dict[str, ParameterDefinition] = {}
        self._load_default_parameters()
    
    def _load_default_parameters(self):
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
        self.parameters["rent_growth_msa"] = ParameterDefinition(
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
        self.parameters["rental_vacancy_rate"] = ParameterDefinition(
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
        self.parameters["multifamily_cap_rate"] = ParameterDefinition(
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
        self.parameters["house_price_index"] = ParameterDefinition(
            name="House Price Index",
            parameter_type=ParameterType.PROPERTY_GROWTH,
            description="FHFA House Price Index growth by MSA",
            unit="percentage",
            typical_range=(-10.0, 20.0),
            data_sources=["FHFA"],
            update_frequency=DataFrequency.QUARTERLY,
            geographic_level="msa",
            fred_series="HPIPONM226S"  # National, need MSA-specific
        )
        
        # Additional Pro Forma Parameters (typically fixed inputs, not forecasted)
        self.parameters["ltv"] = ParameterDefinition(
            name="Loan-to-Value Ratio",
            parameter_type=ParameterType.INTEREST_RATE,  # Financing related
            description="Maximum loan-to-value ratio for financing",
            unit="decimal",
            typical_range=(0.5, 0.9),
            data_sources=["Lender Guidelines", "Market Standards"],
            update_frequency=DataFrequency.QUARTERLY,
            geographic_level="national"
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
        
        self.parameters["lender_reserve_pct"] = ParameterDefinition(
            name="Lender Reserve Percentage",
            parameter_type=ParameterType.EXPENSE_GROWTH,
            description="Lender required reserves as percentage of loan amount",
            unit="decimal",
            typical_range=(0.1, 0.5),
            data_sources=["Lender Requirements"],
            update_frequency=DataFrequency.ANNUALLY,
            geographic_level="national"
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
    # From Excel Assumptions Section
    "interest_rate": "treasury_10y",  # Base rate + spread
    "rent_growth": "rent_growth_msa", 
    "expense_growth": "cpi_housing",
    "vacancy_rate": "rental_vacancy_rate",
    "cap_rate": "multifamily_cap_rate",
    "property_growth": "house_price_index",
    "ltv": "ltv",
    "closing_cost_pct": "closing_cost_pct",
    "lender_reserve_pct": "lender_reserve_pct"
}

def get_pro_forma_parameters() -> Dict[str, ParameterDefinition]:
    """Get parameter definitions mapped to pro forma assumptions."""
    return {
        excel_name: parameters.get_parameter(param_name)
        for excel_name, param_name in PRO_FORMA_PARAMETER_MAPPING.items()
        if parameters.get_parameter(param_name) is not None
    }