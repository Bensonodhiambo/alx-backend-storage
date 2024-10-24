#!/usr/bin/env python3
"""
This module defines a Cache class that interacts with Redis to store, retrieve, 
convert, count method calls, track call history, and replay method calls.
"""
import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """
    A decorator that counts how many times a Cache method is called.

    Args:
        method (Callable): The method to be decorated.

    Returns:
        Callable: The decorated method with counting functionality.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Wrapper function that increments the call count and executes the original method.
        """
        key = method.__qualname__
        # Increment the count in Redis for this method
        self._redis.incr(key)
        # Call the original method
        return method(self, *args, **kwargs)

    return wrapper


def call_history(method: Callable) -> Callable:
    """
    A decorator that stores the history of inputs and outputs for a Cache method.

    Args:
        method (Callable): The method to be decorated.

    Returns:
        Callable: The decorated method with call history functionality.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Wrapper function that stores inputs and outputs in Redis and executes the original method.
        """
        input_key = method.__qualname__ + ":inputs"
        output_key = method.__qualname__ + ":outputs"

        # Store input arguments in the input list
        self._redis.rpush(input_key, str(args))

        # Execute the original method to get the output
        output = method(self, *args, **kwargs)

        # Store output in the output list
        self._redis.rpush(output_key, str(output))

        return output

    return wrapper


class Cache:
    """
    A Cache class for storing, retrieving, counting method calls, tracking call history, 
    and replaying method calls in Redis.
    """
    def __init__(self):
        """
        Initializes the Cache instance with a Redis client and flushes the database.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
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


def replay(method: Callable):
    """
    Displays the history of calls for a particular Cache method.

    Args:
        method (Callable): The method to replay.

    Returns:
        None: Prints the call history of the method.
    """
    cache_instance = method.__self__  # Get the Cache instance
    method_name = method.__qualname__  # Get the method's qualified name

    # Retrieve the inputs and outputs from Redis
    inputs = cache_instance._redis.lrange(f"{method_name}:inputs", 0, -1)
    outputs = cache_instance._redis.lrange(f"{method_name}:outputs", 0, -1)

    # Display the replay of the method's calls
    print(f"{method_name} was called {len(inputs)} times:")
    for inp, out in zip(inputs, outputs):
        inp_str = inp.decode("utf-8")  # Convert bytes to string
        out_str = out.decode("utf-8")  # Convert bytes to string
        print(f"{method_name}(*{inp_str}) -> {out_str}")


# Example usage
if __name__ == "__main__":
    cache = Cache()

    # Storing some data
    s1 = cache.store("foo")
    s2 = cache.store("bar")
    s3 = cache.store(42)

    # Replay the history of the store method
    replay(cache.store)

