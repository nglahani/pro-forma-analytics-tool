"""
Query Result Caching System

Provides intelligent caching for database queries to improve performance
for frequently accessed data and expensive operations.
"""

import hashlib
import json
import pickle
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from functools import wraps
import sqlite3
import threading

from core.logging_config import get_logger


class QueryCache:
    """Thread-safe in-memory and persistent query result cache."""
    
    def __init__(self, cache_dir: Optional[Path] = None, 
                 default_ttl_seconds: int = 3600,
                 max_memory_entries: int = 1000):
        """
        Initialize query cache.
        
        Args:
            cache_dir: Directory for persistent cache storage
            default_ttl_seconds: Default time-to-live for cache entries
            max_memory_entries: Maximum entries to keep in memory
        """
        self.logger = get_logger(__name__)
        self.default_ttl = default_ttl_seconds
        self.max_memory_entries = max_memory_entries
        
        # Setup cache directory
        if cache_dir is None:
            cache_dir = Path(__file__).parent.parent.parent.parent / "data" / "cache"
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache for fast access
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        self._access_times: Dict[str, float] = {}
        self._lock = threading.RLock()
        
        # Initialize persistent cache database
        self._init_persistent_cache()
    
    def _init_persistent_cache(self):
        """Initialize SQLite database for persistent caching."""
        
        self.cache_db_path = self.cache_dir / "query_cache.db"
        
        try:
            with sqlite3.connect(str(self.cache_db_path)) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS cache_entries (
                        cache_key TEXT PRIMARY KEY,
                        data BLOB NOT NULL,
                        created_at TIMESTAMP NOT NULL,
                        expires_at TIMESTAMP NOT NULL,
                        access_count INTEGER DEFAULT 1,
                        last_accessed TIMESTAMP NOT NULL,
                        data_size INTEGER NOT NULL
                    )
                """)
                
                # Create index for efficient cleanup
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_cache_expires 
                    ON cache_entries(expires_at)
                """)
                
                conn.commit()
                self.logger.info(f"Initialized query cache database at {self.cache_db_path}")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize cache database: {e}")
            raise
    
    def _generate_cache_key(self, query: str, params: Tuple = (), 
                          extra_context: Optional[Dict] = None) -> str:
        """Generate a unique cache key for query and parameters."""
        
        # Normalize query (remove extra whitespace)
        normalized_query = " ".join(query.split())
        
        # Create key components
        key_data = {
            'query': normalized_query,
            'params': params,
            'context': extra_context or {}
        }
        
        # Generate SHA256 hash
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    def _is_expired(self, expires_at: datetime) -> bool:
        """Check if a cache entry has expired."""
        return datetime.now() > expires_at
    
    def _evict_memory_cache(self):
        """Evict least recently used entries from memory cache."""
        
        if len(self._memory_cache) <= self.max_memory_entries:
            return
        
        # Sort by access time and remove oldest entries
        sorted_keys = sorted(self._access_times.keys(), 
                           key=lambda k: self._access_times[k])
        
        keys_to_remove = sorted_keys[:len(sorted_keys) - self.max_memory_entries + 100]
        
        for key in keys_to_remove:
            self._memory_cache.pop(key, None)
            self._access_times.pop(key, None)
        
        self.logger.debug(f"Evicted {len(keys_to_remove)} entries from memory cache")
    
    def get(self, query: str, params: Tuple = (), 
            extra_context: Optional[Dict] = None) -> Optional[Any]:
        """
        Retrieve cached query result.
        
        Args:
            query: SQL query string
            params: Query parameters
            extra_context: Additional context for cache key generation
            
        Returns:
            Cached result or None if not found/expired
        """
        cache_key = self._generate_cache_key(query, params, extra_context)
        
        with self._lock:
            # Check memory cache first
            if cache_key in self._memory_cache:
                entry = self._memory_cache[cache_key]
                if not self._is_expired(entry['expires_at']):
                    self._access_times[cache_key] = time.time()
                    self.logger.debug(f"Memory cache hit for key: {cache_key[:16]}...")
                    return entry['data']
                else:
                    # Remove expired entry
                    self._memory_cache.pop(cache_key, None)
                    self._access_times.pop(cache_key, None)
            
            # Check persistent cache
            try:
                with sqlite3.connect(str(self.cache_db_path)) as conn:
                    cursor = conn.execute("""
                        SELECT data, expires_at, access_count 
                        FROM cache_entries 
                        WHERE cache_key = ?
                    """, (cache_key,))
                    
                    row = cursor.fetchone()
                    if row:
                        data_blob, expires_at_str, access_count = row
                        expires_at = datetime.fromisoformat(expires_at_str)
                        
                        if not self._is_expired(expires_at):
                            # Deserialize data
                            data = pickle.loads(data_blob)
                            
                            # Update access statistics
                            conn.execute("""
                                UPDATE cache_entries 
                                SET access_count = ?, last_accessed = ?
                                WHERE cache_key = ?
                            """, (access_count + 1, datetime.now().isoformat(), cache_key))
                            
                            # Add to memory cache for faster future access
                            self._memory_cache[cache_key] = {
                                'data': data,
                                'expires_at': expires_at
                            }
                            self._access_times[cache_key] = time.time()
                            self._evict_memory_cache()
                            
                            self.logger.debug(f"Persistent cache hit for key: {cache_key[:16]}...")
                            return data
                        else:
                            # Remove expired entry
                            conn.execute("DELETE FROM cache_entries WHERE cache_key = ?", 
                                       (cache_key,))
                            
            except Exception as e:
                self.logger.error(f"Error accessing persistent cache: {e}")
        
        return None
    
    def set(self, query: str, params: Tuple, data: Any, 
            ttl_seconds: Optional[int] = None,
            extra_context: Optional[Dict] = None) -> bool:
        """
        Store query result in cache.
        
        Args:
            query: SQL query string
            params: Query parameters
            data: Data to cache
            ttl_seconds: Time-to-live in seconds (uses default if None)
            extra_context: Additional context for cache key generation
            
        Returns:
            True if successfully cached, False otherwise
        """
        if ttl_seconds is None:
            ttl_seconds = self.default_ttl
        
        cache_key = self._generate_cache_key(query, params, extra_context)
        now = datetime.now()
        expires_at = now + timedelta(seconds=ttl_seconds)
        
        try:
            # Serialize data
            data_blob = pickle.dumps(data)
            data_size = len(data_blob)
            
            with self._lock:
                # Store in memory cache
                self._memory_cache[cache_key] = {
                    'data': data,
                    'expires_at': expires_at
                }
                self._access_times[cache_key] = time.time()
                self._evict_memory_cache()
                
                # Store in persistent cache
                with sqlite3.connect(str(self.cache_db_path)) as conn:
                    conn.execute("""
                        INSERT OR REPLACE INTO cache_entries
                        (cache_key, data, created_at, expires_at, 
                         last_accessed, data_size)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (cache_key, data_blob, now.isoformat(), 
                          expires_at.isoformat(), now.isoformat(), data_size))
                    
            self.logger.debug(f"Cached query result: {cache_key[:16]}... ({data_size} bytes)")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cache query result: {e}")
            return False
    
    def invalidate(self, pattern: Optional[str] = None) -> int:
        """
        Invalidate cache entries.
        
        Args:
            pattern: SQL LIKE pattern to match cache keys (None = all)
            
        Returns:
            Number of entries invalidated
        """
        invalidated_count = 0
        
        with self._lock:
            try:
                with sqlite3.connect(str(self.cache_db_path)) as conn:
                    if pattern is None:
                        # Clear all entries
                        cursor = conn.execute("SELECT COUNT(*) FROM cache_entries")
                        invalidated_count = cursor.fetchone()[0]
                        conn.execute("DELETE FROM cache_entries")
                        self._memory_cache.clear()
                        self._access_times.clear()
                    else:
                        # Clear entries matching pattern
                        cursor = conn.execute("""
                            SELECT cache_key FROM cache_entries 
                            WHERE cache_key LIKE ?
                        """, (pattern,))
                        keys_to_remove = [row[0] for row in cursor.fetchall()]
                        
                        for key in keys_to_remove:
                            conn.execute("DELETE FROM cache_entries WHERE cache_key = ?", (key,))
                            self._memory_cache.pop(key, None)
                            self._access_times.pop(key, None)
                            invalidated_count += 1
                    
                    conn.commit()
                    
            except Exception as e:
                self.logger.error(f"Failed to invalidate cache entries: {e}")
        
        self.logger.info(f"Invalidated {invalidated_count} cache entries")
        return invalidated_count
    
    def cleanup_expired(self) -> int:
        """Remove expired entries from cache."""
        
        removed_count = 0
        now = datetime.now()
        
        with self._lock:
            # Clean memory cache
            expired_keys = [
                key for key, entry in self._memory_cache.items()
                if self._is_expired(entry['expires_at'])
            ]
            
            for key in expired_keys:
                self._memory_cache.pop(key, None)
                self._access_times.pop(key, None)
                removed_count += 1
            
            # Clean persistent cache
            try:
                with sqlite3.connect(str(self.cache_db_path)) as conn:
                    cursor = conn.execute("DELETE FROM cache_entries WHERE expires_at < ?", 
                                        (now.isoformat(),))
                    removed_count += cursor.rowcount
                    conn.commit()
                    
            except Exception as e:
                self.logger.error(f"Failed to cleanup expired entries: {e}")
        
        if removed_count > 0:
            self.logger.info(f"Cleaned up {removed_count} expired cache entries")
        
        return removed_count
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        
        stats = {
            'memory_entries': len(self._memory_cache),
            'max_memory_entries': self.max_memory_entries,
            'persistent_entries': 0,
            'total_size_bytes': 0,
            'hit_rate': 0.0,
            'cache_directory': str(self.cache_dir)
        }
        
        try:
            with sqlite3.connect(str(self.cache_db_path)) as conn:
                # Get entry count and total size
                cursor = conn.execute("""
                    SELECT COUNT(*), COALESCE(SUM(data_size), 0) 
                    FROM cache_entries
                """)
                count, total_size = cursor.fetchone()
                stats['persistent_entries'] = count
                stats['total_size_bytes'] = total_size
                
                # Calculate hit rate (simplified)
                cursor = conn.execute("""
                    SELECT AVG(access_count) FROM cache_entries 
                    WHERE access_count > 1
                """)
                avg_access = cursor.fetchone()[0]
                if avg_access:
                    stats['hit_rate'] = min(1.0, (avg_access - 1) / avg_access)
                    
        except Exception as e:
            self.logger.error(f"Failed to get cache stats: {e}")
        
        return stats


# Global cache instance
_global_cache: Optional[QueryCache] = None
_cache_lock = threading.Lock()


def get_query_cache() -> QueryCache:
    """Get the global query cache instance."""
    global _global_cache
    
    if _global_cache is None:
        with _cache_lock:
            if _global_cache is None:
                _global_cache = QueryCache()
    
    return _global_cache


def cached_query(ttl_seconds: int = 3600, 
                cache_key_extra: Optional[Dict] = None):
    """
    Decorator for caching database query results.
    
    Args:
        ttl_seconds: Cache time-to-live in seconds
        cache_key_extra: Additional context for cache key generation
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_query_cache()
            
            # Generate cache key from function name and arguments
            cache_context = {
                'function': func.__name__,
                'args': args,
                'kwargs': kwargs,
                'extra': cache_key_extra or {}
            }
            
            # Try to get from cache (using function name as query)
            cached_result = cache.get(func.__name__, args, cache_context)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(func.__name__, args, result, ttl_seconds, cache_context)
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(pattern: Optional[str] = None) -> int:
    """Invalidate cache entries matching pattern."""
    cache = get_query_cache()
    return cache.invalidate(pattern)


def cleanup_expired_cache() -> int:
    """Clean up expired cache entries."""
    cache = get_query_cache()
    return cache.cleanup_expired()


def get_cache_statistics() -> Dict[str, Any]:
    """Get cache performance statistics."""
    cache = get_query_cache()
    return cache.get_cache_stats()