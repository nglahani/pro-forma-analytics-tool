"""
Comprehensive unit tests for ServiceFactory.
Tests all methods including error scenarios for complete coverage.
"""

import logging
from unittest.mock import Mock, patch

from src.application.factories.service_factory import (
    ServiceFactory,
    create_all_services,
    get_service_factory,
)
from src.application.services.cash_flow_projection_service import (
    CashFlowProjectionService,
)
from src.application.services.dcf_assumptions_service import DCFAssumptionsService
from src.application.services.financial_metrics_service import FinancialMetricsService
from src.application.services.initial_numbers_service import InitialNumbersService


class TestServiceFactory:
    """Comprehensive tests for ServiceFactory class."""

    def test_factory_initialization(self):
        """Test factory initializes with logger."""
        factory = ServiceFactory()

        assert factory.logger is not None
        assert isinstance(factory.logger, logging.Logger)
        assert factory.logger.name == "pro_forma_analytics"

    def test_create_logger_configuration(self):
        """Test logger is properly configured."""
        factory = ServiceFactory()
        logger = factory.logger

        # Should have INFO level
        assert logger.level == logging.INFO

        # Should have at least one handler
        assert len(logger.handlers) >= 1

        # Handler should have formatter
        handler = logger.handlers[0]
        assert handler.formatter is not None

    def test_create_logger_no_duplicate_handlers(self):
        """Test logger doesn't create duplicate handlers."""
        # Create two factories to test handler reuse
        factory1 = ServiceFactory()
        initial_handler_count = len(factory1.logger.handlers)

        factory2 = ServiceFactory()
        final_handler_count = len(factory2.logger.handlers)

        # Handler count should not increase
        assert final_handler_count == initial_handler_count

    def test_create_dcf_assumptions_service(self):
        """Test DCF assumptions service creation."""
        factory = ServiceFactory()
        service = factory.create_dcf_assumptions_service()

        assert isinstance(service, DCFAssumptionsService)
        assert service is not None

    def test_create_initial_numbers_service(self):
        """Test initial numbers service creation."""
        factory = ServiceFactory()
        service = factory.create_initial_numbers_service()

        assert isinstance(service, InitialNumbersService)
        assert service is not None

    def test_create_cash_flow_projection_service(self):
        """Test cash flow projection service creation."""
        factory = ServiceFactory()
        service = factory.create_cash_flow_projection_service()

        assert isinstance(service, CashFlowProjectionService)
        assert service is not None

    def test_create_financial_metrics_service(self):
        """Test financial metrics service creation."""
        factory = ServiceFactory()
        service = factory.create_financial_metrics_service()

        assert isinstance(service, FinancialMetricsService)
        assert service is not None

    def test_services_are_unique_instances(self):
        """Test each service creation returns a new instance."""
        factory = ServiceFactory()

        # Create services twice
        dcf1 = factory.create_dcf_assumptions_service()
        dcf2 = factory.create_dcf_assumptions_service()

        initial1 = factory.create_initial_numbers_service()
        initial2 = factory.create_initial_numbers_service()

        # Should be different instances
        assert dcf1 is not dcf2
        assert initial1 is not initial2

    def test_validate_services_health_all_healthy(self):
        """Test validate_services_health when all services are healthy."""
        factory = ServiceFactory()
        health_status = factory.validate_services_health()

        expected_services = [
            "dcf_assumptions",
            "initial_numbers",
            "cash_flow_projection",
            "financial_metrics",
        ]

        assert len(health_status) == len(expected_services)
        for service_name in expected_services:
            assert service_name in health_status
            assert health_status[service_name] is True

    @patch("src.application.factories.service_factory.DCFAssumptionsService")
    def test_validate_services_health_dcf_assumptions_failure(self, mock_dcf_service):
        """Test validate_services_health handles DCF assumptions service failure."""
        # Setup mock to raise exception
        mock_dcf_service.side_effect = Exception("DCF service creation failed")

        factory = ServiceFactory()
        health_status = factory.validate_services_health()

        assert health_status["dcf_assumptions"] is False
        # Other services should still be healthy
        assert health_status["initial_numbers"] is True
        assert health_status["cash_flow_projection"] is True
        assert health_status["financial_metrics"] is True

    @patch("src.application.factories.service_factory.InitialNumbersService")
    def test_validate_services_health_initial_numbers_failure(
        self, mock_initial_service
    ):
        """Test validate_services_health handles initial numbers service failure."""
        mock_initial_service.side_effect = Exception(
            "Initial numbers service creation failed"
        )

        factory = ServiceFactory()
        health_status = factory.validate_services_health()

        assert health_status["initial_numbers"] is False
        # Other services should still be healthy
        assert health_status["dcf_assumptions"] is True
        assert health_status["cash_flow_projection"] is True
        assert health_status["financial_metrics"] is True

    @patch("src.application.factories.service_factory.CashFlowProjectionService")
    def test_validate_services_health_cash_flow_failure(self, mock_cf_service):
        """Test validate_services_health handles cash flow service failure."""
        mock_cf_service.side_effect = Exception("Cash flow service creation failed")

        factory = ServiceFactory()
        health_status = factory.validate_services_health()

        assert health_status["cash_flow_projection"] is False
        # Other services should still be healthy
        assert health_status["dcf_assumptions"] is True
        assert health_status["initial_numbers"] is True
        assert health_status["financial_metrics"] is True

    @patch("src.application.factories.service_factory.FinancialMetricsService")
    def test_validate_services_health_financial_metrics_failure(self, mock_fm_service):
        """Test validate_services_health handles financial metrics service failure."""
        mock_fm_service.side_effect = Exception(
            "Financial metrics service creation failed"
        )

        factory = ServiceFactory()
        health_status = factory.validate_services_health()

        assert health_status["financial_metrics"] is False
        # Other services should still be healthy
        assert health_status["dcf_assumptions"] is True
        assert health_status["initial_numbers"] is True
        assert health_status["cash_flow_projection"] is True

    @patch("src.application.factories.service_factory.DCFAssumptionsService")
    @patch("src.application.factories.service_factory.InitialNumbersService")
    @patch("src.application.factories.service_factory.CashFlowProjectionService")
    @patch("src.application.factories.service_factory.FinancialMetricsService")
    def test_validate_services_health_all_failures(
        self, mock_fm, mock_cf, mock_initial, mock_dcf
    ):
        """Test validate_services_health when all services fail."""
        # Setup all mocks to fail
        mock_dcf.side_effect = Exception("DCF failed")
        mock_initial.side_effect = Exception("Initial failed")
        mock_cf.side_effect = Exception("Cash flow failed")
        mock_fm.side_effect = Exception("Financial metrics failed")

        factory = ServiceFactory()
        health_status = factory.validate_services_health()

        # All should be False
        assert health_status["dcf_assumptions"] is False
        assert health_status["initial_numbers"] is False
        assert health_status["cash_flow_projection"] is False
        assert health_status["financial_metrics"] is False


class TestGlobalServiceFactory:
    """Test global service factory functions."""

    def test_get_service_factory_singleton(self):
        """Test get_service_factory returns singleton instance."""
        # Clear any existing factory
        import src.application.factories.service_factory as factory_module

        factory_module._factory = None

        # Get factory twice
        factory1 = get_service_factory()
        factory2 = get_service_factory()

        # Should be same instance
        assert factory1 is factory2
        assert isinstance(factory1, ServiceFactory)

    def test_get_service_factory_initialization(self):
        """Test get_service_factory properly initializes factory."""
        # Clear any existing factory
        import src.application.factories.service_factory as factory_module

        factory_module._factory = None

        factory = get_service_factory()

        assert factory is not None
        assert isinstance(factory, ServiceFactory)
        assert factory.logger is not None

    def test_create_all_services_returns_all_services(self):
        """Test create_all_services returns all expected services."""
        services = create_all_services()

        expected_services = [
            "dcf_assumptions",
            "initial_numbers",
            "cash_flow_projection",
            "financial_metrics",
        ]

        assert len(services) == len(expected_services)
        for service_name in expected_services:
            assert service_name in services
            assert services[service_name] is not None

    def test_create_all_services_correct_types(self):
        """Test create_all_services returns correct service types."""
        services = create_all_services()

        assert isinstance(services["dcf_assumptions"], DCFAssumptionsService)
        assert isinstance(services["initial_numbers"], InitialNumbersService)
        assert isinstance(services["cash_flow_projection"], CashFlowProjectionService)
        assert isinstance(services["financial_metrics"], FinancialMetricsService)

    def test_create_all_services_uses_global_factory(self):
        """Test create_all_services uses the global factory instance."""
        # Clear any existing factory
        import src.application.factories.service_factory as factory_module

        factory_module._factory = None

        # Create services
        services = create_all_services()

        # Global factory should now be set
        global_factory = get_service_factory()
        assert global_factory is not None

        # Should have created valid services
        assert len(services) == 4
        for service in services.values():
            assert service is not None

    def test_factory_module_level_functionality(self):
        """Test module-level variables and functions work correctly."""
        import src.application.factories.service_factory as factory_module

        # Reset factory
        factory_module._factory = None

        # Get factory should create new instance
        factory1 = get_service_factory()
        assert factory1 is not None

        # Module should now have factory set
        assert factory_module._factory is factory1

        # Second call should return same instance
        factory2 = get_service_factory()
        assert factory2 is factory1


class TestServiceFactoryIntegration:
    """Integration tests for ServiceFactory."""

    def test_factory_creates_working_services(self):
        """Test factory creates services that can be used."""
        factory = ServiceFactory()

        # Create all services
        dcf_service = factory.create_dcf_assumptions_service()
        initial_service = factory.create_initial_numbers_service()
        cf_service = factory.create_cash_flow_projection_service()
        fm_service = factory.create_financial_metrics_service()

        # All services should have expected attributes/methods
        assert hasattr(
            dcf_service, "create_dcf_assumptions_from_scenario"
        )  # Check for expected method
        assert hasattr(initial_service, "calculate_initial_numbers")
        assert hasattr(cf_service, "calculate_cash_flow_projection")
        assert hasattr(fm_service, "calculate_financial_metrics")

    def test_factory_logging_functionality(self):
        """Test factory logging works correctly."""
        factory = ServiceFactory()

        # Logger should be configured
        assert factory.logger.name == "pro_forma_analytics"
        assert factory.logger.level == logging.INFO

        # Should be able to log without errors
        factory.logger.info("Test message")
        factory.logger.warning("Test warning")
        factory.logger.error("Test error")

    def test_health_check_logs_errors(self):
        """Test health check properly logs errors."""
        with patch(
            "src.application.factories.service_factory.DCFAssumptionsService"
        ) as mock_service:
            mock_service.side_effect = Exception("Test error")

            factory = ServiceFactory()

            # Mock logger to capture calls
            factory.logger = Mock(spec=logging.Logger)

            health_status = factory.validate_services_health()

            # Should have logged error
            assert health_status["dcf_assumptions"] is False
            factory.logger.error.assert_called()

            # Error message should contain the exception
            error_call = factory.logger.error.call_args[0][0]
            assert "DCF Assumptions Service health check failed" in error_call
            assert "Test error" in error_call

    def test_multiple_factory_instances_independent(self):
        """Test multiple factory instances are independent."""
        factory1 = ServiceFactory()
        factory2 = ServiceFactory()

        # Should be different instances
        assert factory1 is not factory2

        # Should both work independently
        service1 = factory1.create_dcf_assumptions_service()
        service2 = factory2.create_dcf_assumptions_service()

        assert service1 is not service2
        assert isinstance(service1, DCFAssumptionsService)
        assert isinstance(service2, DCFAssumptionsService)
