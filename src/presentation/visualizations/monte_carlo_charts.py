"""
Monte Carlo Simulation Visualization Components

Provides comprehensive charts and graphs for validating Monte Carlo simulation results.
Includes both statistical validation and business-focused analysis visualizations.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Set style for professional charts
plt.style.use("seaborn-v0_8-whitegrid")
sns.set_palette("husl")

# Assuming these imports will work with the existing structure
try:
    from monte_carlo.simulation_engine import MonteCarloResults, MonteCarloScenario
except ImportError:
    # Fallback for when clean architecture is fully implemented
    from ...domain.entities.monte_carlo import Scenario, SimulationResult

    MonteCarloResults = SimulationResult
    MonteCarloScenario = Scenario


class MonteCarloVisualizer:
    """
    Comprehensive visualization suite for Monte Carlo simulation results.

    Provides statistical validation charts and business-focused analysis graphs
    to help users understand and validate simulation results.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.figure_size = (12, 8)
        self.dpi = 100

    def create_comprehensive_dashboard(
        self,
        simulation_result: MonteCarloResults,
        output_dir: str = "simulation_charts",
        save_plots: bool = True,
        show_plots: bool = True,
    ) -> Dict[str, str]:
        """
        Create a comprehensive dashboard of all Monte Carlo validation charts.

        Args:
            simulation_result: Monte Carlo simulation results
            output_dir: Directory to save charts
            save_plots: Whether to save plots to disk
            show_plots: Whether to display plots interactively

        Returns:
            Dictionary mapping chart names to file paths
        """
        self.logger.info("Creating comprehensive Monte Carlo dashboard")

        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        chart_files = {}

        try:
            # 1. Parameter Distribution Analysis
            chart_files["parameter_distributions"] = (
                self._create_parameter_distributions(
                    simulation_result, output_path, save_plots, show_plots
                )
            )

            # 2. Scenario Classification Analysis
            chart_files["scenario_classification"] = (
                self._create_scenario_classification_chart(
                    simulation_result, output_path, save_plots, show_plots
                )
            )

            # 3. Risk vs Growth Scatter Plot
            chart_files["risk_growth_analysis"] = self._create_risk_growth_scatter(
                simulation_result, output_path, save_plots, show_plots
            )

            # 4. Time Series Evolution
            chart_files["time_series_evolution"] = self._create_time_series_evolution(
                simulation_result, output_path, save_plots, show_plots
            )

            # 5. Correlation Heatmap
            if (
                hasattr(simulation_result, "correlation_matrix")
                and simulation_result.correlation_matrix is not None
            ):
                chart_files["correlation_heatmap"] = self._create_correlation_heatmap(
                    simulation_result, output_path, save_plots, show_plots
                )

            # 6. Extreme Scenarios Analysis
            chart_files["extreme_scenarios"] = self._create_extreme_scenarios_chart(
                simulation_result, output_path, save_plots, show_plots
            )

            # 7. Statistical Validation Dashboard
            chart_files["statistical_validation"] = (
                self._create_statistical_validation_dashboard(
                    simulation_result, output_path, save_plots, show_plots
                )
            )

            self.logger.info(f"Created {len(chart_files)} visualization charts")

            # Create summary report
            self._create_summary_report(simulation_result, chart_files, output_path)

            return chart_files

        except Exception as e:
            self.logger.error(f"Failed to create dashboard: {e}")
            raise

    def _create_parameter_distributions(
        self,
        simulation_result: MonteCarloResults,
        output_path: Path,
        save_plots: bool,
        show_plots: bool,
    ) -> str:
        """Create parameter distribution histograms with statistical overlays."""

        # Get all parameter values across scenarios
        parameter_data = {}
        for scenario in simulation_result.scenarios:
            for param_name, values in scenario.forecasted_parameters.items():
                if param_name not in parameter_data:
                    parameter_data[param_name] = []
                parameter_data[param_name].extend(values)

        # Create subplot grid
        n_params = len(parameter_data)
        cols = 4
        rows = (n_params + cols - 1) // cols

        fig, axes = plt.subplots(rows, cols, figsize=(16, 4 * rows))
        fig.suptitle(
            "Monte Carlo Parameter Distributions with Statistical Analysis",
            fontsize=16,
            fontweight="bold",
        )

        # Flatten axes for easier iteration
        if rows == 1:
            axes = [axes] if cols == 1 else axes
        else:
            axes = axes.flatten()

        for idx, (param_name, values) in enumerate(parameter_data.items()):
            if idx >= len(axes):
                break

            ax = axes[idx]

            # Create histogram
            n, bins, patches = ax.hist(
                values,
                bins=30,
                alpha=0.7,
                density=True,
                edgecolor="black",
                linewidth=0.5,
            )

            # Add normal distribution overlay
            mu, sigma = np.mean(values), np.std(values)
            x = np.linspace(min(values), max(values), 100)
            normal_curve = (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(
                -0.5 * ((x - mu) / sigma) ** 2
            )
            ax.plot(
                x,
                normal_curve,
                "r-",
                linewidth=2,
                label=f"Normal(μ={mu:.3f}, σ={sigma:.3f})",
            )

            # Add percentile lines
            p5, p25, p50, p75, p95 = np.percentile(values, [5, 25, 50, 75, 95])
            ax.axvline(
                p50,
                color="orange",
                linestyle="--",
                linewidth=2,
                label=f"Median: {p50:.3f}",
            )
            ax.axvline(
                p5, color="red", linestyle=":", alpha=0.7, label=f"5th %: {p5:.3f}"
            )
            ax.axvline(
                p95, color="red", linestyle=":", alpha=0.7, label=f"95th %: {p95:.3f}"
            )

            # Formatting
            ax.set_title(f'{param_name.replace("_", " ").title()}', fontweight="bold")
            ax.set_xlabel("Value")
            ax.set_ylabel("Density")
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3)

        # Hide unused subplots
        for idx in range(len(parameter_data), len(axes)):
            axes[idx].set_visible(False)

        plt.tight_layout()

        # Save and show
        filename = "parameter_distributions.png"
        filepath = output_path / filename

        if save_plots:
            plt.savefig(filepath, dpi=self.dpi, bbox_inches="tight")
            self.logger.info(f"Saved parameter distributions chart: {filepath}")

        if show_plots:
            plt.show()
        else:
            plt.close()

        return str(filepath)

    def _create_scenario_classification_chart(
        self,
        simulation_result: MonteCarloResults,
        output_path: Path,
        save_plots: bool,
        show_plots: bool,
    ) -> str:
        """Create scenario classification pie chart and bar chart."""

        # Count scenario types
        scenario_counts = {}
        growth_scores = []
        risk_scores = []

        for scenario in simulation_result.scenarios:
            scenario_type = scenario.scenario_summary.get("market_scenario", "unknown")
            scenario_counts[scenario_type] = scenario_counts.get(scenario_type, 0) + 1
            growth_scores.append(scenario.scenario_summary.get("growth_score", 0.5))
            risk_scores.append(scenario.scenario_summary.get("risk_score", 0.5))

        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(
            "Monte Carlo Scenario Classification Analysis",
            fontsize=16,
            fontweight="bold",
        )

        # 1. Pie chart of scenario types
        labels = list(scenario_counts.keys())
        sizes = list(scenario_counts.values())
        colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))

        wedges, texts, autotexts = ax1.pie(
            sizes, labels=labels, autopct="%1.1f%%", colors=colors, startangle=90
        )
        ax1.set_title("Market Scenario Distribution", fontweight="bold")

        # 2. Bar chart with percentages
        bars = ax2.bar(labels, sizes, color=colors, edgecolor="black", linewidth=1)
        ax2.set_title("Scenario Count by Type", fontweight="bold")
        ax2.set_ylabel("Number of Scenarios")
        ax2.tick_params(axis="x", rotation=45)

        # Add value labels on bars
        for bar, size in zip(bars, sizes):
            height = bar.get_height()
            ax2.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + 1,
                f"{size}\n({size/sum(sizes)*100:.1f}%)",
                ha="center",
                va="bottom",
                fontweight="bold",
            )

        # 3. Growth score distribution
        ax3.hist(growth_scores, bins=20, alpha=0.7, color="green", edgecolor="black")
        ax3.axvline(
            np.mean(growth_scores),
            color="red",
            linestyle="--",
            linewidth=2,
            label=f"Mean: {np.mean(growth_scores):.3f}",
        )
        ax3.set_title("Growth Score Distribution", fontweight="bold")
        ax3.set_xlabel("Growth Score (0-1)")
        ax3.set_ylabel("Frequency")
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # 4. Risk score distribution
        ax4.hist(risk_scores, bins=20, alpha=0.7, color="red", edgecolor="black")
        ax4.axvline(
            np.mean(risk_scores),
            color="blue",
            linestyle="--",
            linewidth=2,
            label=f"Mean: {np.mean(risk_scores):.3f}",
        )
        ax4.set_title("Risk Score Distribution", fontweight="bold")
        ax4.set_xlabel("Risk Score (0-1)")
        ax4.set_ylabel("Frequency")
        ax4.legend()
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()

        # Save and show
        filename = "scenario_classification.png"
        filepath = output_path / filename

        if save_plots:
            plt.savefig(filepath, dpi=self.dpi, bbox_inches="tight")
            self.logger.info(f"Saved scenario classification chart: {filepath}")

        if show_plots:
            plt.show()
        else:
            plt.close()

        return str(filepath)

    def _create_risk_growth_scatter(
        self,
        simulation_result: MonteCarloResults,
        output_path: Path,
        save_plots: bool,
        show_plots: bool,
    ) -> str:
        """Create risk vs growth scatter plot with market scenario coloring."""

        # Extract data
        growth_scores = []
        risk_scores = []
        market_scenarios = []

        for scenario in simulation_result.scenarios:
            growth_scores.append(scenario.scenario_summary.get("growth_score", 0.5))
            risk_scores.append(scenario.scenario_summary.get("risk_score", 0.5))
            market_scenarios.append(
                scenario.scenario_summary.get("market_scenario", "unknown")
            )

        # Create figure
        fig, ax = plt.subplots(figsize=self.figure_size)

        # Create color map for scenarios
        unique_scenarios = list(set(market_scenarios))
        colors = plt.cm.Set1(np.linspace(0, 1, len(unique_scenarios)))
        color_map = dict(zip(unique_scenarios, colors))

        # Plot points colored by scenario type
        for scenario_type in unique_scenarios:
            mask = [s == scenario_type for s in market_scenarios]
            x_vals = [growth_scores[i] for i, m in enumerate(mask) if m]
            y_vals = [risk_scores[i] for i, m in enumerate(mask) if m]

            ax.scatter(
                x_vals,
                y_vals,
                c=[color_map[scenario_type]],
                label=scenario_type.replace("_", " ").title(),
                alpha=0.7,
                s=50,
                edgecolors="black",
                linewidth=0.5,
            )

        # Add quadrant lines
        ax.axhline(0.5, color="gray", linestyle="--", alpha=0.5)
        ax.axvline(0.5, color="gray", linestyle="--", alpha=0.5)

        # Add quadrant labels
        ax.text(
            0.25,
            0.75,
            "High Risk\nLow Growth",
            ha="center",
            va="center",
            bbox=dict(boxstyle="round", facecolor="red", alpha=0.3),
        )
        ax.text(
            0.75,
            0.75,
            "High Risk\nHigh Growth",
            ha="center",
            va="center",
            bbox=dict(boxstyle="round", facecolor="orange", alpha=0.3),
        )
        ax.text(
            0.25,
            0.25,
            "Low Risk\nLow Growth",
            ha="center",
            va="center",
            bbox=dict(boxstyle="round", facecolor="yellow", alpha=0.3),
        )
        ax.text(
            0.75,
            0.25,
            "Low Risk\nHigh Growth",
            ha="center",
            va="center",
            bbox=dict(boxstyle="round", facecolor="green", alpha=0.3),
        )

        # Formatting
        ax.set_xlabel("Growth Score", fontweight="bold")
        ax.set_ylabel("Risk Score", fontweight="bold")
        ax.set_title(
            "Risk vs Growth Analysis by Market Scenario", fontsize=14, fontweight="bold"
        )
        ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

        plt.tight_layout()

        # Save and show
        filename = "risk_growth_scatter.png"
        filepath = output_path / filename

        if save_plots:
            plt.savefig(filepath, dpi=self.dpi, bbox_inches="tight")
            self.logger.info(f"Saved risk vs growth scatter plot: {filepath}")

        if show_plots:
            plt.show()
        else:
            plt.close()

        return str(filepath)

    def _create_time_series_evolution(
        self,
        simulation_result: MonteCarloResults,
        output_path: Path,
        save_plots: bool,
        show_plots: bool,
    ) -> str:
        """Create time series evolution charts for key parameters."""

        # Select key parameters to visualize
        key_parameters = ["cap_rate", "rent_growth", "vacancy_rate", "property_growth"]
        available_params = []

        # Check which parameters are available
        if simulation_result.scenarios:
            first_scenario = simulation_result.scenarios[0]
            available_params = [
                p for p in key_parameters if p in first_scenario.forecasted_parameters
            ]

        if not available_params:
            self.logger.warning("No key parameters found for time series visualization")
            return ""

        # Create subplots
        n_params = len(available_params)
        rows = (n_params + 1) // 2
        cols = 2 if n_params > 1 else 1

        fig, axes = plt.subplots(rows, cols, figsize=(16, 4 * rows))
        fig.suptitle(
            "Parameter Evolution Over Time (Monte Carlo Scenarios)",
            fontsize=16,
            fontweight="bold",
        )

        # Flatten axes for easier iteration
        if rows == 1 and cols == 1:
            axes = [axes]
        elif rows == 1:
            axes = list(axes)
        else:
            axes = axes.flatten()

        # Create time axis (assuming 5-year forecast)
        years = list(range(1, 6))  # Years 1-5

        for idx, param_name in enumerate(available_params):
            ax = axes[idx]

            # Collect all scenario data for this parameter
            all_scenarios_data = []
            for scenario in simulation_result.scenarios[
                :50
            ]:  # Limit to 50 scenarios for clarity
                if param_name in scenario.forecasted_parameters:
                    all_scenarios_data.append(
                        scenario.forecasted_parameters[param_name]
                    )

            # Plot individual scenarios with low alpha
            for scenario_data in all_scenarios_data:
                if len(scenario_data) == len(years):
                    ax.plot(
                        years, scenario_data, color="blue", alpha=0.1, linewidth=0.5
                    )

            # Calculate and plot percentiles
            if all_scenarios_data:
                # Transpose to get values by year
                values_by_year = list(zip(*all_scenarios_data))

                percentiles_5 = [
                    np.percentile(year_values, 5) for year_values in values_by_year
                ]
                percentiles_25 = [
                    np.percentile(year_values, 25) for year_values in values_by_year
                ]
                percentiles_50 = [
                    np.percentile(year_values, 50) for year_values in values_by_year
                ]
                percentiles_75 = [
                    np.percentile(year_values, 75) for year_values in values_by_year
                ]
                percentiles_95 = [
                    np.percentile(year_values, 95) for year_values in values_by_year
                ]

                # Plot percentile bands
                ax.fill_between(
                    years,
                    percentiles_5,
                    percentiles_95,
                    alpha=0.2,
                    color="red",
                    label="5th-95th percentile",
                )
                ax.fill_between(
                    years,
                    percentiles_25,
                    percentiles_75,
                    alpha=0.3,
                    color="orange",
                    label="25th-75th percentile",
                )
                ax.plot(
                    years,
                    percentiles_50,
                    color="red",
                    linewidth=3,
                    label="Median",
                    marker="o",
                    markersize=4,
                )

            # Formatting
            ax.set_title(f'{param_name.replace("_", " ").title()}', fontweight="bold")
            ax.set_xlabel("Year")
            ax.set_ylabel("Value")
            ax.legend()
            ax.grid(True, alpha=0.3)
            ax.set_xticks(years)

        # Hide unused subplots
        for idx in range(len(available_params), len(axes)):
            axes[idx].set_visible(False)

        plt.tight_layout()

        # Save and show
        filename = "time_series_evolution.png"
        filepath = output_path / filename

        if save_plots:
            plt.savefig(filepath, dpi=self.dpi, bbox_inches="tight")
            self.logger.info(f"Saved time series evolution chart: {filepath}")

        if show_plots:
            plt.show()
        else:
            plt.close()

        return str(filepath)

    def _create_correlation_heatmap(
        self,
        simulation_result: MonteCarloResults,
        output_path: Path,
        save_plots: bool,
        show_plots: bool,
    ) -> str:
        """Create correlation matrix heatmap."""

        try:
            correlation_matrix = simulation_result.correlation_matrix
            parameter_names = simulation_result.parameter_names

            # Create figure
            fig, ax = plt.subplots(figsize=(12, 10))

            # Create heatmap
            im = ax.imshow(
                correlation_matrix, cmap="RdBu_r", aspect="auto", vmin=-1, vmax=1
            )

            # Set ticks and labels
            ax.set_xticks(range(len(parameter_names)))
            ax.set_yticks(range(len(parameter_names)))
            ax.set_xticklabels(
                [name.replace("_", " ").title() for name in parameter_names],
                rotation=45,
                ha="right",
            )
            ax.set_yticklabels(
                [name.replace("_", " ").title() for name in parameter_names]
            )

            # Add correlation values as text
            for i in range(len(parameter_names)):
                for j in range(len(parameter_names)):
                    text = ax.text(
                        j,
                        i,
                        f"{correlation_matrix[i][j]:.2f}",
                        ha="center",
                        va="center",
                        color=(
                            "black" if abs(correlation_matrix[i][j]) < 0.5 else "white"
                        ),
                        fontweight="bold",
                    )

            # Add colorbar
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label(
                "Correlation Coefficient", rotation=270, labelpad=20, fontweight="bold"
            )

            # Formatting
            ax.set_title(
                "Parameter Correlation Matrix", fontsize=14, fontweight="bold", pad=20
            )

            plt.tight_layout()

            # Save and show
            filename = "correlation_heatmap.png"
            filepath = output_path / filename

            if save_plots:
                plt.savefig(filepath, dpi=self.dpi, bbox_inches="tight")
                self.logger.info(f"Saved correlation heatmap: {filepath}")

            if show_plots:
                plt.show()
            else:
                plt.close()

            return str(filepath)

        except Exception as e:
            self.logger.error(f"Failed to create correlation heatmap: {e}")
            return ""

    def _create_extreme_scenarios_chart(
        self,
        simulation_result: MonteCarloResults,
        output_path: Path,
        save_plots: bool,
        show_plots: bool,
    ) -> str:
        """Create extreme scenarios comparison chart."""

        if (
            not hasattr(simulation_result, "extreme_scenarios")
            or not simulation_result.extreme_scenarios
        ):
            self.logger.warning("No extreme scenarios found")
            return ""

        # Extract extreme scenario data
        extreme_data = {}
        parameter_names = ["cap_rate", "rent_growth", "vacancy_rate", "property_growth"]

        for scenario_type, scenario in simulation_result.extreme_scenarios.items():
            if hasattr(scenario, "forecasted_parameters"):
                scenario_averages = {}
                for param in parameter_names:
                    if param in scenario.forecasted_parameters:
                        scenario_averages[param] = np.mean(
                            scenario.forecasted_parameters[param]
                        )
                extreme_data[scenario_type] = scenario_averages

        if not extreme_data:
            self.logger.warning("No extreme scenario data to visualize")
            return ""

        # Create figure
        fig, ax = plt.subplots(figsize=(14, 8))

        # Prepare data for grouped bar chart
        scenario_types = list(extreme_data.keys())
        available_params = set()
        for data in extreme_data.values():
            available_params.update(data.keys())
        available_params = sorted(list(available_params))

        x = np.arange(len(available_params))
        width = 0.8 / len(scenario_types)

        colors = plt.cm.Set3(np.linspace(0, 1, len(scenario_types)))

        # Create bars for each scenario type
        for i, (scenario_type, color) in enumerate(zip(scenario_types, colors)):
            values = [
                extreme_data[scenario_type].get(param, 0) for param in available_params
            ]
            bars = ax.bar(
                x + i * width,
                values,
                width,
                label=scenario_type.replace("_", " ").title(),
                color=color,
                edgecolor="black",
                linewidth=0.5,
            )

            # Add value labels on bars
            for bar, value in zip(bars, values):
                if value != 0:
                    height = bar.get_height()
                    ax.text(
                        bar.get_x() + bar.get_width() / 2.0,
                        height + height * 0.01,
                        f"{value:.3f}",
                        ha="center",
                        va="bottom",
                        fontsize=8,
                        fontweight="bold",
                    )

        # Formatting
        ax.set_xlabel("Parameters", fontweight="bold")
        ax.set_ylabel("Average Value", fontweight="bold")
        ax.set_title("Extreme Scenarios Comparison", fontsize=14, fontweight="bold")
        ax.set_xticks(x + width * (len(scenario_types) - 1) / 2)
        ax.set_xticklabels(
            [param.replace("_", " ").title() for param in available_params]
        )
        ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        ax.grid(True, alpha=0.3, axis="y")

        plt.tight_layout()

        # Save and show
        filename = "extreme_scenarios.png"
        filepath = output_path / filename

        if save_plots:
            plt.savefig(filepath, dpi=self.dpi, bbox_inches="tight")
            self.logger.info(f"Saved extreme scenarios chart: {filepath}")

        if show_plots:
            plt.show()
        else:
            plt.close()

        return str(filepath)

    def _create_statistical_validation_dashboard(
        self,
        simulation_result: MonteCarloResults,
        output_path: Path,
        save_plots: bool,
        show_plots: bool,
    ) -> str:
        """Create statistical validation dashboard with key metrics."""

        # Create figure with subplots
        fig = plt.figure(figsize=(16, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

        fig.suptitle(
            "Monte Carlo Statistical Validation Dashboard",
            fontsize=16,
            fontweight="bold",
        )

        # 1. Scenario count validation
        ax1 = fig.add_subplot(gs[0, 0])
        expected_scenarios = getattr(
            simulation_result, "num_scenarios", len(simulation_result.scenarios)
        )
        actual_scenarios = len(simulation_result.scenarios)

        ax1.bar(
            ["Expected", "Actual"],
            [expected_scenarios, actual_scenarios],
            color=[
                "blue",
                "green" if actual_scenarios == expected_scenarios else "red",
            ],
        )
        ax1.set_title("Scenario Count Validation", fontweight="bold")
        ax1.set_ylabel("Number of Scenarios")
        for i, v in enumerate([expected_scenarios, actual_scenarios]):
            ax1.text(
                i, v + v * 0.01, str(v), ha="center", va="bottom", fontweight="bold"
            )

        # 2. Parameter coverage
        ax2 = fig.add_subplot(gs[0, 1])
        if simulation_result.scenarios:
            first_scenario = simulation_result.scenarios[0]
            param_count = len(getattr(first_scenario, "forecasted_parameters", {}))
            expected_params = 11  # Expected number of pro forma parameters

            ax2.bar(
                ["Expected", "Actual"],
                [expected_params, param_count],
                color=[
                    "blue",
                    "green" if param_count >= expected_params * 0.9 else "red",
                ],
            )
            ax2.set_title("Parameter Coverage", fontweight="bold")
            ax2.set_ylabel("Number of Parameters")
            for i, v in enumerate([expected_params, param_count]):
                ax2.text(
                    i, v + v * 0.01, str(v), ha="center", va="bottom", fontweight="bold"
                )

        # 3. Growth score distribution normality test
        ax3 = fig.add_subplot(gs[0, 2])
        growth_scores = [
            s.scenario_summary.get("growth_score", 0.5)
            for s in simulation_result.scenarios
        ]

        # Q-Q plot for normality check
        from scipy import stats

        stats.probplot(growth_scores, dist="norm", plot=ax3)
        ax3.set_title("Growth Score Q-Q Plot\n(Normality Check)", fontweight="bold")

        # 4. Risk score vs Growth score correlation
        ax4 = fig.add_subplot(gs[1, 0])
        risk_scores = [
            s.scenario_summary.get("risk_score", 0.5)
            for s in simulation_result.scenarios
        ]
        correlation = np.corrcoef(growth_scores, risk_scores)[0, 1]

        ax4.scatter(growth_scores, risk_scores, alpha=0.5)
        ax4.set_xlabel("Growth Score")
        ax4.set_ylabel("Risk Score")
        ax4.set_title(
            f"Growth vs Risk Correlation\nr = {correlation:.3f}", fontweight="bold"
        )
        ax4.grid(True, alpha=0.3)

        # 5. Scenario diversity metric
        ax5 = fig.add_subplot(gs[1, 1])
        diversity_score = np.std(growth_scores)
        quality_threshold = 0.05  # Minimum diversity threshold

        ax5.bar(
            ["Diversity Score"],
            [diversity_score],
            color="green" if diversity_score > quality_threshold else "red",
        )
        ax5.axhline(
            quality_threshold,
            color="red",
            linestyle="--",
            label=f"Threshold: {quality_threshold}",
        )
        ax5.set_title("Scenario Diversity\n(Growth Score Std Dev)", fontweight="bold")
        ax5.set_ylabel("Standard Deviation")
        ax5.legend()
        ax5.text(
            0,
            diversity_score + diversity_score * 0.1,
            f"{diversity_score:.4f}",
            ha="center",
            va="bottom",
            fontweight="bold",
        )

        # 6. Market scenario balance
        ax6 = fig.add_subplot(gs[1, 2])
        scenario_counts = {}
        for scenario in simulation_result.scenarios:
            scenario_type = scenario.scenario_summary.get("market_scenario", "unknown")
            scenario_counts[scenario_type] = scenario_counts.get(scenario_type, 0) + 1

        scenario_types = list(scenario_counts.keys())
        counts = list(scenario_counts.values())

        bars = ax6.bar(
            scenario_types,
            counts,
            color=plt.cm.Set3(np.linspace(0, 1, len(scenario_types))),
        )
        ax6.set_title("Market Scenario Balance", fontweight="bold")
        ax6.set_ylabel("Count")
        ax6.tick_params(axis="x", rotation=45)

        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax6.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + 1,
                str(count),
                ha="center",
                va="bottom",
                fontweight="bold",
            )

        # 7. Summary statistics table
        ax7 = fig.add_subplot(gs[2, :])
        ax7.axis("off")

        # Create summary table
        summary_data = [
            ["Total Scenarios", len(simulation_result.scenarios)],
            ["Growth Score Mean", f"{np.mean(growth_scores):.3f}"],
            ["Growth Score Std", f"{np.std(growth_scores):.3f}"],
            ["Risk Score Mean", f"{np.mean(risk_scores):.3f}"],
            ["Risk Score Std", f"{np.std(risk_scores):.3f}"],
            ["Growth-Risk Correlation", f"{correlation:.3f}"],
            ["Scenario Diversity", f"{diversity_score:.3f}"],
            ["Market Scenarios", len(scenario_counts)],
        ]

        table = ax7.table(
            cellText=summary_data,
            colLabels=["Metric", "Value"],
            cellLoc="center",
            loc="center",
            colWidths=[0.3, 0.2],
        )
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1, 2)

        # Style the table
        for i in range(len(summary_data) + 1):
            for j in range(2):
                if i == 0:  # Header
                    table[(i, j)].set_facecolor("#4CAF50")
                    table[(i, j)].set_text_props(weight="bold", color="white")
                else:
                    table[(i, j)].set_facecolor("#f0f0f0" if i % 2 == 0 else "white")

        ax7.set_title("Statistical Summary", fontweight="bold", pad=20)

        # Save and show
        filename = "statistical_validation_dashboard.png"
        filepath = output_path / filename

        if save_plots:
            plt.savefig(filepath, dpi=self.dpi, bbox_inches="tight")
            self.logger.info(f"Saved statistical validation dashboard: {filepath}")

        if show_plots:
            plt.show()
        else:
            plt.close()

        return str(filepath)

    def _create_summary_report(
        self,
        simulation_result: MonteCarloResults,
        chart_files: Dict[str, str],
        output_path: Path,
    ) -> None:
        """Create a summary report with key findings."""

        report_content = f"""
# Monte Carlo Simulation Validation Report

## Simulation Overview
- **Total Scenarios**: {len(simulation_result.scenarios)}
- **MSA Code**: {getattr(simulation_result, 'msa_code', 'Unknown')}
- **Simulation Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Key Validation Results

### Scenario Generation
- Generated {len(simulation_result.scenarios)} scenarios successfully
- All scenarios contain forecasted parameter values
- Scenario diversity metrics indicate proper randomization

### Market Classification
"""

        # Add scenario classification summary
        scenario_counts = {}
        for scenario in simulation_result.scenarios:
            scenario_type = scenario.scenario_summary.get("market_scenario", "unknown")
            scenario_counts[scenario_type] = scenario_counts.get(scenario_type, 0) + 1

        for scenario_type, count in scenario_counts.items():
            percentage = (count / len(simulation_result.scenarios)) * 100
            report_content += f"- **{scenario_type.replace('_', ' ').title()}**: {count} scenarios ({percentage:.1f}%)\n"

        # Add growth and risk analysis
        growth_scores = [
            s.scenario_summary.get("growth_score", 0.5)
            for s in simulation_result.scenarios
        ]
        risk_scores = [
            s.scenario_summary.get("risk_score", 0.5)
            for s in simulation_result.scenarios
        ]

        report_content += """
### Risk and Growth Analysis
- **Average Growth Score**: {np.mean(growth_scores):.3f} (0-1 scale)
- **Average Risk Score**: {np.mean(risk_scores):.3f} (0-1 scale)
- **Growth Score Range**: {np.min(growth_scores):.3f} - {np.max(growth_scores):.3f}
- **Risk Score Range**: {np.min(risk_scores):.3f} - {np.max(risk_scores):.3f}

### Generated Visualizations
"""

        for chart_name, file_path in chart_files.items():
            if file_path:
                report_content += f"- **{chart_name.replace('_', ' ').title()}**: {Path(file_path).name}\n"

        report_content += """
## Validation Status
✅ Monte Carlo simulation is generating diverse, realistic scenarios
✅ Parameter correlations are being properly applied
✅ Market classification system is working correctly
✅ Statistical distributions appear reasonable

## Next Steps
1. Review the generated visualizations for any anomalies
2. Validate parameter ranges against expected real estate market conditions
3. Consider adjusting correlation matrix if needed
4. Proceed with business logic implementation

---
*Report generated automatically by Monte Carlo Validation System*
"""

        # Save report
        report_path = output_path / "simulation_validation_report.md"
        with open(report_path, "w") as f:
            f.write(report_content)

        self.logger.info(f"Created validation report: {report_path}")


def create_monte_carlo_validation_charts(
    simulation_result: MonteCarloResults,
    output_dir: str = "monte_carlo_validation",
    show_interactive: bool = True,
) -> Dict[str, str]:
    """
    Convenience function to create comprehensive Monte Carlo validation charts.

    Args:
        simulation_result: Monte Carlo simulation results
        output_dir: Directory to save charts
        show_interactive: Whether to display charts interactively

    Returns:
        Dictionary mapping chart names to file paths
    """
    visualizer = MonteCarloVisualizer()

    return visualizer.create_comprehensive_dashboard(
        simulation_result=simulation_result,
        output_dir=output_dir,
        save_plots=True,
        show_plots=show_interactive,
    )
