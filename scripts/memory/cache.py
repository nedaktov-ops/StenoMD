"""
Fast Cache Module

LRU cache for quick access to frequently used items.
Optimizes recall performance for common queries.
"""

import time
from collections import OrderedDict
from typing import Any, Optional, Dict, List
from threading import Lock


class FastCache:
    """
    Thread-safe LRU cache for fast memory access.
    
    Features:
    - O(1) access time
    - LRU eviction policy
    - Access statistics tracking
    - Configurable size limit
    """
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.cache: OrderedDict = OrderedDict()
        self.access_times: Dict[str, float] = {}
        self.hits = 0
        self.misses = 0
        self.lock = Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        with self.lock:
            if key in self.cache:
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                self.access_times[key] = time.time()
                self.hits += 1
                return self.cache[key]
            else:
                self.misses += 1
                return None
    
    def put(self, key: str, value: Any):
        """
        Put value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        with self.lock:
            if key in self.cache:
                # Update existing
                self.cache.move_to_end(key)
            else:
                # Add new
                if len(self.cache) >= self.max_size:
                    # Evict least recently used
                    oldest_key = next(iter(self.cache))
                    del self.cache[oldest_key]
                    if oldest_key in self.access_times:
                        del self.access_times[oldest_key]
            
            self.cache[key] = value
            self.access_times[key] = time.time()
    
    def delete(self, key: str):
        """Remove key from cache."""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]
    
    def clear(self):
        """Clear entire cache."""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()
            self.hits = 0
            self.misses = 0
    
    def size(self) -> int:
        """Get current cache size."""
        return len(self.cache)
    
    def hit_rate(self) -> float:
        """
        Get cache hit rate.
        
        Returns:
            Hit rate as percentage (0-100)
        """
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return (self.hits / total) * 100
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        total = self.hits + self.misses
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': self.hit_rate(),
            'utilization': (len(self.cache) / self.max_size) * 100 if self.max_size > 0 else 0
        }
    
    def get_recent(self, limit: int = 10) -> List[tuple]:
        """
        Get most recently accessed items.
        
        Args:
            limit: Maximum items to return
            
        Returns:
            List of (key, value, access_time) tuples
        """
        with self.lock:
            sorted_times = sorted(self.access_times.items(), key=lambda x: x[1], reverse=True)
            results = []
            for key, access_time in sorted_times[:limit]:
                if key in self.cache:
                    results.append((key, self.cache[key], access_time))
            return results
    
    def get_hot(self, limit: int = 10) -> List[tuple]:
        """
        Get most frequently accessed items.
        
        Note: This requires tracking access counts which is not currently implemented.
        Returns most recently used items as proxy.
        """
        return self.get_recent(limit)
    
    def contains(self, key: str) -> bool:
        """Check if key exists in cache."""
        with self.lock:
            return key in self.cache
    
    def keys(self) -> List[str]:
        """Get all cache keys."""
        with self.lock:
            return list(self.cache.keys())
    
    def update_max_size(self, new_size: int):
        """
        Update max cache size, evicting if necessary.
        
        Args:
            new_size: New maximum size
        """
        with self.lock:
            self.max_size = new_size
            while len(self.cache) > self.max_size:
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                if oldest_key in self.access_times:
                    del self.access_times[oldest_key]


class TimedCache:
    """
    Cache with time-based expiration.
    
    Useful for caching expensive computations that should refresh periodically.
    """
    
    def __init__(self, ttl_seconds: int = 300):
        self.ttl = ttl_seconds
        self.cache: Dict[str, tuple] = {}  # key -> (value, expiry_time)
        self.lock = Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value if not expired."""
        with self.lock:
            if key in self.cache:
                value, expiry = self.cache[key]
                if time.time() < expiry:
                    return value
                else:
                    del self.cache[key]
            return None
    
    def put(self, key: str, value: Any, ttl: int = None):
        """Put value with TTL."""
        with self.lock:
            expiry = time.time() + (ttl if ttl is not None else self.ttl)
            self.cache[key] = (value, expiry)
    
    def delete(self, key: str):
        """Remove key."""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
    
    def clear(self):
        """Clear all expired and non-expired entries."""
        with self.lock:
            self.cache.clear()
    
    def clear_expired(self):
        """Clear only expired entries."""
        with self.lock:
            now = time.time()
            self.cache = {k: v for k, v in self.cache.items() if v[1] > now}
    
    def size(self) -> int:
        """Get cache size."""
        return len(self.cache)


class CacheManager:
    """
    Manages multiple caches for different purposes.
    """
    
    def __init__(self):
        self.caches: Dict[str, FastCache] = {}
    
    def get_cache(self, name: str, max_size: int = 100) -> FastCache:
        """Get or create a named cache."""
        if name not in self.caches:
            self.caches[name] = FastCache(max_size=max_size)
        return self.caches[name]
    
    def get_stats(self) -> dict:
        """Get statistics for all caches."""
        stats = {}
        for name, cache in self.caches.items():
            stats[name] = cache.get_stats()
        return stats
    
    def clear_all(self):
        """Clear all caches."""
        for cache in self.caches.values():
            cache.clear()