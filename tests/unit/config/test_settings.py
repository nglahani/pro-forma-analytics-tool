"""
Unit Tests for Environment Configuration System

Tests the enhanced settings system with multi-environment support,
security validation, and API-ready configuration.
"""

import os
from unittest.mock import patch

import pytest

from config.settings import (
    Environment,
    Settings,
    get_settings,
    reload_settings,
)
from core.exceptions import ConfigurationError


class TestEnvironmentDetection:
    """Test environment detection and validation."""

    def test_default_environment_should_be_development(self):
        """
        GIVEN no environment variable is set
        WHEN creating settings
        THEN environment should default to development
        """
        with patch.dict(os.environ, {}, clear=True):
            with patch.dict(os.environ, {"FRED_API_KEY": "test_key"}, clear=False):
                settings = Settings()
                assert settings.environment == Environment.DEVELOPMENT
                assert settings.is_development()
                assert not settings.is_production()
                assert not settings.is_testing()

    def test_environment_from_environment_variable(self):
        """
        GIVEN PRO_FORMA_ENV environment variable is set
        WHEN creating settings
        THEN environment should match the variable
        """
        with patch.dict(
            os.environ, {"PRO_FORMA_ENV": "testing", "FRED_API_KEY": "test_key"}
        ):
            settings = Settings()
            assert settings.environment == Environment.TESTING
            assert settings.is_testing()

    def test_invalid_environment_should_raise_error(self):
        """
        GIVEN invalid environment name
        WHEN creating settings
        THEN should raise ConfigurationError
        """
        with patch.dict(os.environ, {"PRO_FORMA_ENV": "invalid_env"}):
            with pytest.raises(ConfigurationError) as exc_info:
                Settings()

            assert "Invalid environment: invalid_env" in str(exc_info.value)
            assert "development" in str(exc_info.value)
            assert "testing" in str(exc_info.value)
            assert "production" in str(exc_info.value)


class TestProductionValidation:
    """Test production environment validation."""

    def test_production_without_fred_api_key_should_raise_error(self):
        """
        GIVEN production environment without FRED_API_KEY
        WHEN creating settings
        THEN should raise ConfigurationError
        """
        with patch.dict(os.environ, {"PRO_FORMA_ENV": "production"}, clear=True):
            with pytest.raises(ConfigurationError) as exc_info:
                Settings()

            assert "FRED_API_KEY environment variable is required in production" in str(
                exc_info.value
            )

    def test_production_with_default_secret_key_should_raise_error(self):
        """
        GIVEN production environment with default SECRET_KEY
        WHEN creating settings
        THEN should raise ConfigurationError
        """
        with patch.dict(
            os.environ,
            {
                "PRO_FORMA_ENV": "production",
                "FRED_API_KEY": "valid_key",
                "SECRET_KEY": "dev-secret-key-change-in-production",
            },
        ):
            with pytest.raises(ConfigurationError) as exc_info:
                Settings()

            assert "SECRET_KEY environment variable must be set in production" in str(
                exc_info.value
            )

    def test_production_with_valid_configuration_should_succeed(self):
        """
        GIVEN production environment with valid configuration
        WHEN creating settings
        THEN should succeed without errors
        """
        with patch.dict(
            os.environ,
            {
                "PRO_FORMA_ENV": "production",
                "FRED_API_KEY": "valid_fred_key",
                "SECRET_KEY": "production-secret-key",
            },
        ):
            settings = Settings()
            assert settings.is_production()
            assert settings.external_apis.fred_api_key == "valid_fred_key"
            assert settings.api.secret_key == "production-secret-key"


class TestAPISettings:
    """Test API configuration settings."""

    def test_api_settings_development_defaults(self):
        """
        GIVEN development environment
        WHEN loading API settings
        THEN should have debug and reload enabled
        """
        with patch.dict(
            os.environ, {"PRO_FORMA_ENV": "development", "FRED_API_KEY": "test"}
        ):
            settings = Settings()

            assert settings.api.debug is True
            assert settings.api.reload is True
            assert settings.api.host == "127.0.0.1"
            assert settings.api.port == 8000
            assert settings.api.allowed_origins == ["*"]

    def test_api_settings_production_configuration(self):
        """
        GIVEN production environment
        WHEN loading API settings
        THEN should have debug and reload disabled
        """
        with patch.dict(
            os.environ,
            {
                "PRO_FORMA_ENV": "production",
                "FRED_API_KEY": "test",
                "SECRET_KEY": "prod-secret",
            },
        ):
            settings = Settings()

            assert settings.api.debug is False
            assert settings.api.reload is False

    def test_api_settings_from_environment_variables(self):
        """
        GIVEN API configuration environment variables
        WHEN loading API settings
        THEN should use environment values
        """
        with patch.dict(
            os.environ,
            {
                "PRO_FORMA_ENV": "development",
                "API_HOST": "0.0.0.0",
                "API_PORT": "9000",
                "API_WORKERS": "4",
                "SECRET_KEY": "custom-secret",
                "ALLOWED_ORIGINS": "http://localhost:3000,https://myapp.com",
                "RATE_LIMIT_REQUESTS": "200",
                "RATE_LIMIT_WINDOW": "120",
                "FRED_API_KEY": "test",
            },
        ):
            settings = Settings()

            assert settings.api.host == "0.0.0.0"
            assert settings.api.port == 9000
            assert settings.api.workers == 4
            assert settings.api.secret_key == "custom-secret"
            assert settings.api.allowed_origins == [
                "http://localhost:3000",
                "https://myapp.com",
            ]
            assert settings.api.rate_limit_requests == 200
            assert settings.api.rate_limit_window_seconds == 120

    def test_allowed_origins_wildcard_handling(self):
        """
        GIVEN ALLOWED_ORIGINS set to wildcard
        WHEN loading API settings
        THEN should handle wildcard correctly
        """
        with patch.dict(os.environ, {"ALLOWED_ORIGINS": "*", "FRED_API_KEY": "test"}):
            settings = Settings()
            assert settings.api.allowed_origins == ["*"]


class TestDatabaseSettings:
    """Test database configuration settings."""

    def test_database_settings_development(self):
        """
        GIVEN development environment
        WHEN loading database settings
        THEN should use development defaults
        """
        with patch.dict(
            os.environ, {"PRO_FORMA_ENV": "development", "FRED_API_KEY": "test"}
        ):
            settings = Settings()
            assert settings.database.base_path == "data/databases"

    def test_database_settings_testing(self):
        """
        GIVEN testing environment
        WHEN loading database settings
        THEN should use test database path
        """
        with patch.dict(
            os.environ, {"PRO_FORMA_ENV": "testing", "FRED_API_KEY": "test"}
        ):
            settings = Settings()
            assert settings.database.base_path == "data/databases/test"

    def test_database_settings_production(self):
        """
        GIVEN production environment with database configuration
        WHEN loading database settings
        THEN should use production values
        """
        with patch.dict(
            os.environ,
            {
                "PRO_FORMA_ENV": "production",
                "FRED_API_KEY": "test",
                "SECRET_KEY": "prod-secret",
                "DB_BASE_PATH": "/opt/proforma/databases",
                "DB_BACKUP_FREQUENCY": "3",
            },
        ):
            settings = Settings()
            assert settings.database.base_path == "/opt/proforma/databases"
            assert settings.database.backup_frequency_days == 3


class TestExternalAPISettings:
    """Test external API configuration."""

    def test_external_api_fred_key_from_environment(self):
        """
        GIVEN FRED_API_KEY environment variable
        WHEN loading external API settings
        THEN should use environment value
        """
        with patch.dict(os.environ, {"FRED_API_KEY": "my_fred_key"}):
            settings = Settings()
            assert settings.external_apis.fred_api_key == "my_fred_key"

    def test_external_api_fred_key_empty_when_not_set(self):
        """
        GIVEN no FRED_API_KEY environment variable
        WHEN loading external API settings
        THEN should be empty string
        """
        with patch.dict(os.environ, {}, clear=True):
            # Patch out validation for this test
            with patch.object(Settings, "_validate_configuration"):
                settings = Settings()
                assert settings.external_apis.fred_api_key == ""


class TestSettingsUtilityFunctions:
    """Test utility functions for settings management."""

    def test_get_settings_returns_global_instance(self):
        """
        GIVEN settings module
        WHEN calling get_settings()
        THEN should return global settings instance
        """
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2

    def test_reload_settings_creates_new_instance(self):
        """
        GIVEN existing settings
        WHEN calling reload_settings()
        THEN should create new settings instance
        """
        with patch.dict(os.environ, {"FRED_API_KEY": "test"}):
            original_settings = get_settings()
            new_settings = reload_settings()

            # Should be different objects but same configuration
            assert new_settings is not original_settings
            assert new_settings.environment == original_settings.environment

    def test_settings_to_dict_excludes_sensitive_data(self):
        """
        GIVEN settings instance
        WHEN converting to dictionary
        THEN should exclude sensitive information
        """
        with patch.dict(os.environ, {"FRED_API_KEY": "secret_key"}):
            settings = Settings()
            settings_dict = settings.to_dict()

            # Should include non-sensitive configuration
            assert "environment" in settings_dict
            assert "api" in settings_dict
            assert "database" in settings_dict

            # Should not include sensitive data
            assert "fred_api_key" not in str(settings_dict)
            assert "secret_key" not in str(settings_dict).lower()

            # But should include non-sensitive external API info
            assert "external_apis" in settings_dict
            assert "fred_base_url" in settings_dict["external_apis"]


class TestSettingsEdgeCases:
    """Test edge cases and error scenarios."""

    def test_invalid_integer_environment_variables(self):
        """
        GIVEN invalid integer environment variables
        WHEN creating settings
        THEN should handle gracefully or raise appropriate error
        """
        with patch.dict(
            os.environ, {"API_PORT": "not_a_number", "FRED_API_KEY": "test"}
        ):
            with pytest.raises(ValueError):
                Settings()

    def test_settings_with_minimal_environment(self):
        """
        GIVEN minimal environment configuration
        WHEN creating settings
        THEN should use sensible defaults
        """
        with patch.dict(os.environ, {"FRED_API_KEY": "test"}, clear=True):
            settings = Settings()

            # Should have reasonable defaults
            assert settings.environment == Environment.DEVELOPMENT
            assert settings.api.host == "127.0.0.1"
            assert settings.api.port == 8000
            assert settings.database.base_path == "data/databases"

    def test_environment_case_insensitive(self):
        """
        GIVEN environment variable with different case
        WHEN creating settings
        THEN should handle case insensitively
        """
        with patch.dict(
            os.environ,
            {
                "PRO_FORMA_ENV": "PRODUCTION",
                "FRED_API_KEY": "test",
                "SECRET_KEY": "prod",
            },
        ):
            settings = Settings()
            assert settings.environment == Environment.PRODUCTION

    def test_settings_database_path_helper_methods(self):
        """
        GIVEN settings instance
        WHEN using path helper methods
        THEN should return correct paths
        """
        with patch.dict(os.environ, {"FRED_API_KEY": "test"}):
            settings = Settings()

            # Test path helpers
            data_path = settings.get_data_path("test", "file.db")
            cache_path = settings.get_cache_path("forecasts", "cached.json")

            assert "data" in str(data_path)
            assert "test" in str(data_path)
            assert "file.db" in str(data_path)

            assert "cache" in str(cache_path)
            assert "forecasts" in str(cache_path)
            assert "cached.json" in str(cache_path)
