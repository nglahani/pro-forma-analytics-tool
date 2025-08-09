"""
Property Data Coverage Tests

Tests to improve coverage of property data entities.
"""

from datetime import date

import pytest

from core.exceptions import ValidationError
from src.domain.entities.property_data import (
    CommercialUnits,
    InvestorEquityStructure,
    PropertyClass,
    PropertyFinancialInfo,
    PropertyLocationInfo,
    PropertyPhysicalInfo,
    PropertyType,
    RenovationInfo,
    RenovationStatus,
    ResidentialUnits,
    SimplifiedPropertyInput,
)


class TestPropertyDataCoverage:
    """Test property data entities for better coverage."""

    def test_residential_units_validation_errors(self):
        """Test residential units validation errors."""
        with pytest.raises(ValidationError, match="Residential units must be positive"):
            ResidentialUnits(total_units=0, average_rent_per_unit=2500)

        with pytest.raises(ValidationError, match="Residential rent must be positive"):
            ResidentialUnits(total_units=10, average_rent_per_unit=0)

    def test_commercial_units_validation_errors(self):
        """Test commercial units validation errors."""
        with pytest.raises(ValidationError, match="Commercial units must be positive"):
            CommercialUnits(total_units=0, average_rent_per_unit=50)

        with pytest.raises(ValidationError, match="Commercial rent must be positive"):
            CommercialUnits(total_units=5, average_rent_per_unit=0)

    def test_renovation_info_validation_errors(self):
        """Test renovation info validation errors."""
        with pytest.raises(ValidationError, match="Anticipated duration required"):
            RenovationInfo(status=RenovationStatus.PLANNED)

        with pytest.raises(ValidationError, match="Anticipated duration required"):
            RenovationInfo(
                status=RenovationStatus.PLANNED, anticipated_duration_months=0
            )

        with pytest.raises(
            ValidationError, match="Renovation duration must be between 1 and 60 months"
        ):
            RenovationInfo(
                status=RenovationStatus.PLANNED, anticipated_duration_months=61
            )

    def test_investor_equity_structure_validation_errors(self):
        """Test investor equity structure validation errors."""
        with pytest.raises(
            ValidationError, match="Investor equity share must be between 0 and 100%"
        ):
            InvestorEquityStructure(
                investor_equity_share_pct=101, self_cash_percentage=50
            )

        with pytest.raises(
            ValidationError, match="Self cash percentage must be between 0 and 100%"
        ):
            InvestorEquityStructure(
                investor_equity_share_pct=50, self_cash_percentage=101
            )

    def test_property_physical_info_validation_errors(self):
        """Test property physical info validation errors."""
        with pytest.raises(ValidationError, match="Total units must be positive"):
            PropertyPhysicalInfo(
                property_type=PropertyType.MULTIFAMILY,
                property_class=PropertyClass.CLASS_A,
                total_units=0,
                total_square_feet=5000,
                year_built=2000,
            )

        with pytest.raises(ValidationError, match="Total square feet must be positive"):
            PropertyPhysicalInfo(
                property_type=PropertyType.MULTIFAMILY,
                property_class=PropertyClass.CLASS_A,
                total_units=10,
                total_square_feet=0,
                year_built=2000,
            )

    def test_property_financial_info_validation_errors(self):
        """Test property financial info validation errors."""
        with pytest.raises(ValidationError, match="Purchase price must be positive"):
            PropertyFinancialInfo(
                purchase_price=0, down_payment_pct=0.25, current_noi=50000
            )

        with pytest.raises(
            ValidationError, match="Down payment percentage must be between 0 and 1"
        ):
            PropertyFinancialInfo(
                purchase_price=1000000, down_payment_pct=1.1, current_noi=50000
            )

    def test_property_location_info_validation_errors(self):
        """Test property location info validation errors."""
        with pytest.raises(ValidationError, match="Address is required"):
            PropertyLocationInfo(
                address="",
                city="New York",
                state="NY",
                zip_code="10001",
                msa_code="35620",
            )

        with pytest.raises(ValidationError, match="City is required"):
            PropertyLocationInfo(
                address="123 Test St",
                city="",
                state="NY",
                zip_code="10001",
                msa_code="35620",
            )

        with pytest.raises(ValidationError, match="State must be 2-letter code"):
            PropertyLocationInfo(
                address="123 Test St",
                city="New York",
                state="New York",
                zip_code="10001",
                msa_code="35620",
            )

    def test_residential_units_monthly_gross_rent(self):
        """Test residential units monthly gross rent calculation."""
        units = ResidentialUnits(total_units=10, average_rent_per_unit=2500)
        assert units.monthly_gross_rent == 25000

    def test_commercial_units_monthly_gross_rent(self):
        """Test commercial units monthly gross rent calculation."""
        units = CommercialUnits(total_units=5, average_rent_per_unit=5000)
        assert units.monthly_gross_rent == 25000

    def test_simplified_property_input_mixed_use(self):
        """Test SimplifiedPropertyInput mixed use functionality."""
        residential_units = ResidentialUnits(total_units=10, average_rent_per_unit=2500)
        commercial_units = CommercialUnits(total_units=2, average_rent_per_unit=5000)
        renovation_info = RenovationInfo(status=RenovationStatus.NOT_NEEDED)
        equity_structure = InvestorEquityStructure(
            investor_equity_share_pct=25, self_cash_percentage=75
        )

        prop = SimplifiedPropertyInput(
            property_id="TEST_001",
            property_name="Mixed Use Property",
            analysis_date=date.today(),
            residential_units=residential_units,
            commercial_units=commercial_units,
            renovation_info=renovation_info,
            equity_structure=equity_structure,
        )

        assert prop.is_mixed_use()
        assert prop.get_total_units() == 12
        assert prop.get_monthly_gross_rent() == 35000
        assert prop.get_annual_gross_rent() == 420000
        assert prop.get_property_type_classification() == "mixed_use"

    def test_simplified_property_input_residential_only(self):
        """Test SimplifiedPropertyInput residential only functionality."""
        residential_units = ResidentialUnits(total_units=10, average_rent_per_unit=2500)
        renovation_info = RenovationInfo(status=RenovationStatus.NOT_NEEDED)
        equity_structure = InvestorEquityStructure(
            investor_equity_share_pct=25, self_cash_percentage=75
        )

        prop = SimplifiedPropertyInput(
            property_id="TEST_002",
            property_name="Residential Property",
            analysis_date=date.today(),
            residential_units=residential_units,
            renovation_info=renovation_info,
            equity_structure=equity_structure,
        )

        assert not prop.is_mixed_use()
        assert prop.get_total_units() == 10
        assert prop.get_monthly_gross_rent() == 25000
        assert prop.get_property_type_classification() == "multifamily"

    def test_simplified_property_input_with_purchase_price(self):
        """Test SimplifiedPropertyInput with purchase price calculations."""
        residential_units = ResidentialUnits(total_units=10, average_rent_per_unit=2500)
        renovation_info = RenovationInfo(status=RenovationStatus.NOT_NEEDED)
        equity_structure = InvestorEquityStructure(
            investor_equity_share_pct=25, self_cash_percentage=75
        )

        prop = SimplifiedPropertyInput(
            property_id="TEST_003",
            property_name="Purchase Price Property",
            analysis_date=date.today(),
            residential_units=residential_units,
            renovation_info=renovation_info,
            equity_structure=equity_structure,
            purchase_price=1000000,
            msa_code="35620",
        )

        metrics = prop.calculate_key_metrics()
        assert metrics["purchase_price"] == 1000000
        assert metrics["price_per_unit"] == 100000
        assert metrics["total_cash_required"] == 750000  # 75% of purchase price
        assert metrics["gross_cap_rate"] == 0.3  # 300000 annual rent / 1000000 price

    def test_simplified_property_input_auto_property_id(self):
        """Test SimplifiedPropertyInput with auto-generated property ID."""
        residential_units = ResidentialUnits(total_units=10, average_rent_per_unit=2500)
        renovation_info = RenovationInfo(status=RenovationStatus.NOT_NEEDED)
        equity_structure = InvestorEquityStructure(
            investor_equity_share_pct=25, self_cash_percentage=75
        )

        prop = SimplifiedPropertyInput(
            property_id="",  # Empty property_id should auto-generate
            property_name="Auto ID Property",
            analysis_date=date.today(),
            residential_units=residential_units,
            renovation_info=renovation_info,
            equity_structure=equity_structure,
        )

        assert prop.property_id.startswith("USER_")
        assert len(prop.property_id) > 5

    def test_simplified_property_input_name_validation_error(self):
        """Test SimplifiedPropertyInput property name validation."""
        residential_units = ResidentialUnits(total_units=10, average_rent_per_unit=2500)
        renovation_info = RenovationInfo(status=RenovationStatus.NOT_NEEDED)
        equity_structure = InvestorEquityStructure(
            investor_equity_share_pct=25, self_cash_percentage=75
        )

        with pytest.raises(ValidationError, match="Property name is required"):
            SimplifiedPropertyInput(
                property_id="TEST_004",
                property_name="",  # Empty name should raise error
                analysis_date=date.today(),
                residential_units=residential_units,
                renovation_info=renovation_info,
                equity_structure=equity_structure,
            )

    def test_simplified_property_input_msa_code_error(self):
        """Test SimplifiedPropertyInput MSA code requirement for analysis."""
        residential_units = ResidentialUnits(total_units=10, average_rent_per_unit=2500)
        renovation_info = RenovationInfo(status=RenovationStatus.NOT_NEEDED)
        equity_structure = InvestorEquityStructure(
            investor_equity_share_pct=25, self_cash_percentage=75
        )

        prop = SimplifiedPropertyInput(
            property_id="TEST_005",
            property_name="No MSA Property",
            analysis_date=date.today(),
            residential_units=residential_units,
            renovation_info=renovation_info,
            equity_structure=equity_structure,
        )

        with pytest.raises(
            ValidationError, match="MSA code is required for Monte Carlo analysis"
        ):
            prop.get_msa_code()

    def test_property_location_info_get_msa_code(self):
        """Test property location info MSA code mapping."""
        location = PropertyLocationInfo(
            address="123 Test St",
            city="New York",
            state="NY",
            zip_code="10001",
            msa_code="35620",
        )

        assert location.get_msa_code() == "35620"
