"""
Complete DCF Workflow Integration Tests

End-to-end testing of the entire DCF engine workflow:
Monte Carlo Scenarios → DCF Assumptions → Initial Numbers → Cash Flow → Financial Metrics

This validates that all 4 phases work together correctly and produce
realistic real estate investment analysis results.
"""

import pytest
import sys
from pathlib import Path
from datetime import date
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.application.services.dcf_assumptions_service import DCFAssumptionsService
from src.application.services.initial_numbers_service import InitialNumbersService
from src.application.services.cash_flow_projection_service import CashFlowProjectionService
from src.application.services.financial_metrics_service import FinancialMetricsService
from src.domain.entities.financial_metrics import InvestmentRecommendation, RiskLevel
from src.domain.entities.property_data import SimplifiedPropertyInput, ResidentialUnits, CommercialUnits, RenovationInfo, InvestorEquityStructure, RenovationStatus


class TestCompleteDCFWorkflow:
    """Integration tests for complete DCF workflow."""
    
    def setup_method(self):
        """Setup test fixtures and services."""
        # Initialize all 4 DCF services
        self.dcf_service = DCFAssumptionsService()
        self.initial_numbers_service = InitialNumbersService()
        self.cash_flow_service = CashFlowProjectionService()
        self.financial_metrics_service = FinancialMetricsService()
        
        # Create test property data
        self.test_property = self._create_test_property()
        
        # Create test market scenarios
        self.market_scenarios = self._create_market_scenarios()
    
    def _create_test_property(self) -> SimplifiedPropertyInput:
        """Create a standardized test property for integration testing."""
        return SimplifiedPropertyInput(
            property_id="INTEGRATION_TEST_001",
            property_name="Integration Test Property - Mid-Size Mixed Use",
            analysis_date=date.today(),
            residential_units=ResidentialUnits(
                total_units=15,
                average_rent_per_unit=3500  # $3,500/month per unit
            ),
            commercial_units=CommercialUnits(
                total_units=3,
                average_rent_per_unit=6000  # $6,000/month per unit
            ),
            renovation_info=RenovationInfo(
                status=RenovationStatus.PLANNED,
                anticipated_duration_months=4,
                estimated_cost=300000  # $300k renovation
            ),
            equity_structure=InvestorEquityStructure(
                investor_equity_share_pct=75.0,  # Investor gets 75%
                self_cash_percentage=30.0        # 30% cash down
            ),
            city="Chicago",
            state="IL",
            msa_code="16980",  # Chicago MSA
            purchase_price=4500000  # $4.5M purchase price
        )
    
    def _create_market_scenarios(self) -> List[Dict[str, Any]]:
        """Create realistic market scenarios for testing."""
        
        # Conservative scenario
        conservative_scenario = {
            'scenario_id': 'CONSERVATIVE_TEST_2024',
            'forecasted_parameters': {
                'commercial_mortgage_rate': [0.075, 0.077, 0.079, 0.081, 0.083, 0.085],
                'treasury_10y': [0.045, 0.047, 0.049, 0.051, 0.053, 0.055],
                'fed_funds_rate': [0.030, 0.032, 0.034, 0.036, 0.038, 0.040],
                'cap_rate': [0.070, 0.070, 0.070, 0.070, 0.070, 0.070],
                'rent_growth': [0.0, 0.025, 0.028, 0.022, 0.025, 0.020],
                'expense_growth': [0.0, 0.030, 0.025, 0.028, 0.025, 0.027],
                'property_growth': [0.0, 0.020, 0.025, 0.018, 0.022, 0.015],
                'vacancy_rate': [0.0, 0.055, 0.050, 0.060, 0.055, 0.058],
                'ltv_ratio': [0.70, 0.70, 0.70, 0.70, 0.70, 0.70],
                'closing_cost_pct': [0.055, 0.055, 0.055, 0.055, 0.055, 0.055],
                'lender_reserves': [3.5, 3.5, 3.5, 3.5, 3.5, 3.5]
            }
        }
        
        # Optimistic scenario
        optimistic_scenario = {
            'scenario_id': 'OPTIMISTIC_TEST_2024',
            'forecasted_parameters': {
                'commercial_mortgage_rate': [0.055, 0.057, 0.059, 0.058, 0.056, 0.055],
                'treasury_10y': [0.035, 0.037, 0.039, 0.038, 0.036, 0.035],
                'fed_funds_rate': [0.020, 0.022, 0.024, 0.023, 0.021, 0.020],
                'cap_rate': [0.065, 0.065, 0.063, 0.061, 0.059, 0.057],
                'rent_growth': [0.0, 0.055, 0.048, 0.052, 0.045, 0.042],
                'expense_growth': [0.0, 0.020, 0.018, 0.022, 0.019, 0.021],
                'property_growth': [0.0, 0.045, 0.038, 0.042, 0.035, 0.032],
                'vacancy_rate': [0.0, 0.030, 0.025, 0.035, 0.028, 0.032],
                'ltv_ratio': [0.75, 0.75, 0.75, 0.75, 0.75, 0.75],
                'closing_cost_pct': [0.045, 0.045, 0.045, 0.045, 0.045, 0.045],
                'lender_reserves': [2.5, 2.5, 2.5, 2.5, 2.5, 2.5]
            }
        }
        
        return [conservative_scenario, optimistic_scenario]\n    \n    def test_complete_dcf_workflow_single_scenario(self):\n        \"\"\"Test complete DCF workflow for a single market scenario.\"\"\"\n        scenario = self.market_scenarios[0]  # Conservative scenario\n        \n        # Phase 1: DCF Assumptions\n        dcf_assumptions = self.dcf_service.create_dcf_assumptions_from_scenario(\n            scenario, self.test_property\n        )\n        \n        # Validate DCF assumptions\n        assert dcf_assumptions.property_id == \"INTEGRATION_TEST_001\"\n        assert dcf_assumptions.scenario_id == \"CONSERVATIVE_TEST_2024\"\n        assert len(dcf_assumptions.commercial_mortgage_rate) == 6  # Years 0-5\n        assert all(0.05 < rate < 0.15 for rate in dcf_assumptions.commercial_mortgage_rate)\n        assert dcf_assumptions.investor_equity_share == 0.75\n        \n        # Phase 2: Initial Numbers\n        initial_numbers = self.initial_numbers_service.calculate_initial_numbers(\n            self.test_property, dcf_assumptions\n        )\n        \n        # Validate initial numbers\n        assert initial_numbers.property_id == \"INTEGRATION_TEST_001\"\n        assert initial_numbers.purchase_price == 4500000\n        assert initial_numbers.total_cash_required > 0\n        assert 0.5 < initial_numbers.calculate_ltv_ratio() < 0.8  # Reasonable LTV\n        assert initial_numbers.year_1_rental_income > 0\n        assert initial_numbers.post_renovation_annual_rent > initial_numbers.pre_renovation_annual_rent\n        \n        # Phase 3: Cash Flow Projections\n        cash_flow_projection = self.cash_flow_service.calculate_cash_flow_projection(\n            dcf_assumptions, initial_numbers\n        )\n        \n        # Validate cash flow projections\n        assert cash_flow_projection.property_id == \"INTEGRATION_TEST_001\"\n        assert len(cash_flow_projection.annual_cash_flows) == 6  # Years 0-5\n        assert len(cash_flow_projection.waterfall_distributions) == 6\n        \n        # Validate Year 0 (renovation year)\n        year_0_cf = cash_flow_projection.get_cash_flow_by_year(0)\n        assert year_0_cf.gross_rental_income == 0  # No income during renovation\n        assert year_0_cf.capital_expenditures > 0  # Renovation costs\n        \n        # Validate operational years (1-5)\n        for year in range(1, 6):\n            year_cf = cash_flow_projection.get_cash_flow_by_year(year)\n            assert year_cf.gross_rental_income > 0\n            assert year_cf.net_operating_income > 0\n            assert year_cf.annual_debt_service > 0\n            \n            # Waterfall distribution validation\n            distribution = cash_flow_projection.get_distribution_by_year(year)\n            assert distribution.available_cash >= 0\n            assert distribution.total_cash_distributed <= distribution.available_cash + 0.01  # Allow small rounding\n        \n        # Phase 4: Financial Metrics\n        financial_metrics = self.financial_metrics_service.calculate_financial_metrics(\n            cash_flow_projection, dcf_assumptions, initial_numbers, discount_rate=0.10\n        )\n        \n        # Validate financial metrics\n        assert financial_metrics.property_id == \"INTEGRATION_TEST_001\"\n        assert financial_metrics.scenario_id == \"CONSERVATIVE_TEST_2024\"\n        assert financial_metrics.initial_investment > 0\n        assert isinstance(financial_metrics.net_present_value, float)\n        assert -1.0 < financial_metrics.internal_rate_return < 5.0  # Reasonable IRR range\n        assert financial_metrics.equity_multiple > 0\n        assert financial_metrics.payback_period_years > 0\n        assert isinstance(financial_metrics.investment_recommendation, InvestmentRecommendation)\n        assert isinstance(financial_metrics.risk_level, RiskLevel)\n        assert financial_metrics.terminal_value is not None\n        assert financial_metrics.terminal_value.net_sale_proceeds > 0\n        \n        print(f\"\\n✅ Single Scenario Integration Test Results:\")\n        print(f\"   NPV: ${financial_metrics.net_present_value:,.0f}\")\n        print(f\"   IRR: {financial_metrics.internal_rate_return:.1%}\")\n        print(f\"   Multiple: {financial_metrics.equity_multiple:.2f}x\")\n        print(f\"   Recommendation: {financial_metrics.investment_recommendation.value}\")\n        print(f\"   Risk Level: {financial_metrics.risk_level.value}\")\n    \n    def test_complete_dcf_workflow_multiple_scenarios(self):\n        \"\"\"Test complete DCF workflow with multiple market scenarios.\"\"\"\n        results = []\n        \n        for scenario in self.market_scenarios:\n            # Run complete workflow for each scenario\n            dcf_assumptions = self.dcf_service.create_dcf_assumptions_from_scenario(\n                scenario, self.test_property\n            )\n            \n            initial_numbers = self.initial_numbers_service.calculate_initial_numbers(\n                self.test_property, dcf_assumptions\n            )\n            \n            cash_flow_projection = self.cash_flow_service.calculate_cash_flow_projection(\n                dcf_assumptions, initial_numbers\n            )\n            \n            financial_metrics = self.financial_metrics_service.calculate_financial_metrics(\n                cash_flow_projection, dcf_assumptions, initial_numbers, discount_rate=0.10\n            )\n            \n            results.append({\n                'scenario_id': scenario['scenario_id'],\n                'financial_metrics': financial_metrics,\n                'cash_flow_projection': cash_flow_projection,\n                'initial_numbers': initial_numbers\n            })\n        \n        # Validate we have results for all scenarios\n        assert len(results) == len(self.market_scenarios)\n        \n        # Compare scenarios\n        conservative_result = next(r for r in results if 'CONSERVATIVE' in r['scenario_id'])\n        optimistic_result = next(r for r in results if 'OPTIMISTIC' in r['scenario_id'])\n        \n        conservative_metrics = conservative_result['financial_metrics']\n        optimistic_metrics = optimistic_result['financial_metrics']\n        \n        # Optimistic scenario should generally perform better\n        assert optimistic_metrics.net_present_value >= conservative_metrics.net_present_value\n        assert optimistic_metrics.internal_rate_return >= conservative_metrics.internal_rate_return\n        assert optimistic_metrics.equity_multiple >= conservative_metrics.equity_multiple\n        \n        # Use scenario comparison service\n        comparison = self.financial_metrics_service.compare_scenarios([\n            conservative_metrics, optimistic_metrics\n        ])\n        \n        assert comparison['scenario_count'] == 2\n        assert 'best_npv_scenario' in comparison\n        assert 'best_irr_scenario' in comparison\n        assert 'summary_statistics' in comparison\n        \n        print(f\"\\n✅ Multiple Scenario Integration Test Results:\")\n        print(f\"   Conservative NPV: ${conservative_metrics.net_present_value:,.0f}\")\n        print(f\"   Optimistic NPV: ${optimistic_metrics.net_present_value:,.0f}\")\n        print(f\"   Conservative IRR: {conservative_metrics.internal_rate_return:.1%}\")\n        print(f\"   Optimistic IRR: {optimistic_metrics.internal_rate_return:.1%}\")\n        print(f\"   Best NPV Scenario: {comparison['best_npv_scenario']['scenario_id']}\")\n        print(f\"   Best IRR Scenario: {comparison['best_irr_scenario']['scenario_id']}\")\n    \n    def test_dcf_workflow_data_consistency(self):\n        \"\"\"Test that data flows consistently through all DCF phases.\"\"\"\n        scenario = self.market_scenarios[1]  # Optimistic scenario\n        \n        # Run complete workflow\n        dcf_assumptions = self.dcf_service.create_dcf_assumptions_from_scenario(\n            scenario, self.test_property\n        )\n        \n        initial_numbers = self.initial_numbers_service.calculate_initial_numbers(\n            self.test_property, dcf_assumptions\n        )\n        \n        cash_flow_projection = self.cash_flow_service.calculate_cash_flow_projection(\n            dcf_assumptions, initial_numbers\n        )\n        \n        financial_metrics = self.financial_metrics_service.calculate_financial_metrics(\n            cash_flow_projection, dcf_assumptions, initial_numbers, discount_rate=0.10\n        )\n        \n        # Test data consistency across phases\n        \n        # Property ID consistency\n        assert dcf_assumptions.property_id == self.test_property.property_id\n        assert initial_numbers.property_id == self.test_property.property_id\n        assert cash_flow_projection.property_id == self.test_property.property_id\n        assert financial_metrics.property_id == self.test_property.property_id\n        \n        # Scenario ID consistency\n        assert dcf_assumptions.scenario_id == scenario['scenario_id']\n        assert initial_numbers.scenario_id == scenario['scenario_id']\n        assert cash_flow_projection.scenario_id == scenario['scenario_id']\n        assert financial_metrics.scenario_id == scenario['scenario_id']\n        \n        # Financial data consistency\n        assert initial_numbers.purchase_price == self.test_property.purchase_price\n        assert financial_metrics.initial_investment == initial_numbers.total_cash_required\n        \n        # Cash flow consistency\n        total_distributions = sum(d.total_cash_distributed \n                                for d in cash_flow_projection.waterfall_distributions \n                                if d.year > 0)\n        assert abs(financial_metrics.total_distributions - total_distributions) < 1.0  # Allow rounding\n        \n        print(f\"\\n✅ Data Consistency Validation Passed\")\n        print(f\"   Property ID consistent across all phases\")\n        print(f\"   Scenario ID consistent across all phases\")\n        print(f\"   Financial calculations align between phases\")\n    \n    def test_dcf_workflow_business_logic_validation(self):\n        \"\"\"Test that DCF workflow produces realistic real estate business results.\"\"\"\n        scenario = self.market_scenarios[0]  # Conservative scenario\n        \n        # Run complete workflow\n        dcf_assumptions = self.dcf_service.create_dcf_assumptions_from_scenario(\n            scenario, self.test_property\n        )\n        \n        initial_numbers = self.initial_numbers_service.calculate_initial_numbers(\n            self.test_property, dcf_assumptions\n        )\n        \n        cash_flow_projection = self.cash_flow_service.calculate_cash_flow_projection(\n            dcf_assumptions, initial_numbers\n        )\n        \n        financial_metrics = self.financial_metrics_service.calculate_financial_metrics(\n            cash_flow_projection, dcf_assumptions, initial_numbers, discount_rate=0.10\n        )\n        \n        # Business logic validation\n        \n        # 1. Reasonable property valuation\n        arv = initial_numbers.after_repair_value\n        purchase_price = initial_numbers.purchase_price\n        assert arv > purchase_price, \"After-repair value should exceed purchase price\"\n        assert arv < purchase_price * 2.5, \"After-repair value shouldn't be more than 2.5x purchase price\"\n        \n        # 2. Reasonable leverage\n        ltv = initial_numbers.calculate_ltv_ratio()\n        assert 0.4 < ltv < 0.9, f\"LTV ratio should be reasonable: {ltv:.1%} not in 40-90% range\"\n        \n        # 3. Positive cash flow in operational years\n        for year in range(1, 6):\n            year_cf = cash_flow_projection.get_cash_flow_by_year(year)\n            assert year_cf.net_operating_income > 0, f\"Year {year} should have positive NOI\"\n            assert year_cf.net_operating_income > year_cf.annual_debt_service, f\"Year {year} NOI should cover debt service\"\n        \n        # 4. Debt service coverage ratios\n        avg_dscr = financial_metrics.debt_service_coverage_avg\n        assert avg_dscr > 1.0, f\"Average DSCR should be > 1.0, got {avg_dscr:.2f}\"\n        \n        # 5. Reasonable investment returns\n        if financial_metrics.internal_rate_return > 0:\n            assert 0.02 < financial_metrics.internal_rate_return < 1.0, f\"IRR should be reasonable: {financial_metrics.internal_rate_return:.1%}\"\n        \n        # 6. Terminal value makes sense\n        terminal_value = financial_metrics.terminal_value\n        assert terminal_value.gross_property_value > 0\n        assert terminal_value.net_sale_proceeds > 0\n        assert terminal_value.selling_costs_amount > 0\n        assert terminal_value.net_sale_proceeds < terminal_value.gross_property_value\n        \n        # 7. Break-even analysis is reasonable\n        break_even = financial_metrics.break_even_analysis\n        if break_even:\n            assert 0.5 < break_even.get('break_even_occupancy_rate', 0.7) < 1.0\n            assert break_even.get('break_even_monthly_rent_per_unit', 0) > 0\n        \n        print(f\"\\n✅ Business Logic Validation Passed\")\n        print(f\"   ARV/Purchase Ratio: {arv/purchase_price:.2f}x\")\n        print(f\"   LTV Ratio: {ltv:.1%}\")\n        print(f\"   Average DSCR: {avg_dscr:.2f}x\")\n        print(f\"   Terminal Value: ${terminal_value.net_sale_proceeds:,.0f}\")\n        print(f\"   Break-even Occupancy: {break_even.get('break_even_occupancy_rate', 0):.1%}\")\n    \n    def test_dcf_workflow_error_handling(self):\n        \"\"\"Test DCF workflow handles edge cases and invalid inputs gracefully.\"\"\"\n        \n        # Test with invalid scenario data\n        invalid_scenario = {\n            'scenario_id': 'INVALID_TEST',\n            'forecasted_parameters': {\n                'commercial_mortgage_rate': [0.05, 0.06],  # Wrong length\n                'treasury_10y': [0.03, 0.04, 0.05, 0.06, 0.07, 0.08],\n                'fed_funds_rate': [0.02, 0.03, 0.04, 0.05, 0.06, 0.07],\n                # Missing required parameters\n            }\n        }\n        \n        # This should handle missing parameters gracefully\n        try:\n            dcf_assumptions = self.dcf_service.create_dcf_assumptions_from_scenario(\n                invalid_scenario, self.test_property\n            )\n            # If it succeeds, validate it filled missing data appropriately\n            assert len(dcf_assumptions.commercial_mortgage_rate) == 6\n        except Exception as e:\n            # Should be a validation error, not a system crash\n            assert \"validation\" in str(e).lower() or \"parameter\" in str(e).lower()\n        \n        print(f\"\\n✅ Error Handling Validation Passed\")\n        print(f\"   Invalid inputs handled gracefully\")\n        print(f\"   Validation errors are informative\")\n\n\nif __name__ == \"__main__\":\n    # Run integration tests directly for development\n    import logging\n    logging.basicConfig(level=logging.INFO)\n    \n    test_suite = TestCompleteDCFWorkflow()\n    test_suite.setup_method()\n    \n    print(\"\\n\" + \"=\" * 80)\n    print(\"COMPLETE DCF WORKFLOW INTEGRATION TESTS\")\n    print(\"=\" * 80)\n    \n    try:\n        test_suite.test_complete_dcf_workflow_single_scenario()\n        test_suite.test_complete_dcf_workflow_multiple_scenarios()\n        test_suite.test_dcf_workflow_data_consistency()\n        test_suite.test_dcf_workflow_business_logic_validation()\n        test_suite.test_dcf_workflow_error_handling()\n        \n        print(f\"\\n\" + \"=\" * 80)\n        print(\"[SUCCESS] ALL INTEGRATION TESTS PASSED\")\n        print(\"The complete DCF workflow is functioning correctly!\")\n        print(\"=\" * 80)
        
    except Exception as e:
        print(f"\n[ERROR] Integration test failed: {str(e)}")
        raise