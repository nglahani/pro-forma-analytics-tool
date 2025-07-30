"""
Unified Property Data Structure

Consolidates all property input functionality into a single, comprehensive module.
Supports both legacy PropertyInputData and simplified user input requirements.
"""

import uuid
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from core.exceptions import ValidationError
from core.logging_config import get_logger

logger = get_logger(__name__)


# ============================================================================
# ENUMERATIONS
# ============================================================================


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


class RenovationStatus(Enum):
    """Renovation status classifications."""

    NOT_NEEDED = "not_needed"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


# ============================================================================
# PROPERTY COMPONENTS
# ============================================================================


@dataclass
class ResidentialUnits:
    """Residential unit information."""

    total_units: int
    average_rent_per_unit: float
    unit_types: Optional[str] = None  # JSON string for database compatibility
    average_square_feet_per_unit: Optional[float] = None  # Match database schema

    def __post_init__(self):
        if self.total_units <= 0:
            raise ValidationError("Residential units must be positive")
        if self.average_rent_per_unit <= 0:
            raise ValidationError("Residential rent must be positive")

    @property
    def monthly_gross_rent(self) -> float:
        """Calculate total monthly residential rent."""
        return self.total_units * self.average_rent_per_unit


@dataclass
class CommercialUnits:
    """Commercial unit information."""

    total_units: int
    average_rent_per_unit: float
    unit_types: Optional[str] = None  # JSON string for database compatibility
    average_square_feet_per_unit: Optional[float] = None  # Match database schema

    def __post_init__(self):
        if self.total_units <= 0:
            raise ValidationError("Commercial units must be positive")
        if self.average_rent_per_unit <= 0:
            raise ValidationError("Commercial rent must be positive")

    @property
    def monthly_gross_rent(self) -> float:
        """Calculate total monthly commercial rent."""
        return self.total_units * self.average_rent_per_unit


@dataclass
class RenovationInfo:
    """Renovation timeline and details."""

    status: RenovationStatus
    anticipated_duration_months: Optional[int] = None
    start_date: Optional[date] = None
    completion_date: Optional[date] = None
    estimated_cost: Optional[float] = None
    description: Optional[str] = None

    def __post_init__(self):
        if self.status in [RenovationStatus.PLANNED, RenovationStatus.IN_PROGRESS]:
            if not self.anticipated_duration_months:
                raise ValidationError(
                    "Anticipated duration required for planned/in-progress renovations"
                )
            if (
                self.anticipated_duration_months <= 0
                or self.anticipated_duration_months > 60
            ):
                raise ValidationError(
                    "Renovation duration must be between 1 and 60 months"
                )


@dataclass
class InvestorEquityStructure:
    """Investor equity and financing structure."""

    investor_equity_share_pct: float
    self_cash_percentage: float
    number_of_investors: int = 1  # Match database schema
    investment_structure: Optional[str] = None  # JSON string for database compatibility

    def __post_init__(self):
        if not 0 <= self.investor_equity_share_pct <= 100:
            raise ValidationError("Investor equity share must be between 0 and 100%")
        if not 0 <= self.self_cash_percentage <= 100:
            raise ValidationError("Self cash percentage must be between 0 and 100%")


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


@dataclass
class PropertyFinancialInfo:
    """Financial information about the property."""

    purchase_price: float
    down_payment_pct: float
    current_noi: float
    estimated_renovation_cost: Optional[float] = None
    closing_costs: Optional[float] = None

    def __post_init__(self):
        if self.purchase_price <= 0:
            raise ValidationError("Purchase price must be positive")
        if not 0 <= self.down_payment_pct <= 1:
            raise ValidationError("Down payment percentage must be between 0 and 1")


@dataclass
class PropertyLocationInfo:
    """Location and geographic information."""

    address: str
    city: str
    state: str
    zip_code: str
    msa_code: str
    county: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    def __post_init__(self):
        if not self.address.strip():
            raise ValidationError("Address is required")
        if not self.city.strip():
            raise ValidationError("City is required")
        if len(self.state) != 2:
            raise ValidationError("State must be 2-letter code")

    def get_msa_code(self) -> str:
        """Get MSA code for compatibility with Monte Carlo engine."""
        return self.msa_code


@dataclass
class PropertyOperatingInfo:
    """Operating assumptions and parameters."""

    vacancy_rate_pct: float = 0.05
    management_fee_pct: float = 0.08
    maintenance_reserve_per_unit: float = 500
    annual_rent_growth_pct: float = 0.03
    annual_expense_growth_pct: float = 0.025
    exit_cap_rate: Optional[float] = None

    def __post_init__(self):
        if not 0 <= self.vacancy_rate_pct <= 1:
            raise ValidationError("Vacancy rate must be between 0 and 1")


# ============================================================================
# UNIFIED PROPERTY DATA CLASSES
# ============================================================================


@dataclass
class PropertyInputData:
    """
    Legacy property input data structure.
    Maintains compatibility with existing Monte Carlo engine.
    """

    property_id: str
    property_name: str
    analysis_date: date
    physical_info: PropertyPhysicalInfo
    financial_info: PropertyFinancialInfo
    location_info: PropertyLocationInfo
    operating_info: PropertyOperatingInfo
    notes: Optional[str] = None

    def __post_init__(self):
        if not self.property_id:
            self.property_id = f"PROP_{uuid.uuid4().hex[:8].upper()}"
        if not self.property_name.strip():
            raise ValidationError("Property name is required")

    def get_msa_code(self) -> str:
        """Get MSA code for compatibility with Monte Carlo engine."""
        return self.location_info.msa_code


@dataclass
class SimplifiedPropertyInput:
    """
    Simplified property input matching user requirements.
    Captures the 7 required data fields in an intuitive structure.
    """

    property_id: str
    property_name: str
    analysis_date: date
    residential_units: ResidentialUnits
    renovation_info: RenovationInfo
    equity_structure: InvestorEquityStructure
    commercial_units: Optional[CommercialUnits] = None

    # Optional fields for enhanced analysis
    city: Optional[str] = None
    state: Optional[str] = None
    msa_code: Optional[str] = None
    purchase_price: Optional[float] = None
    property_address: Optional[str] = None
    notes: Optional[str] = None

    def __post_init__(self):
        if not self.property_id:
            self.property_id = f"USER_{uuid.uuid4().hex[:8].upper()}"
        if not self.property_name.strip():
            raise ValidationError("Property name is required")

    # ========================================================================
    # PROPERTY ANALYSIS METHODS
    # ========================================================================

    def is_mixed_use(self) -> bool:
        """Check if property has both residential and commercial units."""
        return (
            self.commercial_units is not None and self.commercial_units.total_units > 0
        )

    def get_total_units(self) -> int:
        """Get total number of units (residential + commercial)."""
        total = self.residential_units.total_units
        if self.commercial_units:
            total += self.commercial_units.total_units
        return total

    def get_monthly_gross_rent(self) -> float:
        """Calculate total monthly gross rent."""
        monthly_rent = self.residential_units.monthly_gross_rent
        if self.commercial_units:
            monthly_rent += self.commercial_units.monthly_gross_rent
        return monthly_rent

    def get_msa_code(self) -> str:
        """Get MSA code for compatibility with Monte Carlo engine."""
        if not self.msa_code:
            raise ValidationError("MSA code is required for Monte Carlo analysis")
        return self.msa_code

    def get_annual_gross_rent(self) -> float:
        """Calculate total annual gross rent."""
        return self.get_monthly_gross_rent() * 12

    def get_property_type_classification(self) -> str:
        """Classify property type based on unit composition."""
        if self.is_mixed_use():
            return "mixed_use"
        else:
            return "multifamily"

    def calculate_key_metrics(self) -> Dict[str, Any]:
        """Calculate key financial metrics."""
        metrics = {
            "total_units": self.get_total_units(),
            "monthly_gross_rent": self.get_monthly_gross_rent(),
            "annual_gross_rent": self.get_annual_gross_rent(),
            "property_type": self.get_property_type_classification(),
            "is_mixed_use": self.is_mixed_use(),
        }

        if self.purchase_price:
            metrics.update(
                {
                    "purchase_price": self.purchase_price,
                    "price_per_unit": self.purchase_price / self.get_total_units(),
                    "total_cash_required": self.purchase_price
                    * (self.equity_structure.self_cash_percentage / 100),
                    "gross_cap_rate": self.get_annual_gross_rent()
                    / self.purchase_price,
                }
            )

        return metrics

    # ========================================================================
    # SERIALIZATION METHODS
    # ========================================================================

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        data = {
            "property_id": self.property_id,
            "property_name": self.property_name,
            "analysis_date": self.analysis_date.isoformat(),
            "residential_units_count": self.residential_units.total_units,
            "residential_rent_per_unit": self.residential_units.average_rent_per_unit,
            "commercial_units_count": (
                self.commercial_units.total_units if self.commercial_units else 0
            ),
            "commercial_rent_per_unit": (
                self.commercial_units.average_rent_per_unit
                if self.commercial_units
                else 0
            ),
            "renovation_status": self.renovation_info.status.value,
            "renovation_duration_months": self.renovation_info.anticipated_duration_months,
            "investor_equity_share_pct": self.equity_structure.investor_equity_share_pct,
            "self_cash_percentage": self.equity_structure.self_cash_percentage,
            "city": self.city,
            "state": self.state,
            "msa_code": self.msa_code,
            "purchase_price": self.purchase_price,
            "property_address": self.property_address,
            "notes": self.notes,
            "calculated_metrics": self.calculate_key_metrics(),
        }
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SimplifiedPropertyInput":
        """Create instance from dictionary."""
        return cls(
            property_id=data["property_id"],
            property_name=data["property_name"],
            analysis_date=date.fromisoformat(data["analysis_date"]),
            residential_units=ResidentialUnits(
                total_units=data["residential_units_count"],
                average_rent_per_unit=data["residential_rent_per_unit"],
            ),
            commercial_units=(
                CommercialUnits(
                    total_units=data["commercial_units_count"],
                    average_rent_per_unit=data["commercial_rent_per_unit"],
                )
                if data["commercial_units_count"] > 0
                else None
            ),
            renovation_info=RenovationInfo(
                status=RenovationStatus(data["renovation_status"]),
                anticipated_duration_months=data.get("renovation_duration_months"),
            ),
            equity_structure=InvestorEquityStructure(
                investor_equity_share_pct=data["investor_equity_share_pct"],
                self_cash_percentage=data["self_cash_percentage"],
            ),
            city=data.get("city"),
            state=data.get("state"),
            msa_code=data.get("msa_code"),
            purchase_price=data.get("purchase_price"),
            property_address=data.get("property_address"),
            notes=data.get("notes"),
        )

    # ========================================================================
    # CONVERSION METHODS
    # ========================================================================

    def to_legacy_format(self) -> PropertyInputData:
        """Convert to legacy PropertyInputData format for Monte Carlo engine."""
        return PropertyInputData(
            property_id=self.property_id,
            property_name=self.property_name,
            analysis_date=self.analysis_date,
            physical_info=PropertyPhysicalInfo(
                property_type=(
                    PropertyType.MIXED_USE
                    if self.is_mixed_use()
                    else PropertyType.MULTIFAMILY
                ),
                property_class=PropertyClass.CLASS_B,  # Default
                total_units=self.get_total_units(),
                total_square_feet=self.get_total_units() * 1000,  # Estimate
                year_built=2015,  # Default
            ),
            financial_info=PropertyFinancialInfo(
                purchase_price=self.purchase_price or self.get_annual_gross_rent() * 12,
                down_payment_pct=self.equity_structure.self_cash_percentage / 100,
                current_noi=self.get_annual_gross_rent() * 0.75,  # Estimate 75% NOI
            ),
            location_info=PropertyLocationInfo(
                address=self.property_address or "123 Investment St",
                city=self.city or "New York",
                state=self.state or "NY",
                zip_code="10001",  # Default
                msa_code=self.msa_code or "35620",  # Default to NYC
            ),
            operating_info=PropertyOperatingInfo(),
        )


# ============================================================================
# PROPERTY MANAGERS
# ============================================================================


class PropertyDataManager:
    """
    Unified manager for both legacy and simplified property data.
    Handles property lifecycle management and data operations.
    """

    def __init__(self):
        self.properties: Dict[
            str, Union[PropertyInputData, SimplifiedPropertyInput]
        ] = {}
        self.logger = get_logger(self.__class__.__name__)

    def add_property(
        self, property_data: Union[PropertyInputData, SimplifiedPropertyInput]
    ) -> bool:
        """Add property to manager."""
        try:
            self.properties[property_data.property_id] = property_data
            self.logger.info(
                f"Added property: {property_data.property_name} ({property_data.property_id})"
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to add property: {e}")
            return False

    def get_property(
        self, property_id: str
    ) -> Optional[Union[PropertyInputData, SimplifiedPropertyInput]]:
        """Get property by ID."""
        return self.properties.get(property_id)

    def list_properties(self) -> List[str]:
        """List all property IDs."""
        return list(self.properties.keys())

    def get_simplified_properties(self) -> List[SimplifiedPropertyInput]:
        """Get all simplified properties."""
        return [
            p
            for p in self.properties.values()
            if isinstance(p, SimplifiedPropertyInput)
        ]

    def get_mixed_use_properties(self) -> List[SimplifiedPropertyInput]:
        """Get all mixed-use properties."""
        return [p for p in self.get_simplified_properties() if p.is_mixed_use()]

    def clear(self):
        """Clear all properties."""
        self.properties.clear()


# ============================================================================
# GLOBAL INSTANCES
# ============================================================================

# Global property manager instance
property_manager = PropertyDataManager()

# Legacy compatibility - simplified property manager
simplified_property_manager = PropertyDataManager()


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================


def validate_property_data(
    property_data: Union[PropertyInputData, SimplifiedPropertyInput],
) -> List[str]:
    """Validate property data and return list of validation errors."""
    errors = []

    try:
        # Basic validation happens in __post_init__
        if isinstance(property_data, SimplifiedPropertyInput):
            # Additional simplified property validation
            if property_data.residential_units.total_units <= 0:
                errors.append("Must have at least one residential unit")

            if (
                property_data.commercial_units
                and property_data.commercial_units.total_units < 0
            ):
                errors.append("Commercial units cannot be negative")

        elif isinstance(property_data, PropertyInputData):
            # Legacy property validation
            if property_data.financial_info.purchase_price <= 0:
                errors.append("Purchase price must be positive")

    except Exception as e:
        errors.append(str(e))

    return errors


def create_sample_property() -> SimplifiedPropertyInput:
    """Create a sample property for testing."""
    return SimplifiedPropertyInput(
        property_id="SAMPLE_001",
        property_name="Sample Mixed-Use Property",
        analysis_date=date.today(),
        residential_units=ResidentialUnits(total_units=8, average_rent_per_unit=2800),
        commercial_units=CommercialUnits(total_units=2, average_rent_per_unit=4200),
        renovation_info=RenovationInfo(status=RenovationStatus.NOT_NEEDED),
        equity_structure=InvestorEquityStructure(
            investor_equity_share_pct=80.0, self_cash_percentage=25.0
        ),
        city="New York",
        state="NY",
        msa_code="35620",
        purchase_price=1800000,
    )


if __name__ == "__main__":
    # Demo usage
    print("=== UNIFIED PROPERTY DATA MODULE ===")

    # Create sample property
    sample = create_sample_property()
    print(f"Created: {sample.property_name}")

    # Show metrics
    metrics = sample.calculate_key_metrics()
    print(f"Total Units: {metrics['total_units']}")
    print(f"Annual Rent: ${metrics['annual_gross_rent']:,.0f}")
    print(f"Mixed Use: {metrics['is_mixed_use']}")

    # Add to manager
    property_manager.add_property(sample)
    print(f"Properties in manager: {len(property_manager.list_properties())}")
