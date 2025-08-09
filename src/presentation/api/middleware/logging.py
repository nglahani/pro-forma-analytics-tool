"""
Request Logging Middleware

Comprehensive request/response logging with correlation IDs and performance tracking.
"""

import json
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from config.settings import get_settings
from core.logging_config import get_logger

settings = get_settings()
logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for comprehensive request/response logging."""

    def __init__(
        self,
        app,
        log_requests: bool = True,
        log_responses: bool = True,
        log_request_body: bool = False,
        log_response_body: bool = False,
        exclude_paths: Optional[set] = None,
    ):
        super().__init__(app)
        self.log_requests = log_requests
        self.log_responses = log_responses
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.exclude_paths = exclude_paths or {
            "/api/v1/health",
            "/api/v1/metrics",
            "/api/v1/docs",
            "/api/v1/redoc",
            "/api/v1/openapi.json",
            "/favicon.ico",
        }

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request logging."""

        # Skip logging for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        # Generate request ID if not already set
        if not hasattr(request.state, "request_id"):
            request.state.request_id = self._generate_request_id()

        start_time = time.time()

        # Log request
        if self.log_requests:
            await self._log_request(request)

        # Process request
        try:
            response = await call_next(request)

            # Calculate processing time
            processing_time = time.time() - start_time

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request.state.request_id
            response.headers["X-Processing-Time"] = f"{processing_time:.3f}s"

            # Log response
            if self.log_responses:
                await self._log_response(request, response, processing_time)

            return response

        except Exception as e:
            processing_time = time.time() - start_time
            await self._log_error(request, e, processing_time)
            raise

    def _generate_request_id(self) -> str:
        """Generate unique request ID."""
        return f"req_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"

    async def _log_request(self, request: Request) -> None:
        """Log incoming request details."""

        # Basic request information
        log_data = {
            "event": "request_started",
            "request_id": request.state.request_id,
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": self._sanitize_headers(dict(request.headers)),
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
            "timestamp": time.time(),
        }

        # Add authentication context if available
        if hasattr(request.state, "authenticated") and request.state.authenticated:
            log_data["authenticated"] = True
            log_data["api_key_name"] = request.state.key_info.get("name", "unknown")
            log_data["permissions"] = request.state.key_info.get("permissions", [])
        else:
            log_data["authenticated"] = False

        # Add request body if enabled (be careful with large payloads)
        if self.log_request_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body and len(body) < 10000:  # Limit body size for logging
                    try:
                        log_data["request_body"] = json.loads(body)
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        log_data["request_body"] = f"<binary_data_{len(body)}_bytes>"
                else:
                    log_data["request_body"] = f"<large_payload_{len(body)}_bytes>"
            except Exception as e:
                log_data["request_body_error"] = str(e)

        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={"structured_data": log_data},
        )

    async def _log_response(
        self, request: Request, response: Response, processing_time: float
    ) -> None:
        """Log response details."""

        log_data = {
            "event": "request_completed",
            "request_id": request.state.request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "processing_time_seconds": round(processing_time, 3),
            "response_headers": dict(response.headers),
            "timestamp": time.time(),
        }

        # Add response body if enabled and response is small enough
        if (
            self.log_response_body
            and hasattr(response, "body")
            and response.body
            and len(response.body) < 10000
        ):
            try:
                log_data["response_body"] = json.loads(response.body)
            except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
                log_data["response_body"] = (
                    f"<non_json_response_{len(response.body)}_bytes>"
                )

        # Log level based on status code
        if response.status_code < 400:
            log_level = "info"
            message = f"Request completed: {request.method} {request.url.path} [{response.status_code}] {processing_time:.3f}s"
        elif response.status_code < 500:
            log_level = "warning"
            message = f"Client error: {request.method} {request.url.path} [{response.status_code}] {processing_time:.3f}s"
        else:
            log_level = "error"
            message = f"Server error: {request.method} {request.url.path} [{response.status_code}] {processing_time:.3f}s"

        getattr(logger, log_level)(message, extra={"structured_data": log_data})

        # Performance warning for slow requests
        if processing_time > 30.0:  # 30 second threshold
            logger.warning(
                f"Slow request detected: {request.method} {request.url.path} "
                f"took {processing_time:.1f}s",
                extra={
                    "structured_data": {
                        "event": "slow_request",
                        "request_id": request.state.request_id,
                        "processing_time_seconds": processing_time,
                        "threshold_seconds": 30.0,
                    }
                },
            )

    async def _log_error(
        self, request: Request, error: Exception, processing_time: float
    ) -> None:
        """Log request processing errors."""

        log_data = {
            "event": "request_error",
            "request_id": request.state.request_id,
            "method": request.method,
            "path": request.url.path,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "processing_time_seconds": round(processing_time, 3),
            "timestamp": time.time(),
        }

        # Add authentication context if available
        if hasattr(request.state, "authenticated"):
            log_data["authenticated"] = request.state.authenticated

        logger.error(
            f"Request error: {request.method} {request.url.path} - {type(error).__name__}: {error}",
            extra={"structured_data": log_data},
            exc_info=True,
        )

    def _sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """
        Sanitize headers to remove sensitive information.

        Args:
            headers: Raw request headers

        Returns:
            Sanitized headers dictionary
        """
        sensitive_headers = {
            "authorization",
            "x-api-key",
            "cookie",
            "x-auth-token",
            "authentication",
        }

        sanitized = {}
        for key, value in headers.items():
            key_lower = key.lower()
            if key_lower in sensitive_headers:
                # Show only first and last 4 characters for sensitive headers
                if len(value) > 8:
                    sanitized[key] = f"{value[:4]}...{value[-4:]}"
                else:
                    sanitized[key] = "***"
            else:
                sanitized[key] = value

        return sanitized


class PerformanceMonitor:
    """Monitor API performance metrics."""

    def __init__(self):
        self.request_counts: Dict[str, int] = {}
        self.response_times: Dict[str, list] = {}
        self.error_counts: Dict[str, int] = {}
        self.start_time = time.time()

    def record_request(
        self, method: str, path: str, status_code: int, processing_time: float
    ) -> None:
        """Record request metrics."""

        endpoint_key = f"{method} {path}"

        # Count requests
        self.request_counts[endpoint_key] = self.request_counts.get(endpoint_key, 0) + 1

        # Record response time
        if endpoint_key not in self.response_times:
            self.response_times[endpoint_key] = []
        self.response_times[endpoint_key].append(processing_time)

        # Keep only recent response times (last 1000 requests)
        if len(self.response_times[endpoint_key]) > 1000:
            self.response_times[endpoint_key] = self.response_times[endpoint_key][
                -1000:
            ]

        # Count errors
        if status_code >= 400:
            error_key = f"{endpoint_key}_{status_code}"
            self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1

    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""

        uptime = time.time() - self.start_time

        # Calculate statistics for each endpoint
        endpoint_stats = {}
        for endpoint, times in self.response_times.items():
            if times:
                times_sorted = sorted(times)
                endpoint_stats[endpoint] = {
                    "request_count": self.request_counts.get(endpoint, 0),
                    "avg_response_time": sum(times) / len(times),
                    "min_response_time": min(times),
                    "max_response_time": max(times),
                    "p50_response_time": times_sorted[len(times_sorted) // 2],
                    "p95_response_time": times_sorted[int(len(times_sorted) * 0.95)],
                    "p99_response_time": times_sorted[int(len(times_sorted) * 0.99)],
                }

        return {
            "uptime_seconds": uptime,
            "total_requests": sum(self.request_counts.values()),
            "total_errors": sum(self.error_counts.values()),
            "endpoint_statistics": endpoint_stats,
            "error_breakdown": self.error_counts,
        }


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def get_performance_metrics() -> Dict[str, Any]:
    """Get current API performance metrics."""
    return performance_monitor.get_metrics()
