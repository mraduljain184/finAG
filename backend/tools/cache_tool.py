"""
finAG — Cache Tool
In-memory TTL cache for analysis results.
Prevents redundant LLM calls for the same ticker within the cache window.
"""

from cachetools import TTLCache
from threading import Lock
from loguru import logger
from config import settings


# TTL cache: stores up to 100 tickers, each for REPORT_CACHE_TTL seconds (default 24h)
_cache = TTLCache(maxsize=100, ttl=settings.REPORT_CACHE_TTL)
_lock = Lock()


def get_cached_report(ticker: str) -> dict | None:
    """
    Retrieve a cached analysis if available and not expired.
    Returns None if no cache hit.
    """
    key = ticker.upper()
    with _lock:
        if key in _cache:
            logger.info(f"[Cache] HIT for {key}")
            return _cache[key]
    logger.info(f"[Cache] MISS for {key}")
    return None


def set_cached_report(ticker: str, data: dict) -> None:
    """Store an analysis in the cache."""
    key = ticker.upper()
    with _lock:
        _cache[key] = data
    logger.info(f"[Cache] Stored {key} (TTL: {settings.REPORT_CACHE_TTL}s)")


def clear_cache() -> int:
    """Clear all cached entries. Returns number of entries cleared."""
    with _lock:
        count = len(_cache)
        _cache.clear()
    logger.info(f"[Cache] Cleared {count} entries")
    return count


def cache_stats() -> dict:
    """Get cache statistics."""
    with _lock:
        return {
            "entries": len(_cache),
            "max_size": _cache.maxsize,
            "ttl_seconds": _cache.ttl,
            "cached_tickers": list(_cache.keys()),
        }