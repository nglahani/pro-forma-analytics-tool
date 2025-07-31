"""
Edge Case Tests for Infrastructure Layer

Tests for error scenarios, edge cases, and boundary conditions
in the infrastructure layer.
"""

import pytest

from src.infrastructure.service_factory import ServiceFactory, get_service_factory, create_all_services


class TestServiceFactoryEdgeCases:
    """Test service factory error scenarios and edge cases."""

    def test_service_factory_creation(self):
        """Test service factory basic functionality."""
        factory = ServiceFactory()
        
        # All services should be created successfully
        dcf_service = factory.create_dcf_assumptions_service()
        initial_service = factory.create_initial_numbers_service()
        cash_flow_service = factory.create_cash_flow_projection_service()
        metrics_service = factory.create_financial_metrics_service()
        
        assert dcf_service is not None
        assert initial_service is not None
        assert cash_flow_service is not None
        assert metrics_service is not None

    def test_service_factory_multiple_instances(self):
        """Test that factory creates new service instances each time."""
        factory = ServiceFactory()
        
        # Create services multiple times
        dcf_service1 = factory.create_dcf_assumptions_service()
        dcf_service2 = factory.create_dcf_assumptions_service()
        
        # Should be different instances
        assert dcf_service1 is not dcf_service2

    def test_global_service_factory_singleton(self):
        """Test that global factory is singleton."""
        factory1 = get_service_factory()
        factory2 = get_service_factory()
        
        # Should be the same instance
        assert factory1 is factory2

    def test_create_all_services_function(self):
        """Test create_all_services helper function."""
        services = create_all_services()
        
        # Verify all services are created
        assert 'dcf_assumptions' in services
        assert 'initial_numbers' in services
        assert 'cash_flow_projection' in services
        assert 'financial_metrics' in services
        
        # Verify services are not None
        assert services['dcf_assumptions'] is not None
        assert services['initial_numbers'] is not None
        assert services['cash_flow_projection'] is not None
        assert services['financial_metrics'] is not None

    def test_service_factory_logger_creation(self):
        """Test that service factory creates logger properly."""
        factory = ServiceFactory()
        
        # Logger should be created
        assert factory.logger is not None
        assert factory.logger.name == "pro_forma_analytics"

    def test_service_types_are_correct(self):
        """Test that created services are of correct types."""
        from src.application.services.dcf_assumptions_service import DCFAssumptionsService
        from src.application.services.initial_numbers_service import InitialNumbersService
        from src.application.services.cash_flow_projection_service import CashFlowProjectionService
        from src.application.services.financial_metrics_service import FinancialMetricsService
        
        factory = ServiceFactory()
        
        dcf_service = factory.create_dcf_assumptions_service()
        initial_service = factory.create_initial_numbers_service()
        cash_flow_service = factory.create_cash_flow_projection_service()
        metrics_service = factory.create_financial_metrics_service()
        
        assert isinstance(dcf_service, DCFAssumptionsService)
        assert isinstance(initial_service, InitialNumbersService)
        assert isinstance(cash_flow_service, CashFlowProjectionService)
        assert isinstance(metrics_service, FinancialMetricsService)