import json
import time
import uuid
from fastapi import HTTPException
import httpx
from typing import List, Dict
from .auth import Auth  # Base authentication class
import redis

# This Python class represents a user with methods to manage API keys and load user data from Auth0.
class User(Auth):

    def __init__(self, token: str, env: Dict[str, str], redis_client: redis.StrictRedis):
        """
        The function initializes various attributes related to user data and API keys using the provided
        token, environment variables, and Redis client.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/13/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param token (str)  - The `token` parameter in the `__init__` method is expected to be a string
        representing some kind of authentication token. It is used to initialize the object along with other
        parameters like `env` and `redis_client`.
        
        .-.-.-.
        
        @ param env (Dict[str, str])  - The `env` parameter in the `__init__` method is a dictionary that
        contains environment variables. These variables are typically used to store configuration settings
        or sensitive information that the application needs to function properly. They can include things
        like database connection strings, API keys, or other settings specific to the environment
        
        .-.-.-.
        
        @ param redis_client (redis.StrictRedis)  - The `redis_client` parameter in the `__init__` method is
        of type `redis.StrictRedis`. This parameter is used to pass an instance of the Redis client to the
        class for interacting with a Redis database. It allows the class to perform operations like setting
        and getting values in the Redis database
        
        .-.-.-.
        
        """
        super().__init__(env, redis_client, token=token)

        self.redis_client = redis_client


        self.identities = None

        self.user_id = None
        self.nickname = None
        self.name = None
        self.username = None
        self.email = None
        self.picture = None
        self.email_verified = None

        self.api_keys: List[str] = []
        
        self.app_metadata = None

        self.created_at = None
        self.updated_at = None

    



    async def get_user_api_keys(self) -> List[str]:
        """
        The function `get_user_api_keys` retrieves a list of API keys associated with a user, handling cases
        where the user ID is not found or no API keys are available.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/13/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        
        
        @ returns A list of API keys is being returned. If the user ID is not found or there are no API keys
        available, an empty list will be returned.
        
        .-.-.-.
        
        
        """
        if not self.user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        if not self.api_keys:
            return []
        return self.api_keys

    async def update_user_api_keys(self, new_keys: List[str]) -> List[str]:
        """
        This Python async function updates the API keys for a user using the Auth0 Management API.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/13/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param new_keys (List[str])  - The `new_keys` parameter in the `update_user_api_keys` function is a
        list of strings representing the new API keys that you want to update for a user in the Auth0
        system. These API keys will be stored in the user's `app_metadata` under the key `api_keys`.
        
        .-.-.-.
        
        
        
        @ returns The `update_user_api_keys` method returns the updated API keys for the user after
        successfully patching the user metadata in the Auth0 management API.
        
        .-.-.-.
        
        
        """
        if not self.user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        token = await self.get_auth0_management_token()
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        url = f"https://{self.auth0_domain}/api/v2/users/{self.user_id}"
        data = {"app_metadata": {"api_keys": new_keys}}
        async with httpx.AsyncClient() as client:
            resp = await client.patch(url, headers=headers, json=data)
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail="Failed to update user metadata")
            self.api_keys = new_keys
            return self.api_keys


    async def create_api_key(self) -> str:
        """
        The `create_api_key` function generates a new API key, adds it to the user's list of API keys, and
        updates the user's API keys.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/13/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        
        
        @ returns The `create_api_key` method is returning a newly generated API key as a string.
        
        .-.-.-.
        
        
        """
        if not self.user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        new_key = str(uuid.uuid4())
        self.api_keys.append(new_key)
        await self.update_user_api_keys(self.api_keys)
        return new_key
        

    async def remove_api_key(self) -> None:
        """
        The `remove_api_key` function removes a specific API key associated with a user.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/13/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        
        
        @ returns If the `user_id` is not found, a `HTTPException` with status code 401 and detail "User ID
        not found" will be raised. If there are no `api_keys` present, the function will return without
        making any changes. If there are `api_keys` present, the function will remove the current `api_key`
        from the list of `api_keys`, update the
        
        .-.-.-.
        
        
        """
        if not self.user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        if not self.api_keys:
            return

        new_keys = [key for key in self.api_keys if key != self.api_key]
        await self.update_user_api_keys(new_keys)
        self.api_keys = new_keys
       
        
    async def load_user_data(self) -> None:
        """
        The `load_user_data` function retrieves user metadata from an external API using an authentication
        token and populates various attributes of the class instance with the retrieved data.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/13/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        
        
        @ returns The `load_user_data` method is an asynchronous function that loads user data from an
        external API (Auth0 in this case) based on the user ID extracted from the payload. If the payload is
        empty, the function returns early. Otherwise, it retrieves the user ID from the payload, makes a
        request to the Auth0 API to fetch user metadata using the user ID, and populates various attributes
        
        .-.-.-.
        
        
        """
        if not self.payload:
            return

        user_id = self.payload.get("sub", None)
        
        self.user_id = user_id

        mgmt_token = await self.get_auth0_management_token()
        headers = {"Authorization": f"Bearer {mgmt_token}"}
        url = f"https://{self.auth0_domain}/api/v2/users/{user_id}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail="Failed to retrieve user metadata")
            user_data = resp.json()
            self.nickname = user_data.get("nickname", None)
            self.name = user_data.get("name", None)
            self.username = user_data.get("username", None)
            self.email = user_data.get("email", None)
            self.picture = user_data.get("picture", None)
            self.email_verified = user_data.get("email_verified", None)
            self.identities = user_data.get("identities", None)
            self.app_metadata = user_data.get("app_metadata", None)
            self.created_at = user_data.get("created_at", None)
            self.updated_at = user_data.get("updated_at", None)
            self.api_keys = self.app_metadata.get("api_keys", []) if self.app_metadata else []
        

