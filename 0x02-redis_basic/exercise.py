#!/usr/bin/env python3
"""
This module defines a Cache class that interacts with Redis to store, retrieve, and convert data,
and a decorator to count how many times a method is called.
"""
import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """
    A decorator that counts the number of times a method is called.

    Args:
        method (Callable): The method to be decorated.

    Returns:
        Callable: The wrapped method that increments the call count.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Wrapper function that increments the call count and calls the original method.
        """
        # Use the method's qualified name as the key
        key = method.__qualname__
        # Increment the count in Redis
        self._redis.incr(key)
        # Call the original method
        return method(self, *args, **kwargs)

    return wrapper


class Cache:
    """
    A Cache class for storing and retrieving data in Redis, with a call counting mechanism.
    """
    def __init__(self):
        """
        Initializes the Cache instance with a Redis client and flushes the database.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Stores the given data in Redis and returns a randomly generated key.

        Args:
            data (Union[str, bytes, int, float]): The data to be stored in Redis.

        Returns:
            str: The key associated with the stored data.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, float, None]:
        """
        Retrieves data from Redis by key and applies an optional conversion function.

        Args:
            key (str): The key to retrieve from Redis.
            fn (Callable, optional): A function to apply to the retrieved data. Defaults to None.

        Returns:
            Union[str, bytes, int, float, None]: The retrieved data, optionally transformed by fn.
        """
        data = self._redis.get(key)
        if data is None:
            return None
        if fn:
            return fn(data)
        return data

    def get_str(self, key: str) -> Optional[str]:
        """
        Retrieves data as a UTF-8 decoded string.

        Args:
            key (str): The key to retrieve from Redis.

        Returns:
            Optional[str]: The data as a decoded string if available, None otherwise.
        """
        return self.get(key, lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> Optional[int]:
        """
        Retrieves data as an integer.

        Args:
            key (str): The key to retrieve from Redis.

        Returns:
            Optional[int]: The data as an integer if available, None otherwise.
        """
        return self.get(key, lambda d: int(d))


# Example usage
if __name__ == "__main__":
    cache = Cache()

    # Call store and check how many times it was called
    cache.store(b"first")
    print(cache.get(cache.store.__qualname__))  # Should print b'1'

    cache.store(b"second")
    cache.store(b"third")
    print(cache.get(cache.store.__qualname__))  # Should print b'3'
