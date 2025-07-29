"""
Initial Numbers Service

Application service that calculates initial investment and acquisition costs
from property data and DCF assumptions.
"""

from datetime import date
from typing import Any, Dict, Optional

from config.dcf_constants import FINANCIAL_CONSTANTS, VALIDATION_CONSTANTS
from core.exceptions import ValidationError
from core.logging_config import get_logger
from src.domain.entities.dcf_assumptions import DCFAssumptions
from src.domain.entities.initial_numbers import InitialNumbers
from src.domain.entities.property_data import SimplifiedPropertyInput


class InitialNumbersService:
    """Service for calculating initial investment numbers."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def calculate_initial_numbers(
        self, property_data: SimplifiedPropertyInput, dcf_assumptions: DCFAssumptions
    ) -> InitialNumbers:
        """
        Calculate initial numbers from property data and DCF assumptions.

        Args:
            property_data: SimplifiedPropertyInput containing property details
            dcf_assumptions: DCFAssumptions containing market parameters

        Returns:
            InitialNumbers object with all acquisition calculations

        Raises:
            ValidationError: If required data is missing or calculations fail
        """
        try:
            self.logger.info(
                f"Calculating initial numbers for property {property_data.property_id}, "
                f"scenario {dcf_assumptions.scenario_id}"
            )

            # 1. Purchase Details Calculations
            purchase_price = self._get_purchase_price(property_data)
            closing_cost_amount = dcf_assumptions.calculate_closing_costs(
                purchase_price
            )
            renovation_capex = self._calculate_renovation_capex(property_data)
            cost_basis = purchase_price + closing_cost_amount + renovation_capex

            # 2. Financing Calculations
            loan_amount = dcf_assumptions.calculate_loan_amount(purchase_price)
            annual_interest_expense = self._calculate_annual_interest(
                loan_amount, dcf_assumptions
            )
            lender_reserves_amount = dcf_assumptions.calculate_lender_reserves(
                annual_interest_expense
            )

            # 3. Equity Requirements
            total_cash_required = self._calculate_total_cash_required(
                purchase_price,
                loan_amount,
                closing_cost_amount,
                renovation_capex,
                lender_reserves_amount,
            )
            investor_cash_required = (
                total_cash_required * dcf_assumptions.investor_equity_share
            )
            operator_cash_required = total_cash_required * (
                1 - dcf_assumptions.investor_equity_share
            )

            # 4. Income Structure
            income_calculations = self._calculate_income_structure(property_data)

            # 5. Operating Expenses
            expense_calculations = self._calculate_operating_expenses(
                property_data, income_calculations["post_renovation_annual_rent"]
            )

            # 6. Valuation Metrics
            after_repair_value = self._calculate_after_repair_value(
                cost_basis,
                income_calculations["post_renovation_annual_rent"],
                dcf_assumptions,
            )
            initial_cap_rate = self._calculate_initial_cap_rate(
                income_calculations["year_1_rental_income"],
                expense_calculations["total_operating_expenses"],
                purchase_price,
            )

            # Create InitialNumbers object
            initial_numbers = InitialNumbers(
                property_id=property_data.property_id,
                scenario_id=dcf_assumptions.scenario_id,
                # Purchase details
                purchase_price=purchase_price,
                closing_cost_amount=closing_cost_amount,
                renovation_capex=renovation_capex,
                cost_basis=cost_basis,
                # Financing
                loan_amount=loan_amount,
                annual_interest_expense=annual_interest_expense,
                lender_reserves_amount=lender_reserves_amount,
                # Equity requirements
                investor_cash_required=investor_cash_required,
                operator_cash_required=operator_cash_required,
                total_cash_required=total_cash_required,
                # Valuation
                after_repair_value=after_repair_value,
                initial_cap_rate=initial_cap_rate,
                # Income structure
                pre_renovation_annual_rent=income_calculations[
                    "pre_renovation_annual_rent"
                ],
                post_renovation_annual_rent=income_calculations[
                    "post_renovation_annual_rent"
                ],
                year_1_rental_income=income_calculations["year_1_rental_income"],
                # Operating expenses
                property_taxes=expense_calculations["property_taxes"],
                insurance=expense_calculations["insurance"],
                repairs_maintenance=expense_calculations["repairs_maintenance"],
                property_management=expense_calculations["property_management"],
                admin_expenses=expense_calculations["admin_expenses"],
                contracting=expense_calculations["contracting"],
                replacement_reserves=expense_calculations["replacement_reserves"],
                total_operating_expenses=expense_calculations[
                    "total_operating_expenses"
                ],
                # Investment structure
                investor_equity_share=dcf_assumptions.investor_equity_share,
                preferred_return_rate=dcf_assumptions.preferred_return_rate,
            )

            self.logger.info(
                f"Successfully calculated initial numbers: "
                f"Purchase ${purchase_price:,.0f}, Cash ${total_cash_required:,.0f}, "
                f"LTV {loan_amount/purchase_price:.1%}"
            )

            return initial_numbers

        except Exception as e:
            self.logger.error(f"Failed to calculate initial numbers: {str(e)}")
            raise ValidationError(
                f"Initial numbers calculation failed: {str(e)}"
            ) from e

    def _get_purchase_price(self, property_data: SimplifiedPropertyInput) -> float:
        """Get purchase price from property data."""
        if not property_data.purchase_price or property_data.purchase_price <= 0:
            raise ValidationError(
                "Property purchase price is required and must be positive"
            )
        return float(property_data.purchase_price)

    def _calculate_renovation_capex(
        self, property_data: SimplifiedPropertyInput
    ) -> float:
        """Calculate renovation capital expenditures."""
        # If renovation cost is specified, use it
        if (
            hasattr(property_data.renovation_info, "estimated_cost")
            and property_data.renovation_info.estimated_cost
        ):
            return float(property_data.renovation_info.estimated_cost)

        # Otherwise estimate based on renovation duration and property size
        renovation_months = (
            property_data.renovation_info.anticipated_duration_months or 0
        )
        if renovation_months == 0:
            return 0.0

        # Estimate: $10,000 per unit per month of renovation (rough approximation)
        total_units = property_data.residential_units.total_units
        if property_data.commercial_units:
            total_units += property_data.commercial_units.total_units

        estimated_capex = (
            total_units
            * FINANCIAL_CONSTANTS.RENOVATION_COST_PER_UNIT
            * (renovation_months / 12)
        )

        self.logger.info(
            f"Estimated renovation CapEx: ${estimated_capex:,.0f} "
            f"({total_units} units, {renovation_months} months)"
        )

        return estimated_capex

    def _calculate_annual_interest(
        self, loan_amount: float, dcf_assumptions: DCFAssumptions
    ) -> float:
        """Calculate annual interest expense using Year 1 mortgage rate."""
        if loan_amount == 0:
            return 0.0

        # Use Year 1 commercial mortgage rate for interest calculation
        year_1_rate = dcf_assumptions.commercial_mortgage_rate[1]
        return loan_amount * year_1_rate

    def _calculate_total_cash_required(
        self,
        purchase_price: float,
        loan_amount: float,
        closing_costs: float,
        renovation_capex: float,
        lender_reserves: float,
    ) -> float:
        """Calculate total cash required for acquisition."""
        down_payment = purchase_price - loan_amount
        total_cash = down_payment + closing_costs + renovation_capex + lender_reserves
        return total_cash

    def _calculate_income_structure(
        self, property_data: SimplifiedPropertyInput
    ) -> Dict[str, float]:
        """Calculate pre-renovation, post-renovation, and Year 1 income."""

        # Calculate monthly gross rent from units
        monthly_residential_rent = property_data.residential_units.monthly_gross_rent
        monthly_commercial_rent = (
            property_data.commercial_units.monthly_gross_rent
            if property_data.commercial_units
            else 0.0
        )
        monthly_total_rent = monthly_residential_rent + monthly_commercial_rent

        # Pre-renovation annual rent (assume current rent is pre-renovation)
        pre_renovation_annual_rent = monthly_total_rent * 12

        # Post-renovation annual rent (configurable increase percentage)
        post_renovation_multiplier = FINANCIAL_CONSTANTS.POST_RENOVATION_RENT_MULTIPLIER
        post_renovation_annual_rent = (
            pre_renovation_annual_rent * post_renovation_multiplier
        )

        # Year 1 rental income (adjusted for renovation period)
        renovation_months = (
            property_data.renovation_info.anticipated_duration_months or 0
        )
        # During renovation, assume no income. After renovation, full post-renovation rent
        year_1_rental_income = (
            post_renovation_annual_rent * (12 - renovation_months) / 12
        )

        self.logger.info(
            f"Income calculations: Pre-reno ${pre_renovation_annual_rent:,.0f}, "
            f"Post-reno ${post_renovation_annual_rent:,.0f}, "
            f"Year 1 ${year_1_rental_income:,.0f} ({renovation_months} month renovation)"
        )

        return {
            "pre_renovation_annual_rent": pre_renovation_annual_rent,
            "post_renovation_annual_rent": post_renovation_annual_rent,
            "year_1_rental_income": year_1_rental_income,
        }

    def _calculate_operating_expenses(
        self, property_data: SimplifiedPropertyInput, annual_rent: float
    ) -> Dict[str, float]:
        """Calculate operating expenses breakdown."""

        # Get total units for per-unit calculations
        total_units = property_data.residential_units.total_units
        if property_data.commercial_units:
            total_units += property_data.commercial_units.total_units

        # Operating expense estimates as percentages of gross rent
        # These could be made configurable or derived from market data
        expense_ratios = {
            "property_taxes": 0.12,  # 12% of gross rent
            "insurance": 0.02,  # 2% of gross rent
            "repairs_maintenance": 0.03,  # 3% of gross rent
            "property_management": 0.05,  # 5% of gross rent
            "admin_expenses": 0.01,  # 1% of gross rent
            "contracting": 0.02,  # 2% of gross rent
            "replacement_reserves": 0.015,  # 1.5% of gross rent
        }

        # Calculate expenses
        expenses = {}
        for category, ratio in expense_ratios.items():
            expenses[category] = annual_rent * ratio

        # Calculate total
        expenses["total_operating_expenses"] = sum(expenses.values())

        expense_ratio = (
            expenses["total_operating_expenses"] / annual_rent if annual_rent > 0 else 0
        )

        self.logger.info(
            f"Operating expenses: ${expenses['total_operating_expenses']:,.0f} "
            f"({expense_ratio:.1%} of gross rent)"
        )

        return expenses

    def _calculate_after_repair_value(
        self, cost_basis: float, annual_rent: float, dcf_assumptions: DCFAssumptions
    ) -> float:
        """Calculate after-repair value using Year 1 cap rate."""
        if annual_rent == 0:
            return cost_basis  # Fallback to cost basis

        # Use Year 1 cap rate for ARV calculation
        year_1_cap_rate = dcf_assumptions.cap_rate[1]

        # ARV = NOI / Cap Rate (simplified - using gross rent with configurable expense ratio)
        assumed_expense_ratio = FINANCIAL_CONSTANTS.DEFAULT_EXPENSE_RATIO
        estimated_noi = annual_rent * (1 - assumed_expense_ratio)
        arv = estimated_noi / year_1_cap_rate

        self.logger.info(
            f"After-repair value: ${arv:,.0f} "
            f"(NOI ${estimated_noi:,.0f} / Cap Rate {year_1_cap_rate:.1%})"
        )

        return arv

    def _calculate_initial_cap_rate(
        self, year_1_income: float, operating_expenses: float, purchase_price: float
    ) -> float:
        """Calculate initial cap rate based on Year 1 NOI."""
        if purchase_price == 0:
            return 0.0

        year_1_noi = year_1_income - operating_expenses
        initial_cap_rate = year_1_noi / purchase_price

        return max(0.0, initial_cap_rate)  # Ensure non-negative

    def get_calculation_summary(
        self, initial_numbers: InitialNumbers
    ) -> Dict[str, Any]:
        """Get summary of initial numbers calculations."""
        acquisition_summary = initial_numbers.get_acquisition_summary()
        equity_distribution = initial_numbers.get_equity_distribution()
        expense_breakdown = initial_numbers.get_operating_expense_breakdown()

        return {
            "property_id": initial_numbers.property_id,
            "scenario_id": initial_numbers.scenario_id,
            "acquisition": acquisition_summary,
            "equity": equity_distribution,
            "expenses": expense_breakdown,
            "key_metrics": {
                "ltv_ratio": acquisition_summary["ltv_ratio"],
                "initial_cap_rate": acquisition_summary["initial_cap_rate"],
                "cash_on_cash_return": acquisition_summary["year_1_cash_on_cash"],
                "debt_service_coverage": acquisition_summary["debt_service_coverage"],
            },
        }

    def validate_initial_numbers(self, initial_numbers: InitialNumbers) -> list:
        """Validate initial numbers for reasonableness."""
        issues = []

        try:
            # Check LTV ratio is reasonable
            ltv = initial_numbers.calculate_ltv_ratio()
            if ltv > 0.90:
                issues.append(f"High LTV ratio: {ltv:.1%}")
            elif ltv < 0.50:
                issues.append(f"Low LTV ratio: {ltv:.1%}")

            # Check debt service coverage
            dscr = initial_numbers.calculate_debt_service_coverage_ratio()
            if dscr < 1.2:
                issues.append(f"Low debt service coverage: {dscr:.2f}")

            # Check expense ratio
            if initial_numbers.post_renovation_annual_rent > 0:
                expense_ratio = (
                    initial_numbers.total_operating_expenses
                    / initial_numbers.post_renovation_annual_rent
                )
                if expense_ratio > 0.50:
                    issues.append(f"High expense ratio: {expense_ratio:.1%}")
                elif expense_ratio < 0.15:
                    issues.append(f"Low expense ratio: {expense_ratio:.1%}")

            # Check cash-on-cash return
            coc_return = initial_numbers.calculate_cash_on_cash_return()
            if coc_return < 0:
                issues.append(f"Negative cash-on-cash return: {coc_return:.1%}")
            elif coc_return > 0.20:
                issues.append(f"Unusually high cash-on-cash return: {coc_return:.1%}")

            # Check initial cap rate
            if initial_numbers.initial_cap_rate < 0.03:
                issues.append(
                    f"Low initial cap rate: {initial_numbers.initial_cap_rate:.1%}"
                )
            elif initial_numbers.initial_cap_rate > 0.15:
                issues.append(
                    f"High initial cap rate: {initial_numbers.initial_cap_rate:.1%}"
                )

        except Exception as e:
            issues.append(f"Validation error: {str(e)}")

        return issues


# Convenience function for easy usage
def calculate_initial_numbers(
    property_data: SimplifiedPropertyInput, dcf_assumptions: DCFAssumptions
) -> InitialNumbers:
    """Convenience function to calculate initial numbers."""
    service = InitialNumbersService()
    return service.calculate_initial_numbers(property_data, dcf_assumptions)
