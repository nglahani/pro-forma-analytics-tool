"""
Comprehensive Test Suite for Simplified Property Input System

Tests all aspects of the simplified property input system including:
- 7 required data fields capture
- Database backend storage
- Pro forma analysis integration
- Mixed-use property support
"""

import pytest
import sys
from pathlib import Path
from datetime import date
import tempfile
import os

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from enhanced_property_inputs import (
    SimplifiedPropertyInput, ResidentialUnits, CommercialUnits,
    RenovationInfo, InvestorEquityStructure, RenovationStatus,
    simplified_property_manager
)
from database.property_database import PropertyDatabase


class TestSimplifiedPropertyInput:
    """Test the simplified property input data structure."""
    
    def test_create_residential_only_property(self):
        """Test creating a residential-only property."""
        property_data = SimplifiedPropertyInput(
            property_id="TEST_RESIDENTIAL_001",
            property_name="Residential Only Property",
            analysis_date=date.today(),
            residential_units=ResidentialUnits(
                total_units=10,
                average_rent_per_unit=2500.0
            ),
            renovation_info=RenovationInfo(
                status=RenovationStatus.NOT_NEEDED
            ),
            equity_structure=InvestorEquityStructure(
                investor_equity_share_pct=100.0,
                self_cash_percentage=25.0
            )
        )
        
        assert property_data.property_name == "Residential Only Property"
        assert property_data.residential_units.total_units == 10
        assert property_data.residential_units.average_rent_per_unit == 2500.0
        assert property_data.commercial_units is None
        assert not property_data.is_mixed_use()
        assert property_data.get_property_type_classification() == "multifamily"
    
    def test_create_mixed_use_property(self):
        """Test creating a mixed-use property with both residential and commercial units."""
        property_data = SimplifiedPropertyInput(
            property_id="TEST_MIXED_001",
            property_name="Mixed-Use Property",
            analysis_date=date.today(),
            residential_units=ResidentialUnits(
                total_units=8,
                average_rent_per_unit=2800.0
            ),
            commercial_units=CommercialUnits(
                total_units=2,
                average_rent_per_unit=4200.0
            ),
            renovation_info=RenovationInfo(
                status=RenovationStatus.PLANNED,
                anticipated_duration_months=6
            ),
            equity_structure=InvestorEquityStructure(
                investor_equity_share_pct=75.0,
                self_cash_percentage=30.0
            )
        )
        
        assert property_data.residential_units.total_units == 8
        assert property_data.commercial_units.total_units == 2
        assert property_data.is_mixed_use()
        assert property_data.get_property_type_classification() == "mixed_use"
        assert property_data.get_total_units() == 10
    
    def test_seven_required_data_fields(self):
        """Test that all 7 required data fields are captured."""
        property_data = SimplifiedPropertyInput(
            property_id="TEST_SEVEN_001",
            property_name="Seven Fields Test",
            analysis_date=date.today(),
            residential_units=ResidentialUnits(
                total_units=12,                 # 1. Number of residential units
                average_rent_per_unit=2600.0    # 5. Residential rent/unit
            ),
            commercial_units=CommercialUnits(
                total_units=3,                  # 3. Number of commercial units
                average_rent_per_unit=4000.0    # 6. Commercial rent/unit
            ),
            renovation_info=RenovationInfo(
                status=RenovationStatus.PLANNED,
                anticipated_duration_months=8   # 2. Anticipated renovation time
            ),
            equity_structure=InvestorEquityStructure(
                investor_equity_share_pct=80.0,  # 4. Investor equity share
                self_cash_percentage=35.0        # 7. Self cash percentage
            )
        )
        
        # Verify all 7 fields are accessible
        assert property_data.residential_units.total_units == 12              # Field 1
        assert property_data.renovation_info.anticipated_duration_months == 8 # Field 2
        assert property_data.commercial_units.total_units == 3               # Field 3
        assert property_data.equity_structure.investor_equity_share_pct == 80.0  # Field 4
        assert property_data.residential_units.average_rent_per_unit == 2600.0   # Field 5
        assert property_data.commercial_units.average_rent_per_unit == 4000.0    # Field 6
        assert property_data.equity_structure.self_cash_percentage == 35.0       # Field 7
    
    def test_calculate_key_metrics(self):
        """Test calculation of key financial metrics."""
        property_data = SimplifiedPropertyInput(
            property_id="TEST_METRICS_001",
            property_name="Metrics Test",
            analysis_date=date.today(),
            residential_units=ResidentialUnits(
                total_units=5,
                average_rent_per_unit=3000.0
            ),
            commercial_units=CommercialUnits(
                total_units=1,
                average_rent_per_unit=5000.0
            ),
            renovation_info=RenovationInfo(status=RenovationStatus.NOT_NEEDED),
            equity_structure=InvestorEquityStructure(
                investor_equity_share_pct=100.0,
                self_cash_percentage=25.0
            ),
            purchase_price=1_200_000
        )
        
        metrics = property_data.calculate_key_metrics()
        
        assert metrics['total_units'] == 6
        assert metrics['monthly_gross_rent'] == 20000.0  # (5 * 3000) + (1 * 5000)
        assert metrics['annual_gross_rent'] == 240000.0  # 20000 * 12
        assert metrics['is_mixed_use'] is True
        assert metrics['purchase_price'] == 1200000
        assert metrics['price_per_unit'] == 200000.0    # 1200000 / 6
        assert metrics['total_cash_required'] == 300000.0  # 1200000 * 0.25
    
    def test_validation_errors(self):
        """Test that validation errors are properly raised."""
        # Test empty property name
        with pytest.raises(Exception):
            SimplifiedPropertyInput(
                property_id="TEST_VALIDATION_001",
                property_name="",  # Should fail
                analysis_date=date.today(),
                residential_units=ResidentialUnits(total_units=1, average_rent_per_unit=1000),
                renovation_info=RenovationInfo(status=RenovationStatus.NOT_NEEDED),
                equity_structure=InvestorEquityStructure(100.0, 25.0)
            )
        
        # Test invalid renovation duration
        with pytest.raises(Exception):
            RenovationInfo(
                status=RenovationStatus.PLANNED,
                anticipated_duration_months=0  # Should fail for planned renovation
            )
        
        # Test invalid equity percentage
        with pytest.raises(Exception):
            InvestorEquityStructure(
                investor_equity_share_pct=150.0,  # Should fail (> 100%)
                self_cash_percentage=25.0
            )
    
    def test_to_dict_serialization(self):
        """Test serialization to dictionary for database storage."""
        property_data = SimplifiedPropertyInput(
            property_id="TEST_SERIAL_001",
            property_name="Serialization Test",
            analysis_date=date.today(),
            residential_units=ResidentialUnits(total_units=4, average_rent_per_unit=2400),
            renovation_info=RenovationInfo(status=RenovationStatus.NOT_NEEDED),
            equity_structure=InvestorEquityStructure(100.0, 30.0)
        )
        
        data_dict = property_data.to_dict()
        
        assert data_dict['property_name'] == "Serialization Test"
        assert data_dict['residential_units_count'] == 4
        assert data_dict['residential_rent_per_unit'] == 2400
        assert data_dict['renovation_status'] == 'not_needed'
        assert data_dict['investor_equity_share_pct'] == 100.0
        assert data_dict['self_cash_percentage'] == 30.0
        assert 'calculated_metrics' in data_dict
    
    def test_from_dict_deserialization(self):
        """Test deserialization from dictionary."""
        data_dict = {
            'property_name': 'Deserialization Test',
            'analysis_date': date.today().isoformat(),
            'residential_units_count': 6,
            'residential_rent_per_unit': 2700,
            'commercial_units_count': 0,
            'renovation_status': 'not_needed',
            'investor_equity_share_pct': 90.0,
            'self_cash_percentage': 20.0
        }
        
        property_data = SimplifiedPropertyInput.from_dict(data_dict)
        
        assert property_data.property_name == "Deserialization Test"
        assert property_data.residential_units.total_units == 6
        assert property_data.residential_units.average_rent_per_unit == 2700
        assert property_data.equity_structure.investor_equity_share_pct == 90.0


class TestPropertyDatabase:
    """Test the property database functionality."""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_file:
            db_path = temp_file.name
        
        db = PropertyDatabase(db_path)
        yield db
        
        # Cleanup
        os.unlink(db_path)
    
    def test_save_and_load_property(self, temp_db):
        """Test saving and loading properties from database."""
        property_data = SimplifiedPropertyInput(
            property_id="TEST_DB_001",
            property_name="Database Test Property",
            analysis_date=date.today(),
            residential_units=ResidentialUnits(total_units=8, average_rent_per_unit=2500),
            renovation_info=RenovationInfo(status=RenovationStatus.NOT_NEEDED),
            equity_structure=InvestorEquityStructure(100.0, 25.0)
        )
        
        # Save property
        success = temp_db.save_property(property_data)
        assert success is True
        
        # Load property
        loaded_property = temp_db.load_property(property_data.property_id)
        assert loaded_property is not None
        assert loaded_property.property_name == "Database Test Property"
        assert loaded_property.residential_units.total_units == 8
    
    def test_list_properties(self, temp_db):
        """Test listing properties from database."""
        # Add multiple properties
        for i in range(3):
            property_data = SimplifiedPropertyInput(
                property_id=f"TEST_PROP_{i+1:03d}",
                property_name=f"Test Property {i+1}",
                analysis_date=date.today(),
                residential_units=ResidentialUnits(total_units=5+i, average_rent_per_unit=2000+i*100),
                renovation_info=RenovationInfo(status=RenovationStatus.NOT_NEEDED),
                equity_structure=InvestorEquityStructure(100.0, 25.0)
            )
            temp_db.save_property(property_data)
        
        # List properties
        properties = temp_db.list_properties()
        assert len(properties) == 3
        assert any(p['property_name'] == "Test Property 1" for p in properties)
    
    def test_user_listings(self, temp_db):
        """Test user listing functionality."""
        property_data = SimplifiedPropertyInput(
            property_id="TEST_USER_001",
            property_name="User Listing Test",
            analysis_date=date.today(),
            residential_units=ResidentialUnits(total_units=6, average_rent_per_unit=2300),
            renovation_info=RenovationInfo(status=RenovationStatus.NOT_NEEDED),
            equity_structure=InvestorEquityStructure(100.0, 25.0)
        )
        
        # Save property and create user listing
        temp_db.save_property(property_data)
        listing_id = temp_db.create_user_listing("test_user", property_data.property_id)
        
        assert listing_id != ""
        
        # Get user listings
        user_listings = temp_db.get_user_listings("test_user")
        assert len(user_listings) == 1
        assert user_listings[0]['property_name'] == "User Listing Test"
    
    def test_database_stats(self, temp_db):
        """Test database statistics functionality."""
        # Add some properties
        residential_property = SimplifiedPropertyInput(
            property_id="TEST_RES_STAT_001",
            property_name="Residential Property",
            analysis_date=date.today(),
            residential_units=ResidentialUnits(total_units=10, average_rent_per_unit=2000),
            renovation_info=RenovationInfo(status=RenovationStatus.NOT_NEEDED),
            equity_structure=InvestorEquityStructure(100.0, 25.0)
        )
        
        mixed_use_property = SimplifiedPropertyInput(
            property_id="TEST_MIXED_STAT_001",
            property_name="Mixed-Use Property",
            analysis_date=date.today(),
            residential_units=ResidentialUnits(total_units=5, average_rent_per_unit=2500),
            commercial_units=CommercialUnits(total_units=2, average_rent_per_unit=3500),
            renovation_info=RenovationInfo(status=RenovationStatus.NOT_NEEDED),
            equity_structure=InvestorEquityStructure(100.0, 25.0)
        )
        
        temp_db.save_property(residential_property)
        temp_db.save_property(mixed_use_property)
        
        stats = temp_db.get_database_stats()
        assert stats['total_properties'] == 2
        assert 'residential' in stats['property_types']
        assert 'mixed_use' in stats['property_types']


class TestIntegration:
    """Test integration between components."""
    
    def test_property_manager_integration(self):
        """Test integration with simplified property manager."""
        property_data = SimplifiedPropertyInput(
            property_id="TEST_MANAGER_001",
            property_name="Manager Integration Test",
            analysis_date=date.today(),
            residential_units=ResidentialUnits(total_units=7, average_rent_per_unit=2400),
            renovation_info=RenovationInfo(status=RenovationStatus.NOT_NEEDED),
            equity_structure=InvestorEquityStructure(100.0, 25.0)
        )
        
        # Clear manager
        simplified_property_manager.properties.clear()
        
        # Add property
        simplified_property_manager.add_property(property_data)
        
        # Test retrieval
        retrieved = simplified_property_manager.get_property(property_data.property_id)
        assert retrieved is not None
        assert retrieved.property_name == "Manager Integration Test"
        
        # Test listing
        property_ids = simplified_property_manager.list_properties()
        assert property_data.property_id in property_ids
        
        # Test mixed-use filtering
        mixed_properties = simplified_property_manager.get_mixed_use_properties()
        assert len(mixed_properties) == 0  # This property is residential only
    
    def test_monte_carlo_integration_data_conversion(self):
        """Test that simplified property data can be converted for Monte Carlo analysis."""
        property_data = SimplifiedPropertyInput(
            property_id="TEST_MC_001",
            property_name="Monte Carlo Test",
            analysis_date=date.today(),
            residential_units=ResidentialUnits(total_units=8, average_rent_per_unit=2800),
            commercial_units=CommercialUnits(total_units=2, average_rent_per_unit=4200),
            renovation_info=RenovationInfo(status=RenovationStatus.NOT_NEEDED),
            equity_structure=InvestorEquityStructure(80.0, 25.0),
            city="New York",
            state="NY",
            msa_code="35620",
            purchase_price=1800000
        )
        
        # Test that we can extract all necessary data for Monte Carlo
        assert property_data.get_total_units() == 10
        assert property_data.get_annual_gross_rent() == 369600  # (8*2800 + 2*4200) * 12
        assert property_data.purchase_price == 1800000
        assert property_data.msa_code == "35620"
        
        # Test calculated metrics needed for analysis
        metrics = property_data.calculate_key_metrics()
        assert metrics['price_per_unit'] == 180000
        assert metrics['total_cash_required'] == 450000  # 1800000 * 0.25
        assert metrics['gross_cap_rate'] > 0  # Should have a positive cap rate


@pytest.mark.integration
class TestEndToEndWorkflow:
    """Test the complete end-to-end workflow."""
    
    def test_complete_workflow(self):
        """Test the complete workflow from input to analysis."""
        # Step 1: Create property with all 7 required fields
        property_data = SimplifiedPropertyInput(
            property_id="TEST_E2E_001",
            property_name="End-to-End Test Property",
            analysis_date=date.today(),
            residential_units=ResidentialUnits(
                total_units=15,              # Field 1
                average_rent_per_unit=2700   # Field 5
            ),
            commercial_units=CommercialUnits(
                total_units=3,               # Field 3
                average_rent_per_unit=4500   # Field 6
            ),
            renovation_info=RenovationInfo(
                status=RenovationStatus.PLANNED,
                anticipated_duration_months=5  # Field 2
            ),
            equity_structure=InvestorEquityStructure(
                investor_equity_share_pct=85.0,  # Field 4
                self_cash_percentage=30.0        # Field 7
            ),
            city="New York",
            state="NY",
            msa_code="35620",
            purchase_price=3600000
        )
        
        # Step 2: Validate all fields are captured
        assert property_data.residential_units.total_units == 15
        assert property_data.renovation_info.anticipated_duration_months == 5
        assert property_data.commercial_units.total_units == 3
        assert property_data.equity_structure.investor_equity_share_pct == 85.0
        assert property_data.residential_units.average_rent_per_unit == 2700
        assert property_data.commercial_units.average_rent_per_unit == 4500
        assert property_data.equity_structure.self_cash_percentage == 30.0
        
        # Step 3: Test database operations
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_file:
            db_path = temp_file.name
        
        try:
            db = PropertyDatabase(db_path)
            
            # Save property
            success = db.save_property(property_data)
            assert success is True
            
            # Create user listing
            listing_id = db.create_user_listing("end_to_end_user", property_data.property_id)
            assert listing_id != ""
            
            # Verify retrieval
            loaded_property = db.load_property(property_data.property_id)
            assert loaded_property.property_name == "End-to-End Test Property"
            
        finally:
            os.unlink(db_path)
        
        # Step 4: Test metrics calculation
        metrics = property_data.calculate_key_metrics()
        expected_monthly_rent = (15 * 2700) + (3 * 4500)  # 40500 + 13500 = 54000
        expected_annual_rent = expected_monthly_rent * 12   # 648000
        
        assert metrics['monthly_gross_rent'] == expected_monthly_rent
        assert metrics['annual_gross_rent'] == expected_annual_rent
        assert metrics['total_units'] == 18
        assert metrics['price_per_unit'] == 200000  # 3600000 / 18
        assert metrics['total_cash_required'] == 1080000  # 3600000 * 0.30
        
        # Step 5: Verify property classification
        assert property_data.is_mixed_use() is True
        assert property_data.get_property_type_classification() == "mixed_use"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])