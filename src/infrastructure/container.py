"""
Dependency Injection Container

Implements IoC container for clean architecture dependency management.
"""

from typing import Dict, Type, Any, Optional, Callable
import logging
from pathlib import Path


class DependencyContainer:
    """
    Simple dependency injection container for managing dependencies.
    
    Supports singleton and transient lifetimes, factory functions,
    and automatic dependency resolution.
    """
    
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable] = {}
        self._singletons: Dict[Type, Any] = {}
        self._logger = logging.getLogger(__name__)
    
    def register_singleton(self, interface: Type, implementation: Type) -> None:
        """
        Register a service as singleton (one instance for the container lifetime).
        
        Args:
            interface: The interface/abstract class
            implementation: The concrete implementation
        """
        self._services[interface] = implementation
        self._logger.debug(f"Registered singleton: {interface.__name__} -> {implementation.__name__}")
    
    def register_transient(self, interface: Type, implementation: Type) -> None:
        """
        Register a service as transient (new instance each time).
        
        Args:
            interface: The interface/abstract class
            implementation: The concrete implementation
        """
        self._services[interface] = implementation
        # Don't use singleton cache for transient services
        self._logger.debug(f"Registered transient: {interface.__name__} -> {implementation.__name__}")
    
    def register_factory(self, interface: Type, factory: Callable) -> None:
        """
        Register a factory function for creating instances.
        
        Args:
            interface: The interface/abstract class
            factory: Factory function that returns an instance
        """
        self._factories[interface] = factory
        self._logger.debug(f"Registered factory: {interface.__name__}")
    
    def register_instance(self, interface: Type, instance: Any) -> None:
        """
        Register a pre-created instance.
        
        Args:
            interface: The interface/abstract class
            instance: The pre-created instance
        """
        self._singletons[interface] = instance
        self._logger.debug(f"Registered instance: {interface.__name__}")
    
    def resolve(self, interface: Type) -> Any:
        """
        Resolve a service instance.
        
        Args:
            interface: The interface/abstract class to resolve
            
        Returns:
            Instance of the requested service
            
        Raises:
            ValueError: If service is not registered
            TypeError: If dependencies cannot be resolved
        """
        # Check for pre-created instance
        if interface in self._singletons:
            return self._singletons[interface]
        
        # Check for factory
        if interface in self._factories:
            factory = self._factories[interface]
            instance = factory()
            # Cache if it's meant to be a singleton
            if interface in self._services:
                self._singletons[interface] = instance
            return instance
        
        # Check for registered service
        if interface not in self._services:
            raise ValueError(f"Service {interface.__name__} is not registered")
        
        implementation = self._services[interface]
        
        # Check if already created (singleton)
        if interface in self._singletons:
            return self._singletons[interface]
        
        # Create new instance with dependency injection
        instance = self._create_instance(implementation)
        
        # Cache for singleton pattern
        self._singletons[interface] = instance
        
        return instance
    
    def _create_instance(self, implementation: Type) -> Any:
        """
        Create an instance with automatic dependency injection.
        
        Args:
            implementation: The concrete class to instantiate
            
        Returns:
            New instance with dependencies injected
        """
        import inspect
        
        # Get constructor signature
        signature = inspect.signature(implementation.__init__)
        parameters = signature.parameters
        
        # Skip 'self' parameter
        param_names = [name for name in parameters.keys() if name != 'self']
        
        # Resolve dependencies
        dependencies = {}
        for param_name in param_names:
            param = parameters[param_name]
            
            # Skip parameters with default values unless they're type-annotated
            if param.default != inspect.Parameter.empty and param.annotation == inspect.Parameter.empty:
                continue
            
            # Get type annotation
            if param.annotation == inspect.Parameter.empty:
                raise TypeError(
                    f"Cannot resolve dependency '{param_name}' for {implementation.__name__}: "
                    "missing type annotation"
                )
            
            param_type = param.annotation
            
            # Handle Optional types
            if hasattr(param_type, '__origin__') and param_type.__origin__ is type(Optional[int]).__origin__:
                # This is Optional[T], extract T
                inner_type = param_type.__args__[0]
                try:
                    dependencies[param_name] = self.resolve(inner_type)
                except ValueError:
                    # Optional dependency not available
                    dependencies[param_name] = None
            else:
                # Required dependency
                dependencies[param_name] = self.resolve(param_type)
        
        self._logger.debug(f"Creating {implementation.__name__} with dependencies: {list(dependencies.keys())}")
        
        return implementation(**dependencies)
    
    def clear(self) -> None:
        """Clear all registrations and cached instances."""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()
        self._logger.debug("Container cleared")


def create_container() -> DependencyContainer:
    """
    Factory function to create and configure the dependency container.
    
    Returns:
        Configured DependencyContainer instance
    """
    container = DependencyContainer()
    
    # Configure logging
    logger = logging.getLogger("pro_forma_analytics")
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    container.register_instance(logging.Logger, logger)
    
    return container


# Global container instance (can be replaced with proper IoC container in production)
_container: Optional[DependencyContainer] = None


def get_container() -> DependencyContainer:
    """Get the global container instance."""
    global _container
    if _container is None:
        _container = create_container()
    return _container


def set_container(container: DependencyContainer) -> None:
    """Set the global container instance (useful for testing)."""
    global _container
    _container = container