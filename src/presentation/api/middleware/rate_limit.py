"""
Rate Limiting Middleware

Token bucket-based rate limiting for API endpoints.
"""

import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional, Tuple

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from config.settings import get_settings
from core.logging_config import get_logger
from src.presentation.api.models.errors import RateLimitError

logger = get_logger(__name__)
settings = get_settings()


@dataclass
class TokenBucket:
    """Token bucket for rate limiting implementation."""

    capacity: int
    tokens: float = field(default_factory=lambda: 0)
    last_refill: float = field(default_factory=time.time)
    refill_rate: float = 1.0  # tokens per second

    def __post_init__(self):
        """Initialize tokens to full capacity."""
        self.tokens = float(self.capacity)

    def consume(self, tokens: int = 1) -> bool:
        """
        Attempt to consume tokens from the bucket.

        Args:
            tokens: Number of tokens to consume

        Returns:
            True if tokens were consumed, False if insufficient tokens
        """
        self._refill()

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True

        return False

    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill

        # Add tokens based on refill rate
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)

        self.last_refill = now

    def get_wait_time(self, tokens: int = 1) -> float:
        """
        Get time to wait until enough tokens are available.

        Args:
            tokens: Number of tokens needed

        Returns:
            Seconds to wait, 0 if tokens are available now
        """
        self._refill()

        if self.tokens >= tokens:
            return 0.0

        tokens_needed = tokens - self.tokens
        return tokens_needed / self.refill_rate


class RateLimitManager:
    """Manages rate limiting for API keys and IP addresses."""

    def __init__(self):
        self._buckets: Dict[str, TokenBucket] = {}
        self._cleanup_interval = 300  # 5 minutes
        self._last_cleanup = time.time()

    def get_bucket(
        self, identifier: str, capacity: int, refill_rate: float
    ) -> TokenBucket:
        """
        Get or create a token bucket for an identifier.

        Args:
            identifier: Unique identifier (API key, IP address, etc.)
            capacity: Maximum tokens in bucket
            refill_rate: Tokens added per second

        Returns:
            TokenBucket instance
        """
        if identifier not in self._buckets:
            self._buckets[identifier] = TokenBucket(
                capacity=capacity, refill_rate=refill_rate
            )

        # Periodic cleanup of old buckets
        if time.time() - self._last_cleanup > self._cleanup_interval:
            self._cleanup_old_buckets()

        return self._buckets[identifier]

    def check_rate_limit(
        self, identifier: str, capacity: int, refill_rate: float, tokens: int = 1
    ) -> Tuple[bool, float]:
        """
        Check rate limit for an identifier.

        Args:
            identifier: Unique identifier
            capacity: Maximum requests in window
            refill_rate: Requests per second refill rate
            tokens: Number of tokens to consume

        Returns:
            Tuple of (allowed, wait_time_seconds)
        """
        bucket = self.get_bucket(identifier, capacity, refill_rate)

        if bucket.consume(tokens):
            return True, 0.0

        wait_time = bucket.get_wait_time(tokens)
        return False, wait_time

    def _cleanup_old_buckets(self) -> None:
        """Remove buckets that haven't been used recently."""
        now = time.time()
        cutoff_time = now - 3600  # 1 hour

        old_keys = [
            key
            for key, bucket in self._buckets.items()
            if bucket.last_refill < cutoff_time
        ]

        for key in old_keys:
            del self._buckets[key]

        self._last_cleanup = now

        if old_keys:
            logger.info(f"Cleaned up {len(old_keys)} old rate limit buckets")


# Global rate limit manager
rate_limit_manager = RateLimitManager()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting API requests."""

    def __init__(
        self,
        app,
        default_capacity: int = 100,
        default_refill_rate: float = 1.0,
        exclude_paths: Optional[set] = None,
    ):
        super().__init__(app)
        self.default_capacity = default_capacity
        self.default_refill_rate = default_refill_rate
        self.exclude_paths = exclude_paths or {
            "/api/v1/health",
            "/api/v1/docs",
            "/api/v1/redoc",
            "/api/v1/openapi.json",
        }

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request rate limiting."""

        # Skip rate limiting for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        # Determine rate limit parameters
        capacity, refill_rate = self._get_rate_limit_params(request)
        identifier = self._get_rate_limit_identifier(request)

        # Check rate limit
        allowed, wait_time = rate_limit_manager.check_rate_limit(
            identifier=identifier, capacity=capacity, refill_rate=refill_rate, tokens=1
        )

        if not allowed:
            logger.warning(
                f"Rate limit exceeded for {identifier} on {request.url.path}. "
                f"Wait time: {wait_time:.1f}s"
            )
            return self._create_rate_limit_error_response(
                capacity, wait_time, identifier
            )

        # Add rate limit headers to response
        response = await call_next(request)
        self._add_rate_limit_headers(response, identifier, capacity, refill_rate)

        return response

    def _get_rate_limit_params(self, request: Request) -> Tuple[int, float]:
        """
        Get rate limit parameters for a request.

        Args:
            request: FastAPI request object

        Returns:
            Tuple of (capacity, refill_rate)
        """
        # Use API key-specific limits if available
        if hasattr(request.state, "key_info"):
            key_info = request.state.key_info
            capacity = key_info.get("rate_limit", self.default_capacity)
            # Calculate refill rate to replenish capacity over 1 minute
            refill_rate = capacity / 60.0
            return capacity, refill_rate

        # Use default limits
        return self.default_capacity, self.default_refill_rate

    def _get_rate_limit_identifier(self, request: Request) -> str:
        """
        Get unique identifier for rate limiting.

        Args:
            request: FastAPI request object

        Returns:
            Unique identifier string
        """
        # Use API key if available (authenticated requests)
        if hasattr(request.state, "api_key"):
            return f"key:{request.state.api_key}"

        # Fall back to IP address for unauthenticated requests
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"

    def _create_rate_limit_error_response(
        self, limit: int, wait_time: float, identifier: str
    ) -> Response:
        """Create rate limit exceeded error response."""
        from fastapi import status
        from fastapi.responses import JSONResponse

        error = RateLimitError(
            message=f"Rate limit exceeded. Limit: {limit} requests per minute",
            limit=limit,
            window_seconds=60,
            retry_after_seconds=int(wait_time) + 1,
            details={
                "identifier": (
                    identifier[:16] + "..." if len(identifier) > 16 else identifier
                ),
                "wait_time_seconds": wait_time,
            },
        )

        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content=error.model_dump(),
            headers={
                "Retry-After": str(int(wait_time) + 1),
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(time.time() + wait_time)),
            },
        )

    def _add_rate_limit_headers(
        self, response: Response, identifier: str, capacity: int, refill_rate: float
    ) -> None:
        """Add rate limit headers to successful responses."""
        try:
            bucket = rate_limit_manager.get_bucket(identifier, capacity, refill_rate)
            remaining = max(0, int(bucket.tokens))
            reset_time = int(time.time() + (capacity - bucket.tokens) / refill_rate)

            response.headers["X-RateLimit-Limit"] = str(capacity)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(reset_time)

        except Exception as e:
            logger.warning(f"Failed to add rate limit headers: {e}")


def get_rate_limit_status(identifier: str) -> Dict[str, any]:
    """
    Get current rate limit status for an identifier.

    Args:
        identifier: Rate limit identifier

    Returns:
        Dictionary with rate limit status information
    """
    bucket = rate_limit_manager._buckets.get(identifier)

    if not bucket:
        return {
            "identifier": identifier,
            "tokens_available": 0,
            "capacity": 0,
            "last_refill": None,
            "status": "no_bucket",
        }

    bucket._refill()  # Update token count

    return {
        "identifier": identifier,
        "tokens_available": int(bucket.tokens),
        "capacity": bucket.capacity,
        "refill_rate": bucket.refill_rate,
        "last_refill": bucket.last_refill,
        "status": "active",
    }
