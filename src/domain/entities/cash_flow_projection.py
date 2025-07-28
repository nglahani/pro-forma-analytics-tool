"""
Cash Flow Projection Domain Entity

Represents annual cash flow projections for Years 0-5 of the investment.
Corresponds to "Cash Flow Projections" section in Excel pro forma.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import date

from core.exceptions import ValidationError


@dataclass
class AnnualCashFlow:
    """
    Represents cash flow for a single year.
    """

    year: int

    # Income
    gross_rental_income: float = 0.0
    vacancy_loss: float = 0.0
    effective_gross_income: float = 0.0

    # Operating Expenses
    property_taxes: float = 0.0
    insurance: float = 0.0
    repairs_maintenance: float = 0.0
    property_management: float = 0.0
    admin_expenses: float = 0.0
    contracting: float = 0.0
    replacement_reserves: float = 0.0
    total_operating_expenses: float = 0.0

    # Net Operating Income
    net_operating_income: float = 0.0

    # Debt Service
    annual_debt_service: float = 0.0

    # Before-Tax Cash Flow
    before_tax_cash_flow: float = 0.0

    # Capital Expenditures (if any)
    capital_expenditures: float = 0.0

    # Net Cash Flow (available for distribution)
    net_cash_flow: float = 0.0

    def __post_init__(self):
        """Validate annual cash flow calculations."""
        self._validate_year()
        self._validate_income_calculations()
        self._validate_expense_calculations()
        self._validate_cash_flow_calculations()

    def _validate_year(self):
        """Validate year is in valid range."""
        if not (0 <= self.year <= 5):
            raise ValidationError(f"Year must be between 0-5, got {self.year}")

    def _validate_income_calculations(self):
        """Validate income calculations are consistent."""
        if self.gross_rental_income < 0:
            raise ValidationError("Gross rental income cannot be negative")
        if self.vacancy_loss < 0:
            raise ValidationError("Vacancy loss cannot be negative")

        # Check effective gross income calculation
        expected_egi = self.gross_rental_income - self.vacancy_loss
        if abs(self.effective_gross_income - expected_egi) > 0.01:
            raise ValidationError(
                f"Effective gross income ({self.effective_gross_income:,.2f}) "
                f"doesn't match calculation ({expected_egi:,.2f})"
            )

    def _validate_expense_calculations(self):
        """Validate operating expense calculations."""
        expense_components = [
            self.property_taxes,
            self.insurance,
            self.repairs_maintenance,
            self.property_management,
            self.admin_expenses,
            self.contracting,
            self.replacement_reserves,
        ]

        for expense in expense_components:
            if expense < 0:
                raise ValidationError("Operating expenses cannot be negative")

        expected_total = sum(expense_components)
        if abs(self.total_operating_expenses - expected_total) > 0.01:
            raise ValidationError(
                f"Total operating expenses ({self.total_operating_expenses:,.2f}) "
                f"doesn't match sum of components ({expected_total:,.2f})"
            )

    def _validate_cash_flow_calculations(self):
        """Validate cash flow calculations are consistent."""
        if self.annual_debt_service < 0:
            raise ValidationError("Annual debt service cannot be negative")
        if self.capital_expenditures < 0:
            raise ValidationError("Capital expenditures cannot be negative")

        # Check NOI calculation
        expected_noi = self.effective_gross_income - self.total_operating_expenses
        if abs(self.net_operating_income - expected_noi) > 0.01:
            raise ValidationError(
                f"Net operating income ({self.net_operating_income:,.2f}) "
                f"doesn't match calculation ({expected_noi:,.2f})"
            )

        # Check before-tax cash flow
        expected_btcf = self.net_operating_income - self.annual_debt_service
        if abs(self.before_tax_cash_flow - expected_btcf) > 0.01:
            raise ValidationError(
                f"Before-tax cash flow ({self.before_tax_cash_flow:,.2f}) "
                f"doesn't match calculation ({expected_btcf:,.2f})"
            )

        # Check net cash flow
        expected_ncf = self.before_tax_cash_flow - self.capital_expenditures
        if abs(self.net_cash_flow - expected_ncf) > 0.01:
            raise ValidationError(
                f"Net cash flow ({self.net_cash_flow:,.2f}) "
                f"doesn't match calculation ({expected_ncf:,.2f})"
            )


@dataclass
class WaterfallDistribution:
    """
    Represents waterfall distribution of cash flows.
    """

    year: int

    # Available cash for distribution
    available_cash: float = 0.0

    # Preferred return calculations
    investor_preferred_return_due: float = 0.0
    investor_preferred_return_paid: float = 0.0
    investor_preferred_return_accrued: float = 0.0
    cumulative_unpaid_preferred: float = 0.0

    # Cash distributions
    investor_cash_distribution: float = 0.0
    operator_cash_distribution: float = 0.0
    total_cash_distributed: float = 0.0

    # Remaining cash (if any)
    remaining_cash: float = 0.0

    def __post_init__(self):
        """Validate waterfall distribution calculations."""
        self._validate_year()
        self._validate_amounts()
        self._validate_distribution_calculations()

    def _validate_year(self):
        """Validate year is in valid range."""
        if not (0 <= self.year <= 5):
            raise ValidationError(f"Year must be between 0-5, got {self.year}")

    def _validate_amounts(self):
        """Validate all amounts are non-negative."""
        amounts = {
            "available_cash": self.available_cash,
            "investor_preferred_return_due": self.investor_preferred_return_due,
            "investor_preferred_return_paid": self.investor_preferred_return_paid,
            "investor_preferred_return_accrued": self.investor_preferred_return_accrued,
            "cumulative_unpaid_preferred": self.cumulative_unpaid_preferred,
            "investor_cash_distribution": self.investor_cash_distribution,
            "operator_cash_distribution": self.operator_cash_distribution,
            "total_cash_distributed": self.total_cash_distributed,
            "remaining_cash": self.remaining_cash,
        }

        for name, amount in amounts.items():
            if amount < -0.01:  # Allow for small floating point errors
                raise ValidationError(
                    f"Distribution amount '{name}' cannot be negative: {amount}"
                )

    def _validate_distribution_calculations(self):
        """Validate distribution calculations are consistent."""
        # Check total distribution
        expected_total = (
            self.investor_cash_distribution + self.operator_cash_distribution
        )
        if abs(self.total_cash_distributed - expected_total) > 0.01:
            raise ValidationError(
                f"Total distributed ({self.total_cash_distributed:,.2f}) "
                f"doesn't match sum ({expected_total:,.2f})"
            )

        # Check remaining cash
        expected_remaining = self.available_cash - self.total_cash_distributed
        if abs(self.remaining_cash - expected_remaining) > 0.01:
            raise ValidationError(
                f"Remaining cash ({self.remaining_cash:,.2f}) "
                f"doesn't match calculation ({expected_remaining:,.2f})"
            )


@dataclass
class CashFlowProjection:
    """
    Complete cash flow projection for property investment (Years 0-5).
    Corresponds to "Cash Flow Projections" section in Excel pro forma.
    """

    property_id: str
    scenario_id: str
    calculation_date: date = field(default_factory=date.today)

    # Annual cash flows (Year 0-5)
    annual_cash_flows: List[AnnualCashFlow] = field(default_factory=list)

    # Waterfall distributions (Year 0-5)
    waterfall_distributions: List[WaterfallDistribution] = field(default_factory=list)

    # Investment structure parameters
    investor_equity_share: float = 0.0
    preferred_return_rate: float = 0.0

    # Summary metrics
    total_gross_income: float = 0.0
    total_operating_expenses: float = 0.0
    total_noi: float = 0.0
    total_debt_service: float = 0.0
    total_before_tax_cash_flow: float = 0.0
    total_investor_distributions: float = 0.0
    total_operator_distributions: float = 0.0

    def __post_init__(self):
        """Validate cash flow projection after creation."""
        self._validate_identifiers()
        self._validate_investment_structure()
        self._validate_annual_cash_flows()
        self._validate_waterfall_distributions()
        self._calculate_summary_metrics()

    def _validate_identifiers(self):
        """Validate required identifiers."""
        if not self.property_id:
            raise ValidationError("Property ID is required")
        if not self.scenario_id:
            raise ValidationError("Scenario ID is required")

    def _validate_investment_structure(self):
        """Validate investment structure parameters."""
        if not (0.0 <= self.investor_equity_share <= 1.0):
            raise ValidationError("Investor equity share must be between 0% and 100%")
        if not (0.0 <= self.preferred_return_rate <= 0.25):
            raise ValidationError("Preferred return rate must be between 0% and 25%")

    def _validate_annual_cash_flows(self):
        """Validate annual cash flows are complete and sequential."""
        if len(self.annual_cash_flows) != 6:
            raise ValidationError("Must have exactly 6 annual cash flows (Years 0-5)")

        for i, cash_flow in enumerate(self.annual_cash_flows):
            if cash_flow.year != i:
                raise ValidationError(
                    f"Cash flow {i} has incorrect year {cash_flow.year}"
                )

    def _validate_waterfall_distributions(self):
        """Validate waterfall distributions are complete and sequential."""
        if len(self.waterfall_distributions) != 6:
            raise ValidationError(
                "Must have exactly 6 waterfall distributions (Years 0-5)"
            )

        for i, distribution in enumerate(self.waterfall_distributions):
            if distribution.year != i:
                raise ValidationError(
                    f"Distribution {i} has incorrect year {distribution.year}"
                )

    def _calculate_summary_metrics(self):
        """Calculate summary metrics from annual cash flows."""
        self.total_gross_income = sum(
            cf.gross_rental_income for cf in self.annual_cash_flows
        )
        self.total_operating_expenses = sum(
            cf.total_operating_expenses for cf in self.annual_cash_flows
        )
        self.total_noi = sum(cf.net_operating_income for cf in self.annual_cash_flows)
        self.total_debt_service = sum(
            cf.annual_debt_service for cf in self.annual_cash_flows
        )
        self.total_before_tax_cash_flow = sum(
            cf.before_tax_cash_flow for cf in self.annual_cash_flows
        )
        self.total_investor_distributions = sum(
            wd.investor_cash_distribution for wd in self.waterfall_distributions
        )
        self.total_operator_distributions = sum(
            wd.operator_cash_distribution for wd in self.waterfall_distributions
        )

    def get_cash_flow_by_year(self, year: int) -> Optional[AnnualCashFlow]:
        """Get cash flow for a specific year."""
        if not (0 <= year <= 5):
            return None
        return (
            self.annual_cash_flows[year] if year < len(self.annual_cash_flows) else None
        )

    def get_distribution_by_year(self, year: int) -> Optional[WaterfallDistribution]:
        """Get waterfall distribution for a specific year."""
        if not (0 <= year <= 5):
            return None
        return (
            self.waterfall_distributions[year]
            if year < len(self.waterfall_distributions)
            else None
        )

    def get_annual_summary(self) -> List[Dict[str, Any]]:
        """Get annual summary combining cash flows and distributions."""
        summary = []
        for year in range(6):
            cash_flow = self.get_cash_flow_by_year(year)
            distribution = self.get_distribution_by_year(year)

            if cash_flow and distribution:
                summary.append(
                    {
                        "year": year,
                        "gross_income": cash_flow.gross_rental_income,
                        "operating_expenses": cash_flow.total_operating_expenses,
                        "noi": cash_flow.net_operating_income,
                        "debt_service": cash_flow.annual_debt_service,
                        "before_tax_cash_flow": cash_flow.before_tax_cash_flow,
                        "investor_distribution": distribution.investor_cash_distribution,
                        "operator_distribution": distribution.operator_cash_distribution,
                        "cumulative_unpaid_preferred": distribution.cumulative_unpaid_preferred,
                    }
                )

        return summary

    def get_performance_metrics(self) -> Dict[str, float]:
        """Get key performance metrics from cash flow projection."""
        if not self.annual_cash_flows:
            return {}

        # Average metrics over operational years (Years 1-5)
        operational_years = self.annual_cash_flows[1:]  # Exclude Year 0

        avg_noi = sum(cf.net_operating_income for cf in operational_years) / len(
            operational_years
        )
        avg_cash_flow = sum(cf.before_tax_cash_flow for cf in operational_years) / len(
            operational_years
        )

        # Calculate expense ratios
        total_income = sum(cf.effective_gross_income for cf in operational_years)
        total_expenses = sum(cf.total_operating_expenses for cf in operational_years)
        avg_expense_ratio = total_expenses / total_income if total_income > 0 else 0

        return {
            "average_annual_noi": avg_noi,
            "average_annual_cash_flow": avg_cash_flow,
            "average_expense_ratio": avg_expense_ratio,
            "total_investor_distributions": self.total_investor_distributions,
            "total_operator_distributions": self.total_operator_distributions,
            "years_projected": len(self.annual_cash_flows),
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "property_id": self.property_id,
            "scenario_id": self.scenario_id,
            "calculation_date": self.calculation_date.isoformat(),
            "annual_cash_flows": [
                {
                    "year": cf.year,
                    "gross_rental_income": cf.gross_rental_income,
                    "vacancy_loss": cf.vacancy_loss,
                    "effective_gross_income": cf.effective_gross_income,
                    "property_taxes": cf.property_taxes,
                    "insurance": cf.insurance,
                    "repairs_maintenance": cf.repairs_maintenance,
                    "property_management": cf.property_management,
                    "admin_expenses": cf.admin_expenses,
                    "contracting": cf.contracting,
                    "replacement_reserves": cf.replacement_reserves,
                    "total_operating_expenses": cf.total_operating_expenses,
                    "net_operating_income": cf.net_operating_income,
                    "annual_debt_service": cf.annual_debt_service,
                    "before_tax_cash_flow": cf.before_tax_cash_flow,
                    "capital_expenditures": cf.capital_expenditures,
                    "net_cash_flow": cf.net_cash_flow,
                }
                for cf in self.annual_cash_flows
            ],
            "waterfall_distributions": [
                {
                    "year": wd.year,
                    "available_cash": wd.available_cash,
                    "investor_preferred_return_due": wd.investor_preferred_return_due,
                    "investor_preferred_return_paid": wd.investor_preferred_return_paid,
                    "investor_preferred_return_accrued": wd.investor_preferred_return_accrued,
                    "cumulative_unpaid_preferred": wd.cumulative_unpaid_preferred,
                    "investor_cash_distribution": wd.investor_cash_distribution,
                    "operator_cash_distribution": wd.operator_cash_distribution,
                    "total_cash_distributed": wd.total_cash_distributed,
                    "remaining_cash": wd.remaining_cash,
                }
                for wd in self.waterfall_distributions
            ],
            "investor_equity_share": self.investor_equity_share,
            "preferred_return_rate": self.preferred_return_rate,
            "summary_metrics": {
                "total_gross_income": self.total_gross_income,
                "total_noi": self.total_noi,
                "total_debt_service": self.total_debt_service,
                "total_investor_distributions": self.total_investor_distributions,
                "total_operator_distributions": self.total_operator_distributions,
            },
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CashFlowProjection":
        """Create from dictionary (deserialization)."""
        calculation_date = (
            date.fromisoformat(data["calculation_date"])
            if "calculation_date" in data
            else date.today()
        )

        # Reconstruct annual cash flows
        annual_cash_flows = []
        for cf_data in data.get("annual_cash_flows", []):
            annual_cash_flows.append(
                AnnualCashFlow(
                    year=cf_data["year"],
                    gross_rental_income=cf_data["gross_rental_income"],
                    vacancy_loss=cf_data["vacancy_loss"],
                    effective_gross_income=cf_data["effective_gross_income"],
                    property_taxes=cf_data["property_taxes"],
                    insurance=cf_data["insurance"],
                    repairs_maintenance=cf_data["repairs_maintenance"],
                    property_management=cf_data["property_management"],
                    admin_expenses=cf_data["admin_expenses"],
                    contracting=cf_data["contracting"],
                    replacement_reserves=cf_data["replacement_reserves"],
                    total_operating_expenses=cf_data["total_operating_expenses"],
                    net_operating_income=cf_data["net_operating_income"],
                    annual_debt_service=cf_data["annual_debt_service"],
                    before_tax_cash_flow=cf_data["before_tax_cash_flow"],
                    capital_expenditures=cf_data["capital_expenditures"],
                    net_cash_flow=cf_data["net_cash_flow"],
                )
            )

        # Reconstruct waterfall distributions
        waterfall_distributions = []
        for wd_data in data.get("waterfall_distributions", []):
            waterfall_distributions.append(
                WaterfallDistribution(
                    year=wd_data["year"],
                    available_cash=wd_data["available_cash"],
                    investor_preferred_return_due=wd_data[
                        "investor_preferred_return_due"
                    ],
                    investor_preferred_return_paid=wd_data[
                        "investor_preferred_return_paid"
                    ],
                    investor_preferred_return_accrued=wd_data[
                        "investor_preferred_return_accrued"
                    ],
                    cumulative_unpaid_preferred=wd_data["cumulative_unpaid_preferred"],
                    investor_cash_distribution=wd_data["investor_cash_distribution"],
                    operator_cash_distribution=wd_data["operator_cash_distribution"],
                    total_cash_distributed=wd_data["total_cash_distributed"],
                    remaining_cash=wd_data["remaining_cash"],
                )
            )

        return cls(
            property_id=data["property_id"],
            scenario_id=data["scenario_id"],
            calculation_date=calculation_date,
            annual_cash_flows=annual_cash_flows,
            waterfall_distributions=waterfall_distributions,
            investor_equity_share=data["investor_equity_share"],
            preferred_return_rate=data["preferred_return_rate"],
        )

    def __str__(self) -> str:
        """String representation for debugging."""
        return (
            f"CashFlowProjection(property={self.property_id}, scenario={self.scenario_id}, "
            f"total_noi=${self.total_noi:,.0f}, investor_distributions=${self.total_investor_distributions:,.0f})"
        )
