"""
Enhanced Property Input Structure for Mixed-Use Properties

Extends the existing property input system to support your specific requirements:
- Mixed residential/commercial properties
- Renovation timeline tracking
- Investor equity structures
- Simplified rent per unit inputs
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import date, datetime
from enum import Enum
import uuid

from core.exceptions import ValidationError, PropertyDataError
from core.logging_config import get_logger


class RenovationStatus(Enum):
    """Renovation status classifications."""
    NOT_NEEDED = "not_needed"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


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
                raise ValidationError("Anticipated duration required for planned/in-progress renovations")
            if self.anticipated_duration_months <= 0 or self.anticipated_duration_months > 60:
                raise ValidationError("Renovation duration must be between 1 and 60 months")


@dataclass
class ResidentialUnits:
    """Residential unit information."""
    total_units: int
    average_rent_per_unit: float
    average_square_feet_per_unit: Optional[int] = None
    unit_types: Optional[str] = None  # e.g., "Mix of 1BR, 2BR, 3BR"
    
    def __post_init__(self):
        if self.total_units <= 0:
            raise ValidationError("Residential units must be positive")
        if self.average_rent_per_unit <= 0:
            raise ValidationError("Average rent per unit must be positive")
        if self.average_square_feet_per_unit and self.average_square_feet_per_unit <= 0:
            raise ValidationError("Average square feet must be positive")


@dataclass 
class CommercialUnits:
    """Commercial unit information."""
    total_units: int
    average_rent_per_unit: float
    average_square_feet_per_unit: Optional[int] = None
    unit_types: Optional[str] = None  # e.g., "Retail, Office, Restaurant"
    
    def __post_init__(self):
        if self.total_units <= 0:
            raise ValidationError("Commercial units must be positive")
        if self.average_rent_per_unit <= 0:
            raise ValidationError("Average rent per unit must be positive")
        if self.average_square_feet_per_unit and self.average_square_feet_per_unit <= 0:
            raise ValidationError("Average square feet must be positive")


@dataclass
class InvestorEquityStructure:
    """Investor equity and ownership structure."""
    investor_equity_share_pct: float  # Percentage of ownership (0-100)
    self_cash_percentage: float       # Percentage of purchase price as cash (0-100)
    total_equity_required: Optional[float] = None
    number_of_investors: Optional[int] = 1
    investment_structure: Optional[str] = None  # e.g., "LLC", "Partnership", "Individual"
    
    def __post_init__(self):
        if not 0 <= self.investor_equity_share_pct <= 100:
            raise ValidationError("Investor equity share must be between 0% and 100%")
        if not 0 <= self.self_cash_percentage <= 100:
            raise ValidationError("Self cash percentage must be between 0% and 100%")
        if self.number_of_investors and self.number_of_investors <= 0:
            raise ValidationError("Number of investors must be positive")


@dataclass
class SimplifiedPropertyInput:
    """Simplified property input matching your exact requirements."""
    
    # Basic identification
    property_id: str
    property_name: str
    analysis_date: date
    
    # Core data points (your requirements)
    residential_units: ResidentialUnits
    commercial_units: Optional[CommercialUnits] = None
    renovation_info: RenovationInfo = field(default_factory=lambda: RenovationInfo(RenovationStatus.NOT_NEEDED))
    equity_structure: InvestorEquityStructure = field(default_factory=lambda: InvestorEquityStructure(100.0, 25.0))
    
    # Location (minimal required for market analysis)
    city: str = ""
    state: str = ""
    msa_code: str = ""
    
    # Additional context
    property_address: Optional[str] = None
    purchase_price: Optional[float] = None
    notes: Optional[str] = None
    
    def __post_init__(self):
        if not self.property_id:
            self.property_id = f"PROP_{uuid.uuid4().hex[:8].upper()}"
        if not self.property_name:
            raise ValidationError("Property name is required")
        
        # Ensure we have either residential or commercial units
        if self.residential_units.total_units == 0 and (not self.commercial_units or self.commercial_units.total_units == 0):
            raise ValidationError("Property must have at least one residential or commercial unit")
    
    def get_total_units(self) -> int:
        """Get total units across residential and commercial."""
        residential = self.residential_units.total_units
        commercial = self.commercial_units.total_units if self.commercial_units else 0
        return residential + commercial
    
    def get_total_monthly_rent(self) -> float:
        """Calculate total monthly rental income."""
        residential_rent = self.residential_units.total_units * self.residential_units.average_rent_per_unit
        commercial_rent = 0
        if self.commercial_units:
            commercial_rent = self.commercial_units.total_units * self.commercial_units.average_rent_per_unit
        return residential_rent + commercial_rent
    
    def get_annual_gross_rent(self) -> float:
        """Calculate annual gross rental income."""
        return self.get_total_monthly_rent() * 12
    
    def is_mixed_use(self) -> bool:
        """Check if property is mixed-use (both residential and commercial)."""
        has_residential = self.residential_units.total_units > 0
        has_commercial = self.commercial_units and self.commercial_units.total_units > 0
        return has_residential and has_commercial
    
    def get_property_type_classification(self) -> str:
        """Get property type for analysis purposes."""
        if self.is_mixed_use():
            return "mixed_use"
        elif self.residential_units.total_units > 0:
            return "multifamily"
        else:
            return "commercial"
    
    def calculate_key_metrics(self) -> Dict[str, Any]:
        """Calculate key financial metrics."""
        metrics = {}
        
        # Basic rental metrics
        metrics['total_units'] = self.get_total_units()
        metrics['monthly_gross_rent'] = self.get_total_monthly_rent()
        metrics['annual_gross_rent'] = self.get_annual_gross_rent()
        
        # Unit breakdown
        metrics['residential_units'] = self.residential_units.total_units
        metrics['commercial_units'] = self.commercial_units.total_units if self.commercial_units else 0
        
        # Rent per unit
        if self.get_total_units() > 0:
            metrics['average_rent_per_unit'] = self.get_total_monthly_rent() / self.get_total_units()
        
        # Property classification
        metrics['property_type'] = self.get_property_type_classification()
        metrics['is_mixed_use'] = self.is_mixed_use()
        
        # Investment structure
        metrics['investor_equity_share'] = self.equity_structure.investor_equity_share_pct
        metrics['self_cash_percentage'] = self.equity_structure.self_cash_percentage
        
        # Renovation status
        metrics['renovation_status'] = self.renovation_info.status.value
        if self.renovation_info.anticipated_duration_months:
            metrics['renovation_duration_months'] = self.renovation_info.anticipated_duration_months
        
        # Purchase price dependent metrics
        if self.purchase_price:
            metrics['purchase_price'] = self.purchase_price
            metrics['price_per_unit'] = self.purchase_price / self.get_total_units()
            
            # Cash requirements
            cash_percentage = self.equity_structure.self_cash_percentage / 100
            metrics['total_cash_required'] = self.purchase_price * cash_percentage
            metrics['cash_per_unit'] = metrics['total_cash_required'] / self.get_total_units()
            
            # Basic cap rate (if we have annual rent)
            annual_rent = self.get_annual_gross_rent()
            if annual_rent > 0:
                # Rough gross cap rate (actual would need NOI)
                metrics['gross_cap_rate'] = annual_rent / self.purchase_price
        
        return metrics
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            'property_id': self.property_id,
            'property_name': self.property_name,
            'analysis_date': self.analysis_date.isoformat(),
            
            # Core data points
            'residential_units_count': self.residential_units.total_units,
            'residential_rent_per_unit': self.residential_units.average_rent_per_unit,
            'residential_sqft_per_unit': self.residential_units.average_square_feet_per_unit,
            'residential_unit_types': self.residential_units.unit_types,
            
            'commercial_units_count': self.commercial_units.total_units if self.commercial_units else 0,
            'commercial_rent_per_unit': self.commercial_units.average_rent_per_unit if self.commercial_units else 0,
            'commercial_sqft_per_unit': self.commercial_units.average_square_feet_per_unit if self.commercial_units else None,
            'commercial_unit_types': self.commercial_units.unit_types if self.commercial_units else None,
            
            'renovation_status': self.renovation_info.status.value,
            'renovation_duration_months': self.renovation_info.anticipated_duration_months,
            'renovation_start_date': self.renovation_info.start_date.isoformat() if self.renovation_info.start_date else None,
            'renovation_estimated_cost': self.renovation_info.estimated_cost,
            
            'investor_equity_share_pct': self.equity_structure.investor_equity_share_pct,
            'self_cash_percentage': self.equity_structure.self_cash_percentage,
            'number_of_investors': self.equity_structure.number_of_investors,
            'investment_structure': self.equity_structure.investment_structure,
            
            # Location
            'city': self.city,
            'state': self.state,
            'msa_code': self.msa_code,
            'property_address': self.property_address,
            
            # Additional
            'purchase_price': self.purchase_price,
            'notes': self.notes,
            
            # Calculated metrics
            'calculated_metrics': self.calculate_key_metrics()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SimplifiedPropertyInput':
        """Create instance from dictionary (for database loading)."""
        
        # Reconstruct residential units
        residential_units = ResidentialUnits(
            total_units=data.get('residential_units_count', 0),
            average_rent_per_unit=data.get('residential_rent_per_unit', 0),
            average_square_feet_per_unit=data.get('residential_sqft_per_unit'),
            unit_types=data.get('residential_unit_types')
        )
        
        # Reconstruct commercial units if present
        commercial_units = None
        if data.get('commercial_units_count', 0) > 0:
            commercial_units = CommercialUnits(
                total_units=data.get('commercial_units_count', 0),
                average_rent_per_unit=data.get('commercial_rent_per_unit', 0),
                average_square_feet_per_unit=data.get('commercial_sqft_per_unit'),
                unit_types=data.get('commercial_unit_types')
            )
        
        # Reconstruct renovation info
        renovation_info = RenovationInfo(
            status=RenovationStatus(data.get('renovation_status', 'not_needed')),
            anticipated_duration_months=data.get('renovation_duration_months'),
            start_date=date.fromisoformat(data['renovation_start_date']) if data.get('renovation_start_date') else None,
            estimated_cost=data.get('renovation_estimated_cost')
        )
        
        # Reconstruct equity structure
        equity_structure = InvestorEquityStructure(
            investor_equity_share_pct=data.get('investor_equity_share_pct', 100.0),
            self_cash_percentage=data.get('self_cash_percentage', 25.0),
            number_of_investors=data.get('number_of_investors', 1),
            investment_structure=data.get('investment_structure')
        )
        
        return cls(
            property_id=data.get('property_id', ''),
            property_name=data.get('property_name', ''),
            analysis_date=date.fromisoformat(data['analysis_date']) if data.get('analysis_date') else date.today(),
            residential_units=residential_units,
            commercial_units=commercial_units,
            renovation_info=renovation_info,
            equity_structure=equity_structure,
            city=data.get('city', ''),
            state=data.get('state', ''),
            msa_code=data.get('msa_code', ''),
            property_address=data.get('property_address'),
            purchase_price=data.get('purchase_price'),
            notes=data.get('notes')
        )


class SimplifiedPropertyManager:
    """Manager for simplified property data with database storage capability."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.properties: Dict[str, SimplifiedPropertyInput] = {}
    
    def add_property(self, property_data: SimplifiedPropertyInput) -> None:
        """Add property to the manager."""
        try:
            self.properties[property_data.property_id] = property_data
            self.logger.info(f"Added property: {property_data.property_name} ({property_data.property_id})")
        except Exception as e:
            raise PropertyDataError(f"Failed to add property: {e}") from e
    
    def get_property(self, property_id: str) -> Optional[SimplifiedPropertyInput]:
        """Get property by ID."""
        return self.properties.get(property_id)
    
    def list_properties(self) -> List[str]:
        """List all property IDs."""
        return list(self.properties.keys())
    
    def get_properties_by_type(self, property_type: str) -> List[SimplifiedPropertyInput]:
        """Get properties by type classification."""
        return [prop for prop in self.properties.values() 
                if prop.get_property_type_classification() == property_type]
    
    def get_mixed_use_properties(self) -> List[SimplifiedPropertyInput]:
        """Get all mixed-use properties."""
        return [prop for prop in self.properties.values() if prop.is_mixed_use()]
    
    def export_to_database_format(self) -> List[Dict[str, Any]]:
        """Export all properties in database-ready format."""
        return [prop.to_dict() for prop in self.properties.values()]
    
    def import_from_database_format(self, properties_data: List[Dict[str, Any]]) -> None:
        """Import properties from database format."""
        for prop_data in properties_data:
            try:
                property_obj = SimplifiedPropertyInput.from_dict(prop_data)
                self.add_property(property_obj)
            except Exception as e:
                self.logger.error(f"Failed to import property {prop_data.get('property_id', 'unknown')}: {e}")


# Global manager instance
simplified_property_manager = SimplifiedPropertyManager()


def create_sample_simplified_property() -> SimplifiedPropertyInput:
    """Create a sample property using the simplified structure."""
    return SimplifiedPropertyInput(
        property_id="SIMPLE_001",
        property_name="Mixed-Use Investment Property",
        analysis_date=date.today(),
        residential_units=ResidentialUnits(
            total_units=12,
            average_rent_per_unit=2500.0,
            average_square_feet_per_unit=900,
            unit_types="Mix of 1BR and 2BR apartments"
        ),
        commercial_units=CommercialUnits(
            total_units=3,
            average_rent_per_unit=4500.0,
            average_square_feet_per_unit=1200,
            unit_types="Retail and office space"
        ),
        renovation_info=RenovationInfo(
            status=RenovationStatus.PLANNED,
            anticipated_duration_months=6,
            estimated_cost=150000,
            description="Kitchen and bathroom upgrades"
        ),
        equity_structure=InvestorEquityStructure(
            investor_equity_share_pct=75.0,
            self_cash_percentage=30.0,
            number_of_investors=2,
            investment_structure="LLC"
        ),
        city="New York",
        state="NY",
        msa_code="35620",
        property_address="789 Investment Boulevard",
        purchase_price=2_800_000,
        notes="Prime location with good foot traffic"
    )