"""
Response Cache Middleware

Lightweight in-memory cache middleware with TTL-based expiration and configurable cache strategies.
"""

import hashlib
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from core.logging_config import get_logger

logger = get_logger(__name__)


class CacheEntry:
    """Represents a cached response with TTL and metadata."""

    def __init__(
        self,
        content: bytes,
        headers: Dict[str, str],
        status_code: int,
        ttl_seconds: int,
        content_type: str = "application/json",
    ):
        self.content = content
        self.headers = headers
        self.status_code = status_code
        self.content_type = content_type
        self.created_at = time.time()
        self.expires_at = self.created_at + ttl_seconds
        self.access_count = 0
        self.last_accessed = self.created_at

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return time.time() > self.expires_at

    def is_fresh(self) -> bool:
        """Check if cache entry is still fresh (not expired)."""
        return not self.is_expired()

    def record_access(self) -> None:
        """Record an access to this cache entry."""
        self.access_count += 1
        self.last_accessed = time.time()

    def get_age_seconds(self) -> float:
        """Get the age of this cache entry in seconds."""
        return time.time() - self.created_at

    def get_ttl_remaining(self) -> float:
        """Get remaining TTL in seconds."""
        return max(0, self.expires_at - time.time())


class ResponseCacheMiddleware(BaseHTTPMiddleware):
    """
    Lightweight in-memory response cache middleware with configurable TTL and size limits.

    Features:
    - TTL-based cache expiration
    - Configurable cache strategies per endpoint pattern
    - LRU eviction for memory management
    - Cache hit/miss metrics
    - Cache control headers
    """

    def __init__(
        self,
        app: ASGIApp,
        cache_config: Optional[Dict[str, int]] = None,
        max_cache_size_mb: int = 100,
        cleanup_interval_seconds: int = 300,  # 5 minutes
        enable_cache_headers: bool = True,
    ):
        super().__init__(app)
        self.cache: Dict[str, CacheEntry] = {}
        self.max_cache_size_mb = max_cache_size_mb
        self.max_cache_size_bytes = max_cache_size_mb * 1024 * 1024
        self.enable_cache_headers = enable_cache_headers
        self.cleanup_interval_seconds = cleanup_interval_seconds
        self.last_cleanup = time.time()

        # Default cache configuration (TTL in seconds)
        self.cache_config = cache_config or {
            "/api/v1/data/market": 900,  # 15 minutes - market data
            "/api/v1/data/forecast": 1800,  # 30 minutes - forecast data
            "/api/v1/system/config": 3600,  # 60 minutes - system config
            "/api/v1/system/health": 0,  # No caching - real-time status
            "/api/v1/analysis": 0,  # No caching - unique per request
            "/api/v1/simulation": 0,  # No caching - unique per request
        }

        # Cache statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "expired_cleanups": 0,
            "total_requests": 0,
            "cache_size_bytes": 0,
            "entry_count": 0,
        }

        logger.info(
            f"Response cache middleware initialized: max_size={max_cache_size_mb}MB, cleanup_interval={cleanup_interval_seconds}s"
        )

    def _get_cache_ttl(self, path: str) -> int:
        """Get cache TTL for a given path."""
        # Check exact matches first
        if path in self.cache_config:
            return self.cache_config[path]

        # Check pattern matches (longest match wins)
        matching_patterns = [
            pattern
            for pattern in self.cache_config.keys()
            if path.startswith(pattern.rstrip("*"))
        ]

        if matching_patterns:
            # Get the longest matching pattern
            best_match = max(matching_patterns, key=len)
            return self.cache_config[best_match]

        # Default: no caching
        return 0

    def _is_cacheable_request(self, request: Request) -> bool:
        """Determine if a request is cacheable."""
        # Only cache GET requests
        if request.method != "GET":
            return False

        # Check if path has a cache TTL > 0
        ttl = self._get_cache_ttl(request.url.path)
        return ttl > 0

    def _generate_cache_key(self, request: Request) -> str:
        """Generate a deterministic cache key for the request."""
        # Include method, path, and sorted query parameters
        method = request.method
        path = request.url.path

        # Sort query parameters for consistent cache keys
        query_params = dict(request.query_params)
        sorted_params = urlencode(sorted(query_params.items()))

        # Create cache key components
        key_components = [method, path, sorted_params]
        key_string = ":".join(key_components)

        # Hash for consistent length and no special characters
        cache_key = hashlib.md5(key_string.encode()).hexdigest()

        return cache_key

    def _get_cache_size_bytes(self) -> int:
        """Calculate current cache size in bytes."""
        total_size = 0
        for entry in self.cache.values():
            total_size += len(entry.content)
            total_size += sum(
                len(k.encode()) + len(v.encode()) for k, v in entry.headers.items()
            )
        return total_size

    def _cleanup_expired_entries(self) -> int:
        """Remove expired cache entries and return count removed."""
        expired_keys = [key for key, entry in self.cache.items() if entry.is_expired()]

        for key in expired_keys:
            del self.cache[key]

        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
            self.stats["expired_cleanups"] += len(expired_keys)

        return len(expired_keys)

    def _evict_lru_entries(self, target_size_bytes: int) -> int:
        """Evict least recently used entries to reach target size."""
        evicted_count = 0

        # Sort entries by last accessed time (LRU first)
        sorted_entries = sorted(self.cache.items(), key=lambda x: x[1].last_accessed)

        current_size = self._get_cache_size_bytes()

        for key, entry in sorted_entries:
            if current_size <= target_size_bytes:
                break

            # Remove this entry
            entry_size = len(entry.content)
            del self.cache[key]
            current_size -= entry_size
            evicted_count += 1

        if evicted_count > 0:
            logger.debug(f"Evicted {evicted_count} LRU cache entries")
            self.stats["evictions"] += evicted_count

        return evicted_count

    def _periodic_cleanup(self) -> None:
        """Perform periodic cache maintenance."""
        current_time = time.time()

        # Check if cleanup is needed
        if current_time - self.last_cleanup < self.cleanup_interval_seconds:
            return

        # Clean up expired entries
        self._cleanup_expired_entries()

        # Check memory usage and evict if necessary
        current_size = self._get_cache_size_bytes()
        if current_size > self.max_cache_size_bytes:
            target_size = int(self.max_cache_size_bytes * 0.8)  # Reduce to 80% of max
            self._evict_lru_entries(target_size)

        # Update statistics
        self.stats["cache_size_bytes"] = self._get_cache_size_bytes()
        self.stats["entry_count"] = len(self.cache)

        self.last_cleanup = current_time

    def _add_cache_headers(self, response: Response, cache_entry: CacheEntry) -> None:
        """Add cache-related headers to response."""
        if not self.enable_cache_headers:
            return

        age_seconds = int(cache_entry.get_age_seconds())
        ttl_remaining = int(cache_entry.get_ttl_remaining())

        # Add cache control headers
        response.headers["Cache-Control"] = f"public, max-age={ttl_remaining}"
        response.headers["Age"] = str(age_seconds)
        response.headers["X-Cache"] = "HIT"
        response.headers["X-Cache-TTL-Remaining"] = str(ttl_remaining)

    def _store_in_cache(
        self,
        cache_key: str,
        content: bytes,
        headers: Dict[str, str],
        status_code: int,
        ttl_seconds: int,
    ) -> None:
        """Store response in cache."""
        # Don't cache if TTL is 0 or negative
        if ttl_seconds <= 0:
            return

        # Create cache entry
        cache_entry = CacheEntry(
            content=content,
            headers=headers,
            status_code=status_code,
            ttl_seconds=ttl_seconds,
        )

        # Store in cache
        self.cache[cache_key] = cache_entry

        logger.debug(
            f"Stored response in cache: key={cache_key[:8]}..., ttl={ttl_seconds}s"
        )

    async def dispatch(self, request: Request, call_next) -> Response:
        """Main middleware dispatch method."""
        self.stats["total_requests"] += 1

        # Perform periodic cleanup
        self._periodic_cleanup()

        # Check if request is cacheable
        if not self._is_cacheable_request(request):
            response = await call_next(request)
            if self.enable_cache_headers:
                response.headers["X-Cache"] = "BYPASS"
            return response

        # Generate cache key
        cache_key = self._generate_cache_key(request)

        # Check for cached response
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]

            # Check if entry is still fresh
            if cache_entry.is_fresh():
                # Cache hit - return cached response
                cache_entry.record_access()
                self.stats["hits"] += 1

                # Create response from cache
                cached_response = Response(
                    content=cache_entry.content,
                    status_code=cache_entry.status_code,
                    headers=cache_entry.headers,
                    media_type=cache_entry.content_type,
                )

                # Add cache headers
                self._add_cache_headers(cached_response, cache_entry)

                logger.debug(f"Cache HIT: {request.url.path} (key={cache_key[:8]}...)")
                return cached_response
            else:
                # Entry expired - remove it
                del self.cache[cache_key]
                self.stats["expired_cleanups"] += 1

        # Cache miss - call next middleware/endpoint
        self.stats["misses"] += 1
        logger.debug(f"Cache MISS: {request.url.path} (key={cache_key[:8]}...)")

        response = await call_next(request)

        # Only cache successful responses
        if response.status_code == 200:
            ttl_seconds = self._get_cache_ttl(request.url.path)

            if ttl_seconds > 0:
                # Read response content
                response_body = b""
                async for chunk in response.body_iterator:
                    response_body += chunk

                # Store in cache
                self._store_in_cache(
                    cache_key=cache_key,
                    content=response_body,
                    headers=dict(response.headers),
                    status_code=response.status_code,
                    ttl_seconds=ttl_seconds,
                )

                # Create new response with same content
                cached_response = Response(
                    content=response_body,
                    status_code=response.status_code,
                    headers=response.headers,
                    media_type=response.media_type,
                )

                if self.enable_cache_headers:
                    cached_response.headers["X-Cache"] = "MISS"
                    cached_response.headers["Cache-Control"] = (
                        f"public, max-age={ttl_seconds}"
                    )

                return cached_response

        # Add bypass header for non-cached responses
        if self.enable_cache_headers:
            response.headers["X-Cache"] = "BYPASS"

        return response

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get current cache statistics."""
        total_requests = max(1, self.stats["total_requests"])  # Avoid division by zero
        hit_rate = (self.stats["hits"] / total_requests) * 100

        return {
            "cache_enabled": True,
            "hit_rate_percent": round(hit_rate, 2),
            "total_requests": self.stats["total_requests"],
            "cache_hits": self.stats["hits"],
            "cache_misses": self.stats["misses"],
            "evictions": self.stats["evictions"],
            "expired_cleanups": self.stats["expired_cleanups"],
            "current_entries": len(self.cache),
            "cache_size_bytes": self._get_cache_size_bytes(),
            "cache_size_mb": round(self._get_cache_size_bytes() / (1024 * 1024), 2),
            "max_cache_size_mb": self.max_cache_size_mb,
            "memory_usage_percent": round(
                (self._get_cache_size_bytes() / self.max_cache_size_bytes) * 100, 2
            ),
        }

    def clear_cache(self) -> int:
        """Clear all cache entries and return count cleared."""
        cleared_count = len(self.cache)
        self.cache.clear()

        # Reset relevant statistics
        self.stats["cache_size_bytes"] = 0
        self.stats["entry_count"] = 0

        logger.info(f"Cache cleared: {cleared_count} entries removed")
        return cleared_count

    def clear_expired_entries(self) -> int:
        """Clear only expired entries and return count cleared."""
        return self._cleanup_expired_entries()

    def get_cache_entry_info(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific cache entry."""
        if cache_key not in self.cache:
            return None

        entry = self.cache[cache_key]
        return {
            "cache_key": cache_key,
            "created_at": entry.created_at,
            "expires_at": entry.expires_at,
            "age_seconds": entry.get_age_seconds(),
            "ttl_remaining_seconds": entry.get_ttl_remaining(),
            "is_expired": entry.is_expired(),
            "access_count": entry.access_count,
            "last_accessed": entry.last_accessed,
            "content_size_bytes": len(entry.content),
            "status_code": entry.status_code,
            "content_type": entry.content_type,
        }
