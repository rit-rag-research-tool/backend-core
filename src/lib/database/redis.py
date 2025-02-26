import json
from typing import Any, Optional

import redis


# The `RedisClient` class provides methods for interacting with a Redis database, including setting
# and getting values, deleting keys, checking key existence, incrementing keys, and closing the
# connection.
class RedisClient:
    def __init__(self, host: str, port: int, db: int = 0, decode_responses: bool = True):
        self.host = host
        self.port = port
        self.db = db
        self.decode_responses = decode_responses

        self.client: redis.Redis = redis.StrictRedis(
            host=self.host,
            port=self.port,
            db=self.db,
            decode_responses=self.decode_responses
        )

    def set_value(self, key: str, value: Any, expire_time: Optional[int] = None) -> bool:
        """
        The function `set_value` sets a key-value pair in Redis with an optional expiration time,
        converting the value to JSON if it is a dictionary or list.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/14/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param key (str)  - The `key` parameter in the `set_value` method is a string that represents
        the key under which the value will be stored in the Redis database. It is used to uniquely
        identify the value being set or updated in the database.
        
        .-.-.-.
        
        @ param value ()  - The `value` parameter in the `set_value` method is the data that you want to
        store in Redis under the specified `key`. It can be of any data type (e.g., string, integer,
        list, dictionary). If the value is a dictionary or a list, it will be
        
        .-.-.-.
        
        @ param expire_time (int)  - The `expire_time` parameter in the `set_value` method is an
        optional parameter that specifies the expiration time for the key-value pair being set in Redis.
        If provided, the key-value pair will expire and be automatically deleted from the Redis database
        after the specified number of seconds. If `expire_time
        
        .-.-.-.
        
        
        
        @ returns The `set_value` method returns a boolean value - `True` if the value was successfully
        set in Redis, and `False` if there was an error encountered during the process.
        
        .-.-.-.
        
        
        """
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)  # Convert to JSON if necessary
            self.client.set(key, value, ex=expire_time)
            return True
        except Exception as e:
            print(f"Error setting value in Redis: {str(e)}")
            return False

    def get_value(self, key: str) -> Any:
        """
        The function `get_value` retrieves a value from a Redis client by a given key, handling JSON
        decoding errors and exceptions.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/14/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param key (str)  - The `key` parameter in the `get_value` method is a string that represents
        the key for which you want to retrieve the value from Redis.
        
        .-.-.-.
        
        
        
        @ returns The `get_value` method returns the value associated with the given key from a Redis
        client. If the value is a JSON string, it is converted back to a Python object using
        `json.loads`. If the value is not a valid JSON string, the original value is returned. If an
        error occurs during the process, the method prints an error message and returns `None`.
        
        .-.-.-.
        
        
        """
        try:
            value = self.client.get(key)
            if value:
                try:
                    if isinstance(value, (str, bytes, bytearray)):
                        return json.loads(value)  # Convert JSON strings back to Python objects
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            print(f"Error getting value from Redis: {str(e)}")
            return None

    def delete_key(self, key: str) -> bool:
        """
        The function `delete_key` attempts to delete a key from a client object and handles any
        exceptions that may occur during the process.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/14/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param key (str)  - The `delete_key` method takes a `key` parameter, which is a string
        representing the key that you want to delete from the client. The method attempts to delete the
        key using the client's `delete` method. If an exception occurs during the deletion process, it
        catches the exception, prints
        
        .-.-.-.
        
        
        
        @ returns The `delete_key` method is attempting to delete a key from the client. If the deletion
        is successful, it will return the result of the deletion operation. If an exception occurs
        during the deletion process, it will print an error message indicating the key that failed to be
        deleted along with the exception message, and then return `False`.
        
        .-.-.-.
        
        
        """
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            print(f"Error deleting key {key}: {str(e)}")
            return False

    async def key_exists(self, key: str) -> bool:
        """
        The function `key_exists` checks if a key exists in a client and returns a boolean value.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/14/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param key (str)  - The `key_exists` method is a function that checks if a key exists in a data
        store. The `key` parameter is a string that represents the key you want to check for existence
        in the data store. The function will return a boolean value - `True` if the key exists, and
        
        .-.-.-.
        
        
        
        @ returns The `key_exists` method is returning a boolean value indicating whether the key exists
        in the client. If the key exists, it will return `True`, otherwise it will return `False`.
        
        .-.-.-.
        
        
        """
        try:
            result = await self.client.exists(key)
            return bool(result > 0)
        except Exception as e:
            print(f"Error checking if key exists: {str(e)}")
            return False

    def increment_key(self, key: str, amount: int = 1) -> Optional[int]:
        """
        This Python function increments the value of a key in a client object by a specified amount,
        handling exceptions and returning the result or printing an error message.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/14/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param key (str)  - The `key` parameter is a string that represents the key in a key-value
        store where you want to increment the value.
        
        .-.-.-.
        
        @ param amount (int) 1 - The `amount` parameter in the `increment_key` method specifies the
        value by which the key's value should be incremented. By default, if no value is provided for
        `amount`, it will be incremented by 1. However, you can specify a different integer value for
        `amount` if you
        
        .-.-.-.
        
        
        
        @ returns The `increment_key` method is returning the result of incrementing the value
        associated with the given key by the specified amount. If the operation is successful, it
        returns the new value of the key after incrementing. If an exception occurs during the increment
        operation, it prints an error message and returns `None`.
        
        .-.-.-.
        
        
        """
        try:
            result = self.client.incr(key, amount)
            return int(str(result)) if result is not None else None
        except Exception as e:
            print(f"Error incrementing key {key}: {str(e)}")
            return None

    def close_connection(self) -> None:
        """
        The `close_connection` function attempts to close a Redis connection and prints an error message if
        an exception occurs.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/14/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        
        """
        try:
            self.client.close() #type: ignore
        except Exception as e:
            print(f"Error closing Redis connection: {str(e)}")

