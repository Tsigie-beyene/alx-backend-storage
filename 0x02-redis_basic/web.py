#!/usr/bin/env python3
"""
Implements an expiring web cache and access counter using Redis.
"""

import redis
import requests
from functools import wraps
from typing import Callable

# Connect to Redis (default localhost:6379)
redis_store = redis.Redis()

def count_and_cache(method: Callable[[str], str]) -> Callable[[str], str]:
    """
    Decorator to:
    - Increment access counter for the given URL (key: count:{url})
    - Cache the result in Redis for 10 seconds (key: result:{url})
    """
    @wraps(method)
    def wrapper(url: str) -> str:
        # Track number of times URL is accessed
        redis_store.incr(f"count:{url}")

        # Return cached result if available
        cached_result = redis_store.get(f"result:{url}")
        if cached_result:
            return cached_result.decode('utf-8')

        # Fetch, cache result with TTL=10 seconds
        result = method(url)
        redis_store.setex(f"result:{url}", 10, result)
        return result

    return wrapper

@count_and_cache
def get_page(url: str) -> str:
    """
    Fetches HTML content of the given URL using requests,
    with caching and access count tracking.
    """
    response = requests.get(url)
    return response.text
