"""
Unit Tests for Dependency Injection Container

Tests the infrastructure layer dependency injection container.
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional

import pytest

from src.infrastructure.container import (
    DependencyContainer,
    create_container,
    get_container,
    set_container,
)


# Test interfaces and implementations for dependency injection testing
class ITestService(ABC):
    """Test service interface."""

    @abstractmethod
    def get_name(self) -> str:
        pass


class ITestRepository(ABC):
    """Test repository interface."""

    @abstractmethod
    def get_data(self) -> str:
        pass


class TestRepository(ITestRepository):
    """Test repository implementation."""

    def get_data(self) -> str:
        return "test_data"


class TestService(ITestService):
    """Test service implementation with dependency."""

    def __init__(self, repository: ITestRepository):
        self.repository = repository

    def get_name(self) -> str:
        return f"test_service_with_{self.repository.get_data()}"


class TestServiceWithOptionalDependency(ITestService):
    """Test service with optional dependency."""

    def __init__(
        self, repository: ITestRepository, logger: Optional[logging.Logger] = None
    ):
        self.repository = repository
        self.logger = logger

    def get_name(self) -> str:
        return "test_service_with_optional"


class TestServiceWithoutDependencies(ITestService):
    """Test service without dependencies."""

    def get_name(self) -> str:
        return "test_service_standalone"


class TestServiceWithPrimitiveDependency:
    """Test service with primitive parameter (should be skipped)."""

    def __init__(self, name: str = "default"):
        self.name = name


class TestDependencyContainer:
    """Test cases for DependencyContainer."""

    @pytest.fixture
    def container(self):
        """Create a fresh container for each test."""
        return DependencyContainer()

    def test_register_singleton_stores_service_mapping(self, container):
        """
        GIVEN a dependency container
        WHEN registering a singleton service
        THEN it should store the interface-to-implementation mapping
        """
        # Act
        container.register_singleton(ITestRepository, TestRepository)

        # Assert
        assert ITestRepository in container._services
        assert container._services[ITestRepository] == TestRepository

    def test_register_transient_stores_service_mapping(self, container):
        """
        GIVEN a dependency container
        WHEN registering a transient service
        THEN it should store the interface-to-implementation mapping
        """
        # Act
        container.register_transient(ITestRepository, TestRepository)

        # Assert
        assert ITestRepository in container._services
        assert container._services[ITestRepository] == TestRepository

    def test_register_factory_stores_factory_function(self, container):
        """
        GIVEN a dependency container
        WHEN registering a factory function
        THEN it should store the factory mapping
        """

        # Arrange
        def repository_factory():
            return TestRepository()

        # Act
        container.register_factory(ITestRepository, repository_factory)

        # Assert
        assert ITestRepository in container._factories
        assert container._factories[ITestRepository] == repository_factory

    def test_register_instance_stores_pre_created_instance(self, container):
        """
        GIVEN a dependency container
        WHEN registering a pre-created instance
        THEN it should store the instance directly
        """
        # Arrange
        instance = TestRepository()

        # Act
        container.register_instance(ITestRepository, instance)

        # Assert
        assert ITestRepository in container._singletons
        assert container._singletons[ITestRepository] is instance

    def test_resolve_returns_registered_instance(self, container):
        """
        GIVEN a registered instance
        WHEN resolving the interface
        THEN it should return the registered instance
        """
        # Arrange
        instance = TestRepository()
        container.register_instance(ITestRepository, instance)

        # Act
        resolved = container.resolve(ITestRepository)

        # Assert
        assert resolved is instance

    def test_resolve_creates_instance_from_factory(self, container):
        """
        GIVEN a registered factory
        WHEN resolving the interface
        THEN it should create instance using the factory
        """

        # Arrange
        def repository_factory():
            return TestRepository()

        container.register_factory(ITestRepository, repository_factory)

        # Act
        resolved = container.resolve(ITestRepository)

        # Assert
        assert isinstance(resolved, TestRepository)
        assert resolved.get_data() == "test_data"

    def test_resolve_creates_singleton_instance(self, container):
        """
        GIVEN a registered singleton service
        WHEN resolving multiple times
        THEN it should return the same instance
        """
        # Arrange
        container.register_singleton(ITestRepository, TestRepository)

        # Act
        first_resolve = container.resolve(ITestRepository)
        second_resolve = container.resolve(ITestRepository)

        # Assert
        assert first_resolve is second_resolve
        assert isinstance(first_resolve, TestRepository)

    def test_resolve_injects_dependencies_automatically(self, container):
        """
        GIVEN a service with dependencies
        WHEN resolving the service
        THEN it should automatically inject the dependencies
        """
        # Arrange
        container.register_singleton(ITestRepository, TestRepository)
        container.register_singleton(ITestService, TestService)

        # Act
        service = container.resolve(ITestService)

        # Assert
        assert isinstance(service, TestService)
        assert isinstance(service.repository, TestRepository)
        assert service.get_name() == "test_service_with_test_data"

    def test_resolve_handles_optional_dependencies(self, container):
        """
        GIVEN a service with optional dependencies
        WHEN resolving without registering optional dependency
        THEN it should inject None for optional dependencies
        """
        # Arrange
        container.register_singleton(ITestRepository, TestRepository)
        container.register_singleton(ITestService, TestServiceWithOptionalDependency)

        # Act
        service = container.resolve(ITestService)

        # Assert
        assert isinstance(service, TestServiceWithOptionalDependency)
        assert isinstance(service.repository, TestRepository)
        assert service.logger is None

    def test_resolve_provides_optional_dependencies_when_available(self, container):
        """
        GIVEN a service with optional dependencies
        WHEN resolving with optional dependency registered
        THEN it should inject the optional dependency
        """
        # Arrange
        logger = logging.getLogger("test")
        container.register_instance(logging.Logger, logger)
        container.register_singleton(ITestRepository, TestRepository)
        container.register_singleton(ITestService, TestServiceWithOptionalDependency)

        # Act
        service = container.resolve(ITestService)

        # Assert
        assert isinstance(service, TestServiceWithOptionalDependency)
        assert service.logger is logger

    def test_resolve_handles_services_without_dependencies(self, container):
        """
        GIVEN a service without dependencies
        WHEN resolving the service
        THEN it should create the instance successfully
        """
        # Arrange
        container.register_singleton(ITestService, TestServiceWithoutDependencies)

        # Act
        service = container.resolve(ITestService)

        # Assert
        assert isinstance(service, TestServiceWithoutDependencies)
        assert service.get_name() == "test_service_standalone"

    def test_resolve_skips_primitive_parameters_with_defaults(self, container):
        """
        GIVEN a service with primitive parameters with defaults
        WHEN resolving the service
        THEN it should skip primitive parameters and use defaults
        """
        # Arrange
        container.register_singleton(
            TestServiceWithPrimitiveDependency, TestServiceWithPrimitiveDependency
        )

        # Act
        service = container.resolve(TestServiceWithPrimitiveDependency)

        # Assert
        assert isinstance(service, TestServiceWithPrimitiveDependency)
        assert service.name == "default"

    def test_resolve_raises_value_error_for_unregistered_service(self, container):
        """
        GIVEN an empty container
        WHEN resolving an unregistered service
        THEN it should raise ValueError
        """
        # Act & Assert
        with pytest.raises(
            ValueError, match="Service ITestRepository is not registered"
        ):
            container.resolve(ITestRepository)

    def test_resolve_raises_type_error_for_missing_annotations(self, container):
        """
        GIVEN a service with unannotated required dependencies
        WHEN resolving the service
        THEN it should raise TypeError
        """

        # Arrange
        class ServiceWithUnannotatedDependency:
            def __init__(self, dependency):  # No type annotation
                self.dependency = dependency

        container.register_singleton(
            ServiceWithUnannotatedDependency, ServiceWithUnannotatedDependency
        )

        # Act & Assert
        with pytest.raises(TypeError, match="missing type annotation"):
            container.resolve(ServiceWithUnannotatedDependency)

    def test_clear_removes_all_registrations(self, container):
        """
        GIVEN a container with registered services
        WHEN clearing the container
        THEN it should remove all registrations and cached instances
        """
        # Arrange
        container.register_singleton(ITestRepository, TestRepository)
        container.register_factory(
            ITestService, lambda: TestServiceWithoutDependencies()
        )
        container.register_instance(logging.Logger, logging.getLogger("test"))

        # Act
        container.clear()

        # Assert
        assert len(container._services) == 0
        assert len(container._factories) == 0
        assert len(container._singletons) == 0

    def test_complex_dependency_chain_resolves_correctly(self, container):
        """
        GIVEN multiple services with dependency chain
        WHEN resolving the top-level service
        THEN it should resolve the entire dependency chain
        """

        # Arrange - Create a dependency chain
        class IComplexService(ABC):
            @abstractmethod
            def process(self) -> str:
                pass

        class ComplexService(IComplexService):
            def __init__(
                self, simple_service: ITestService, repository: ITestRepository
            ):
                self.simple_service = simple_service
                self.repository = repository

            def process(self) -> str:
                return f"complex_{self.simple_service.get_name()}_{self.repository.get_data()}"

        container.register_singleton(ITestRepository, TestRepository)
        container.register_singleton(ITestService, TestServiceWithoutDependencies)
        container.register_singleton(IComplexService, ComplexService)

        # Act
        complex_service = container.resolve(IComplexService)

        # Assert
        assert isinstance(complex_service, ComplexService)
        assert complex_service.process() == "complex_test_service_standalone_test_data"


class TestContainerFactoryFunctions:
    """Test cases for container factory functions."""

    def test_create_container_returns_configured_container(self):
        """
        GIVEN no parameters
        WHEN calling create_container
        THEN it should return a configured container with logger
        """
        # Act
        container = create_container()

        # Assert
        assert isinstance(container, DependencyContainer)
        assert logging.Logger in container._singletons
        logger = container._singletons[logging.Logger]
        assert isinstance(logger, logging.Logger)
        assert logger.name == "pro_forma_analytics"

    def test_get_container_returns_global_instance(self):
        """
        GIVEN no previous container
        WHEN calling get_container
        THEN it should return the global container instance
        """
        # Act
        container1 = get_container()
        container2 = get_container()

        # Assert
        assert container1 is container2
        assert isinstance(container1, DependencyContainer)

    def test_set_container_replaces_global_instance(self):
        """
        GIVEN a custom container
        WHEN setting the global container
        THEN subsequent calls should return the custom container
        """
        # Arrange
        custom_container = DependencyContainer()
        custom_container.register_instance(str, "custom_marker")

        # Act
        set_container(custom_container)

        # Assert
        retrieved_container = get_container()
        assert retrieved_container is custom_container
        assert retrieved_container.resolve(str) == "custom_marker"

        # Cleanup - reset to avoid affecting other tests
        set_container(create_container())

    @pytest.fixture(autouse=True)
    def cleanup_global_container(self):
        """Reset global container after each test."""
        yield
        # Reset global container to clean state
        set_container(create_container())
