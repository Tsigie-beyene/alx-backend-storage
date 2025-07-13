#!/usr/bin/env python3
"""
This module provides a function to retrieve web pages with caching
and access counting using Redis. The page content is cached for a
limited time to improve efficiency and performance.
"""

import redis
import requests
from functools import wraps
from typing import Callable

redis_store = redis.Redis()
"""
The Redis client instance used to store cached page content and count accesses.
"""


def count_and_cache(method: Callable[[str], str]) -> Callable[[str], str]:
    """
    Decorator that counts how many times a URL has been accessed
    and caches the web page response for 10 seconds.

    Args:
        method: The function used to retrieve the web page content.

    Returns:
        A decorated function that counts accesses and caches the result.
    """
    @wraps(method)
    def wrapper(url: str) -> str:
        """
        Wrapper function that implements the counting and caching logic.

        Args:
            url: The URL to retrieve content from.

        Returns:
            The HTML content of the URL as a string. Cached if previously requested.
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
    Fetches the content of a web page using the requests module.

    This function is decorated to count how many times the URL was requested
    and cache the result for 10 seconds using Redis.

    Args:
        url: The URL of the web page to fetch.

    Returns:
        The content of the web page as a string.
    """
    response = requests.get(url)
    return response.text
