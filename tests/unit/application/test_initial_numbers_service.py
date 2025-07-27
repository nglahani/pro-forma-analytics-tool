"""
Unit Tests for Initial Numbers Service

Tests the initial numbers calculation service following BDD/TDD principles.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import date

from src.application.services.initial_numbers_service import InitialNumbersService
from src.domain.entities.initial_numbers import InitialNumbers
from src.domain.entities.dcf_assumptions import DCFAssumptions
from src.domain.entities.property_data import SimplifiedPropertyInput, ResidentialUnits, InvestorEquityStructure, RenovationInfo, RenovationStatus
from core.exceptions import ValidationError


class TestInitialNumbersService:
    """Test cases for InitialNumbersService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return InitialNumbersService()
    
    @pytest.fixture
    def sample_property_data(self):
        """Sample property data for testing."""
        return SimplifiedPropertyInput(
            property_id="test_property_123",
            property_name="Test Investment Property",
            analysis_date=date.today(),
            purchase_price=1000000,
            city="New York",
            state="NY",
            msa_code="35620",
            residential_units=ResidentialUnits(
                total_units=10,
                average_rent_per_unit=1500
            ),
            equity_structure=InvestorEquityStructure(
                investor_equity_share_pct=80,
                self_cash_percentage=20
            ),
            renovation_info=RenovationInfo(
                status=RenovationStatus.PLANNED,
                anticipated_duration_months=6,
                estimated_cost=100000
            )
        )
    
    @pytest.fixture
    def sample_dcf_assumptions(self):
        """Sample DCF assumptions for testing."""
        return DCFAssumptions(
            scenario_id="test_scenario_001",
            msa_code="35620",
            property_id="test_property_123",
            commercial_mortgage_rate=[0.045, 0.047, 0.048, 0.049, 0.050, 0.051],
            treasury_10y_rate=[0.035, 0.036, 0.037, 0.038, 0.039, 0.040],
            fed_funds_rate=[0.025, 0.026, 0.027, 0.028, 0.029, 0.030],
            cap_rate=[0.055, 0.056, 0.057, 0.058, 0.059, 0.060],
            rent_growth_rate=[0.035, 0.038, 0.040, 0.042, 0.045, 0.048],
            expense_growth_rate=[0.025, 0.027, 0.028, 0.030, 0.032, 0.034],
            property_growth_rate=[0.040, 0.042, 0.045, 0.047, 0.050, 0.052],
            vacancy_rate=[0.050, 0.048, 0.045, 0.043, 0.040, 0.038],
            ltv_ratio=0.75,
            closing_cost_pct=0.025,
            lender_reserves_months=6.0,
            investor_equity_share=0.80,
            preferred_return_rate=0.06,
            self_cash_percentage=0.20
        )

    def test_calculate_initial_numbers_should_return_valid_initial_numbers(
        self, 
        service, 
        sample_property_data, 
        sample_dcf_assumptions
    ):
        """
        GIVEN valid property data and DCF assumptions
        WHEN calculating initial numbers
        THEN it should return valid InitialNumbers object
        """
        # Act
        result = service.calculate_initial_numbers(sample_property_data, sample_dcf_assumptions)
        
        # Assert
        assert isinstance(result, InitialNumbers)
        assert result.property_id == "test_property_123"
        assert result.scenario_id == "test_scenario_001"
        assert result.purchase_price == 1000000
        assert result.renovation_capex == 100000  # From estimated_cost
        assert result.loan_amount == 750000  # 75% LTV of $1M
        assert result.closing_cost_amount == 25000  # 2.5% of $1M
        assert result.cost_basis == 1125000  # $1M + $25K + $100K

    def test_calculate_initial_numbers_should_calculate_correct_equity_distribution(
        self, 
        service, 
        sample_property_data, 
        sample_dcf_assumptions
    ):
        """
        GIVEN property with 80/20 investor/operator split
        WHEN calculating initial numbers
        THEN it should correctly distribute equity requirements
        """
        # Act
        result = service.calculate_initial_numbers(sample_property_data, sample_dcf_assumptions)
        
        # Assert
        # Total cash = down payment + closing costs + renovation + lender reserves
        # Down payment = $1M - $750K = $250K
        # Closing costs = $25K, Renovation = $100K
        # Lender reserves = annual interest × months = ($750K × 4.7%) × 6/12 = ~$17.6K
        total_cash = result.total_cash_required
        assert total_cash > 390000  # Roughly $250K + $25K + $100K + $17K
        assert abs(result.investor_cash_required - total_cash * 0.80) < 1  # Allow rounding
        assert abs(result.operator_cash_required - total_cash * 0.20) < 1  # Allow rounding
        assert abs(result.investor_cash_required + result.operator_cash_required - total_cash) < 1  # Rounding

    def test_calculate_initial_numbers_should_handle_no_renovation_scenario(
        self, 
        service, 
        sample_property_data, 
        sample_dcf_assumptions
    ):
        """
        GIVEN property with no renovation planned
        WHEN calculating initial numbers
        THEN renovation CapEx should be zero
        """
        # Arrange
        no_renovation_property = sample_property_data
        no_renovation_property.renovation_info.status = RenovationStatus.NOT_NEEDED
        no_renovation_property.renovation_info.anticipated_duration_months = 0
        no_renovation_property.renovation_info.estimated_cost = None
        
        # Act
        result = service.calculate_initial_numbers(no_renovation_property, sample_dcf_assumptions)
        
        # Assert
        assert result.renovation_capex == 0

    def test_calculate_initial_numbers_should_estimate_renovation_cost_when_not_provided(
        self, 
        service, 
        sample_property_data, 
        sample_dcf_assumptions
    ):
        """
        GIVEN property with renovation duration but no estimated cost
        WHEN calculating initial numbers
        THEN it should estimate renovation cost based on units and duration
        """
        # Arrange - create a new property instance to avoid modifying the fixture
        property_no_cost = SimplifiedPropertyInput(
            property_id="test_property_456",
            property_name="Test Property No Cost",
            analysis_date=date.today(),
            purchase_price=1000000,
            city="New York",
            state="NY",
            msa_code="35620",
            residential_units=ResidentialUnits(
                total_units=10,
                average_rent_per_unit=1500
            ),
            equity_structure=InvestorEquityStructure(
                investor_equity_share_pct=80,
                self_cash_percentage=20
            ),
            renovation_info=RenovationInfo(
                status=RenovationStatus.PLANNED,
                anticipated_duration_months=12,
                estimated_cost=None  # No cost provided
            )
        )
        
        # Act
        result = service.calculate_initial_numbers(property_no_cost, sample_dcf_assumptions)
        
        # Assert
        # Should estimate based on units × cost per unit × (months/12)
        # 10 units × default cost per unit × 1 year = estimated amount
        assert result.renovation_capex > 0
        # Check that it's using the estimation formula (not zero, reasonable amount)
        assert 50000 <= result.renovation_capex <= 200000  # Reasonable range for 10 units

    def test_calculate_initial_numbers_with_missing_purchase_price_should_raise_validation_error(
        self, 
        service, 
        sample_property_data, 
        sample_dcf_assumptions
    ):
        """
        GIVEN property data without purchase price
        WHEN calculating initial numbers
        THEN it should raise ValidationError
        """
        # Arrange
        sample_property_data.purchase_price = None
        
        # Act & Assert
        with pytest.raises(ValidationError, match="Property purchase price is required"):
            service.calculate_initial_numbers(sample_property_data, sample_dcf_assumptions)

    def test_calculate_initial_numbers_with_zero_purchase_price_should_raise_validation_error(
        self, 
        service, 
        sample_property_data, 
        sample_dcf_assumptions
    ):
        """
        GIVEN property data with zero purchase price
        WHEN calculating initial numbers
        THEN it should raise ValidationError
        """
        # Arrange
        sample_property_data.purchase_price = 0
        
        # Act & Assert
        with pytest.raises(ValidationError, match="Property purchase price is required"):
            service.calculate_initial_numbers(sample_property_data, sample_dcf_assumptions)

    def test_calculate_income_structure_should_account_for_renovation_period(
        self, 
        service, 
        sample_property_data, 
        sample_dcf_assumptions
    ):
        """
        GIVEN property with 6-month renovation
        WHEN calculating initial numbers
        THEN Year 1 income should be reduced for renovation period
        """
        # Act
        result = service.calculate_initial_numbers(sample_property_data, sample_dcf_assumptions)
        
        # Assert
        # Post-renovation annual rent should be higher than pre-renovation
        assert result.post_renovation_annual_rent > result.pre_renovation_annual_rent
        
        # Year 1 income should be 6 months (50%) of post-renovation rent
        expected_year_1 = result.post_renovation_annual_rent * 0.5
        assert abs(result.year_1_rental_income - expected_year_1) < 1000  # Allow small rounding

    def test_calculate_operating_expenses_should_be_percentage_of_rent(
        self, 
        service, 
        sample_property_data, 
        sample_dcf_assumptions
    ):
        """
        GIVEN property data
        WHEN calculating initial numbers
        THEN operating expenses should be reasonable percentage of rent
        """
        # Act
        result = service.calculate_initial_numbers(sample_property_data, sample_dcf_assumptions)
        
        # Assert
        expense_ratio = result.total_operating_expenses / result.post_renovation_annual_rent
        assert 0.15 <= expense_ratio <= 0.50  # Reasonable expense ratio
        
        # Individual expense categories should be positive
        assert result.property_taxes > 0
        assert result.insurance > 0
        assert result.repairs_maintenance > 0
        assert result.property_management > 0

    def test_validate_initial_numbers_should_identify_high_ltv(
        self, 
        service, 
        sample_property_data, 
        sample_dcf_assumptions
    ):
        """
        GIVEN initial numbers with high LTV ratio
        WHEN validating initial numbers
        THEN it should flag high LTV as an issue
        """
        # Arrange
        high_ltv_assumptions = sample_dcf_assumptions
        high_ltv_assumptions.ltv_ratio = 0.95  # 95% LTV
        
        initial_numbers = service.calculate_initial_numbers(sample_property_data, high_ltv_assumptions)
        
        # Act
        issues = service.validate_initial_numbers(initial_numbers)
        
        # Assert
        assert len(issues) > 0
        assert any("High LTV ratio" in issue for issue in issues)

    def test_validate_initial_numbers_should_identify_low_dscr(
        self, 
        service, 
        sample_property_data, 
        sample_dcf_assumptions
    ):
        """
        GIVEN initial numbers with low debt service coverage
        WHEN validating initial numbers
        THEN it should flag low DSCR as an issue
        """
        # Arrange - create scenario with high mortgage rate to reduce DSCR
        high_rate_assumptions = sample_dcf_assumptions
        high_rate_assumptions.commercial_mortgage_rate = [0.15] * 6  # 15% rate
        
        initial_numbers = service.calculate_initial_numbers(sample_property_data, high_rate_assumptions)
        
        # Act
        issues = service.validate_initial_numbers(initial_numbers)
        
        # Assert
        assert len(issues) > 0
        assert any("debt service coverage" in issue for issue in issues)

    def test_get_calculation_summary_should_return_comprehensive_summary(
        self, 
        service, 
        sample_property_data, 
        sample_dcf_assumptions
    ):
        """
        GIVEN calculated initial numbers
        WHEN getting calculation summary
        THEN it should return dictionary with all key metrics
        """
        # Arrange
        initial_numbers = service.calculate_initial_numbers(sample_property_data, sample_dcf_assumptions)
        
        # Act
        summary = service.get_calculation_summary(initial_numbers)
        
        # Assert
        assert 'property_id' in summary
        assert 'scenario_id' in summary
        assert 'acquisition' in summary
        assert 'equity' in summary
        assert 'expenses' in summary
        assert 'key_metrics' in summary
        
        # Key metrics should include important ratios
        key_metrics = summary['key_metrics']
        assert 'ltv_ratio' in key_metrics
        assert 'initial_cap_rate' in key_metrics
        assert 'cash_on_cash_return' in key_metrics
        assert 'debt_service_coverage' in key_metrics

    def test_calculate_after_repair_value_should_use_cap_rate_valuation(
        self, 
        service, 
        sample_property_data, 
        sample_dcf_assumptions
    ):
        """
        GIVEN property with post-renovation income
        WHEN calculating initial numbers
        THEN ARV should be based on cap rate valuation
        """
        # Act
        result = service.calculate_initial_numbers(sample_property_data, sample_dcf_assumptions)
        
        # Assert
        # ARV should be significantly higher than purchase price for good deal
        assert result.after_repair_value > result.purchase_price
        
        # ARV should be calculated as NOI / Cap Rate
        # This should result in a reasonable valuation
        assert result.after_repair_value > 1000000  # Should be above purchase price
        assert result.after_repair_value < 3000000  # But not unreasonably high

    @patch('src.application.services.initial_numbers_service.get_logger')
    def test_calculate_initial_numbers_should_log_calculation_details(
        self, 
        mock_logger, 
        service, 
        sample_property_data, 
        sample_dcf_assumptions
    ):
        """
        GIVEN valid inputs
        WHEN calculating initial numbers
        THEN it should log calculation details
        """
        # Arrange
        mock_logger_instance = Mock()
        mock_logger.return_value = mock_logger_instance
        service.logger = mock_logger_instance
        
        # Act
        service.calculate_initial_numbers(sample_property_data, sample_dcf_assumptions)
        
        # Assert
        mock_logger_instance.info.assert_called()
        logged_messages = [call[0][0] for call in mock_logger_instance.info.call_args_list]
        assert any("Calculating initial numbers" in msg for msg in logged_messages)
        assert any("Successfully calculated initial numbers" in msg for msg in logged_messages)

    def test_calculate_initial_numbers_should_handle_commercial_units(
        self, 
        service, 
        sample_property_data, 
        sample_dcf_assumptions
    ):
        """
        GIVEN property with both residential and commercial units
        WHEN calculating initial numbers
        THEN it should include commercial rent in calculations
        """
        # Arrange
        from src.domain.entities.property_data import CommercialUnits
        sample_property_data.commercial_units = CommercialUnits(
            total_units=2,
            average_rent_per_unit=3000
        )
        
        # Act
        result = service.calculate_initial_numbers(sample_property_data, sample_dcf_assumptions)
        
        # Assert
        # Total rent should include both residential and commercial
        # Residential: 10 units × $1500 = $15,000/month = $180,000/year
        # Commercial: 2 units × $3000 = $6,000/month = $72,000/year
        # Total: $252,000/year pre-renovation
        expected_residential = 10 * 1500 * 12  # $180,000
        expected_commercial = 2 * 3000 * 12    # $72,000
        expected_total = expected_residential + expected_commercial  # $252,000
        
        assert abs(result.pre_renovation_annual_rent - expected_total) < 1000

    def test_calculate_initial_numbers_should_handle_error_gracefully(
        self, 
        service, 
        sample_property_data, 
        sample_dcf_assumptions
    ):
        """
        GIVEN invalid DCF assumptions that cause calculation error
        WHEN calculating initial numbers
        THEN it should raise ValidationError with meaningful message
        """
        # Arrange - create invalid assumptions
        invalid_assumptions = sample_dcf_assumptions
        invalid_assumptions.ltv_ratio = -1  # Invalid LTV
        
        # Act & Assert
        with pytest.raises(ValidationError, match="Initial numbers calculation failed"):
            service.calculate_initial_numbers(sample_property_data, invalid_assumptions)