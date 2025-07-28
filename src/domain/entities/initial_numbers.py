"""
Initial Numbers Domain Entity

Represents property acquisition and initial investment calculations.
Corresponds to "Initial Numbers" section in Excel pro forma.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import date

from core.exceptions import ValidationError


@dataclass
class InitialNumbers:
    """
    Property acquisition and initial investment calculations.
    Corresponds to "Initial Numbers" section in Excel pro forma.
    """

    property_id: str
    scenario_id: str
    calculation_date: date = field(default_factory=date.today)

    # Purchase Details
    purchase_price: float = 0.0
    closing_cost_amount: float = 0.0
    renovation_capex: float = 0.0
    cost_basis: float = 0.0

    # Financing Calculations
    loan_amount: float = 0.0
    annual_interest_expense: float = 0.0
    lender_reserves_amount: float = 0.0

    # Equity Requirements
    investor_cash_required: float = 0.0
    operator_cash_required: float = 0.0
    total_cash_required: float = 0.0

    # Valuation Metrics
    after_repair_value: float = 0.0
    initial_cap_rate: float = 0.0

    # Income Structure
    pre_renovation_annual_rent: float = 0.0
    post_renovation_annual_rent: float = 0.0
    year_1_rental_income: float = 0.0  # Adjusted for renovation period

    # Operating Expenses (Year 1 baseline)
    property_taxes: float = 0.0
    insurance: float = 0.0
    repairs_maintenance: float = 0.0
    property_management: float = 0.0
    admin_expenses: float = 0.0
    contracting: float = 0.0
    replacement_reserves: float = 0.0
    total_operating_expenses: float = 0.0

    # Investment Structure
    investor_equity_share: float = 0.0
    preferred_return_rate: float = 0.0

    def __post_init__(self):
        """Validate initial numbers after creation."""
        self._validate_identifiers()
        self._validate_purchase_details()
        self._validate_financing()
        self._validate_equity_structure()
        self._validate_income_structure()
        self._validate_operating_expenses()

    def _validate_identifiers(self):
        """Validate required identifiers."""
        if not self.property_id:
            raise ValidationError("Property ID is required")
        if not self.scenario_id:
            raise ValidationError("Scenario ID is required")

    def _validate_purchase_details(self):
        """Validate purchase and acquisition details."""
        if self.purchase_price <= 0:
            raise ValidationError("Purchase price must be positive")
        if self.closing_cost_amount < 0:
            raise ValidationError("Closing costs cannot be negative")
        if self.renovation_capex < 0:
            raise ValidationError("Renovation CapEx cannot be negative")
        if self.cost_basis <= 0:
            raise ValidationError("Cost basis must be positive")

        # Verify cost basis calculation
        expected_cost_basis = (
            self.purchase_price + self.closing_cost_amount + self.renovation_capex
        )
        if abs(self.cost_basis - expected_cost_basis) > 0.01:
            raise ValidationError(
                f"Cost basis ({self.cost_basis:,.2f}) doesn't match "
                f"expected calculation ({expected_cost_basis:,.2f})"
            )

    def _validate_financing(self):
        """Validate financing calculations."""
        if self.loan_amount < 0:
            raise ValidationError("Loan amount cannot be negative")
        if self.loan_amount > self.purchase_price:
            raise ValidationError("Loan amount cannot exceed purchase price")
        if self.annual_interest_expense < 0:
            raise ValidationError("Annual interest expense cannot be negative")
        if self.lender_reserves_amount < 0:
            raise ValidationError("Lender reserves cannot be negative")

    def _validate_equity_structure(self):
        """Validate equity requirements and structure."""
        if self.total_cash_required <= 0:
            raise ValidationError("Total cash required must be positive")
        if self.investor_cash_required < 0:
            raise ValidationError("Investor cash cannot be negative")
        if self.operator_cash_required < 0:
            raise ValidationError("Operator cash cannot be negative")

        # Verify equity split adds up
        expected_total = self.investor_cash_required + self.operator_cash_required
        if abs(self.total_cash_required - expected_total) > 0.01:
            raise ValidationError(
                f"Total cash ({self.total_cash_required:,.2f}) doesn't match "
                f"investor + operator cash ({expected_total:,.2f})"
            )

        if not (0.0 <= self.investor_equity_share <= 1.0):
            raise ValidationError("Investor equity share must be between 0% and 100%")
        if not (0.0 <= self.preferred_return_rate <= 0.25):
            raise ValidationError("Preferred return rate must be between 0% and 25%")

    def _validate_income_structure(self):
        """Validate income calculations."""
        if self.pre_renovation_annual_rent < 0:
            raise ValidationError("Pre-renovation rent cannot be negative")
        if self.post_renovation_annual_rent < 0:
            raise ValidationError("Post-renovation rent cannot be negative")
        if self.year_1_rental_income < 0:
            raise ValidationError("Year 1 rental income cannot be negative")
        if self.initial_cap_rate < 0:
            raise ValidationError("Initial cap rate cannot be negative")

    def _validate_operating_expenses(self):
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

    def calculate_ltv_ratio(self) -> float:
        """Calculate loan-to-value ratio."""
        if self.purchase_price == 0:
            return 0.0
        return self.loan_amount / self.purchase_price

    def calculate_debt_service_coverage_ratio(self) -> float:
        """Calculate debt service coverage ratio (NOI / Annual Debt Service)."""
        if self.annual_interest_expense == 0:
            return float("inf")

        year_1_noi = self.year_1_rental_income - self.total_operating_expenses
        return year_1_noi / self.annual_interest_expense

    def calculate_cash_on_cash_return(self) -> float:
        """Calculate Year 1 cash-on-cash return."""
        if self.total_cash_required == 0:
            return 0.0

        year_1_noi = self.year_1_rental_income - self.total_operating_expenses
        year_1_cash_flow = year_1_noi - self.annual_interest_expense

        return year_1_cash_flow / self.total_cash_required

    def calculate_price_per_unit(self, total_units: int) -> float:
        """Calculate price per unit."""
        if total_units == 0:
            return 0.0
        return self.purchase_price / total_units

    def calculate_gross_rent_multiplier(self) -> float:
        """Calculate gross rent multiplier."""
        if self.post_renovation_annual_rent == 0:
            return 0.0
        return self.purchase_price / self.post_renovation_annual_rent

    def get_acquisition_summary(self) -> Dict[str, float]:
        """Get summary of acquisition metrics."""
        return {
            "purchase_price": self.purchase_price,
            "total_acquisition_cost": self.cost_basis,
            "loan_amount": self.loan_amount,
            "total_cash_required": self.total_cash_required,
            "ltv_ratio": self.calculate_ltv_ratio(),
            "initial_cap_rate": self.initial_cap_rate,
            "year_1_cash_on_cash": self.calculate_cash_on_cash_return(),
            "debt_service_coverage": self.calculate_debt_service_coverage_ratio(),
        }

    def get_equity_distribution(self) -> Dict[str, float]:
        """Get equity distribution breakdown."""
        return {
            "investor_cash_required": self.investor_cash_required,
            "operator_cash_required": self.operator_cash_required,
            "investor_equity_share": self.investor_equity_share,
            "operator_equity_share": 1.0 - self.investor_equity_share,
            "preferred_return_rate": self.preferred_return_rate,
        }

    def get_operating_expense_breakdown(self) -> Dict[str, float]:
        """Get operating expense breakdown."""
        return {
            "property_taxes": self.property_taxes,
            "insurance": self.insurance,
            "repairs_maintenance": self.repairs_maintenance,
            "property_management": self.property_management,
            "admin_expenses": self.admin_expenses,
            "contracting": self.contracting,
            "replacement_reserves": self.replacement_reserves,
            "total_operating_expenses": self.total_operating_expenses,
            "expense_ratio": (
                self.total_operating_expenses / self.post_renovation_annual_rent
                if self.post_renovation_annual_rent > 0
                else 0.0
            ),
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "property_id": self.property_id,
            "scenario_id": self.scenario_id,
            "calculation_date": self.calculation_date.isoformat(),
            # Purchase details
            "purchase_price": self.purchase_price,
            "closing_cost_amount": self.closing_cost_amount,
            "renovation_capex": self.renovation_capex,
            "cost_basis": self.cost_basis,
            # Financing
            "loan_amount": self.loan_amount,
            "annual_interest_expense": self.annual_interest_expense,
            "lender_reserves_amount": self.lender_reserves_amount,
            # Equity requirements
            "investor_cash_required": self.investor_cash_required,
            "operator_cash_required": self.operator_cash_required,
            "total_cash_required": self.total_cash_required,
            # Valuation
            "after_repair_value": self.after_repair_value,
            "initial_cap_rate": self.initial_cap_rate,
            # Income structure
            "pre_renovation_annual_rent": self.pre_renovation_annual_rent,
            "post_renovation_annual_rent": self.post_renovation_annual_rent,
            "year_1_rental_income": self.year_1_rental_income,
            # Operating expenses
            "property_taxes": self.property_taxes,
            "insurance": self.insurance,
            "repairs_maintenance": self.repairs_maintenance,
            "property_management": self.property_management,
            "admin_expenses": self.admin_expenses,
            "contracting": self.contracting,
            "replacement_reserves": self.replacement_reserves,
            "total_operating_expenses": self.total_operating_expenses,
            # Investment structure
            "investor_equity_share": self.investor_equity_share,
            "preferred_return_rate": self.preferred_return_rate,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InitialNumbers":
        """Create from dictionary (deserialization)."""
        calculation_date = (
            date.fromisoformat(data["calculation_date"])
            if "calculation_date" in data
            else date.today()
        )

        return cls(
            property_id=data["property_id"],
            scenario_id=data["scenario_id"],
            calculation_date=calculation_date,
            # Purchase details
            purchase_price=data["purchase_price"],
            closing_cost_amount=data["closing_cost_amount"],
            renovation_capex=data["renovation_capex"],
            cost_basis=data["cost_basis"],
            # Financing
            loan_amount=data["loan_amount"],
            annual_interest_expense=data["annual_interest_expense"],
            lender_reserves_amount=data["lender_reserves_amount"],
            # Equity requirements
            investor_cash_required=data["investor_cash_required"],
            operator_cash_required=data["operator_cash_required"],
            total_cash_required=data["total_cash_required"],
            # Valuation
            after_repair_value=data["after_repair_value"],
            initial_cap_rate=data["initial_cap_rate"],
            # Income structure
            pre_renovation_annual_rent=data["pre_renovation_annual_rent"],
            post_renovation_annual_rent=data["post_renovation_annual_rent"],
            year_1_rental_income=data["year_1_rental_income"],
            # Operating expenses
            property_taxes=data["property_taxes"],
            insurance=data["insurance"],
            repairs_maintenance=data["repairs_maintenance"],
            property_management=data["property_management"],
            admin_expenses=data["admin_expenses"],
            contracting=data["contracting"],
            replacement_reserves=data["replacement_reserves"],
            total_operating_expenses=data["total_operating_expenses"],
            # Investment structure
            investor_equity_share=data["investor_equity_share"],
            preferred_return_rate=data["preferred_return_rate"],
        )

    def __str__(self) -> str:
        """String representation for debugging."""
        return (
            f"InitialNumbers(property={self.property_id}, scenario={self.scenario_id}, "
            f"purchase_price=${self.purchase_price:,.0f}, "
            f"loan=${self.loan_amount:,.0f}, cash=${self.total_cash_required:,.0f})"
        )
