#!/usr/bin/env python3
"""
This module implements a web cache and tracker using Redis.
It fetches web pages, caches them, and tracks the number of accesses.
"""
import redis
import requests
from typing import Callable
from functools import wraps


# Initialize Redis client
_redis = redis.Redis()


def count_requests(method: Callable) -> Callable:
    """
    A decorator to count how many times a URL has been requested.

    Args:
        method (Callable): The method to be decorated.

    Returns:
        Callable: The decorated method that increments the count for the URL.
    """
    @wraps(method)
    def wrapper(url: str) -> str:
        """
        Wrapper function that increments the count for a given URL and calls the original method.
        """
        # Increment the counter for the URL
        key = f"count:{url}"
        _redis.incr(key)

        # Call the original method to get the page content
        return method(url)

    return wrapper


@count_requests
def get_page(url: str) -> str:
    """
    Fetches the HTML content of the given URL and caches it for 10 seconds.

    Args:
        url (str): The URL to fetch.

    Returns:
        str: The HTML content of the page.
    """
    cache_key = f"cached:{url}"
    cached_content = _redis.get(cache_key)

    if cached_content:
        # Return cached content if available
        return cached_content.decode('utf-8')

    # Fetch page content using requests
    response = requests.get(url)
    html_content = response.text

    # Cache the page content with an expiration time of 10 seconds
    _redis.setex(cache_key, 10, html_content)

    return html_content


if __name__ == "__main__":
    # Example usage
    url = "http://slowwly.robertomurray.co.uk/delay/5000/url/http://www.example.com"
    print(get_page(url))  # This will take time only the first time
    print(get_page(url))  # This should return quickly from cache

    # Check how many times the URL was accessed
    count_key = f"count:{url}"
    print(f"URL {url} was accessed {_redis.get(count_key).decode('utf-8')} times.")
