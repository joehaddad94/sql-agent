"""
Smart caching system for SQL Agent with data-change awareness
"""

import hashlib
import json
import time
from typing import Any, Optional, Dict, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)
# Set debug level to see cache key generation
logger.setLevel(logging.DEBUG)

class QueryType(Enum):
    """Types of queries for different caching strategies."""
    COUNT = "count"           # Application counts, user counts
    LIST = "list"             # Lists of applications, programs
    DETAIL = "detail"         # Detailed information
    SCHEMA = "schema"         # Database schema, table info
    STATIC = "static"         # Static reference data
    REAL_TIME = "real_time"   # No caching

@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    result: Any
    timestamp: float
    query_type: QueryType
    table_hashes: Dict[str, str]  # Table name -> last modification hash
    access_count: int = 0
    last_accessed: float = 0

class SmartCache:
    """
    Intelligent caching system with data-change detection and TTL rules.
    """
    
    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        
        # TTL rules for different query types (in minutes)
        self.ttl_rules = {
            QueryType.COUNT: 5,      # 5 minutes for counts
            QueryType.LIST: 15,      # 15 minutes for lists
            QueryType.DETAIL: 30,    # 30 minutes for details
            QueryType.SCHEMA: 1440,  # 24 hours for schema
            QueryType.STATIC: 1440,  # 24 hours for static data
            QueryType.REAL_TIME: 0   # No caching
        }
        
        # Table modification tracking
        self.table_modifications: Dict[str, float] = {}
        
        # Cache statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "invalidations": 0,
            "expirations": 0
        }
    
    def _generate_key(self, query: str, metadata: dict = None) -> str:
        """Generate cache key from query and metadata."""
        # Normalize query: trim whitespace, lowercase, remove extra spaces
        normalized_query = " ".join(query.strip().lower().split())
        
        # Filter out volatile metadata fields that shouldn't affect caching
        if metadata:
            # Create a copy of metadata without volatile fields
            stable_metadata = {}
            for key, value in metadata.items():
                if key not in ['timestamp', 'custom_fields']:
                    stable_metadata[key] = value
                elif key == 'custom_fields' and isinstance(value, dict):
                    # Include custom fields but exclude timestamp
                    stable_custom = {k: v for k, v in value.items() if k != 'timestamp'}
                    if stable_custom:  # Only add if there are stable custom fields
                        stable_metadata[key] = stable_custom
        else:
            stable_metadata = {}
        
        content = f"{normalized_query}:{json.dumps(stable_metadata, sort_keys=True) if stable_metadata else ''}"
        key = hashlib.md5(content.encode()).hexdigest()
        logger.debug(f"Generated cache key: {key} for query: '{query}' (normalized: '{normalized_query}') with metadata: {metadata} -> stable: {stable_metadata}")
        return key
    
    def _get_table_hashes(self, query: str) -> Dict[str, str]:
        """
        Generate hashes for tables that might affect this query.
        This is a simplified version - in production you'd check actual table modification times.
        """
        # Extract table names from query (simplified)
        tables = set()
        query_lower = query.lower()
        
        # Common tables in your educational application system
        if any(word in query_lower for word in ['application', 'applications', 'apply', 'submission']):
            tables.add('application_news')
        if any(word in query_lower for word in ['program', 'programs', 'course', 'courses', 'curriculum']):
            tables.add('programs')
        if any(word in query_lower for word in ['user', 'users', 'student', 'students', 'applicant']):
            tables.add('up_users')
        if any(word in query_lower for word in ['cycle', 'cycles', 'academic', 'semester', 'term']):
            tables.add('cycles')
        if any(word in query_lower for word in ['information', 'info', 'details', 'data', 'content']):
            tables.add('information')
        if any(word in query_lower for word in ['decision', 'acceptance', 'rejection', 'status']):
            tables.add('decision_dates')
        if any(word in query_lower for word in ['link', 'links', 'relationship', 'connection']):
            tables.add('application_news_links')
        
        # Generate simple hash based on current time (in production, use actual table modification times)
        current_time = int(time.time() / 60)  # Round to nearest minute
        return {table: str(current_time) for table in tables}
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry has expired based on TTL rules."""
        ttl_minutes = self.ttl_rules.get(entry.query_type, 5)
        if ttl_minutes == 0:  # No caching
            return True
        
        age_minutes = (time.time() - entry.timestamp) / 60
        return age_minutes > ttl_minutes
    
    def _has_data_changed(self, entry: CacheEntry) -> bool:
        """Check if relevant data has changed since caching."""
        current_hashes = self._get_table_hashes("")  # Get current table state
        
        for table, cached_hash in entry.table_hashes.items():
            if table in current_hashes:
                current_hash = current_hashes[table]
                if cached_hash != current_hash:
                    logger.info(f"Data changed in table {table}, invalidating cache")
                    return True
        
        return False
    
    def _cleanup_expired(self):
        """Remove expired entries and enforce max size."""
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self.cache.items():
            if self._is_expired(entry):
                expired_keys.append(key)
                self.stats["expirations"] += 1
        
        # Remove expired entries
        for key in expired_keys:
            del self.cache[key]
        
        # If still over max size, remove least recently used
        if len(self.cache) > self.max_size:
            # Sort by last accessed time and remove oldest
            sorted_items = sorted(self.cache.items(), key=lambda x: x[1].last_accessed)
            items_to_remove = len(self.cache) - self.max_size
            
            for i in range(items_to_remove):
                del self.cache[sorted_items[i][0]]
    
    def get(self, query: str, query_type: QueryType = QueryType.COUNT, metadata: dict = None) -> Optional[Any]:
        """
        Get cached result if valid.
        
        Args:
            query: The natural language query
            query_type: Type of query for TTL determination
            metadata: Additional metadata for cache key generation
        
        Returns:
            Cached result if valid, None otherwise
        """
        key = self._generate_key(query, metadata)
        logger.debug(f"Cache GET - Key: {key}, Query: '{query}', Metadata: {metadata}")
        logger.debug(f"Cache state during GET: {len(self.cache)} entries, keys: {list(self.cache.keys())[:5]}")
        
        if key in self.cache:
            entry = self.cache[key]
            
            # Check if expired
            if self._is_expired(entry):
                del self.cache[key]
                self.stats["expirations"] += 1
                self.stats["misses"] += 1
                return None
            
            # Check if data has changed
            if self._has_data_changed(entry):
                del self.cache[key]
                self.stats["invalidations"] += 1
                self.stats["misses"] += 1
                return None
            
            # Update access statistics
            entry.access_count += 1
            entry.last_accessed = time.time()
            
            self.stats["hits"] += 1
            logger.info(f"Cache HIT for query: {query[:50]}...")
            return entry.result
        
        self.stats["misses"] += 1
        logger.info(f"Cache MISS for query: {query[:50]}...")
        return None
    
    def set(self, query: str, result: Any, query_type: QueryType = QueryType.COUNT, metadata: dict = None):
        """
        Cache a result with metadata.
        
        Args:
            query: The natural language query
            result: The result to cache
            query_type: Type of query for TTL determination
            metadata: Additional metadata for cache key generation
        """
        if query_type == QueryType.REAL_TIME:
            return  # Don't cache real-time data
        
        key = self._generate_key(query, metadata)
        table_hashes = self._get_table_hashes(query)
        logger.debug(f"Cache SET - Key: {key}, Query: '{query}', Metadata: {metadata}")
        
        entry = CacheEntry(
            result=result,
            timestamp=time.time(),
            query_type=query_type,
            table_hashes=table_hashes,
            access_count=1,
            last_accessed=time.time()
        )
        
        self.cache[key] = entry
        logger.info(f"Cached result for query: {query[:50]}... (type: {query_type.value})")
        logger.debug(f"Cache state after SET: {len(self.cache)} entries, keys: {list(self.cache.keys())[:5]}")
        
        # Cleanup if needed
        self._cleanup_expired()
    
    def invalidate_pattern(self, pattern: str):
        """
        Invalidate cache entries matching a pattern.
        
        Args:
            pattern: Pattern to match against cached queries
        """
        keys_to_remove = []
        pattern_lower = pattern.lower()
        
        for key, entry in self.cache.items():
            # This is a simplified pattern matching - in production you might use regex
            if pattern_lower in str(entry.result).lower():
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.cache[key]
        
        self.stats["invalidations"] += len(keys_to_remove)
        logger.info(f"Invalidated {len(keys_to_remove)} cache entries matching pattern: {pattern}")
    
    def invalidate_table(self, table_name: str):
        """
        Invalidate all cache entries that might be affected by changes to a specific table.
        
        Args:
            table_name: Name of the table that changed
        """
        keys_to_remove = []
        
        for key, entry in self.cache.items():
            if table_name in entry.table_hashes:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.cache[key]
        
        self.stats["invalidations"] += len(keys_to_remove)
        logger.info(f"Invalidated {len(keys_to_remove)} cache entries due to table change: {table_name}")
    
    def clear(self):
        """Clear all cached data."""
        cleared_count = len(self.cache)
        self.cache.clear()
        logger.info(f"Cleared {cleared_count} cache entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        hit_rate = 0
        if self.stats["hits"] + self.stats["misses"] > 0:
            hit_rate = self.stats["hits"] / (self.stats["hits"] + self.stats["misses"])
        
        return {
            **self.stats,
            "hit_rate": f"{hit_rate:.2%}",
            "current_size": len(self.cache),
            "max_size": self.max_size
        }
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get detailed information about cached items."""
        info = {
            "total_entries": len(self.cache),
            "by_type": {},
            "oldest_entry": None,
            "newest_entry": None
        }
        
        if self.cache:
            # Group by query type
            for entry in self.cache.values():
                query_type = entry.query_type.value
                if query_type not in info["by_type"]:
                    info["by_type"][query_type] = 0
                info["by_type"][query_type] += 1
            
            # Find oldest and newest entries
            timestamps = [entry.timestamp for entry in self.cache.values()]
            info["oldest_entry"] = datetime.fromtimestamp(min(timestamps)).isoformat()
            info["newest_entry"] = datetime.fromtimestamp(max(timestamps)).isoformat()
        
        return info
