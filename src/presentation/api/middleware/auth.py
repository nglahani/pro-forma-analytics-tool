"""
Authentication Middleware

API key-based authentication for securing API endpoints.
"""

import hashlib
import hmac
import sys
import time
from pathlib import Path
from typing import Dict, Optional, Set

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from config.settings import get_settings
from core.logging_config import get_logger
from src.presentation.api.models.errors import AuthenticationError, ErrorCode

logger = get_logger(__name__)
settings = get_settings()


class APIKeyManager:
    """Manages API key validation and permissions."""

    def __init__(self):
        self._valid_keys: Dict[str, Dict[str, any]] = self._load_api_keys()
        self._rate_limits: Dict[str, Dict[str, any]] = {}

    def _load_api_keys(self) -> Dict[str, Dict[str, any]]:
        """Load valid API keys from configuration."""
        # In production, this would load from a secure store (database, vault, etc.)
        # For now, using environment-based configuration

        api_keys = {}

        # Development/testing keys
        if settings.environment.value in ["development", "testing"]:
            api_keys.update(
                {
                    "dev_test_key_12345678901234567890123": {
                        "name": "Development Test Key",
                        "permissions": ["read", "write", "admin"],
                        "rate_limit": 1000,  # Higher limit for development
                        "created_at": "2025-01-01T00:00:00Z",
                    },
                    "readonly_key_09876543210987654321098": {
                        "name": "Read-Only Test Key",
                        "permissions": ["read"],
                        "rate_limit": 500,
                        "created_at": "2025-01-01T00:00:00Z",
                    },
                }
            )

        # Production keys would be loaded from environment variables
        # Format: API_KEY_{KEY_ID}=key_value
        # Format: API_KEY_{KEY_ID}_PERMISSIONS=read,write
        # Format: API_KEY_{KEY_ID}_RATE_LIMIT=100

        return api_keys

    def validate_api_key(self, api_key: str) -> Optional[Dict[str, any]]:
        """
        Validate an API key and return its metadata.

        Args:
            api_key: The API key to validate

        Returns:
            Key metadata if valid, None if invalid
        """
        if not api_key or len(api_key) < 32:
            return None

        key_info = self._valid_keys.get(api_key)
        if key_info:
            logger.info(f"Valid API key used: {key_info['name']}")
            return key_info

        logger.warning(f"Invalid API key attempted: {api_key[:8]}...")
        return None

    def check_permission(self, api_key: str, required_permission: str) -> bool:
        """
        Check if an API key has the required permission.

        Args:
            api_key: The API key to check
            required_permission: Required permission level

        Returns:
            True if permission is granted, False otherwise
        """
        key_info = self.validate_api_key(api_key)
        if not key_info:
            return False

        permissions = key_info.get("permissions", [])
        return required_permission in permissions or "admin" in permissions

    def get_rate_limit(self, api_key: str) -> int:
        """Get rate limit for an API key."""
        key_info = self.validate_api_key(api_key)
        if not key_info:
            return 0

        return key_info.get("rate_limit", settings.api.rate_limit_requests)


# Global API key manager instance
api_key_manager = APIKeyManager()


class APIKeyAuthMiddleware(BaseHTTPMiddleware):
    """Middleware for API key authentication."""

    def __init__(self, app, exclude_paths: Optional[Set[str]] = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or {
            "/api/v1/health",
            "/api/v1/docs",
            "/api/v1/redoc",
            "/api/v1/openapi.json",
        }

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request authentication."""

        # Skip authentication for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        # Extract API key from header
        api_key = request.headers.get(settings.api.api_key_header)

        if not api_key:
            logger.warning(f"Missing API key for {request.url.path}")
            return self._create_auth_error_response(
                "API key required", "missing_api_key"
            )

        # Validate API key
        key_info = api_key_manager.validate_api_key(api_key)
        if not key_info:
            logger.warning(f"Invalid API key for {request.url.path}")
            return self._create_auth_error_response(
                "Invalid API key", "invalid_api_key"
            )

        # Add authentication context to request
        request.state.api_key = api_key
        request.state.key_info = key_info
        request.state.authenticated = True

        # Generate request ID for logging correlation
        if not hasattr(request.state, "request_id"):
            request.state.request_id = self._generate_request_id(api_key)

        logger.info(
            f"Authenticated request {request.state.request_id} "
            f"for {request.url.path} using {key_info['name']}"
        )

        return await call_next(request)

    def _create_auth_error_response(self, message: str, error_type: str) -> Response:
        """Create authentication error response."""
        from fastapi.responses import JSONResponse

        error = AuthenticationError(
            message=message, auth_method="api_key", details={"error_type": error_type}
        )

        # Convert datetime to string for JSON serialization
        error_dict = error.model_dump(mode="json")
        if "timestamp" in error_dict:
            error_dict["timestamp"] = error.timestamp.isoformat()

        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED, content=error_dict
        )

    def _generate_request_id(self, api_key: str) -> str:
        """Generate unique request ID."""
        timestamp = str(int(time.time() * 1000))
        key_hash = hashlib.md5(api_key.encode()).hexdigest()[:8]
        return f"req_{timestamp}_{key_hash}"


def require_permission(permission: str):
    """
    Dependency for requiring specific permissions.

    Args:
        permission: Required permission level

    Returns:
        FastAPI dependency function
    """

    def check_permission_dependency(request: Request):
        if (
            not hasattr(request.state, "authenticated")
            or not request.state.authenticated
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        api_key = request.state.api_key
        if not api_key_manager.check_permission(api_key, permission):
            logger.warning(
                f"Permission denied: {permission} required for "
                f"{request.url.path} using {request.state.key_info['name']}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required",
            )

        return True

    return check_permission_dependency


def get_authenticated_user(request: Request) -> Dict[str, any]:
    """
    Get authenticated user information from request.

    Args:
        request: FastAPI request object

    Returns:
        User information dictionary
    """
    if not hasattr(request.state, "authenticated") or not request.state.authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )

    return {
        "api_key": request.state.api_key[:8] + "...",  # Truncated for security
        "key_info": request.state.key_info,
        "request_id": getattr(request.state, "request_id", "unknown"),
        "permissions": request.state.key_info.get("permissions", []),
    }


# Security scheme for OpenAPI documentation
api_key_scheme = HTTPBearer(
    scheme_name="API Key", description="API key required in Authorization header"
)
