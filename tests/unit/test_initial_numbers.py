"""
Unit tests for Initial Numbers functionality.

Tests the calculation of acquisition costs, financing, and initial investment numbers.
"""

import pytest
from datetime import date
from src.domain.entities.initial_numbers import InitialNumbers
from src.application.services.initial_numbers_service import InitialNumbersService
from src.domain.entities.dcf_assumptions import DCFAssumptions
from property_data import SimplifiedPropertyInput, ResidentialUnits, CommercialUnits, RenovationInfo, InvestorEquityStructure, RenovationStatus
from core.exceptions import ValidationError


class TestInitialNumbers:
    """Test Initial Numbers entity."""
    
    def test_initial_numbers_creation(self):
        """Test basic initial numbers creation."""
        initial_numbers = InitialNumbers(
            property_id="test_property_001",
            scenario_id="test_scenario_001",
            purchase_price=1000000,
            closing_cost_amount=50000,
            renovation_capex=100000,
            cost_basis=1150000,
            loan_amount=750000,
            annual_interest_expense=45000,
            lender_reserves_amount=11250,
            investor_cash_required=320000,
            operator_cash_required=80000,
            total_cash_required=400000,
            after_repair_value=1300000,
            initial_cap_rate=0.065,
            pre_renovation_annual_rent=80000,
            post_renovation_annual_rent=90000,
            year_1_rental_income=85000,
            property_taxes=10800,
            insurance=1800,
            repairs_maintenance=2700,
            property_management=4500,
            admin_expenses=900,
            contracting=1800,
            replacement_reserves=1350,
            total_operating_expenses=23850,
            investor_equity_share=0.80,
            preferred_return_rate=0.06
        )
        
        assert initial_numbers.property_id == "test_property_001"
        assert initial_numbers.purchase_price == 1000000
        assert initial_numbers.total_cash_required == 400000
        assert initial_numbers.investor_equity_share == 0.80
    
    def test_ltv_calculation(self):
        """Test LTV ratio calculation."""
        initial_numbers = InitialNumbers(
            property_id="test_property_001",
            scenario_id="test_scenario_001",
            purchase_price=1000000,
            closing_cost_amount=50000,
            renovation_capex=100000,
            cost_basis=1150000,
            loan_amount=800000,
            annual_interest_expense=48000,
            lender_reserves_amount=12000,
            investor_cash_required=320000,
            operator_cash_required=80000,
            total_cash_required=400000,
            after_repair_value=1300000,
            initial_cap_rate=0.065,
            pre_renovation_annual_rent=80000,
            post_renovation_annual_rent=90000,
            year_1_rental_income=85000,
            property_taxes=10800,
            insurance=1800,
            repairs_maintenance=2700,
            property_management=4500,
            admin_expenses=900,
            contracting=1800,
            replacement_reserves=1350,
            total_operating_expenses=23850,
            investor_equity_share=0.80,
            preferred_return_rate=0.06
        )
        
        ltv = initial_numbers.calculate_ltv_ratio()
        assert ltv == 0.80  # 800k / 1M
    
    def test_cash_on_cash_return(self):
        """Test cash-on-cash return calculation."""
        initial_numbers = InitialNumbers(
            property_id="test_property_001",
            scenario_id="test_scenario_001",
            purchase_price=1000000,
            closing_cost_amount=50000,
            renovation_capex=100000,
            cost_basis=1150000,
            loan_amount=750000,
            annual_interest_expense=45000,
            lender_reserves_amount=11250,
            investor_cash_required=320000,
            operator_cash_required=80000,
            total_cash_required=400000,
            after_repair_value=1300000,
            initial_cap_rate=0.065,
            pre_renovation_annual_rent=80000,
            post_renovation_annual_rent=90000,
            year_1_rental_income=85000,
            property_taxes=10800,
            insurance=1800,
            repairs_maintenance=2700,
            property_management=4500,
            admin_expenses=900,
            contracting=1800,
            replacement_reserves=1350,
            total_operating_expenses=23850,
            investor_equity_share=0.80,
            preferred_return_rate=0.06
        )
        
        coc_return = initial_numbers.calculate_cash_on_cash_return()
        # Year 1 NOI = 85000 - 23850 = 61150
        # Year 1 Cash Flow = 61150 - 45000 = 16150
        # Cash-on-Cash = 16150 / 400000 = 0.040375
        expected_coc = 16150 / 400000
        assert abs(coc_return - expected_coc) < 0.001
    
    def test_debt_service_coverage(self):
        """Test debt service coverage ratio calculation."""
        initial_numbers = InitialNumbers(
            property_id="test_property_001",
            scenario_id="test_scenario_001",
            purchase_price=1000000,
            closing_cost_amount=50000,
            renovation_capex=100000,
            cost_basis=1150000,
            loan_amount=750000,
            annual_interest_expense=45000,
            lender_reserves_amount=11250,
            investor_cash_required=320000,
            operator_cash_required=80000,
            total_cash_required=400000,
            after_repair_value=1300000,
            initial_cap_rate=0.065,
            pre_renovation_annual_rent=80000,
            post_renovation_annual_rent=90000,
            year_1_rental_income=85000,
            property_taxes=10800,
            insurance=1800,
            repairs_maintenance=2700,
            property_management=4500,
            admin_expenses=900,
            contracting=1800,
            replacement_reserves=1350,
            total_operating_expenses=23850,
            investor_equity_share=0.80,
            preferred_return_rate=0.06
        )
        
        dscr = initial_numbers.calculate_debt_service_coverage_ratio()
        # Year 1 NOI = 85000 - 23850 = 61150
        # DSCR = 61150 / 45000 = 1.359
        expected_dscr = 61150 / 45000
        assert abs(dscr - expected_dscr) < 0.001
    
    def test_validation_errors(self):
        """Test validation of invalid initial numbers."""
        with pytest.raises(ValidationError):
            # Invalid purchase price
            InitialNumbers(
                property_id="test_property_001",
                scenario_id="test_scenario_001",
                purchase_price=0,  # Invalid: must be positive
                closing_cost_amount=50000,
                renovation_capex=100000,
                cost_basis=1150000,
                loan_amount=750000,
                annual_interest_expense=45000,
                lender_reserves_amount=11250,
                investor_cash_required=320000,
                operator_cash_required=80000,
                total_cash_required=400000,
                after_repair_value=1300000,
                initial_cap_rate=0.065,
                pre_renovation_annual_rent=80000,
                post_renovation_annual_rent=90000,
                year_1_rental_income=85000,
                property_taxes=10800,
                insurance=1800,
                repairs_maintenance=2700,
                property_management=4500,
                admin_expenses=900,
                contracting=1800,
                replacement_reserves=1350,
                total_operating_expenses=23850,
                investor_equity_share=0.80,
                preferred_return_rate=0.06
            )
    
    def test_cost_basis_validation(self):
        """Test cost basis calculation validation."""
        with pytest.raises(ValidationError):
            # Cost basis doesn't match purchase + closing + renovation
            InitialNumbers(
                property_id="test_property_001",
                scenario_id="test_scenario_001",
                purchase_price=1000000,
                closing_cost_amount=50000,
                renovation_capex=100000,
                cost_basis=2000000,  # Invalid: doesn't match calculation
                loan_amount=750000,
                annual_interest_expense=45000,
                lender_reserves_amount=11250,
                investor_cash_required=320000,
                operator_cash_required=80000,
                total_cash_required=400000,
                after_repair_value=1300000,
                initial_cap_rate=0.065,
                pre_renovation_annual_rent=80000,
                post_renovation_annual_rent=90000,
                year_1_rental_income=85000,
                property_taxes=10800,
                insurance=1800,
                repairs_maintenance=2700,
                property_management=4500,
                admin_expenses=900,
                contracting=1800,
                replacement_reserves=1350,
                total_operating_expenses=23850,
                investor_equity_share=0.80,
                preferred_return_rate=0.06
            )
    
    def test_serialization(self):
        """Test to_dict and from_dict serialization."""
        original = InitialNumbers(
            property_id="test_property_001",
            scenario_id="test_scenario_001",
            purchase_price=1000000,
            closing_cost_amount=50000,
            renovation_capex=100000,
            cost_basis=1150000,
            loan_amount=750000,
            annual_interest_expense=45000,
            lender_reserves_amount=11250,
            investor_cash_required=320000,
            operator_cash_required=80000,
            total_cash_required=400000,
            after_repair_value=1300000,
            initial_cap_rate=0.065,
            pre_renovation_annual_rent=80000,
            post_renovation_annual_rent=90000,
            year_1_rental_income=85000,
            property_taxes=10800,
            insurance=1800,
            repairs_maintenance=2700,
            property_management=4500,
            admin_expenses=900,
            contracting=1800,
            replacement_reserves=1350,
            total_operating_expenses=23850,
            investor_equity_share=0.80,
            preferred_return_rate=0.06
        )
        
        # Serialize
        data_dict = original.to_dict()
        
        # Deserialize
        restored = InitialNumbers.from_dict(data_dict)
        
        assert restored.property_id == original.property_id
        assert restored.purchase_price == original.purchase_price
        assert restored.total_cash_required == original.total_cash_required


class TestInitialNumbersService:
    """Test Initial Numbers Service."""
    
    def create_sample_property(self) -> SimplifiedPropertyInput:
        """Create sample property for testing."""
        return SimplifiedPropertyInput(
            property_id="TEST_PROP_001",
            property_name="Test Property",
            analysis_date=date.today(),
            residential_units=ResidentialUnits(
                total_units=10,
                average_rent_per_unit=3000
            ),
            commercial_units=CommercialUnits(
                total_units=2,
                average_rent_per_unit=5000
            ),
            renovation_info=RenovationInfo(
                status=RenovationStatus.PLANNED,
                anticipated_duration_months=6,
                estimated_cost=150000
            ),
            equity_structure=InvestorEquityStructure(
                investor_equity_share_pct=75.0,
                self_cash_percentage=30.0
            ),
            city="New York",
            state="NY",
            msa_code="35620",
            purchase_price=2000000
        )
    
    def create_sample_dcf_assumptions(self) -> DCFAssumptions:
        """Create sample DCF assumptions for testing."""
        return DCFAssumptions(
            scenario_id="test_scenario_001",
            msa_code="35620",
            property_id="TEST_PROP_001",
            commercial_mortgage_rate=[0.06, 0.065, 0.067, 0.069, 0.071, 0.073],
            treasury_10y_rate=[0.04, 0.042, 0.044, 0.046, 0.048, 0.050],
            fed_funds_rate=[0.02, 0.025, 0.03, 0.032, 0.034, 0.036],
            cap_rate=[0.07, 0.07, 0.07, 0.07, 0.07, 0.065],
            rent_growth_rate=[0.0, 0.03, 0.032, 0.029, 0.031, 0.028],
            expense_growth_rate=[0.0, 0.02, 0.025, 0.022, 0.024, 0.021],
            property_growth_rate=[0.0, 0.02, 0.025, 0.018, 0.022, 0.019],
            vacancy_rate=[0.0, 0.05, 0.04, 0.06, 0.045, 0.05],
            ltv_ratio=0.75,
            closing_cost_pct=0.05,
            lender_reserves_months=3.0,
            investor_equity_share=0.75,
            preferred_return_rate=0.06,
            self_cash_percentage=0.30
        )
    
    def test_calculate_initial_numbers(self):
        """Test calculating initial numbers from property data and DCF assumptions."""
        service = InitialNumbersService()
        property_data = self.create_sample_property()
        dcf_assumptions = self.create_sample_dcf_assumptions()
        
        initial_numbers = service.calculate_initial_numbers(property_data, dcf_assumptions)
        
        assert initial_numbers.property_id == "TEST_PROP_001"
        assert initial_numbers.scenario_id == "test_scenario_001"
        assert initial_numbers.purchase_price == 2000000
        assert initial_numbers.loan_amount == 1500000  # 75% LTV
        assert initial_numbers.closing_cost_amount == 100000  # 5% of purchase price
        assert initial_numbers.renovation_capex == 150000  # From property data
        assert initial_numbers.cost_basis == 2250000  # 2M + 100K + 150K
    
    def test_income_calculations(self):
        """Test income structure calculations."""
        service = InitialNumbersService()
        property_data = self.create_sample_property()
        dcf_assumptions = self.create_sample_dcf_assumptions()
        
        initial_numbers = service.calculate_initial_numbers(property_data, dcf_assumptions)
        
        # Monthly rent: (10 * 3000) + (2 * 5000) = 40,000
        # Pre-renovation annual: 40,000 * 12 = 480,000
        expected_pre_reno = 480000
        assert initial_numbers.pre_renovation_annual_rent == expected_pre_reno
        
        # Post-renovation: 480,000 * 1.125 = 540,000
        expected_post_reno = 540000
        assert initial_numbers.post_renovation_annual_rent == expected_post_reno
        
        # Year 1 with 6 months renovation: 540,000 * (12-6)/12 = 270,000
        expected_year_1 = 270000
        assert initial_numbers.year_1_rental_income == expected_year_1
    
    def test_operating_expense_calculations(self):
        """Test operating expense calculations."""
        service = InitialNumbersService()
        property_data = self.create_sample_property()
        dcf_assumptions = self.create_sample_dcf_assumptions()
        
        initial_numbers = service.calculate_initial_numbers(property_data, dcf_assumptions)
        
        # Should be calculated as percentages of post-renovation annual rent
        post_reno_rent = 540000
        
        # Total should be around 26.5% of gross rent (based on actual ratios in service)
        expected_total_expenses = post_reno_rent * 0.265
        assert abs(initial_numbers.total_operating_expenses - expected_total_expenses) < 1000
        
        # Check individual components exist and are positive
        assert initial_numbers.property_taxes > 0
        assert initial_numbers.insurance > 0
        assert initial_numbers.property_management > 0
    
    def test_equity_distribution(self):
        """Test equity distribution calculations."""
        service = InitialNumbersService()
        property_data = self.create_sample_property()
        dcf_assumptions = self.create_sample_dcf_assumptions()
        
        initial_numbers = service.calculate_initial_numbers(property_data, dcf_assumptions)
        
        # Check equity distribution
        total_cash = initial_numbers.total_cash_required
        investor_cash = initial_numbers.investor_cash_required
        operator_cash = initial_numbers.operator_cash_required
        
        # Should add up to total
        assert abs((investor_cash + operator_cash) - total_cash) < 0.01
        
        # Investor should have 75% of equity
        expected_investor_cash = total_cash * 0.75
        assert abs(investor_cash - expected_investor_cash) < 0.01
    
    def test_validation_functionality(self):
        """Test validation of calculated initial numbers."""
        service = InitialNumbersService()
        property_data = self.create_sample_property()
        dcf_assumptions = self.create_sample_dcf_assumptions()
        
        initial_numbers = service.calculate_initial_numbers(property_data, dcf_assumptions)
        issues = service.validate_initial_numbers(initial_numbers)
        
        # Should have no major validation issues for reasonable inputs
        major_issues = [issue for issue in issues if 'error' in issue.lower() or 'negative' in issue.lower()]
        assert len(major_issues) == 0
    
    def test_calculation_summary(self):
        """Test getting calculation summary."""
        service = InitialNumbersService()
        property_data = self.create_sample_property()
        dcf_assumptions = self.create_sample_dcf_assumptions()
        
        initial_numbers = service.calculate_initial_numbers(property_data, dcf_assumptions)
        summary = service.get_calculation_summary(initial_numbers)
        
        assert 'property_id' in summary
        assert 'acquisition' in summary
        assert 'equity' in summary
        assert 'expenses' in summary
        assert 'key_metrics' in summary
        
        # Check key metrics are present
        assert 'ltv_ratio' in summary['key_metrics']
        assert 'initial_cap_rate' in summary['key_metrics']
        assert 'cash_on_cash_return' in summary['key_metrics']
    
    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        service = InitialNumbersService()
        property_data = self.create_sample_property()
        dcf_assumptions = self.create_sample_dcf_assumptions()
        
        # Test with invalid purchase price
        property_data.purchase_price = 0
        
        with pytest.raises(ValidationError):
            service.calculate_initial_numbers(property_data, dcf_assumptions)