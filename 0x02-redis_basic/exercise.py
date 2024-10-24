#!/usr/bin/env python3
"""
This module defines a Cache class that interacts with Redis to store and retrieve data.
"""
import redis
import uuid
from typing import Union


class Cache:
    """
    A Cache class for storing data in Redis.
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
