"""
Property-Specific Input Data Structure

Defines data structures for property-specific inputs that will be used
in conjunction with forecasted market parameters for investment analysis.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import date
from enum import Enum

from core.exceptions import ValidationError, PropertyDataError
from core.logging_config import get_logger


class PropertyType(Enum):
    """Property type classifications."""
    MULTIFAMILY = "multifamily"
    OFFICE = "office"
    RETAIL = "retail"
    INDUSTRIAL = "industrial"
    MIXED_USE = "mixed_use"


class PropertyClass(Enum):
    """Property class ratings."""
    CLASS_A = "class_a"
    CLASS_B = "class_b"
    CLASS_C = "class_c"


@dataclass
class PropertyPhysicalInfo:
    """Physical characteristics of the property."""
    property_type: PropertyType
    property_class: PropertyClass
    total_units: int
    total_square_feet: int
    year_built: int
    year_renovated: Optional[int] = None
    parking_spaces: Optional[int] = None
    stories: Optional[int] = None
    lot_size_sf: Optional[int] = None
    
    def __post_init__(self):
        if self.total_units <= 0:
            raise ValidationError("Total units must be positive")
        if self.total_square_feet <= 0:
            raise ValidationError("Total square feet must be positive")
        if self.year_built < 1800 or self.year_built > date.today().year:
            raise ValidationError("Invalid year built")


@dataclass
class PropertyFinancialInfo:
    """Financial characteristics of the property."""
    purchase_price: float
    down_payment_pct: float
    loan_amount: Optional[float] = None
    annual_debt_service: Optional[float] = None
    current_noi: Optional[float] = None  # Net Operating Income
    current_gross_rent: Optional[float] = None
    current_expenses: Optional[float] = None
    
    def __post_init__(self):
        if self.purchase_price <= 0:
            raise ValidationError("Purchase price must be positive")
        if not 0 < self.down_payment_pct <= 1:
            raise ValidationError("Down payment percentage must be between 0 and 1")
        
        # Calculate loan amount if not provided
        if self.loan_amount is None:
            self.loan_amount = self.purchase_price * (1 - self.down_payment_pct)


@dataclass 
class PropertyLocationInfo:
    """Location and market information."""
    address: str
    city: str
    state: str
    zip_code: str
    msa_code: str  # Metropolitan Statistical Area code
    county_fips: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    submarket: Optional[str] = None
    
    def __post_init__(self):
        if not all([self.address, self.city, self.state, self.zip_code, self.msa_code]):
            raise ValidationError("Address, city, state, zip code, and MSA code are required")


@dataclass
class UnitMix:
    """Unit mix information for multifamily properties."""
    unit_type: str  # e.g., "1BR/1BA", "2BR/2BA"
    count: int
    avg_square_feet: int
    current_rent: float
    
    def __post_init__(self):
        if self.count <= 0:
            raise ValidationError("Unit count must be positive")
        if self.avg_square_feet <= 0:
            raise ValidationError("Average square feet must be positive")
        if self.current_rent <= 0:
            raise ValidationError("Current rent must be positive")


@dataclass
class PropertyOperatingInfo:
    """Operating information and assumptions."""
    management_fee_pct: float = 0.05  # 5% default
    maintenance_reserve_pct: float = 0.02  # 2% default
    insurance_annual: Optional[float] = None
    property_tax_annual: Optional[float] = None
    utilities_annual: Optional[float] = None
    other_expenses_annual: Optional[float] = None
    unit_mix: List[UnitMix] = field(default_factory=list)
    
    def __post_init__(self):
        if not 0 <= self.management_fee_pct <= 0.2:
            raise ValidationError("Management fee must be between 0% and 20%")
        if not 0 <= self.maintenance_reserve_pct <= 0.1:
            raise ValidationError("Maintenance reserve must be between 0% and 10%")


@dataclass
class PropertyInputData:
    """Complete property-specific input data for DCF analysis."""
    property_id: str
    property_name: str
    analysis_date: date
    physical_info: PropertyPhysicalInfo
    financial_info: PropertyFinancialInfo
    location_info: PropertyLocationInfo
    operating_info: PropertyOperatingInfo
    custom_assumptions: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.property_id:
            raise ValidationError("Property ID is required")
        if not self.property_name:
            raise ValidationError("Property name is required")
        
        # Validate unit mix total matches property units
        if (self.operating_info.unit_mix and 
            self.physical_info.property_type == PropertyType.MULTIFAMILY):
            total_units_in_mix = sum(unit.count for unit in self.operating_info.unit_mix)
            if total_units_in_mix != self.physical_info.total_units:
                raise ValidationError(
                    f"Unit mix total ({total_units_in_mix}) doesn't match "
                    f"property total units ({self.physical_info.total_units})"
                )
    
    def get_msa_code(self) -> str:
        """Get the MSA code for market parameter lookup."""
        return self.location_info.msa_code
    
    def calculate_price_per_unit(self) -> float:
        """Calculate price per unit."""
        return self.financial_info.purchase_price / self.physical_info.total_units
    
    def calculate_price_per_sf(self) -> float:
        """Calculate price per square foot."""
        return self.financial_info.purchase_price / self.physical_info.total_square_feet
    
    def get_current_cap_rate(self) -> Optional[float]:
        """Calculate current cap rate if NOI is available."""
        if self.financial_info.current_noi:
            return self.financial_info.current_noi / self.financial_info.purchase_price
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "property_id": self.property_id,
            "property_name": self.property_name,
            "analysis_date": self.analysis_date.isoformat(),
            "physical_info": {
                "property_type": self.physical_info.property_type.value,
                "property_class": self.physical_info.property_class.value,
                "total_units": self.physical_info.total_units,
                "total_square_feet": self.physical_info.total_square_feet,
                "year_built": self.physical_info.year_built
            },
            "financial_info": {
                "purchase_price": self.financial_info.purchase_price,
                "down_payment_pct": self.financial_info.down_payment_pct,
                "loan_amount": self.financial_info.loan_amount,
                "current_noi": self.financial_info.current_noi
            },
            "location_info": {
                "city": self.location_info.city,
                "state": self.location_info.state,
                "msa_code": self.location_info.msa_code
            },
            "operating_info": {
                "management_fee_pct": self.operating_info.management_fee_pct,
                "maintenance_reserve_pct": self.operating_info.maintenance_reserve_pct
            },
            "custom_assumptions": self.custom_assumptions
        }


class PropertyDataManager:
    """Manages property-specific input data."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.properties: Dict[str, PropertyInputData] = {}
    
    def add_property(self, property_data: PropertyInputData) -> None:
        """Add property data to the manager."""
        try:
            self.properties[property_data.property_id] = property_data
            self.logger.info(f"Added property: {property_data.property_name} ({property_data.property_id})")
        except Exception as e:
            raise PropertyDataError(f"Failed to add property: {e}") from e
    
    def get_property(self, property_id: str) -> Optional[PropertyInputData]:
        """Get property data by ID."""
        return self.properties.get(property_id)
    
    def list_properties(self) -> List[str]:
        """List all property IDs."""
        return list(self.properties.keys())
    
    def validate_property(self, property_data: PropertyInputData) -> List[str]:
        """Validate property data and return list of issues."""
        issues = []
        
        try:
            # Basic validation happens in __post_init__ methods
            pass
        except ValidationError as e:
            issues.append(str(e))
        
        # Additional business logic validation
        if property_data.physical_info.property_type == PropertyType.MULTIFAMILY:
            if property_data.physical_info.total_units < 5:
                issues.append("Multifamily properties should have at least 5 units")
        
        if property_data.financial_info.purchase_price > 100_000_000:  # $100M
            issues.append("Purchase price exceeds $100M - please verify")
        
        return issues


# Global property data manager instance
property_manager = PropertyDataManager()


def create_sample_property() -> PropertyInputData:
    """Create a sample property for testing."""
    return PropertyInputData(
        property_id="SAMPLE_001",
        property_name="Sample Multifamily Property",
        analysis_date=date.today(),
        physical_info=PropertyPhysicalInfo(
            property_type=PropertyType.MULTIFAMILY,
            property_class=PropertyClass.CLASS_B,
            total_units=50,
            total_square_feet=45000,
            year_built=2010,
            parking_spaces=60
        ),
        financial_info=PropertyFinancialInfo(
            purchase_price=5_000_000,
            down_payment_pct=0.25,
            current_noi=350_000,
            current_gross_rent=500_000
        ),
        location_info=PropertyLocationInfo(
            address="123 Main Street",
            city="New York",
            state="NY", 
            zip_code="10001",
            msa_code="35620"  # NYC MSA
        ),
        operating_info=PropertyOperatingInfo(
            management_fee_pct=0.05,
            maintenance_reserve_pct=0.025,
            unit_mix=[
                UnitMix("1BR/1BA", 20, 800, 2200),
                UnitMix("2BR/2BA", 25, 1100, 2800),
                UnitMix("3BR/2BA", 5, 1300, 3200)
            ]
        )
    )