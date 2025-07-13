#!/usr/bin/env python3
"""
A module that implements an expiring web cache and request tracker using Redis.
"""

import redis
import requests
from functools import wraps
from typing import Callable

# Initialize Redis client
redis_store = redis.Redis()

def data_cacher(method: Callable[[str], str]) -> Callable[[str], str]:
    """
    Decorator to cache page responses and track access count.
    """
    @wraps(method)
    def wrapper(url: str) -> str:
        # Track how many times this URL is accessed
        redis_store.incr(f"count:{url}")

        # Try to get cached result
        cached_result = redis_store.get(f"result:{url}")
        if cached_result:
            return cached_result.decode('utf-8')

        # If not cached, fetch result and cache it for 10 seconds
        result = method(url)
        redis_store.setex(f"result:{url}", 10, result)
        return result

    return wrapper

@data_cacher
def get_page(url: str) -> str:
    """
    Fetches and returns the content of a URL.
    Caching and tracking are handled by the data_cacher decorator.
    """
    response = requests.get(url)
    return response.text
