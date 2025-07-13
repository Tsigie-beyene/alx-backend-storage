#!/usr/bin/env python3
"""
Module that implements request caching and tracking using Redis.

This module defines a get_page function that fetches the content of a
web page and caches it for 10 seconds. It also tracks how many times
each URL has been accessed using a Redis counter.
"""

import redis
import requests
from functools import wraps
from typing import Callable

redis_store = redis.Redis()
"""
Redis client instance for caching and counting URL accesses.
"""


def count_and_cache(method: Callable[[str], str]) -> Callable[[str], str]:
    """
    Decorator that tracks the number of times a URL is accessed
    and caches the response for 10 seconds.

    Args:
        method: The function to wrap.

    Returns:
        The wrapped function.
    """
    @wraps(method)
    def wrapper(url: str) -> str:
        """
        Wrapper function that applies counting and caching.

        Args:
            url: The URL to fetch.

        Returns:
            The content of the URL, cached if available.
        """
        redis_store.incr(f"count:{url}")
        cached_result = redis_store.get(f"result:{url}")
        if cached_result:
            return cached_result.decode('utf-8')
        result = method(url)
        redis_store.setex(f"result:{url}", 10, result)
        return result

    return wrapper


@count_and_cache
def get_page(url: str) -> str:
    """
    Fetches and returns the HTML content of the given URL.

    Uses the requests module to get the web page content.

    Args:
        url: The URL to fetch.

    Returns:
        The content of the URL as a string.
    """
    response = requests.get(url)
    return response.text
