#!/usr/bin/env python3
"""
This module defines a Cache class that interacts with Redis to store, retrieve, and convert data.
"""
import redis
import uuid
from typing import Union, Callable, Optional


class Cache:
    """
    A Cache class for storing and retrieving data in Redis.
    """
    def __init__(self):
        """
        Initializes the Cache instance with a Redis client and flushes the database.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

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

    def get_str(self
