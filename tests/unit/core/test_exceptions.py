"""
Unit Tests for Custom Exceptions

Tests the standardized exception handling with error codes and context.
"""

import pytest

from core.exceptions import (
    APIError,
    ConfigurationError,
    DatabaseError,
    DataNotFoundError,
    ErrorCode,
    ForecastError,
    MonteCarloError,
    ProFormaAnalyticsError,
    PropertyDataError,
    ValidationError,
)


class TestErrorCode:
    """Test cases for ErrorCode enum."""

    def test_error_codes_have_correct_format(self):
        """
        GIVEN ErrorCode enum values
        WHEN checking their format
        THEN they should follow the pattern E[category][number]
        """
        for error_code in ErrorCode:
            assert error_code.value.startswith("E")
            assert len(error_code.value) == 5  # E + 4 digits
            assert error_code.value[1:].isdigit()

    def test_error_codes_are_unique(self):
        """
        GIVEN all ErrorCode values
        WHEN checking for uniqueness
        THEN all error codes should be unique
        """
        error_values = [code.value for code in ErrorCode]
        assert len(error_values) == len(set(error_values))

    def test_error_codes_are_categorized_correctly(self):
        """
        GIVEN error codes by category
        WHEN checking their numbering
        THEN they should be in correct ranges
        """
        # Data errors should be 1000-1999
        data_errors = [code for code in ErrorCode if code.value.startswith("E1")]
        assert all(1000 <= int(code.value[1:]) <= 1999 for code in data_errors)

        # Database errors should be 2000-2999
        db_errors = [code for code in ErrorCode if code.value.startswith("E2")]
        assert all(2000 <= int(code.value[1:]) <= 2999 for code in db_errors)


class TestProFormaAnalyticsError:
    """Test cases for base ProFormaAnalyticsError."""

    def test_basic_exception_creation(self):
        """
        GIVEN a basic error message
        WHEN creating ProFormaAnalyticsError
        THEN it should store the message correctly
        """
        # Act
        error = ProFormaAnalyticsError("Test error message")

        # Assert
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.error_code is None
        assert error.context == {}
        assert error.cause is None

    def test_exception_with_error_code(self):
        """
        GIVEN an error message and error code
        WHEN creating ProFormaAnalyticsError
        THEN it should format the message with error code
        """
        # Act
        error = ProFormaAnalyticsError("Test error", ErrorCode.DATA_NOT_FOUND)

        # Assert
        assert str(error) == "[E1001] Test error"
        assert error.error_code == ErrorCode.DATA_NOT_FOUND

    def test_exception_with_context(self):
        """
        GIVEN an error with context information
        WHEN creating ProFormaAnalyticsError
        THEN it should include context in string representation
        """
        # Arrange
        context = {"parameter": "cap_rate", "msa": "35620"}

        # Act
        error = ProFormaAnalyticsError(
            "Test error", ErrorCode.DATA_NOT_FOUND, context=context
        )

        # Assert
        assert "[E1001]" in str(error)
        assert "Test error" in str(error)
        assert "Context: parameter=cap_rate, msa=35620" in str(error)
        assert error.context == context

    def test_exception_with_cause(self):
        """
        GIVEN an error with a causing exception
        WHEN creating ProFormaAnalyticsError
        THEN it should store the cause
        """
        # Arrange
        original_error = ValueError("Original problem")

        # Act
        error = ProFormaAnalyticsError("Wrapped error", cause=original_error)

        # Assert
        assert error.cause is original_error

    def test_to_dict_serialization(self):
        """
        GIVEN a complete ProFormaAnalyticsError
        WHEN serializing to dictionary
        THEN it should include all relevant information
        """
        # Arrange
        context = {"field": "value"}
        cause = ValueError("Original error")
        error = ProFormaAnalyticsError(
            "Test error", ErrorCode.VALIDATION_FAILED, context=context, cause=cause
        )

        # Act
        error_dict = error.to_dict()

        # Assert
        assert error_dict["error_type"] == "ProFormaAnalyticsError"
        assert error_dict["message"] == "Test error"
        assert error_dict["error_code"] == "E3001"
        assert error_dict["context"] == context
        assert error_dict["cause"] == "Original error"


class TestDataNotFoundError:
    """Test cases for DataNotFoundError."""

    def test_basic_data_not_found_error(self):
        """
        GIVEN basic DataNotFoundError
        WHEN creating the exception
        THEN it should have correct default values
        """
        # Act
        error = DataNotFoundError()

        # Assert
        assert error.message == "Required data not found"
        assert error.error_code == ErrorCode.DATA_NOT_FOUND
        assert "[E1001]" in str(error)

    def test_data_not_found_with_parameter_info(self):
        """
        GIVEN parameter information
        WHEN creating DataNotFoundError
        THEN it should include parameter details in context
        """
        # Act
        error = DataNotFoundError(
            "Cap rate data not found",
            parameter_name="cap_rate",
            geographic_code="35620",
            date_range="2020-2023",
        )

        # Assert
        assert error.message == "Cap rate data not found"
        assert error.context["parameter_name"] == "cap_rate"
        assert error.context["geographic_code"] == "35620"
        assert error.context["date_range"] == "2020-2023"
        assert "parameter_name=cap_rate" in str(error)


class TestForecastError:
    """Test cases for ForecastError."""

    def test_forecast_error_with_model_info(self):
        """
        GIVEN forecasting model information
        WHEN creating ForecastError
        THEN it should include model details in context
        """
        # Act
        error = ForecastError(
            "Prophet model failed to converge",
            model_type="prophet",
            parameter_name="rent_growth",
            horizon_years=5,
        )

        # Assert
        assert error.error_code == ErrorCode.FORECAST_MODEL_FAILED
        assert error.context["model_type"] == "prophet"
        assert error.context["parameter_name"] == "rent_growth"
        assert error.context["horizon_years"] == 5


class TestDatabaseError:
    """Test cases for DatabaseError."""

    def test_database_error_with_operation_info(self):
        """
        GIVEN database operation information
        WHEN creating DatabaseError
        THEN it should include operation details in context
        """
        # Act
        error = DatabaseError(
            "Failed to insert data", operation="INSERT", table_name="historical_data"
        )

        # Assert
        assert error.error_code == ErrorCode.DATABASE_QUERY_FAILED
        assert error.context["operation"] == "INSERT"
        assert error.context["table_name"] == "historical_data"


class TestValidationError:
    """Test cases for ValidationError."""

    def test_validation_error_with_field_info(self):
        """
        GIVEN field validation information
        WHEN creating ValidationError
        THEN it should include field details in context
        """
        # Act
        error = ValidationError(
            "Invalid date format",
            field_name="start_date",
            field_value="invalid-date",
            expected_type="ISO date string",
        )

        # Assert
        assert error.error_code == ErrorCode.VALIDATION_FAILED
        assert error.context["field_name"] == "start_date"
        assert error.context["field_value"] == "invalid-date"
        assert error.context["expected_type"] == "ISO date string"


class TestConfigurationError:
    """Test cases for ConfigurationError."""

    def test_configuration_error_with_config_info(self):
        """
        GIVEN configuration information
        WHEN creating ConfigurationError
        THEN it should include config details in context
        """
        # Act
        error = ConfigurationError(
            "Missing database configuration",
            config_key="database.path",
            config_file="settings.py",
        )

        # Assert
        assert error.error_code == ErrorCode.CONFIG_INVALID
        assert error.context["config_key"] == "database.path"
        assert error.context["config_file"] == "settings.py"


class TestAPIError:
    """Test cases for APIError."""

    def test_api_error_with_request_info(self):
        """
        GIVEN API request information
        WHEN creating APIError
        THEN it should include request details in context
        """
        # Act
        error = APIError(
            "FRED API request failed",
            api_endpoint="/data/series",
            status_code=429,
            response_data="Rate limit exceeded",
        )

        # Assert
        assert error.error_code == ErrorCode.API_REQUEST_FAILED
        assert error.context["api_endpoint"] == "/data/series"
        assert error.context["status_code"] == 429
        assert error.context["response_data"] == "Rate limit exceeded"


class TestMonteCarloError:
    """Test cases for MonteCarloError."""

    def test_monte_carlo_error_with_simulation_info(self):
        """
        GIVEN Monte Carlo simulation information
        WHEN creating MonteCarloError
        THEN it should include simulation details in context
        """
        # Act
        error = MonteCarloError(
            "Simulation failed to complete", num_scenarios=1000, simulation_id="sim_001"
        )

        # Assert
        assert error.error_code == ErrorCode.MONTE_CARLO_EXECUTION_FAILED
        assert error.context["num_scenarios"] == 1000
        assert error.context["simulation_id"] == "sim_001"


class TestPropertyDataError:
    """Test cases for PropertyDataError."""

    def test_property_data_error_with_property_info(self):
        """
        GIVEN property information
        WHEN creating PropertyDataError
        THEN it should include property details in context
        """
        # Act
        error = PropertyDataError(
            "Invalid property configuration",
            property_id="PROP_001",
            property_type="multifamily",
        )

        # Assert
        assert error.error_code == ErrorCode.PROPERTY_DATA_INVALID
        assert error.context["property_id"] == "PROP_001"
        assert error.context["property_type"] == "multifamily"


class TestExceptionChaining:
    """Test cases for exception chaining and context preservation."""

    def test_exception_chaining_preserves_context(self):
        """
        GIVEN a chain of exceptions
        WHEN wrapping one exception in another
        THEN context should be preserved throughout the chain
        """
        # Arrange
        original_error = ValueError("Database connection failed")

        # Act
        db_error = DatabaseError(
            "Failed to query data", operation="SELECT", cause=original_error
        )

        app_error = ProFormaAnalyticsError(
            "Application error occurred",
            ErrorCode.DATA_NOT_FOUND,
            context={"layer": "application"},
            cause=db_error,
        )

        # Assert
        assert app_error.cause is db_error
        assert db_error.cause is original_error
        assert "Database connection failed" in str(app_error.cause.cause)

    def test_nested_error_serialization(self):
        """
        GIVEN nested exceptions
        WHEN serializing to dictionary
        THEN all levels should be represented
        """
        # Arrange
        original = ValueError("Root cause")
        wrapper = DataNotFoundError("Data missing", cause=original)

        # Act
        serialized = wrapper.to_dict()

        # Assert
        assert serialized["cause"] == "Root cause"
        assert serialized["error_type"] == "DataNotFoundError"
        assert serialized["error_code"] == "E1001"


class TestExceptionInheritance:
    """Test cases for exception inheritance hierarchy."""

    def test_all_custom_exceptions_inherit_from_base(self):
        """
        GIVEN all custom exception classes
        WHEN checking inheritance
        THEN they should all inherit from ProFormaAnalyticsError
        """
        custom_exceptions = [
            DataNotFoundError,
            ForecastError,
            DatabaseError,
            ValidationError,
            ConfigurationError,
            APIError,
            MonteCarloError,
            PropertyDataError,
        ]

        for exception_class in custom_exceptions:
            assert issubclass(exception_class, ProFormaAnalyticsError)
            assert issubclass(exception_class, Exception)

    def test_exception_can_be_caught_by_base_class(self):
        """
        GIVEN specific exception types
        WHEN catching with base exception
        THEN they should be caught correctly
        """
        # Test that specific exceptions can be caught by base class
        with pytest.raises(ProFormaAnalyticsError):
            raise DataNotFoundError("Test error")

        with pytest.raises(ProFormaAnalyticsError):
            raise ForecastError("Test error")

        with pytest.raises(Exception):
            raise ValidationError("Test error")
