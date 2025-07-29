"""
Cash Flow Projection Service

Application service that calculates Years 0-5 cash flow projections
from DCF assumptions and initial numbers.
"""

from typing import Any, Dict, List

from core.exceptions import ValidationError
from core.logging_config import get_logger
from src.domain.entities.cash_flow_projection import (
    AnnualCashFlow,
    CashFlowProjection,
    WaterfallDistribution,
)
from src.domain.entities.dcf_assumptions import DCFAssumptions
from src.domain.entities.initial_numbers import InitialNumbers


class CashFlowProjectionService:
    """Service for calculating cash flow projections and waterfall distributions."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def calculate_cash_flow_projection(
        self, dcf_assumptions: DCFAssumptions, initial_numbers: InitialNumbers
    ) -> CashFlowProjection:
        """
        Calculate complete cash flow projection from DCF assumptions and initial numbers.

        Args:
            dcf_assumptions: DCFAssumptions containing market parameters
            initial_numbers: InitialNumbers containing acquisition details

        Returns:
            CashFlowProjection object with Years 0-5 projections

        Raises:
            ValidationError: If calculations fail or inputs are invalid
        """
        try:
            self.logger.info(
                f"Calculating cash flow projection for property {initial_numbers.property_id}, "
                f"scenario {dcf_assumptions.scenario_id}"
            )

            # Calculate annual cash flows for Years 0-5
            annual_cash_flows = []
            for year in range(6):
                cash_flow = self._calculate_annual_cash_flow(
                    year, dcf_assumptions, initial_numbers
                )
                annual_cash_flows.append(cash_flow)

            # Calculate waterfall distributions for Years 0-5
            waterfall_distributions = []
            cumulative_unpaid_preferred = 0.0

            for year in range(6):
                distribution, cumulative_unpaid_preferred = (
                    self._calculate_waterfall_distribution(
                        year,
                        annual_cash_flows[year],
                        dcf_assumptions,
                        initial_numbers,
                        cumulative_unpaid_preferred,
                    )
                )
                waterfall_distributions.append(distribution)

            # Create cash flow projection
            cash_flow_projection = CashFlowProjection(
                property_id=initial_numbers.property_id,
                scenario_id=dcf_assumptions.scenario_id,
                annual_cash_flows=annual_cash_flows,
                waterfall_distributions=waterfall_distributions,
                investor_equity_share=dcf_assumptions.investor_equity_share,
                preferred_return_rate=dcf_assumptions.preferred_return_rate,
            )

            self.logger.info(
                f"Successfully calculated cash flow projection: "
                f"Total NOI ${cash_flow_projection.total_noi:,.0f}, "
                f"Investor distributions ${cash_flow_projection.total_investor_distributions:,.0f}"
            )

            return cash_flow_projection

        except Exception as e:
            self.logger.error(f"Failed to calculate cash flow projection: {str(e)}")
            raise ValidationError(
                f"Cash flow projection calculation failed: {str(e)}"
            ) from e

    def _calculate_annual_cash_flow(
        self,
        year: int,
        dcf_assumptions: DCFAssumptions,
        initial_numbers: InitialNumbers,
    ) -> AnnualCashFlow:
        """Calculate cash flow for a specific year."""

        # Get year-specific assumptions
        year_assumptions = dcf_assumptions.get_year_assumptions(year)

        # Calculate gross rental income
        if year == 0:
            # Year 0: No income during acquisition/renovation
            gross_rental_income = 0.0
        else:
            # Years 1-5: Apply rent growth from previous year
            base_rent = initial_numbers.post_renovation_annual_rent
            if year == 1:
                # Year 1: Use the pre-calculated year 1 income (accounts for renovation period)
                gross_rental_income = initial_numbers.year_1_rental_income
                # Convert to full-year equivalent by adjusting for non-renovation period
                renovation_months = getattr(initial_numbers, "renovation_months", 0)
                if (
                    hasattr(initial_numbers, "pre_renovation_annual_rent")
                    and initial_numbers.pre_renovation_annual_rent > 0
                ):
                    # Estimate renovation months from the year 1 calculation
                    renovation_months = 12 - (
                        initial_numbers.year_1_rental_income
                        / initial_numbers.post_renovation_annual_rent
                        * 12
                    )
                    renovation_months = max(0, min(12, renovation_months))

                # Apply rent growth to get full year
                rent_growth_rate = year_assumptions["rent_growth_rate"]
                if renovation_months < 12:  # If there was renovation
                    gross_rental_income = base_rent * (1 + rent_growth_rate)
            else:
                # Years 2-5: Compound rent growth from Year 1 base
                year_1_base = initial_numbers.post_renovation_annual_rent
                rent_growth_compound = 1.0
                for y in range(1, year + 1):
                    year_growth = dcf_assumptions.get_year_assumptions(y)[
                        "rent_growth_rate"
                    ]
                    rent_growth_compound *= 1 + year_growth
                gross_rental_income = year_1_base * rent_growth_compound

        # Calculate vacancy loss
        vacancy_rate = year_assumptions["vacancy_rate"]
        vacancy_loss = gross_rental_income * vacancy_rate

        # Calculate effective gross income
        effective_gross_income = gross_rental_income - vacancy_loss

        # Calculate operating expenses with growth
        if year == 0:
            # Year 0: No operating expenses
            operating_expenses = {
                "property_taxes": 0.0,
                "insurance": 0.0,
                "repairs_maintenance": 0.0,
                "property_management": 0.0,
                "admin_expenses": 0.0,
                "contracting": 0.0,
                "replacement_reserves": 0.0,
            }
        else:
            # Years 1-5: Apply expense growth
            expense_growth_compound = 1.0
            for y in range(1, year + 1):
                year_growth = dcf_assumptions.get_year_assumptions(y)[
                    "expense_growth_rate"
                ]
                expense_growth_compound *= 1 + year_growth

            operating_expenses = {
                "property_taxes": initial_numbers.property_taxes
                * expense_growth_compound,
                "insurance": initial_numbers.insurance * expense_growth_compound,
                "repairs_maintenance": initial_numbers.repairs_maintenance
                * expense_growth_compound,
                "property_management": initial_numbers.property_management
                * expense_growth_compound,
                "admin_expenses": initial_numbers.admin_expenses
                * expense_growth_compound,
                "contracting": initial_numbers.contracting * expense_growth_compound,
                "replacement_reserves": initial_numbers.replacement_reserves
                * expense_growth_compound,
            }

        total_operating_expenses = sum(operating_expenses.values())

        # Calculate net operating income
        net_operating_income = effective_gross_income - total_operating_expenses

        # Calculate annual debt service
        if year == 0:
            annual_debt_service = 0.0
        else:
            annual_debt_service = initial_numbers.annual_interest_expense

        # Calculate before-tax cash flow
        before_tax_cash_flow = net_operating_income - annual_debt_service

        # Calculate capital expenditures
        if year == 0:
            # Year 0: Initial renovation CapEx
            capital_expenditures = initial_numbers.renovation_capex
        else:
            # Years 1-5: Assume minimal ongoing CapEx (already in replacement reserves)
            capital_expenditures = 0.0

        # Calculate net cash flow
        net_cash_flow = before_tax_cash_flow - capital_expenditures

        return AnnualCashFlow(
            year=year,
            gross_rental_income=gross_rental_income,
            vacancy_loss=vacancy_loss,
            effective_gross_income=effective_gross_income,
            property_taxes=operating_expenses["property_taxes"],
            insurance=operating_expenses["insurance"],
            repairs_maintenance=operating_expenses["repairs_maintenance"],
            property_management=operating_expenses["property_management"],
            admin_expenses=operating_expenses["admin_expenses"],
            contracting=operating_expenses["contracting"],
            replacement_reserves=operating_expenses["replacement_reserves"],
            total_operating_expenses=total_operating_expenses,
            net_operating_income=net_operating_income,
            annual_debt_service=annual_debt_service,
            before_tax_cash_flow=before_tax_cash_flow,
            capital_expenditures=capital_expenditures,
            net_cash_flow=net_cash_flow,
        )

    def _calculate_waterfall_distribution(
        self,
        year: int,
        annual_cash_flow: AnnualCashFlow,
        dcf_assumptions: DCFAssumptions,
        initial_numbers: InitialNumbers,
        cumulative_unpaid_preferred: float,
    ) -> tuple[WaterfallDistribution, float]:
        """Calculate waterfall distribution for a specific year."""

        # Available cash for distribution (cannot be negative)
        available_cash = max(0.0, annual_cash_flow.net_cash_flow)

        # Calculate preferred return due for this year
        investor_cash_invested = initial_numbers.investor_cash_required
        preferred_return_rate = dcf_assumptions.preferred_return_rate

        if year == 0:
            # Year 0: No preferred return due during acquisition/renovation
            investor_preferred_return_due = 0.0
        else:
            # Years 1-5: Annual preferred return
            investor_preferred_return_due = (
                investor_cash_invested * preferred_return_rate
            )

        # Add any unpaid preferred return from previous years
        total_preferred_due = (
            investor_preferred_return_due + cumulative_unpaid_preferred
        )

        # Calculate how much preferred return can be paid
        investor_preferred_return_paid = min(available_cash, total_preferred_due)

        # Calculate remaining unpaid preferred (cannot be negative)
        investor_preferred_return_accrued = max(
            0.0, investor_preferred_return_due - investor_preferred_return_paid
        )
        new_cumulative_unpaid_preferred = max(
            0.0,
            cumulative_unpaid_preferred
            + investor_preferred_return_due
            - investor_preferred_return_paid,
        )

        # Calculate remaining cash after preferred return
        remaining_after_preferred = available_cash - investor_preferred_return_paid

        # Distribute remaining cash according to equity shares
        if remaining_after_preferred > 0:
            investor_equity_distribution = (
                remaining_after_preferred * dcf_assumptions.investor_equity_share
            )
            operator_equity_distribution = remaining_after_preferred * (
                1 - dcf_assumptions.investor_equity_share
            )
        else:
            investor_equity_distribution = 0.0
            operator_equity_distribution = 0.0

        # Total distributions
        investor_cash_distribution = (
            investor_preferred_return_paid + investor_equity_distribution
        )
        operator_cash_distribution = operator_equity_distribution
        total_cash_distributed = investor_cash_distribution + operator_cash_distribution

        # Remaining cash (should be 0 in normal cases, clean up floating point errors)
        remaining_cash = available_cash - total_cash_distributed
        if abs(remaining_cash) < 0.01:
            remaining_cash = 0.0

        distribution = WaterfallDistribution(
            year=year,
            available_cash=available_cash,
            investor_preferred_return_due=investor_preferred_return_due,
            investor_preferred_return_paid=investor_preferred_return_paid,
            investor_preferred_return_accrued=investor_preferred_return_accrued,
            cumulative_unpaid_preferred=new_cumulative_unpaid_preferred,
            investor_cash_distribution=investor_cash_distribution,
            operator_cash_distribution=operator_cash_distribution,
            total_cash_distributed=total_cash_distributed,
            remaining_cash=remaining_cash,
        )

        return distribution, new_cumulative_unpaid_preferred

    def get_projection_summary(self, projection: CashFlowProjection) -> Dict[str, Any]:
        """Get summary of cash flow projection for reporting."""
        annual_summary = projection.get_annual_summary()
        performance_metrics = projection.get_performance_metrics()

        return {
            "property_id": projection.property_id,
            "scenario_id": projection.scenario_id,
            "investment_structure": {
                "investor_equity_share": projection.investor_equity_share,
                "preferred_return_rate": projection.preferred_return_rate,
            },
            "annual_summary": annual_summary,
            "performance_metrics": performance_metrics,
            "key_totals": {
                "total_gross_income": projection.total_gross_income,
                "total_noi": projection.total_noi,
                "total_debt_service": projection.total_debt_service,
                "total_investor_distributions": projection.total_investor_distributions,
                "total_operator_distributions": projection.total_operator_distributions,
            },
        }

    def validate_cash_flow_projection(
        self, projection: CashFlowProjection
    ) -> List[str]:
        """Validate cash flow projection for reasonableness."""
        issues = []

        try:
            # Check for negative NOI in operational years
            for year in range(1, 6):
                cash_flow = projection.get_cash_flow_by_year(year)
                if cash_flow and cash_flow.net_operating_income < 0:
                    issues.append(
                        f"Negative NOI in Year {year}: ${cash_flow.net_operating_income:,.0f}"
                    )

            # Check for extremely high expense ratios
            performance_metrics = projection.get_performance_metrics()
            if performance_metrics.get("average_expense_ratio", 0) > 0.6:
                issues.append(
                    f"High expense ratio: {performance_metrics['average_expense_ratio']:.1%}"
                )

            # Check for unpaid preferred returns
            final_distribution = projection.get_distribution_by_year(5)
            if (
                final_distribution
                and final_distribution.cumulative_unpaid_preferred > 1000
            ):
                issues.append(
                    f"Significant unpaid preferred return: ${final_distribution.cumulative_unpaid_preferred:,.0f}"
                )

            # Check for reasonable cash flow growth
            year_1_cf = projection.get_cash_flow_by_year(1)
            year_5_cf = projection.get_cash_flow_by_year(5)
            if year_1_cf and year_5_cf and year_1_cf.net_operating_income > 0:
                noi_growth = (
                    year_5_cf.net_operating_income / year_1_cf.net_operating_income
                ) - 1
                if noi_growth > 1.0:  # More than 100% growth
                    issues.append(f"Extreme NOI growth over 5 years: {noi_growth:.1%}")
                elif noi_growth < -0.5:  # More than 50% decline
                    issues.append(
                        f"Significant NOI decline over 5 years: {noi_growth:.1%}"
                    )

        except Exception as e:
            issues.append(f"Validation error: {str(e)}")

        return issues

    def calculate_annual_returns(
        self, projection: CashFlowProjection
    ) -> Dict[int, Dict[str, float]]:
        """Calculate annual returns for each year."""
        annual_returns = {}

        for year in range(1, 6):  # Years 1-5
            cash_flow = projection.get_cash_flow_by_year(year)
            distribution = projection.get_distribution_by_year(year)

            if cash_flow and distribution:
                # Calculate returns based on initial investment
                # Note: This is simplified - full IRR calculation would be in Phase 4
                annual_returns[year] = {
                    "noi": cash_flow.net_operating_income,
                    "before_tax_cash_flow": cash_flow.before_tax_cash_flow,
                    "investor_distribution": distribution.investor_cash_distribution,
                    "operator_distribution": distribution.operator_cash_distribution,
                    "unpaid_preferred": distribution.cumulative_unpaid_preferred,
                }

        return annual_returns


# Convenience function for easy usage
def calculate_cash_flow_projection(
    dcf_assumptions: DCFAssumptions, initial_numbers: InitialNumbers
) -> CashFlowProjection:
    """Convenience function to calculate cash flow projection."""
    service = CashFlowProjectionService()
    return service.calculate_cash_flow_projection(dcf_assumptions, initial_numbers)
