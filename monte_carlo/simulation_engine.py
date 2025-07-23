"""
Monte Carlo Simulation Engine

Integrates Prophet forecasts with property-specific inputs to generate
probabilistic scenarios for real estate investment analysis.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from scipy.stats import multivariate_normal, norm
import json
from datetime import date

from data.databases.database_manager import db_manager
from core.logging_config import get_logger
from core.exceptions import MonteCarloError, DataNotFoundError
from core.property_inputs import PropertyInputData
from config.settings import settings


@dataclass
class MonteCarloScenario:
    """Single Monte Carlo scenario result."""
    scenario_id: int
    forecasted_parameters: Dict[str, List[float]]  # 5-year forecasts per parameter
    scenario_summary: Dict[str, float]  # Summary statistics for this scenario
    percentile_rank: Optional[float] = None  # Where this scenario ranks (0-100)
    

@dataclass
class MonteCarloResults:
    """Results from Monte Carlo simulation."""
    property_id: str
    msa_code: str
    simulation_date: date
    num_scenarios: int
    horizon_years: int
    scenarios: List[MonteCarloScenario]
    summary_statistics: Dict[str, Dict[str, float]]  # Per parameter: {mean, std, p5, p95, etc.}
    correlation_matrix: Optional[np.ndarray] = None
    parameter_names: List[str] = None  # For correlation matrix reference
    extreme_scenarios: Dict[str, MonteCarloScenario] = None  # Best/worst case scenarios
    

class MonteCarloEngine:
    """Monte Carlo simulation engine for pro forma scenarios."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.cached_forecasts: Dict[str, Dict] = {}
    
    def load_forecasts_for_msa(self, msa_code: str, horizon_years: int = 5) -> Dict[str, Dict]:
        """
        Load all Prophet forecasts for a specific MSA.
        
        Args:
            msa_code: MSA code for geographic forecasts
            horizon_years: Forecast horizon
            
        Returns:
            Dictionary of forecasts by parameter name
        """
        cache_key = f"{msa_code}_{horizon_years}"
        if cache_key in self.cached_forecasts:
            return self.cached_forecasts[cache_key]
        
        try:
            forecasts = {}
            
            # Define the 11 parameters and their geographies
            parameters = [
                # National parameters
                ('treasury_10y', 'NATIONAL'),
                ('commercial_mortgage_rate', 'NATIONAL'),
                ('fed_funds_rate', 'NATIONAL'),
                # MSA-specific parameters
                ('cap_rate', msa_code),
                ('vacancy_rate', msa_code),
                ('rent_growth', msa_code),
                ('expense_growth', msa_code),
                ('ltv_ratio', msa_code),
                ('closing_cost_pct', msa_code),
                ('lender_reserves', msa_code),
                ('property_growth', msa_code)
            ]
            
            for param_name, geo_code in parameters:
                forecast_data = db_manager.get_cached_prophet_forecast(
                    param_name, geo_code, horizon_years, max_age_days=30
                )
                
                if forecast_data:
                    forecasts[param_name] = {
                        'values': json.loads(forecast_data['forecast_values']),
                        'lower_bound': json.loads(forecast_data['lower_bound']),
                        'upper_bound': json.loads(forecast_data['upper_bound']),
                        'dates': json.loads(forecast_data['forecast_dates']),
                        'performance': json.loads(forecast_data['model_performance']),
                        'trend_info': json.loads(forecast_data['trend_info'])
                    }
                else:
                    self.logger.warning(f"No forecast found for {param_name} ({geo_code})")
            
            if len(forecasts) != 11:
                raise DataNotFoundError(
                    f"Expected 11 forecasts, found {len(forecasts)} for MSA {msa_code}"
                )
            
            self.cached_forecasts[cache_key] = forecasts
            self.logger.info(f"Loaded {len(forecasts)} forecasts for MSA {msa_code}")
            return forecasts
            
        except Exception as e:
            raise MonteCarloError(f"Failed to load forecasts for MSA {msa_code}: {e}") from e
    
    def estimate_correlation_matrix(self, forecasts: Dict[str, Dict]) -> Tuple[np.ndarray, List[str]]:
        """
        Estimate correlation matrix between parameters using economic relationships.
        
        Args:
            forecasts: Dictionary of forecast data
            
        Returns:
            Tuple of (correlation matrix, parameter names list)
        """
        try:
            param_names = list(forecasts.keys())
            n_params = len(param_names)
            
            self.logger.info(f"Estimating correlations for {n_params} parameters")
            
            # Create correlation matrix with realistic economic relationships
            correlation_matrix = np.eye(n_params)
            
            # Define correlation rules based on economic theory
            correlation_rules = {
                # Interest rate correlations (strong positive)
                ('treasury_10y', 'commercial_mortgage_rate'): 0.85,
                ('treasury_10y', 'fed_funds_rate'): 0.75,
                ('commercial_mortgage_rate', 'fed_funds_rate'): 0.70,
                
                # Growth correlations (moderate positive)
                ('rent_growth', 'property_growth'): 0.60,
                ('rent_growth', 'expense_growth'): 0.40,
                ('property_growth', 'expense_growth'): 0.35,
                
                # Market condition correlations
                ('cap_rate', 'vacancy_rate'): 0.45,        # Both reflect market stress
                ('cap_rate', 'treasury_10y'): 0.55,       # Cap rates track interest rates
                ('vacancy_rate', 'rent_growth'): -0.40,   # High vacancy suppresses rent growth
                
                # Lending requirement correlations
                ('ltv_ratio', 'closing_cost_pct'): -0.25,  # Stricter lending = higher costs
                ('ltv_ratio', 'lender_reserves'): -0.35,   # Conservative lending relationship
                ('closing_cost_pct', 'lender_reserves'): 0.30,
                
                # Economic cycle correlations
                ('treasury_10y', 'cap_rate'): 0.65,       # Both driven by risk appetite
                ('fed_funds_rate', 'vacancy_rate'): 0.25, # Economic policy effects
                ('property_growth', 'cap_rate'): -0.30,   # Inverse relationship
            }
            
            # Apply correlation rules
            for i, param1 in enumerate(param_names):
                for j, param2 in enumerate(param_names):
                    if i != j:
                        # Check both directions for correlation rules
                        correlation = None
                        if (param1, param2) in correlation_rules:
                            correlation = correlation_rules[(param1, param2)]
                        elif (param2, param1) in correlation_rules:
                            correlation = correlation_rules[(param2, param1)]
                        
                        if correlation is not None:
                            correlation_matrix[i, j] = correlation
                        else:
                            # Default small positive correlation for unspecified pairs
                            correlation_matrix[i, j] = 0.05
            
            # Ensure positive definite matrix
            correlation_matrix = self._make_positive_definite(correlation_matrix)
            
            self.logger.info("Correlation matrix estimated successfully")
            return correlation_matrix, param_names
            
        except Exception as e:
            self.logger.warning(f"Failed to estimate correlations: {e}")
            param_names = list(forecasts.keys())
            return np.eye(len(param_names)), param_names
    
    def _make_positive_definite(self, matrix: np.ndarray) -> np.ndarray:
        """Ensure matrix is positive definite for multivariate normal sampling."""
        eigenvals, eigenvecs = np.linalg.eigh(matrix)
        eigenvals = np.maximum(eigenvals, 0.01)  # Ensure positive eigenvalues
        return eigenvecs @ np.diag(eigenvals) @ eigenvecs.T
    
    def generate_scenarios(
        self, 
        property_data: PropertyInputData,
        num_scenarios: int = None,
        horizon_years: int = 5,
        use_correlations: bool = True
    ) -> MonteCarloResults:
        """
        Generate Monte Carlo scenarios for a property.
        
        Args:
            property_data: Property-specific input data
            num_scenarios: Number of scenarios to generate
            horizon_years: Forecast horizon in years
            use_correlations: Whether to model parameter correlations
            
        Returns:
            MonteCarloResults with all scenarios and statistics
        """
        if num_scenarios is None:
            num_scenarios = settings.monte_carlo.default_num_simulations
        
        try:
            self.logger.info(
                f"Generating {num_scenarios} scenarios for property {property_data.property_id}"
            )
            
            # Load forecasts for the property's MSA
            msa_code = property_data.get_msa_code()
            forecasts = self.load_forecasts_for_msa(msa_code, horizon_years)
            
            # Estimate correlation matrix
            correlation_matrix = None
            param_names = list(forecasts.keys())
            if use_correlations:
                correlation_matrix, param_names = self.estimate_correlation_matrix(forecasts)
            
            # Generate scenarios
            scenarios = []
            
            # Pre-compute means and standard deviations for each parameter
            param_stats = {}
            for param_name, forecast_data in forecasts.items():
                values = np.array(forecast_data['values'])
                lower = np.array(forecast_data['lower_bound'])
                upper = np.array(forecast_data['upper_bound'])
                
                # Estimate standard deviation from confidence intervals
                std_dev = (upper - lower) / (2 * 1.96)  # 95% CI assumption
                
                param_stats[param_name] = {
                    'mean': values,
                    'std': std_dev
                }
            
            for scenario_id in range(num_scenarios):
                scenario_params = {}
                
                if use_correlations and correlation_matrix is not None:
                    # Generate correlated samples for each year
                    for year_idx in range(horizon_years):
                        means = [param_stats[param]['mean'][year_idx] for param in param_names]
                        stds = [param_stats[param]['std'][year_idx] for param in param_names]
                        
                        # Create covariance matrix from correlation and standard deviations
                        cov_matrix = np.outer(stds, stds) * correlation_matrix
                        
                        # Sample from multivariate normal
                        samples = multivariate_normal.rvs(mean=means, cov=cov_matrix)
                        
                        # Store samples for each parameter
                        for param_idx, param_name in enumerate(param_names):
                            if param_name not in scenario_params:
                                scenario_params[param_name] = []
                            scenario_params[param_name].append(samples[param_idx])
                else:
                    # Generate independent samples
                    for param_name in param_names:
                        means = param_stats[param_name]['mean']
                        stds = param_stats[param_name]['std']
                        samples = norm.rvs(loc=means, scale=stds)
                        scenario_params[param_name] = samples.tolist()
                
                # Create comprehensive scenario summary
                scenario_summary = {
                    # Key market indicators (5-year averages)
                    'avg_cap_rate': np.mean(scenario_params.get('cap_rate', [0])),
                    'avg_rent_growth': np.mean(scenario_params.get('rent_growth', [0])),
                    'avg_expense_growth': np.mean(scenario_params.get('expense_growth', [0])),
                    'avg_vacancy_rate': np.mean(scenario_params.get('vacancy_rate', [0])),
                    'avg_property_growth': np.mean(scenario_params.get('property_growth', [0])),
                    
                    # Interest rate environment
                    'avg_treasury_rate': np.mean(scenario_params.get('treasury_10y', [0])),
                    'avg_mortgage_rate': np.mean(scenario_params.get('commercial_mortgage_rate', [0])),
                    
                    # Market scenario classification
                    'market_scenario': self._classify_market_scenario(scenario_params),
                    
                    # Volatility measures
                    'rent_growth_volatility': np.std(scenario_params.get('rent_growth', [0])),
                    'cap_rate_volatility': np.std(scenario_params.get('cap_rate', [0])),
                    
                    # Composite scores
                    'growth_score': self._calculate_growth_score(scenario_params),
                    'risk_score': self._calculate_risk_score(scenario_params)
                }
                
                scenarios.append(MonteCarloScenario(
                    scenario_id=scenario_id,
                    forecasted_parameters=scenario_params,
                    scenario_summary=scenario_summary
                ))
            
            # Calculate summary statistics across all scenarios
            summary_stats = self._calculate_summary_statistics(scenarios, param_names)
            
            # Identify extreme scenarios
            extreme_scenarios = self._identify_extreme_scenarios(scenarios)
            
            # Calculate percentile ranks for scenarios
            self._calculate_percentile_ranks(scenarios)
            
            results = MonteCarloResults(
                property_id=property_data.property_id,
                msa_code=msa_code,
                simulation_date=date.today(),
                num_scenarios=num_scenarios,
                horizon_years=horizon_years,
                scenarios=scenarios,
                summary_statistics=summary_stats,
                correlation_matrix=correlation_matrix,
                parameter_names=param_names,
                extreme_scenarios=extreme_scenarios
            )
            
            self.logger.info(f"Generated {num_scenarios} scenarios successfully")
            return results
            
        except Exception as e:
            raise MonteCarloError(f"Failed to generate scenarios: {e}") from e
    
    def _calculate_summary_statistics(
        self, 
        scenarios: List[MonteCarloScenario], 
        param_names: List[str]
    ) -> Dict[str, Dict[str, float]]:
        """Calculate summary statistics across all scenarios."""
        
        summary_stats = {}
        percentiles = settings.monte_carlo.percentiles
        
        for param_name in param_names:
            # Collect all values for this parameter across scenarios
            all_values = []
            for scenario in scenarios:
                if param_name in scenario.forecasted_parameters:
                    all_values.extend(scenario.forecasted_parameters[param_name])
            
            if all_values:
                stats = {
                    'mean': float(np.mean(all_values)),
                    'std': float(np.std(all_values)),
                    'min': float(np.min(all_values)),
                    'max': float(np.max(all_values))
                }
                
                # Add percentiles
                for p in percentiles:
                    stats[f'p{p}'] = float(np.percentile(all_values, p))
                
                summary_stats[param_name] = stats
        
        return summary_stats
    
    def _classify_market_scenario(self, scenario_params: Dict[str, List[float]]) -> str:
        """Classify market scenario as bull, bear, or neutral based on key metrics."""
        
        # Calculate composite growth and risk indicators
        growth_score = self._calculate_growth_score(scenario_params)
        risk_score = self._calculate_risk_score(scenario_params)
        
        # Classification thresholds
        if growth_score > 0.6 and risk_score < 0.4:
            return "bull_market"
        elif growth_score < 0.4 and risk_score > 0.6:
            return "bear_market"
        elif growth_score > 0.7:  # High growth even with some risk
            return "growth_market"
        elif risk_score > 0.7:    # High risk even with decent growth
            return "stress_market"
        else:
            return "neutral_market"
    
    def _calculate_growth_score(self, scenario_params: Dict[str, List[float]]) -> float:
        """Calculate composite growth score (0-1 scale) based on growth metrics."""
        
        score_components = []
        
        # Rent growth (positive contributor)
        if 'rent_growth' in scenario_params:
            rent_growth_avg = np.mean(scenario_params['rent_growth'])
            # Normalize: 0% = 0, 6% = 1
            rent_score = min(max(rent_growth_avg / 0.06, 0), 1)
            score_components.append(('rent_growth', rent_score, 0.3))
        
        # Property growth (positive contributor)
        if 'property_growth' in scenario_params:
            prop_growth_avg = np.mean(scenario_params['property_growth'])
            # Normalize: 0% = 0, 8% = 1
            prop_score = min(max(prop_growth_avg / 0.08, 0), 1)
            score_components.append(('property_growth', prop_score, 0.25))
        
        # Cap rate (negative contributor - lower cap rates = higher growth)
        if 'cap_rate' in scenario_params:
            cap_rate_avg = np.mean(scenario_params['cap_rate'])
            # Normalize: 8% = 0, 4% = 1 (inverted)
            cap_score = min(max((0.08 - cap_rate_avg) / 0.04, 0), 1)
            score_components.append(('cap_rate', cap_score, 0.25))
        
        # Vacancy rate (negative contributor)
        if 'vacancy_rate' in scenario_params:
            vacancy_avg = np.mean(scenario_params['vacancy_rate'])
            # Normalize: 15% = 0, 3% = 1 (inverted)
            vacancy_score = min(max((0.15 - vacancy_avg) / 0.12, 0), 1)
            score_components.append(('vacancy_rate', vacancy_score, 0.2))
        
        # Calculate weighted average
        if score_components:
            total_weight = sum(weight for _, _, weight in score_components)
            weighted_sum = sum(score * weight for _, score, weight in score_components) 
            return weighted_sum / total_weight
        
        return 0.5  # Neutral if no components available
    
    def _calculate_risk_score(self, scenario_params: Dict[str, List[float]]) -> float:
        """Calculate composite risk score (0-1 scale) based on risk metrics."""
        
        score_components = []
        
        # Interest rate risk
        if 'treasury_10y' in scenario_params:
            treasury_avg = np.mean(scenario_params['treasury_10y'])
            # Normalize: 2% = 0, 7% = 1
            treasury_score = min(max((treasury_avg - 0.02) / 0.05, 0), 1)
            score_components.append(('treasury_risk', treasury_score, 0.2))
        
        if 'commercial_mortgage_rate' in scenario_params:
            mortgage_avg = np.mean(scenario_params['commercial_mortgage_rate'])
            # Normalize: 3% = 0, 8% = 1
            mortgage_score = min(max((mortgage_avg - 0.03) / 0.05, 0), 1)
            score_components.append(('mortgage_risk', mortgage_score, 0.25))
        
        # Market risk
        if 'cap_rate' in scenario_params:
            cap_rate_avg = np.mean(scenario_params['cap_rate'])
            cap_volatility = np.std(scenario_params['cap_rate'])
            # High cap rates and high volatility = high risk
            cap_level_score = min(max((cap_rate_avg - 0.04) / 0.04, 0), 1)
            cap_vol_score = min(max(cap_volatility / 0.02, 0), 1)  # 2% std = max
            cap_risk_score = (cap_level_score + cap_vol_score) / 2
            score_components.append(('cap_risk', cap_risk_score, 0.25))
        
        # Vacancy risk
        if 'vacancy_rate' in scenario_params:
            vacancy_avg = np.mean(scenario_params['vacancy_rate'])
            vacancy_volatility = np.std(scenario_params['vacancy_rate'])
            # High vacancy and high volatility = high risk
            vacancy_level_score = min(max((vacancy_avg - 0.03) / 0.12, 0), 1)
            vacancy_vol_score = min(max(vacancy_volatility / 0.05, 0), 1)  # 5% std = max
            vacancy_risk_score = (vacancy_level_score + vacancy_vol_score) / 2
            score_components.append(('vacancy_risk', vacancy_risk_score, 0.15))
        
        # Lending risk (LTV constraints)
        if 'ltv_ratio' in scenario_params:
            ltv_avg = np.mean(scenario_params['ltv_ratio'])
            # Lower LTV = higher lending risk/tighter standards
            ltv_score = min(max((0.80 - ltv_avg) / 0.10, 0), 1)
            score_components.append(('lending_risk', ltv_score, 0.15))
        
        # Calculate weighted average
        if score_components:
            total_weight = sum(weight for _, _, weight in score_components)
            weighted_sum = sum(score * weight for _, score, weight in score_components)
            return weighted_sum / total_weight
        
        return 0.5  # Neutral if no components available
    
    def _identify_extreme_scenarios(self, scenarios: List[MonteCarloScenario]) -> Dict[str, MonteCarloScenario]:
        """Identify best case, worst case, and other extreme scenarios."""
        
        if not scenarios:
            return {}
        
        extreme_scenarios = {}
        
        # Sort by growth score
        growth_sorted = sorted(scenarios, key=lambda s: s.scenario_summary.get('growth_score', 0.5))
        extreme_scenarios['worst_growth'] = growth_sorted[0]
        extreme_scenarios['best_growth'] = growth_sorted[-1]
        
        # Sort by risk score
        risk_sorted = sorted(scenarios, key=lambda s: s.scenario_summary.get('risk_score', 0.5))
        extreme_scenarios['lowest_risk'] = risk_sorted[0]
        extreme_scenarios['highest_risk'] = risk_sorted[-1]
        
        # Find scenarios with highest rent growth
        if any('rent_growth' in s.forecasted_parameters for s in scenarios):
            rent_sorted = sorted(scenarios, 
                               key=lambda s: np.mean(s.forecasted_parameters.get('rent_growth', [0])))
            extreme_scenarios['highest_rent_growth'] = rent_sorted[-1]
            extreme_scenarios['lowest_rent_growth'] = rent_sorted[0]
        
        # Find scenarios with extreme cap rates
        if any('cap_rate' in s.forecasted_parameters for s in scenarios):
            cap_sorted = sorted(scenarios,
                              key=lambda s: np.mean(s.forecasted_parameters.get('cap_rate', [0])))
            extreme_scenarios['lowest_cap_rate'] = cap_sorted[0]
            extreme_scenarios['highest_cap_rate'] = cap_sorted[-1]
        
        return extreme_scenarios
    
    def _calculate_percentile_ranks(self, scenarios: List[MonteCarloScenario]) -> None:
        """Calculate and assign percentile ranks to scenarios based on growth score."""
        
        if not scenarios:
            return
        
        # Extract growth scores
        growth_scores = [s.scenario_summary.get('growth_score', 0.5) for s in scenarios]
        
        # Calculate percentile ranks
        for i, scenario in enumerate(scenarios):
            scenario_score = growth_scores[i]
            # Count scenarios with lower scores
            lower_count = sum(1 for score in growth_scores if score < scenario_score)
            percentile = (lower_count / len(scenarios)) * 100
            scenario.percentile_rank = percentile
    
    def save_results(self, results: MonteCarloResults) -> None:
        """Save Monte Carlo results to database."""
        try:
            # Save to monte_carlo_results table
            results_data = {
                'simulation_id': f"{results.property_id}_{results.simulation_date.isoformat()}",
                'geographic_code': results.msa_code,
                'forecast_horizon_years': results.horizon_years,
                'result_statistics': json.dumps(results.summary_statistics),
                'simulation_date': results.simulation_date.isoformat()
            }
            
            db_manager.insert_data('forecast_cache', 'monte_carlo_results', results_data)
            
            self.logger.info(f"Saved Monte Carlo results for property {results.property_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to save Monte Carlo results: {e}")


# Global Monte Carlo engine instance
monte_carlo_engine = MonteCarloEngine()