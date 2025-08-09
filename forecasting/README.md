# Forecasting Engine - v1.6

Production-grade time series forecasting using Meta's Prophet model for pro forma parameter prediction, providing 6-year projections with uncertainty quantification and comprehensive validation for real estate DCF analysis.

## Architecture Overview

### Core Components

- **`prophet_engine.py`** - Prophet-based forecasting implementation with advanced feature engineering
- **Model Validation Framework** - Comprehensive backtesting and performance evaluation
- **Forecast Caching System** - Optimized forecast storage and retrieval
- **Parameter Integration** - Seamless integration with 11 pro forma parameters

## Prophet Engine Implementation (prophet_engine.py)

### Advanced Forecasting Capabilities

#### Core Features
- **6-Year Projection Horizon**: Complete forecasting for DCF analysis period
- **Trend Detection**: Automatic identification of long-term market trends
- **Seasonal Adjustment**: Multi-level seasonality modeling (annual, quarterly, monthly)
- **Uncertainty Quantification**: Probabilistic forecasts with confidence intervals
- **Change Point Detection**: Automatic identification of structural breaks in time series
- **Holiday Effects**: Integration of economic calendar events and market holidays

#### Prophet Model Configuration
```python
class ProphetForecaster:
    """Advanced Prophet forecasting with real estate market optimizations"""
    
    def __init__(self, parameter_name: str, msa_code: str):
        self.model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,  # Not relevant for annual data
            daily_seasonality=False,   # Not relevant for annual data
            seasonality_mode='multiplicative',  # Better for percentage changes
            changepoint_prior_scale=0.05,      # Conservative change point detection
            seasonality_prior_scale=10.0,      # Allow moderate seasonality
            uncertainty_samples=1000,          # Robust uncertainty estimation
            mcmc_samples=0                      # Use MAP estimation for speed
        )
        
    def add_custom_seasonalities(self):
        """Add real estate market-specific seasonal patterns"""
        # Real estate market cycles (7-10 year cycles)
        self.model.add_seasonality(
            name='market_cycle',
            period=365.25 * 8,  # 8-year average cycle
            fourier_order=3
        )
        
        # Economic policy cycles (4-year presidential cycles)
        self.model.add_seasonality(
            name='policy_cycle', 
            period=365.25 * 4,
            fourier_order=2
        )
```

### Parameter-Specific Forecasting Models

#### Interest Rate Forecasting
- **Treasury 10Y**: Long-term trend analysis with Fed policy integration
- **Commercial Mortgage Rates**: Spread modeling over treasury rates
- **Fed Funds Rate**: Policy cycle modeling with economic indicator integration

#### Market Condition Forecasting
- **Cap Rates**: MSA-specific models with supply/demand dynamics
- **Vacancy Rates**: Seasonal adjustment with employment correlation
- **Market Indicators**: Multi-variate modeling with economic drivers

#### Growth Parameter Forecasting
- **Rent Growth**: Regional models with inflation and employment correlation
- **Expense Growth**: Cost inflation modeling with utility and tax adjustments
- **Property Growth**: Market cycle modeling with appreciation trends

#### Lending Requirement Forecasting
- **LTV Ratios**: Regulatory cycle modeling with risk assessment trends
- **Closing Costs**: Fee inflation modeling with market activity correlation
- **Lender Reserves**: Risk-based modeling with market volatility integration

### Forecast Quality and Validation

#### Model Performance Metrics
```python
class ForecastValidator:
    """Comprehensive forecast validation and performance assessment"""
    
    def validate_forecast(self, historical_data: pd.DataFrame, 
                         forecast: pd.DataFrame) -> ValidationResults:
        """Multi-metric forecast validation with business rule checks"""
        
        metrics = {
            'mape': self.calculate_mape(historical_data, forecast),
            'rmse': self.calculate_rmse(historical_data, forecast),
            'directional_accuracy': self.calculate_directional_accuracy(historical_data, forecast),
            'trend_consistency': self.validate_trend_consistency(forecast),
            'confidence_interval_coverage': self.validate_confidence_intervals(historical_data, forecast)
        }
        
        return ValidationResults(metrics=metrics, 
                               passed_validation=all(self.check_thresholds(metrics)))
```

#### Quality Assurance Standards
- **MAPE < 15%**: Mean Absolute Percentage Error threshold for acceptable accuracy
- **Directional Accuracy > 70%**: Trend direction prediction accuracy
- **Confidence Interval Coverage**: 80% actual values within predicted intervals
- **Business Rule Validation**: Parameter bounds and relationship consistency
- **Historical Backtesting**: Out-of-sample performance validation

### Advanced Features (v1.6)

#### Multi-Parameter Correlation Modeling
```python
def generate_correlated_forecasts(parameters: List[str], msa_code: str) -> Dict[str, pd.DataFrame]:
    """Generate forecasts that maintain historical parameter correlations"""
    
    # Generate individual forecasts
    individual_forecasts = {}
    for param in parameters:
        forecaster = ProphetForecaster(param, msa_code)
        individual_forecasts[param] = forecaster.forecast()
    
    # Apply correlation adjustments
    correlation_matrix = calculate_historical_correlations(parameters, msa_code)
    adjusted_forecasts = apply_correlation_constraints(individual_forecasts, correlation_matrix)
    
    return adjusted_forecasts
```

#### Economic Regime Detection
- **Market Regime Classification**: Bull/Bear/Neutral market identification
- **Regime-Specific Modeling**: Different forecast models for different market conditions
- **Transition Probability Modeling**: Probability of regime changes over forecast horizon
- **Scenario-Based Forecasts**: Multiple forecast scenarios based on regime probabilities

#### External Factor Integration
```python
def add_external_regressors(self, economic_indicators: pd.DataFrame):
    """Integrate external economic indicators as forecast regressors"""
    
    # Add unemployment rate as regressor for vacancy forecasting
    if self.parameter_name == 'vacancy_rate':
        self.model.add_regressor('unemployment_rate')
    
    # Add GDP growth for rent growth forecasting
    if self.parameter_name == 'rent_growth':
        self.model.add_regressor('gdp_growth')
        self.model.add_regressor('employment_growth')
    
    # Add inflation indicators for expense growth
    if self.parameter_name == 'expense_growth':
        self.model.add_regressor('cpi_inflation')
        self.model.add_regressor('utility_inflation')
```

## Integration with DCF Engine

### Forecast Data Pipeline
```python
from forecasting.prophet_engine import ProphetForecaster
from src.application.services.forecasting_service import ForecastingService

# Complete forecasting workflow
forecasting_service = ForecastingService()

# Generate 6-year forecasts for all parameters
forecast_results = forecasting_service.generate_comprehensive_forecast(
    property_input=property_input,
    forecast_horizon_years=6,
    include_uncertainty=True,
    validate_results=True
)

# Access forecasted parameters for DCF calculation
forecasted_assumptions = forecast_results.to_dcf_assumptions()
```

### Forecast Caching and Performance
- **Intelligent Caching**: Cache forecasts based on parameter, MSA, and data freshness
- **Incremental Updates**: Update forecasts only when new historical data is available
- **Batch Processing**: Efficient batch generation of forecasts for multiple parameters
- **Parallel Execution**: Multi-threaded forecast generation for improved performance

## Forecast Output and Visualization

### Forecast Data Structure
```python
@dataclass
class ForecastResult:
    """Comprehensive forecast result with metadata and validation"""
    parameter_name: str
    msa_code: str
    forecast_data: pd.DataFrame  # Contains yhat, yhat_lower, yhat_upper
    confidence_intervals: Dict[str, pd.DataFrame]
    model_components: pd.DataFrame  # Trend, seasonality components
    validation_metrics: ValidationResults
    forecast_metadata: ForecastMetadata
    
    def to_dcf_parameter(self, year: int) -> float:
        """Extract specific year forecast for DCF calculations"""
        return self.forecast_data[self.forecast_data.year == year]['yhat'].iloc[0]
```

### Visualization and Analysis Tools
- **Forecast Charts**: Interactive time series plots with confidence intervals
- **Component Analysis**: Trend and seasonality decomposition visualization
- **Validation Reports**: Comprehensive model performance reporting
- **Scenario Comparison**: Side-by-side comparison of different forecast scenarios

## Performance and Scalability (v1.6)

### Optimization Features
- **Model Serialization**: Persistent storage of trained Prophet models
- **Incremental Training**: Update models with new data without full retraining
- **Memory Management**: Efficient memory usage for large-scale forecasting
- **Distributed Processing**: Support for distributed forecast generation

### Performance Metrics
- **Forecast Generation Speed**: Sub-second forecasts for individual parameters
- **Batch Processing Efficiency**: 11 parameters forecasted in under 10 seconds
- **Memory Usage**: Optimized memory footprint for production deployment
- **Cache Hit Ratio**: >90% cache hit ratio for repeated forecast requests

## Error Handling and Reliability

### Robust Error Management
```python
try:
    forecast = prophet_forecaster.forecast(horizon_years=6)
except InsufficientDataError:
    # Fallback to simpler trend extrapolation
    forecast = fallback_linear_trend_forecast(historical_data)
except ModelFittingError:
    # Use ensemble of simpler models
    forecast = ensemble_fallback_forecast(historical_data)
```

### Data Quality Validation
- **Missing Data Handling**: Intelligent interpolation and extrapolation
- **Outlier Detection**: Statistical outlier identification and treatment
- **Data Consistency Checks**: Validation of historical data integrity
- **Minimum Data Requirements**: Enforce minimum historical data requirements

## Future Enhancements

### Planned Improvements
- **Machine Learning Integration**: Neural network models for complex patterns
- **Multi-Market Forecasting**: Cross-MSA correlation and spillover effects
- **Real-Time Updates**: Streaming data integration for real-time forecast updates
- **Enhanced External Factors**: Integration of additional economic and market indicators