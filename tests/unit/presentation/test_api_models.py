"""
Unit tests for API models (requests, responses, errors).
"""

from datetime import UTC, date, datetime

import pytest

from src.domain.entities.property_data import (
    InvestorEquityStructure,
    RenovationInfo,
    RenovationStatus,
    ResidentialUnits,
    SimplifiedPropertyInput,
)
from src.presentation.api.models.errors import (
    APIError,
    BusinessLogicError,
    ErrorCode,
    ValidationError,
)
from src.presentation.api.models.requests import (
    AnalysisOptions,
    BatchAnalysisRequest,
    ForecastRequest,
    MarketDataRequest,
    PropertyAnalysisRequest,
)
from src.presentation.api.models.responses import (
    AnalysisMetadata,
    ConfigurationResponse,
    HealthResponse,
)


class TestAnalysisOptions:
    """Test AnalysisOptions model validation."""

    def test_default_values(self):
        """Test that default values are set correctly."""
        options = AnalysisOptions()

        assert options.monte_carlo_simulations == 10000
        assert options.forecast_horizon_years == 6
        assert options.include_scenarios is True
        assert options.confidence_level == 0.95
        assert options.detailed_cash_flows is True

    def test_valid_ranges(self):
        """Test validation of parameter ranges."""
        options = AnalysisOptions(
            monte_carlo_simulations=1000,
            forecast_horizon_years=5,
            confidence_level=0.90,
        )

        assert options.monte_carlo_simulations == 1000
        assert options.forecast_horizon_years == 5
        assert options.confidence_level == 0.90

    def test_invalid_ranges(self):
        """Test validation fails for out-of-range values."""
        with pytest.raises(ValueError):
            AnalysisOptions(monte_carlo_simulations=100)  # Below minimum

        with pytest.raises(ValueError):
            AnalysisOptions(forecast_horizon_years=15)  # Above maximum

        with pytest.raises(ValueError):
            AnalysisOptions(confidence_level=1.1)  # Above maximum


class TestPropertyAnalysisRequest:
    """Test PropertyAnalysisRequest model validation."""

    def test_with_simplified_property_input(self):
        """Test request with valid SimplifiedPropertyInput."""
        property_data = SimplifiedPropertyInput(
            property_id="TEST_001",
            property_name="Test Property",
            analysis_date=date.today(),
            residential_units=ResidentialUnits(
                total_units=10, average_rent_per_unit=2000, unit_types="1BR and 2BR"
            ),
            renovation_info=RenovationInfo(
                status=RenovationStatus.NOT_NEEDED, anticipated_duration_months=0
            ),
            equity_structure=InvestorEquityStructure(
                investor_equity_share_pct=80.0,
                self_cash_percentage=25.0,
                number_of_investors=1,
            ),
            city="Chicago",
            state="IL",
            purchase_price=500000.0,
        )

        request = PropertyAnalysisRequest(property_data=property_data)

        assert request.property_data.property_id == "TEST_001"
        assert request.options is not None
        assert isinstance(request.options, AnalysisOptions)

    def test_default_options_creation(self):
        """Test that default options are created when not provided."""
        property_data = SimplifiedPropertyInput(
            property_id="TEST_002",
            property_name="Test Property 2",
            analysis_date=date.today(),
            residential_units=ResidentialUnits(
                total_units=5, average_rent_per_unit=1800, unit_types="Studio"
            ),
            renovation_info=RenovationInfo(
                status=RenovationStatus.NOT_NEEDED, anticipated_duration_months=0
            ),
            equity_structure=InvestorEquityStructure(
                investor_equity_share_pct=75.0,
                self_cash_percentage=30.0,
                number_of_investors=1,
            ),
            city="Miami",
            state="FL",
            purchase_price=300000.0,
        )

        request = PropertyAnalysisRequest(property_data=property_data)

        assert request.options.monte_carlo_simulations == 10000
        assert request.options.forecast_horizon_years == 6


class TestBatchAnalysisRequest:
    """Test BatchAnalysisRequest model validation."""

    def test_valid_batch_size(self):
        """Test batch request with valid number of properties."""
        property_data = SimplifiedPropertyInput(
            property_id="BATCH_001",
            property_name="Batch Property",
            analysis_date=date.today(),
            residential_units=ResidentialUnits(
                total_units=8, average_rent_per_unit=1900, unit_types="Mixed"
            ),
            renovation_info=RenovationInfo(
                status=RenovationStatus.NOT_NEEDED, anticipated_duration_months=0
            ),
            equity_structure=InvestorEquityStructure(
                investor_equity_share_pct=70.0,
                self_cash_percentage=35.0,
                number_of_investors=1,
            ),
            city="NYC",
            state="NY",
            purchase_price=800000.0,
        )

        properties = [
            PropertyAnalysisRequest(property_data=property_data) for _ in range(5)
        ]

        batch_request = BatchAnalysisRequest(properties=properties)

        assert len(batch_request.properties) == 5
        assert batch_request.parallel_processing is True
        assert batch_request.max_concurrent == 10

    def test_batch_size_limits(self):
        """Test batch size validation."""
        # Test empty batch
        with pytest.raises(ValueError):
            BatchAnalysisRequest(properties=[])


class TestMarketDataRequest:
    """Test MarketDataRequest model validation."""

    def test_supported_msa(self):
        """Test validation of supported MSAs."""
        request = MarketDataRequest(msa="NYC")
        assert request.msa == "NYC"

        request = MarketDataRequest(msa="Chicago")
        assert request.msa == "Chicago"

    def test_unsupported_msa(self):
        """Test rejection of unsupported MSAs."""
        with pytest.raises(ValueError):
            MarketDataRequest(msa="InvalidMSA")


class TestForecastRequest:
    """Test ForecastRequest model validation."""

    def test_supported_parameter(self):
        """Test validation of supported forecast parameters."""
        request = ForecastRequest(parameter="rent_growth_msa", msa="LA")

        assert request.parameter == "rent_growth_msa"
        assert request.msa == "LA"
        assert request.horizon_years == 5  # Default

    def test_unsupported_parameter(self):
        """Test rejection of unsupported parameters."""
        with pytest.raises(ValueError):
            ForecastRequest(parameter="invalid_parameter", msa="DC")


class TestAPIError:
    """Test API error models."""

    def test_basic_api_error(self):
        """Test basic APIError creation."""
        error = APIError(
            error_code=ErrorCode.VALIDATION_ERROR, message="Test validation error"
        )

        assert error.error_code == ErrorCode.VALIDATION_ERROR
        assert error.message == "Test validation error"
        assert error.details is None
        assert isinstance(error.timestamp, datetime)

    def test_validation_error(self):
        """Test ValidationError with field errors."""
        error = ValidationError(
            message="Multiple field validation errors",
            field_errors={
                "property_id": ["Field is required"],
                "purchase_price": ["Must be greater than 0"],
            },
            invalid_fields=["property_id", "purchase_price"],
        )

        assert error.error_code == ErrorCode.VALIDATION_ERROR
        assert len(error.field_errors) == 2
        assert "property_id" in error.invalid_fields

    def test_business_logic_error(self):
        """Test BusinessLogicError with rule context."""
        error = BusinessLogicError(
            message="DCF calculation failed",
            business_rule="Positive cash flow required",
            suggested_action="Increase rent or reduce expenses",
            rule_context={"negative_years": [1, 2, 3]},
        )

        assert error.error_code == ErrorCode.BUSINESS_RULE_VIOLATION
        assert error.business_rule == "Positive cash flow required"
        assert error.rule_context["negative_years"] == [1, 2, 3]


class TestResponseModels:
    """Test response model creation."""

    def test_analysis_metadata(self):
        """Test AnalysisMetadata model."""
        metadata = AnalysisMetadata(
            processing_time_seconds=12.5,
            analysis_timestamp=datetime.now(UTC),
            data_sources={"market_data": "FRED API", "forecasts": "Prophet"},
            assumptions_summary={"interest_rate": 5.5, "cap_rate": 6.0},
        )

        assert metadata.processing_time_seconds == 12.5
        assert metadata.dcf_engine_version == "1.0.0"
        assert "market_data" in metadata.data_sources

    def test_health_response(self):
        """Test HealthResponse model."""
        health = HealthResponse(
            status="healthy",
            timestamp=datetime.now(UTC),
            version="1.0.0",
            environment="testing",
            uptime_seconds=3600.0,
            dependencies={"database": "healthy", "external_api": "healthy"},
        )

        assert health.status == "healthy"
        assert health.uptime_seconds == 3600.0
        assert health.dependencies["database"] == "healthy"

    def test_configuration_response(self):
        """Test ConfigurationResponse model."""
        config = ConfigurationResponse(
            supported_msas=["NYC", "LA", "Chicago", "DC", "Miami"],
            supported_parameters=["rent_growth_msa", "multifamily_cap_rate"],
            analysis_limits={"max_batch_size": 50, "max_simulations": 50000},
            dcf_methodology={"phases": "4", "framework": "Clean Architecture"},
            api_version="1.0.0",
            last_updated=datetime.now(UTC),
        )

        assert len(config.supported_msas) == 5
        assert "NYC" in config.supported_msas
        assert config.analysis_limits["max_batch_size"] == 50
