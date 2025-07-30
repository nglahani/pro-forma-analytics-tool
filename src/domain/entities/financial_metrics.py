"""
Financial Metrics Domain Entity

Represents comprehensive financial analysis and KPIs for real estate investment.
Corresponds to "KPIs" section in Excel pro forma with NPV, IRR, and investment recommendations.
"""

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Any, Dict, List, Optional

from core.exceptions import ValidationError


class InvestmentRecommendation(Enum):
    """Investment recommendation categories."""

    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"


class RiskLevel(Enum):
    """Risk level classifications."""

    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


@dataclass
class TerminalValue:
    """
    Represents terminal value calculations for property exit.
    """

    year: int = 5  # Exit year (typically Year 5)

    # Property value calculations
    final_noi: float = 0.0
    exit_cap_rate: float = 0.0
    gross_property_value: float = 0.0

    # Disposition costs
    selling_costs_rate: float = 0.03  # 3% of gross value
    selling_costs_amount: float = 0.0

    # Debt payoff
    remaining_loan_balance: float = 0.0

    # Net proceeds
    net_sale_proceeds: float = 0.0

    # Distributions
    investor_terminal_distribution: float = 0.0
    operator_terminal_distribution: float = 0.0

    def __post_init__(self) -> None:
        """Validate terminal value calculations."""
        self._validate_inputs()
        self._calculate_terminal_value()

    def _validate_inputs(self) -> None:
        """Validate input parameters."""
        if self.year < 1 or self.year > 10:
            raise ValidationError("Exit year must be between 1 and 10")
        if self.final_noi < 0:
            raise ValidationError("Final NOI cannot be negative")
        if not (0.02 <= self.exit_cap_rate <= 0.15):
            raise ValidationError("Exit cap rate must be between 2% and 15%")
        if not (0.01 <= self.selling_costs_rate <= 0.10):
            raise ValidationError("Selling costs rate must be between 1% and 10%")

    def _calculate_terminal_value(self) -> None:
        """Calculate terminal value components."""
        # Gross property value = NOI / Cap Rate
        self.gross_property_value = (
            self.final_noi / self.exit_cap_rate if self.exit_cap_rate > 0 else 0.0
        )

        # Selling costs
        self.selling_costs_amount = self.gross_property_value * self.selling_costs_rate

        # Net sale proceeds after debt payoff and selling costs
        self.net_sale_proceeds = (
            self.gross_property_value
            - self.selling_costs_amount
            - self.remaining_loan_balance
        )


@dataclass
class CashFlowSummary:
    """
    Summary of cash flows for financial analysis.
    """

    # Initial investment (Year 0)
    initial_investment: float = 0.0

    # Annual cash flows (Years 1-5)
    annual_cash_flows: List[float] = field(default_factory=list)

    # Terminal cash flow (Year 5)
    terminal_cash_flow: float = 0.0

    # Total cash flows for analysis
    total_cash_flows: List[float] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate and compile cash flows."""
        self._validate_cash_flows()
        self._compile_total_cash_flows()

    def _validate_cash_flows(self) -> None:
        """Validate cash flow inputs."""
        if self.initial_investment <= 0:
            raise ValidationError("Initial investment must be positive")
        if len(self.annual_cash_flows) < 1:
            raise ValidationError("Must have at least one annual cash flow")
        if len(self.annual_cash_flows) > 10:
            raise ValidationError("Cannot have more than 10 years of cash flows")

    def _compile_total_cash_flows(self) -> None:
        """Compile total cash flows including initial investment and terminal value."""
        # Start with negative initial investment
        self.total_cash_flows = [-self.initial_investment]

        # Add annual cash flows (except the last year)
        for i, cash_flow in enumerate(self.annual_cash_flows):
            if i == len(self.annual_cash_flows) - 1:
                # Last year: add both annual cash flow and terminal value
                self.total_cash_flows.append(cash_flow + self.terminal_cash_flow)
            else:
                self.total_cash_flows.append(cash_flow)


@dataclass
class FinancialMetrics:
    """
    Comprehensive financial metrics and KPIs for real estate investment.
    Corresponds to "KPIs" section in Excel pro forma.
    """

    property_id: str
    scenario_id: str
    calculation_date: date = field(default_factory=date.today)

    # Investment summary
    initial_investment: float = 0.0
    total_distributions: float = 0.0
    terminal_value: Optional[TerminalValue] = None

    # Core financial metrics
    net_present_value: float = 0.0
    internal_rate_return: float = 0.0
    modified_irr: float = 0.0
    cash_on_cash_return_year_1: float = 0.0
    average_annual_return: float = 0.0

    # Return multiples
    equity_multiple: float = 0.0
    total_return_multiple: float = 0.0

    # Risk metrics
    payback_period_years: float = 0.0
    break_even_analysis: Dict[str, float] = field(default_factory=dict)

    # Profitability ratios
    return_on_investment: float = 0.0
    annualized_return: float = 0.0

    # Investment analysis
    discount_rate: float = 0.10  # Default 10% discount rate
    investment_horizon_years: int = 5

    # Qualitative assessments
    risk_level: RiskLevel = RiskLevel.MODERATE
    investment_recommendation: InvestmentRecommendation = InvestmentRecommendation.HOLD
    recommendation_rationale: str = ""

    # Additional metrics
    debt_service_coverage_avg: float = 0.0
    loan_to_value_ratio: float = 0.0
    cap_rate_year_1: float = 0.0

    def __post_init__(self) -> None:
        """Validate financial metrics after creation."""
        self._validate_identifiers()
        self._validate_financial_inputs()
        self._validate_metrics()

    def _validate_identifiers(self) -> None:
        """Validate required identifiers."""
        if not self.property_id:
            raise ValidationError("Property ID is required")
        if not self.scenario_id:
            raise ValidationError("Scenario ID is required")

    def _validate_financial_inputs(self) -> None:
        """Validate financial input parameters."""
        if self.initial_investment <= 0:
            raise ValidationError("Initial investment must be positive")
        if not (0.03 <= self.discount_rate <= 0.25):
            raise ValidationError("Discount rate must be between 3% and 25%")
        if not (1 <= self.investment_horizon_years <= 15):
            raise ValidationError("Investment horizon must be between 1 and 15 years")

    def _validate_metrics(self) -> None:
        """Validate calculated metrics are reasonable."""
        if self.internal_rate_return < -1.0 or self.internal_rate_return > 5.0:
            raise ValidationError(
                f"IRR seems unreasonable: {self.internal_rate_return:.1%}"
            )
        if self.equity_multiple < 0:
            raise ValidationError("Equity multiple cannot be negative")
        if self.payback_period_years < 0:
            raise ValidationError("Payback period cannot be negative")

    def get_investment_summary(self) -> Dict[str, Any]:
        """Get summary of key investment metrics."""
        return {
            "property_id": self.property_id,
            "scenario_id": self.scenario_id,
            "initial_investment": self.initial_investment,
            "total_distributions": self.total_distributions,
            "terminal_value": (
                self.terminal_value.net_sale_proceeds if self.terminal_value else 0.0
            ),
            "total_return": self.total_distributions
            + (self.terminal_value.net_sale_proceeds if self.terminal_value else 0.0),
            "net_present_value": self.net_present_value,
            "internal_rate_return": self.internal_rate_return,
            "equity_multiple": self.equity_multiple,
            "payback_period": self.payback_period_years,
            "investment_recommendation": self.investment_recommendation.value,
            "risk_level": self.risk_level.value,
        }

    def get_profitability_analysis(self) -> Dict[str, float]:
        """Get detailed profitability analysis."""
        return {
            "net_present_value": self.net_present_value,
            "internal_rate_return": self.internal_rate_return,
            "modified_irr": self.modified_irr,
            "cash_on_cash_year_1": self.cash_on_cash_return_year_1,
            "average_annual_return": self.average_annual_return,
            "equity_multiple": self.equity_multiple,
            "total_return_multiple": self.total_return_multiple,
            "return_on_investment": self.return_on_investment,
            "annualized_return": self.annualized_return,
        }

    def get_risk_analysis(self) -> Dict[str, Any]:
        """Get risk analysis metrics."""
        return {
            "risk_level": self.risk_level.value,
            "payback_period_years": self.payback_period_years,
            "debt_service_coverage_avg": self.debt_service_coverage_avg,
            "loan_to_value_ratio": self.loan_to_value_ratio,
            "break_even_analysis": self.break_even_analysis,
            "discount_rate_used": self.discount_rate,
        }

    def get_investment_recommendation(self) -> Dict[str, str]:
        """Get investment recommendation with rationale."""
        return {
            "recommendation": self.investment_recommendation.value,
            "risk_level": self.risk_level.value,
            "rationale": self.recommendation_rationale,
            "key_metrics": f"NPV: ${self.net_present_value:,.0f}, IRR: {self.internal_rate_return:.1%}, Multiple: {self.equity_multiple:.2f}x",
        }

    def calculate_sensitivity_metrics(
        self, base_case: "FinancialMetrics"
    ) -> Dict[str, float]:
        """Calculate sensitivity compared to base case."""
        if not base_case:
            return {}

        return {
            "npv_variance": (
                (
                    (self.net_present_value - base_case.net_present_value)
                    / abs(base_case.net_present_value)
                )
                if base_case.net_present_value != 0
                else 0
            ),
            "irr_variance": self.internal_rate_return - base_case.internal_rate_return,
            "equity_multiple_variance": self.equity_multiple
            - base_case.equity_multiple,
            "payback_variance": self.payback_period_years
            - base_case.payback_period_years,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "property_id": self.property_id,
            "scenario_id": self.scenario_id,
            "calculation_date": self.calculation_date.isoformat(),
            "initial_investment": self.initial_investment,
            "total_distributions": self.total_distributions,
            "terminal_value": (
                {
                    "year": self.terminal_value.year,
                    "final_noi": self.terminal_value.final_noi,
                    "exit_cap_rate": self.terminal_value.exit_cap_rate,
                    "gross_property_value": self.terminal_value.gross_property_value,
                    "selling_costs_amount": self.terminal_value.selling_costs_amount,
                    "remaining_loan_balance": self.terminal_value.remaining_loan_balance,
                    "net_sale_proceeds": self.terminal_value.net_sale_proceeds,
                    "investor_terminal_distribution": self.terminal_value.investor_terminal_distribution,
                    "operator_terminal_distribution": self.terminal_value.operator_terminal_distribution,
                }
                if self.terminal_value
                else None
            ),
            "financial_metrics": {
                "net_present_value": self.net_present_value,
                "internal_rate_return": self.internal_rate_return,
                "modified_irr": self.modified_irr,
                "cash_on_cash_return_year_1": self.cash_on_cash_return_year_1,
                "average_annual_return": self.average_annual_return,
                "equity_multiple": self.equity_multiple,
                "total_return_multiple": self.total_return_multiple,
                "payback_period_years": self.payback_period_years,
                "return_on_investment": self.return_on_investment,
                "annualized_return": self.annualized_return,
                "debt_service_coverage_avg": self.debt_service_coverage_avg,
                "loan_to_value_ratio": self.loan_to_value_ratio,
                "cap_rate_year_1": self.cap_rate_year_1,
            },
            "investment_analysis": {
                "discount_rate": self.discount_rate,
                "investment_horizon_years": self.investment_horizon_years,
                "risk_level": self.risk_level.value,
                "investment_recommendation": self.investment_recommendation.value,
                "recommendation_rationale": self.recommendation_rationale,
            },
            "break_even_analysis": self.break_even_analysis,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FinancialMetrics":
        """Create from dictionary (deserialization)."""
        calculation_date = (
            date.fromisoformat(data["calculation_date"])
            if "calculation_date" in data
            else date.today()
        )

        # Reconstruct terminal value if present
        terminal_value = None
        if data.get("terminal_value"):
            tv_data = data["terminal_value"]
            terminal_value = TerminalValue(
                year=tv_data["year"],
                final_noi=tv_data["final_noi"],
                exit_cap_rate=tv_data["exit_cap_rate"],
                gross_property_value=tv_data["gross_property_value"],
                selling_costs_amount=tv_data["selling_costs_amount"],
                remaining_loan_balance=tv_data["remaining_loan_balance"],
                net_sale_proceeds=tv_data["net_sale_proceeds"],
                investor_terminal_distribution=tv_data[
                    "investor_terminal_distribution"
                ],
                operator_terminal_distribution=tv_data[
                    "operator_terminal_distribution"
                ],
            )

        metrics_data = data.get("financial_metrics", {})
        analysis_data = data.get("investment_analysis", {})

        return cls(
            property_id=data["property_id"],
            scenario_id=data["scenario_id"],
            calculation_date=calculation_date,
            initial_investment=data["initial_investment"],
            total_distributions=data["total_distributions"],
            terminal_value=terminal_value,
            net_present_value=metrics_data.get("net_present_value", 0.0),
            internal_rate_return=metrics_data.get("internal_rate_return", 0.0),
            modified_irr=metrics_data.get("modified_irr", 0.0),
            cash_on_cash_return_year_1=metrics_data.get(
                "cash_on_cash_return_year_1", 0.0
            ),
            average_annual_return=metrics_data.get("average_annual_return", 0.0),
            equity_multiple=metrics_data.get("equity_multiple", 0.0),
            total_return_multiple=metrics_data.get("total_return_multiple", 0.0),
            payback_period_years=metrics_data.get("payback_period_years", 0.0),
            return_on_investment=metrics_data.get("return_on_investment", 0.0),
            annualized_return=metrics_data.get("annualized_return", 0.0),
            debt_service_coverage_avg=metrics_data.get(
                "debt_service_coverage_avg", 0.0
            ),
            loan_to_value_ratio=metrics_data.get("loan_to_value_ratio", 0.0),
            cap_rate_year_1=metrics_data.get("cap_rate_year_1", 0.0),
            discount_rate=analysis_data.get("discount_rate", 0.10),
            investment_horizon_years=analysis_data.get("investment_horizon_years", 5),
            risk_level=RiskLevel(analysis_data.get("risk_level", "MODERATE")),
            investment_recommendation=InvestmentRecommendation(
                analysis_data.get("investment_recommendation", "HOLD")
            ),
            recommendation_rationale=analysis_data.get("recommendation_rationale", ""),
            break_even_analysis=data.get("break_even_analysis", {}),
        )

    def __str__(self) -> str:
        """String representation for debugging."""
        return (
            f"FinancialMetrics(property={self.property_id}, scenario={self.scenario_id}, "
            f"NPV=${self.net_present_value:,.0f}, IRR={self.internal_rate_return:.1%}, "
            f"Multiple={self.equity_multiple:.2f}x, Rec={self.investment_recommendation.value})"
        )
