"""
Pro-Forma Analytics Tool - Clean Architecture Implementation

This package implements a complete real estate DCF analysis engine following Clean Architecture principles.
"""

__version__ = "1.6.0"

# Export main service factory for easy access
from .application.factories.service_factory import ServiceFactory, get_service_factory

__all__ = [
    "__version__",
    "ServiceFactory",
    "get_service_factory",
]
