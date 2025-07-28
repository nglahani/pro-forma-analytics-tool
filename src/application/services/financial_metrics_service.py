"""
Financial Metrics Service

Application service that calculates comprehensive financial metrics including
NPV, IRR, and investment recommendations from cash flow projections.
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import date

from src.domain.entities.financial_metrics import (
    FinancialMetrics,
    TerminalValue,
    CashFlowSummary,
    InvestmentRecommendation,
    RiskLevel,
)
from src.domain.entities.cash_flow_projection import CashFlowProjection
from src.domain.entities.dcf_assumptions import DCFAssumptions
from src.domain.entities.initial_numbers import InitialNumbers
from core.logging_config import get_logger
from core.exceptions import ValidationError
from config.dcf_constants import (
    FINANCIAL_CONSTANTS,
    RISK_THRESHOLDS,
    INVESTMENT_THRESHOLDS,
)


class FinancialMetricsService:
    """Service for calculating comprehensive financial metrics and investment analysis."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def calculate_financial_metrics(
        self,
        cash_flow_projection: CashFlowProjection,
        dcf_assumptions: DCFAssumptions,
        initial_numbers: InitialNumbers,
        discount_rate: float = 0.10,
    ) -> FinancialMetrics:
        """
        Calculate comprehensive financial metrics from cash flow projections.

        Args:
            cash_flow_projection: CashFlowProjection with Years 0-5 projections
            dcf_assumptions: DCFAssumptions containing market parameters
            initial_numbers: InitialNumbers containing acquisition details
            discount_rate: Discount rate for NPV calculation (default 10%)

        Returns:
            FinancialMetrics object with complete analysis

        Raises:
            ValidationError: If calculations fail or inputs are invalid
        """
        try:
            self.logger.info(
                f"Calculating financial metrics for property {cash_flow_projection.property_id}, "
                f"scenario {cash_flow_projection.scenario_id}"
            )

            # Calculate terminal value
            terminal_value = self._calculate_terminal_value(
                cash_flow_projection, dcf_assumptions, initial_numbers
            )

            # Prepare cash flows for analysis
            cash_flow_summary = self._prepare_cash_flows(
                cash_flow_projection, initial_numbers, terminal_value
            )

            # Calculate core financial metrics
            npv = self._calculate_npv(cash_flow_summary.total_cash_flows, discount_rate)
            irr = self._calculate_irr(cash_flow_summary.total_cash_flows)
            modified_irr = self._calculate_modified_irr(
                cash_flow_summary.total_cash_flows, discount_rate
            )

            # Calculate return metrics
            total_distributions = sum(cash_flow_summary.annual_cash_flows)
            total_return = total_distributions + terminal_value.net_sale_proceeds
            equity_multiple = (
                total_return / cash_flow_summary.initial_investment
                if cash_flow_summary.initial_investment > 0
                else 0
            )

            # Calculate other metrics
            cash_on_cash_year_1 = (
                cash_flow_summary.annual_cash_flows[0]
                / cash_flow_summary.initial_investment
                if len(cash_flow_summary.annual_cash_flows) > 0
                and cash_flow_summary.initial_investment > 0
                else 0
            )
            payback_period = self._calculate_payback_period(
                cash_flow_summary.total_cash_flows
            )
            average_annual_return = self._calculate_average_annual_return(
                cash_flow_summary.annual_cash_flows,
                cash_flow_summary.initial_investment,
            )

            # Calculate risk metrics
            debt_service_coverage_avg = self._calculate_average_dscr(
                cash_flow_projection
            )
            ltv_ratio = initial_numbers.calculate_ltv_ratio()
            cap_rate_year_1 = initial_numbers.initial_cap_rate

            # Calculate break-even analysis
            break_even_analysis = self._calculate_break_even_analysis(
                cash_flow_projection, initial_numbers
            )

            # Determine risk level and investment recommendation
            risk_level = self._assess_risk_level(
                irr, equity_multiple, debt_service_coverage_avg, ltv_ratio
            )
            investment_recommendation, rationale = (
                self._generate_investment_recommendation(
                    npv, irr, equity_multiple, payback_period, risk_level
                )
            )

            # Create financial metrics object
            financial_metrics = FinancialMetrics(
                property_id=cash_flow_projection.property_id,
                scenario_id=cash_flow_projection.scenario_id,
                initial_investment=cash_flow_summary.initial_investment,
                total_distributions=total_distributions,
                terminal_value=terminal_value,
                net_present_value=npv,
                internal_rate_return=irr,
                modified_irr=modified_irr,
                cash_on_cash_return_year_1=cash_on_cash_year_1,
                average_annual_return=average_annual_return,
                equity_multiple=equity_multiple,
                total_return_multiple=equity_multiple,  # Same for this analysis
                payback_period_years=payback_period,
                return_on_investment=(
                    (total_return - cash_flow_summary.initial_investment)
                    / cash_flow_summary.initial_investment
                    if cash_flow_summary.initial_investment > 0
                    else 0
                ),
                annualized_return=irr,  # IRR is the annualized return
                discount_rate=discount_rate,
                investment_horizon_years=len(cash_flow_summary.annual_cash_flows),
                risk_level=risk_level,
                investment_recommendation=investment_recommendation,
                recommendation_rationale=rationale,
                debt_service_coverage_avg=debt_service_coverage_avg,
                loan_to_value_ratio=ltv_ratio,
                cap_rate_year_1=cap_rate_year_1,
                break_even_analysis=break_even_analysis,
            )

            self.logger.info(
                f"Successfully calculated financial metrics: "
                f"NPV ${npv:,.0f}, IRR {irr:.1%}, Multiple {equity_multiple:.2f}x, "
                f"Recommendation {investment_recommendation.value}"
            )

            return financial_metrics

        except Exception as e:
            self.logger.error(f"Failed to calculate financial metrics: {str(e)}")
            raise ValidationError(
                f"Financial metrics calculation failed: {str(e)}"
            ) from e

    def _calculate_terminal_value(
        self,
        cash_flow_projection: CashFlowProjection,
        dcf_assumptions: DCFAssumptions,
        initial_numbers: InitialNumbers,
    ) -> TerminalValue:
        """Calculate terminal value at exit (Year 5)."""

        # Get Year 5 cash flow and assumptions
        year_5_cash_flow = cash_flow_projection.get_cash_flow_by_year(5)
        if not year_5_cash_flow:
            raise ValidationError(
                "Year 5 cash flow not found for terminal value calculation"
            )

        # Use Year 5 NOI and exit cap rate
        final_noi = year_5_cash_flow.net_operating_income
        exit_cap_rate = dcf_assumptions.cap_rate[5]  # Year 5 cap rate

        # Estimate remaining loan balance (simplified - assume interest-only payments)
        # In practice, this would use an amortization schedule
        original_loan = initial_numbers.loan_amount
        annual_principal_payment = (
            original_loan * FINANCIAL_CONSTANTS.ANNUAL_PRINCIPAL_PAYDOWN_RATE
        )
        remaining_loan_balance = max(0, original_loan - (annual_principal_payment * 5))

        # Calculate distributions based on equity structure
        investor_share = dcf_assumptions.investor_equity_share

        # Calculate terminal value with proper distributions
        terminal_value = TerminalValue(
            year=5,
            final_noi=final_noi,
            exit_cap_rate=exit_cap_rate,
            remaining_loan_balance=remaining_loan_balance,
            selling_costs_rate=FINANCIAL_CONSTANTS.DEFAULT_SELLING_COSTS_RATE,
        )

        # Get calculated net proceeds after __post_init__
        net_proceeds = terminal_value.net_sale_proceeds
        if net_proceeds > 0:
            # Apply waterfall logic - recreate with distributions
            terminal_value = TerminalValue(
                year=5,
                final_noi=final_noi,
                exit_cap_rate=exit_cap_rate,
                remaining_loan_balance=remaining_loan_balance,
                selling_costs_rate=FINANCIAL_CONSTANTS.DEFAULT_SELLING_COSTS_RATE,
                investor_terminal_distribution=net_proceeds * investor_share,
                operator_terminal_distribution=net_proceeds * (1 - investor_share),
            )

        return terminal_value

    def _prepare_cash_flows(
        self,
        cash_flow_projection: CashFlowProjection,
        initial_numbers: InitialNumbers,
        terminal_value: TerminalValue,
    ) -> CashFlowSummary:
        """Prepare cash flows for financial analysis."""

        # Extract annual cash flows for the investor (using distributions)
        annual_cash_flows = []
        for year in range(1, 6):  # Years 1-5
            distribution = cash_flow_projection.get_distribution_by_year(year)
            if distribution:
                # Use investor's share of total distributions
                total_year_distribution = (
                    distribution.investor_cash_distribution
                    + distribution.operator_cash_distribution
                )
                annual_cash_flows.append(total_year_distribution)
            else:
                annual_cash_flows.append(0.0)

        # Terminal cash flow includes both Year 5 distribution and terminal value
        terminal_cash_flow = terminal_value.net_sale_proceeds

        return CashFlowSummary(
            initial_investment=initial_numbers.total_cash_required,
            annual_cash_flows=annual_cash_flows,
            terminal_cash_flow=terminal_cash_flow,
        )

    def _calculate_npv(self, cash_flows: List[float], discount_rate: float) -> float:
        """Calculate Net Present Value."""
        if not cash_flows:
            return 0.0

        npv = 0.0
        for i, cash_flow in enumerate(cash_flows):
            npv += cash_flow / ((1 + discount_rate) ** i)

        return npv

    def _calculate_irr(
        self,
        cash_flows: List[float],
        max_iterations: int = None,
        precision: float = None,
    ) -> float:
        """Calculate Internal Rate of Return using Newton-Raphson method."""
        if not cash_flows or len(cash_flows) < 2:
            return 0.0

        # Use configured constants
        max_iterations = max_iterations or FINANCIAL_CONSTANTS.IRR_MAX_ITERATIONS
        precision = precision or FINANCIAL_CONSTANTS.IRR_PRECISION

        # Initial guess
        irr_guess = FINANCIAL_CONSTANTS.INITIAL_IRR_GUESS

        for iteration in range(max_iterations):
            # Calculate NPV and its derivative
            npv = 0.0
            npv_derivative = 0.0

            for i, cash_flow in enumerate(cash_flows):
                if i == 0:
                    npv += cash_flow
                else:
                    discount_factor = (1 + irr_guess) ** i
                    npv += cash_flow / discount_factor
                    npv_derivative -= (
                        i * cash_flow / (discount_factor * (1 + irr_guess))
                    )

            # Check for convergence
            if abs(npv) < precision:
                return irr_guess

            # Newton-Raphson iteration
            if npv_derivative != 0:
                irr_guess = irr_guess - npv / npv_derivative
            else:
                break

            # Bounds checking
            if irr_guess < FINANCIAL_CONSTANTS.IRR_MIN_BOUND:
                irr_guess = FINANCIAL_CONSTANTS.IRR_MIN_BOUND
            elif irr_guess > FINANCIAL_CONSTANTS.IRR_MAX_BOUND:
                irr_guess = FINANCIAL_CONSTANTS.IRR_MAX_BOUND

        # If convergence failed, return the best guess
        # Note: numpy doesn't have np.irr, would need numpy-financial
        return irr_guess if -1.0 < irr_guess < 10.0 else 0.0

    def _calculate_modified_irr(
        self, cash_flows: List[float], discount_rate: float
    ) -> float:
        """Calculate Modified Internal Rate of Return."""
        if not cash_flows or len(cash_flows) < 2:
            return 0.0

        try:
            # Separate positive and negative cash flows
            pv_negative = 0.0  # Present value of negative cash flows
            fv_positive = 0.0  # Future value of positive cash flows

            n = len(cash_flows) - 1  # Investment period

            for i, cash_flow in enumerate(cash_flows):
                if cash_flow < 0:
                    pv_negative += cash_flow / ((1 + discount_rate) ** i)
                elif cash_flow > 0:
                    fv_positive += cash_flow * ((1 + discount_rate) ** (n - i))

            if pv_negative >= 0 or fv_positive <= 0:
                return 0.0

            # MIRR = (FV_positive / |PV_negative|)^(1/n) - 1
            mirr = (fv_positive / abs(pv_negative)) ** (1 / n) - 1

            return mirr if -1.0 < mirr < 10.0 else 0.0

        except:
            return 0.0

    def _calculate_payback_period(self, cash_flows: List[float]) -> float:
        """Calculate payback period in years."""
        if not cash_flows or len(cash_flows) < 2:
            return 0.0

        cumulative = cash_flows[0]  # Start with initial investment (negative)

        for i in range(1, len(cash_flows)):
            if cumulative + cash_flows[i] >= 0:
                # Payback occurs during this year
                if cash_flows[i] > 0:
                    fraction = abs(cumulative) / cash_flows[i]
                    return i - 1 + fraction
                else:
                    return float(i)

            cumulative += cash_flows[i]

        # If never paid back
        return float(len(cash_flows))

    def _calculate_average_annual_return(
        self, annual_cash_flows: List[float], initial_investment: float
    ) -> float:
        """Calculate average annual return."""
        if not annual_cash_flows or initial_investment <= 0:
            return 0.0

        total_return = sum(annual_cash_flows)
        years = len(annual_cash_flows)

        return (total_return / years) / initial_investment if years > 0 else 0.0

    def _calculate_average_dscr(
        self, cash_flow_projection: CashFlowProjection
    ) -> float:
        """Calculate average debt service coverage ratio."""
        dscr_values = []

        for year in range(1, 6):  # Years 1-5
            cash_flow = cash_flow_projection.get_cash_flow_by_year(year)
            if cash_flow and cash_flow.annual_debt_service > 0:
                dscr = cash_flow.net_operating_income / cash_flow.annual_debt_service
                dscr_values.append(dscr)

        return sum(dscr_values) / len(dscr_values) if dscr_values else 0.0

    def _calculate_break_even_analysis(
        self, cash_flow_projection: CashFlowProjection, initial_numbers: InitialNumbers
    ) -> Dict[str, float]:
        """Calculate break-even analysis metrics."""

        # Get Year 1 cash flow for analysis
        year_1_cash_flow = cash_flow_projection.get_cash_flow_by_year(1)
        if not year_1_cash_flow:
            return {}

        # Break-even occupancy rate
        fixed_costs = (
            year_1_cash_flow.total_operating_expenses
            + year_1_cash_flow.annual_debt_service
        )
        gross_potential_income = (
            year_1_cash_flow.gross_rental_income
            / (1 - year_1_cash_flow.vacancy_loss / year_1_cash_flow.gross_rental_income)
            if year_1_cash_flow.gross_rental_income > 0
            else 0
        )
        break_even_occupancy = (
            fixed_costs / gross_potential_income if gross_potential_income > 0 else 1.0
        )

        # Break-even rent (per unit per month)
        total_units = (
            initial_numbers.residential_units.total_units
            if hasattr(initial_numbers, "residential_units")
            else 20
        )  # Estimate
        break_even_monthly_rent = (
            fixed_costs / (12 * total_units) if total_units > 0 else 0
        )

        # Break-even cap rate
        break_even_cap_rate = (
            year_1_cash_flow.net_operating_income / initial_numbers.purchase_price
            if initial_numbers.purchase_price > 0
            else 0
        )

        return {
            "break_even_occupancy_rate": min(break_even_occupancy, 1.0),
            "break_even_monthly_rent_per_unit": break_even_monthly_rent,
            "break_even_cap_rate": break_even_cap_rate,
            "current_occupancy_rate": (
                1.0
                - (year_1_cash_flow.vacancy_loss / year_1_cash_flow.gross_rental_income)
                if year_1_cash_flow.gross_rental_income > 0
                else 0
            ),
        }

    def _assess_risk_level(
        self, irr: float, equity_multiple: float, avg_dscr: float, ltv_ratio: float
    ) -> RiskLevel:
        """Assess investment risk level based on key metrics."""

        risk_score = 0

        # IRR assessment
        if irr < 0.08:
            risk_score += 2  # Low returns increase risk
        elif irr > 0.20:
            risk_score += 1  # Very high returns may indicate high risk

        # Equity multiple assessment
        if equity_multiple < 1.2:
            risk_score += 2  # Low returns
        elif equity_multiple < 1.5:
            risk_score += 1

        # Debt service coverage assessment
        if avg_dscr < 1.2:
            risk_score += 2  # Tight debt coverage
        elif avg_dscr < 1.5:
            risk_score += 1

        # LTV assessment
        if ltv_ratio > 0.85:
            risk_score += 2  # High leverage
        elif ltv_ratio > 0.75:
            risk_score += 1

        # Determine risk level
        if risk_score >= 6:
            return RiskLevel.VERY_HIGH
        elif risk_score >= 4:
            return RiskLevel.HIGH
        elif risk_score >= 2:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.LOW

    def _generate_investment_recommendation(
        self,
        npv: float,
        irr: float,
        equity_multiple: float,
        payback_period: float,
        risk_level: RiskLevel,
    ) -> Tuple[InvestmentRecommendation, str]:
        """Generate investment recommendation with rationale."""

        # Score the investment
        score = 0
        rationale_points = []

        # NPV assessment
        if npv > 500000:
            score += 2
            rationale_points.append(f"Strong positive NPV (${npv:,.0f})")
        elif npv > 100000:
            score += 1
            rationale_points.append(f"Positive NPV (${npv:,.0f})")
        elif npv < -100000:
            score -= 2
            rationale_points.append(f"Negative NPV (${npv:,.0f})")

        # IRR assessment
        if irr > 0.18:
            score += 2
            rationale_points.append(f"Excellent IRR ({irr:.1%})")
        elif irr > 0.12:
            score += 1
            rationale_points.append(f"Good IRR ({irr:.1%})")
        elif irr < 0.08:
            score -= 2
            rationale_points.append(f"Low IRR ({irr:.1%})")

        # Equity multiple assessment
        if equity_multiple > 2.0:
            score += 2
            rationale_points.append(f"Strong return multiple ({equity_multiple:.2f}x)")
        elif equity_multiple > 1.5:
            score += 1
            rationale_points.append(f"Good return multiple ({equity_multiple:.2f}x)")
        elif equity_multiple < 1.2:
            score -= 2
            rationale_points.append(f"Low return multiple ({equity_multiple:.2f}x)")

        # Payback period assessment
        if payback_period < 3.0:
            score += 1
            rationale_points.append(f"Quick payback ({payback_period:.1f} years)")
        elif payback_period > 6.0:
            score -= 1
            rationale_points.append(f"Long payback ({payback_period:.1f} years)")

        # Risk adjustment
        if risk_level == RiskLevel.LOW:
            score += 1
            rationale_points.append("Low risk profile")
        elif risk_level == RiskLevel.HIGH:
            score -= 1
            rationale_points.append("High risk profile")
        elif risk_level == RiskLevel.VERY_HIGH:
            score -= 2
            rationale_points.append("Very high risk profile")

        # Determine recommendation
        if score >= 5:
            recommendation = InvestmentRecommendation.STRONG_BUY
        elif score >= 2:
            recommendation = InvestmentRecommendation.BUY
        elif score >= -1:
            recommendation = InvestmentRecommendation.HOLD
        elif score >= -3:
            recommendation = InvestmentRecommendation.SELL
        else:
            recommendation = InvestmentRecommendation.STRONG_SELL

        rationale = "; ".join(rationale_points[:3])  # Top 3 rationale points

        return recommendation, rationale

    def get_metrics_summary(
        self, financial_metrics: FinancialMetrics
    ) -> Dict[str, Any]:
        """Get comprehensive summary of financial metrics."""
        return {
            "investment_summary": financial_metrics.get_investment_summary(),
            "profitability_analysis": financial_metrics.get_profitability_analysis(),
            "risk_analysis": financial_metrics.get_risk_analysis(),
            "investment_recommendation": financial_metrics.get_investment_recommendation(),
        }

    def compare_scenarios(self, metrics_list: List[FinancialMetrics]) -> Dict[str, Any]:
        """Compare multiple scenarios and rank by attractiveness."""
        if not metrics_list:
            return {}

        # Sort by NPV (descending)
        sorted_by_npv = sorted(
            metrics_list, key=lambda m: m.net_present_value, reverse=True
        )

        # Sort by IRR (descending)
        sorted_by_irr = sorted(
            metrics_list, key=lambda m: m.internal_rate_return, reverse=True
        )

        # Calculate summary statistics
        npv_values = [m.net_present_value for m in metrics_list]
        irr_values = [m.internal_rate_return for m in metrics_list]

        return {
            "scenario_count": len(metrics_list),
            "best_npv_scenario": {
                "scenario_id": sorted_by_npv[0].scenario_id,
                "npv": sorted_by_npv[0].net_present_value,
                "irr": sorted_by_npv[0].internal_rate_return,
                "recommendation": sorted_by_npv[0].investment_recommendation.value,
            },
            "best_irr_scenario": {
                "scenario_id": sorted_by_irr[0].scenario_id,
                "npv": sorted_by_irr[0].net_present_value,
                "irr": sorted_by_irr[0].internal_rate_return,
                "recommendation": sorted_by_irr[0].investment_recommendation.value,
            },
            "summary_statistics": {
                "avg_npv": sum(npv_values) / len(npv_values),
                "max_npv": max(npv_values),
                "min_npv": min(npv_values),
                "avg_irr": sum(irr_values) / len(irr_values),
                "max_irr": max(irr_values),
                "min_irr": min(irr_values),
            },
            "recommendations": {
                rec.value: len(
                    [m for m in metrics_list if m.investment_recommendation == rec]
                )
                for rec in InvestmentRecommendation
            },
        }


# Convenience function for easy usage
def calculate_financial_metrics(
    cash_flow_projection: CashFlowProjection,
    dcf_assumptions: DCFAssumptions,
    initial_numbers: InitialNumbers,
    discount_rate: float = 0.10,
) -> FinancialMetrics:
    """Convenience function to calculate financial metrics."""
    service = FinancialMetricsService()
    return service.calculate_financial_metrics(
        cash_flow_projection, dcf_assumptions, initial_numbers, discount_rate
    )
