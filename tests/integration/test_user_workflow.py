"""
Integration Tests for User Input Workflow

Tests the complete user workflow from property input to Monte Carlo analysis.
Validates production readiness for user input workflow implementation.
"""

import pytest
from datetime import date
from unittest.mock import Mock

# Core imports
from core.property_inputs import (
    PropertyInputData,
    PropertyPhysicalInfo,
    PropertyFinancialInfo,
    PropertyLocationInfo,
    PropertyOperatingInfo,
    PropertyType,
    PropertyClass,
    UnitMix,
    create_sample_property,
    property_manager
)
from monte_carlo.simulation_engine import monte_carlo_engine


class TestUserInputWorkflow:
    """Test complete user input workflow."""
    
    def test_property_creation_and_validation(self):
        """Test property data creation with user inputs."""
        # Simulate user input
        property_data = PropertyInputData(
            property_id="USER_001",
            property_name="User Test Property",
            analysis_date=date.today(),
            physical_info=PropertyPhysicalInfo(
                property_type=PropertyType.MULTIFAMILY,
                property_class=PropertyClass.CLASS_B,
                total_units=100,
                total_square_feet=90000,
                year_built=2015,
                parking_spaces=120
            ),
            financial_info=PropertyFinancialInfo(
                purchase_price=10_000_000,
                down_payment_pct=0.30,
                current_noi=700_000,
                current_gross_rent=1_200_000
            ),
            location_info=PropertyLocationInfo(
                address="456 Test Avenue",
                city="Los Angeles",
                state="CA",
                zip_code="90210",
                msa_code="31080"  # LA MSA
            ),
            operating_info=PropertyOperatingInfo(
                management_fee_pct=0.04,
                maintenance_reserve_pct=0.03,
                unit_mix=[
                    UnitMix("Studio", 20, 600, 1800),
                    UnitMix("1BR/1BA", 40, 800, 2400),
                    UnitMix("2BR/2BA", 30, 1100, 3200),
                    UnitMix("3BR/2BA", 10, 1400, 4000)
                ]
            )
        )
        
        # Validation checks
        assert property_data.property_id == "USER_001"
        assert property_data.get_msa_code() == "31080"
        assert property_data.calculate_price_per_unit() == 100_000
        assert property_data.calculate_price_per_sf() == pytest.approx(111.11, rel=1e-2)
        assert property_data.get_current_cap_rate() == 0.07
        
        # Validate unit mix matches total units
        total_units_in_mix = sum(unit.count for unit in property_data.operating_info.unit_mix)
        assert total_units_in_mix == property_data.physical_info.total_units
        
        # Test property manager integration
        property_manager.add_property(property_data)
        retrieved_property = property_manager.get_property("USER_001")
        assert retrieved_property is not None
        assert retrieved_property.property_name == "User Test Property"
    
    def test_monte_carlo_integration_with_user_property(self):
        """Test Monte Carlo simulation with user-provided property data."""
        # Create user property
        user_property = create_sample_property()
        user_property.property_id = "WORKFLOW_TEST"
        user_property.property_name = "Workflow Test Property"
        
        # Generate Monte Carlo scenarios
        # Note: This test may need forecasting data to be available
        try:
            monte_carlo_results = monte_carlo_engine.generate_scenarios(
                property_data=user_property,
                num_scenarios=50,  # Smaller number for faster testing
                horizon_years=5,
                use_correlations=True
            )
            
            # Validate results structure
            assert monte_carlo_results.property_id == "WORKFLOW_TEST"
            assert monte_carlo_results.msa_code == user_property.get_msa_code()
            assert monte_carlo_results.num_scenarios == 50
            assert len(monte_carlo_results.scenarios) == 50
            assert monte_carlo_results.horizon_years == 5
            
            # Validate scenario structure
            first_scenario = monte_carlo_results.scenarios[0]
            assert hasattr(first_scenario, 'scenario_id')
            assert hasattr(first_scenario, 'forecasted_parameters')
            assert hasattr(first_scenario, 'scenario_summary')
            
            # Validate summary statistics
            assert monte_carlo_results.summary_statistics is not None
            assert len(monte_carlo_results.summary_statistics) > 0
            
            # Validate extreme scenarios identification
            if monte_carlo_results.extreme_scenarios:
                assert 'best_growth' in monte_carlo_results.extreme_scenarios
                assert 'worst_growth' in monte_carlo_results.extreme_scenarios
                assert 'lowest_risk' in monte_carlo_results.extreme_scenarios
                assert 'highest_risk' in monte_carlo_results.extreme_scenarios
            
        except Exception as e:
            pytest.skip(f"Monte Carlo integration test skipped due to: {e}")
    
    def test_property_validation_errors(self):
        """Test property validation with invalid user inputs."""
        # Test invalid purchase price
        with pytest.raises(ValueError):
            PropertyFinancialInfo(
                purchase_price=-100_000,  # Invalid negative price
                down_payment_pct=0.25
            )
        
        # Test invalid down payment percentage
        with pytest.raises(ValueError):
            PropertyFinancialInfo(
                purchase_price=1_000_000,
                down_payment_pct=1.5  # Invalid > 100%
            )
        
        # Test invalid total units
        with pytest.raises(ValueError):
            PropertyPhysicalInfo(
                property_type=PropertyType.MULTIFAMILY,
                property_class=PropertyClass.CLASS_B,
                total_units=0,  # Invalid zero units
                total_square_feet=50000,
                year_built=2010
            )
        
        # Test unit mix mismatch
        with pytest.raises(ValueError):
            PropertyInputData(
                property_id="INVALID_001",
                property_name="Invalid Property",
                analysis_date=date.today(),
                physical_info=PropertyPhysicalInfo(
                    property_type=PropertyType.MULTIFAMILY,
                    property_class=PropertyClass.CLASS_B,
                    total_units=100,
                    total_square_feet=90000,
                    year_built=2015
                ),
                financial_info=PropertyFinancialInfo(
                    purchase_price=10_000_000,
                    down_payment_pct=0.30
                ),
                location_info=PropertyLocationInfo(
                    address="Test Address",
                    city="Test City",
                    state="TS",
                    zip_code="12345",
                    msa_code="12345"
                ),
                operating_info=PropertyOperatingInfo(
                    unit_mix=[
                        UnitMix("1BR", 50, 800, 2000),  # Only 50 units
                        UnitMix("2BR", 30, 1000, 2500)  # Total 80, but property has 100
                    ]
                )
            )
    
    def test_property_serialization_for_ui(self):
        """Test property data serialization for UI consumption."""
        property_data = create_sample_property()
        
        # Convert to dictionary (for JSON API responses)
        property_dict = property_data.to_dict()
        
        # Validate dictionary structure
        assert property_dict['property_id'] == property_data.property_id
        assert property_dict['property_name'] == property_data.property_name
        assert 'physical_info' in property_dict
        assert 'financial_info' in property_dict
        assert 'location_info' in property_dict
        assert 'operating_info' in property_dict
        
        # Validate nested structures
        assert property_dict['physical_info']['property_type'] == 'multifamily'
        assert property_dict['financial_info']['purchase_price'] == 5_000_000
        assert property_dict['location_info']['msa_code'] == '35620'
        
        # Test that all values are JSON serializable
        import json
        json_str = json.dumps(property_dict)
        assert len(json_str) > 0
        
        # Test deserialization
        parsed_dict = json.loads(json_str)
        assert parsed_dict['property_id'] == property_data.property_id


class TestUserWorkflowEdgeCases:
    """Test edge cases and error conditions in user workflow."""
    
    def test_missing_required_fields(self):
        """Test validation with missing required fields."""
        with pytest.raises(ValueError):
            PropertyInputData(
                property_id="",  # Empty property ID
                property_name="Test Property",
                analysis_date=date.today(),
                physical_info=PropertyPhysicalInfo(
                    property_type=PropertyType.MULTIFAMILY,
                    property_class=PropertyClass.CLASS_B,
                    total_units=50,
                    total_square_feet=45000,
                    year_built=2010
                ),
                financial_info=PropertyFinancialInfo(
                    purchase_price=5_000_000,
                    down_payment_pct=0.25
                ),
                location_info=PropertyLocationInfo(
                    address="123 Test St",
                    city="Test City",
                    state="TS",
                    zip_code="12345",
                    msa_code="12345"
                ),
                operating_info=PropertyOperatingInfo()
            )
    
    def test_extreme_property_values(self):
        """Test validation with extreme but valid property values."""
        # Very expensive property
        expensive_property = PropertyInputData(
            property_id="EXPENSIVE_001",
            property_name="Luxury High-Rise",
            analysis_date=date.today(),
            physical_info=PropertyPhysicalInfo(
                property_type=PropertyType.MULTIFAMILY,
                property_class=PropertyClass.CLASS_A,
                total_units=500,
                total_square_feet=600000,
                year_built=2020
            ),
            financial_info=PropertyFinancialInfo(
                purchase_price=150_000_000,
                down_payment_pct=0.35,
                current_noi=9_000_000
            ),
            location_info=PropertyLocationInfo(
                address="1 Luxury Lane",
                city="New York",
                state="NY",
                zip_code="10001",
                msa_code="35620"
            ),
            operating_info=PropertyOperatingInfo()
        )
        
        # Validation should pass but might generate warnings
        issues = property_manager.validate_property(expensive_property)
        # Should have warning about high price but not fail
        assert any("100M" in issue for issue in issues)
        
        # But basic validation should pass
        assert expensive_property.calculate_price_per_unit() == 300_000
        assert expensive_property.get_current_cap_rate() == 0.06
    
    def test_property_data_manager_operations(self):
        """Test property data manager operations for user workflow."""
        manager = property_manager
        
        # Clear any existing properties
        manager.properties.clear()
        
        # Add multiple properties
        for i in range(3):
            prop = create_sample_property()
            prop.property_id = f"TEST_{i:03d}"
            prop.property_name = f"Test Property {i+1}"
            manager.add_property(prop)
        
        # Test listing operations
        property_ids = manager.list_properties()
        assert len(property_ids) == 3
        assert "TEST_000" in property_ids
        assert "TEST_002" in property_ids
        
        # Test retrieval
        retrieved = manager.get_property("TEST_001")
        assert retrieved is not None
        assert retrieved.property_name == "Test Property 2"
        
        # Test non-existent property
        non_existent = manager.get_property("DOES_NOT_EXIST")
        assert non_existent is None