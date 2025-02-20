import time
import httpx
import redis
from jose import jwt
from hashlib import sha256
from typing import Tuple, Dict, Optional, Any
from fastapi import HTTPException



# The `Auth` class in Python handles authentication using environment variables, Redis client, token
# management, JWT decoding, and token revocation checks.
class Auth:
    def __init__(self, env: Dict[str, str], redis_client: redis.StrictRedis, token: Optional[str] = None) -> None:
        """
        The function initializes various attributes related to authentication using environment
        variables and a Redis client in Python.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/19/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param env (Dict[str, str])  - The `env` parameter in the `__init__` method is a dictionary
        that contains various environment variables related to authentication and authorization. These
        variables include:
        
        .-.-.-.
        
        @ param redis_client (redis.StrictRedis)  - The `redis_client` parameter in the `__init__`
        method is of type `redis.StrictRedis`. This parameter is used to pass an instance of the Redis
        client to the class when it is instantiated. The class will then use this client to interact
        with a Redis server for various operations like caching
        
        .-.-.-.
        
        @ param token (Optional[str])  - The `token` parameter in the `__init__` method is an optional
        string parameter that represents an authentication token. It is used for authentication purposes
        within the class or object that is being initialized. If a token is provided during
        initialization, it will be stored in the `self.token` attribute of
        
        .-.-.-.
        
        
        """

        self.auth0_domain = env["AUTH0_DOMAIN"]
        self.auth0_client_id = env["AUTH0_CLIENT_ID"]
        self.auth0_client_secret = env["AUTH0_CLIENT_SECRET"]
        self.auth0_audience = env["AUTH0_AUDIENCE"]
        self.auth0_mgmt_client_id = env["AUTH0_MGMT_CLIENT_ID"]
        self.auth0_mgmt_client_secret = env["AUTH0_MGMT_CLIENT_SECRET"]
        self.auth0_mgmt_audience = f"https://{self.auth0_domain}/api/v2/"

        self.redis_client = redis_client

        self.token = token
        self.payload: Dict[str, Any] = {}        

        self.known_jwks: Dict[str, Dict[str, str]] = {}

        self.auth0_mgmt_token = ""
        self.auth0_mgmt_token_expiry = 0




    def get_token_hash(self) -> str:
        """
        The function `get_token_hash` takes a token as input, checks if it exists, and returns its
        SHA-256 hash value.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/19/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        
        
        @ returns The `get_token_hash` method returns the SHA-256 hash of the token attribute after
        encoding it.
        
        .-.-.-.
        
        
        """
        if not self.token:
            raise HTTPException(status_code=401, detail="Token is required")
        return sha256(self.token.encode()).hexdigest()
        

    async def revoke_token(self) -> None:
        """
        This Python async function revokes a token by setting it as revoked in a Redis cache with an
        expiration time.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/19/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        
        """
        try:
            if self.payload:
                exp = self.payload.get("exp", int(time.time()) + 3600)
                token_hash = self.get_token_hash()
            else:
                self.payload = self.decode_jwt()
            
                self.redis_client.setex(f"revoked_token:{token_hash}", exp - int(time.time()), "revoked")
                print(f"Token revoked and will expire in {exp - int(time.time())} seconds.")
        except Exception as e:
            print(f"Failed to revoke token: {str(e)}")

    async def is_token_revoked(self) -> bool:
        """
        The function `is_token_revoked` checks if a token is revoked by looking up its hash in a Redis
        database.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/19/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        
        
        @ returns The function `is_token_revoked` returns a boolean value indicating whether the token
        is revoked or not. It checks if a token hash exists in a Redis database under the key
        "revoked_token:{token_hash}". If the token hash exists, it returns `True`, indicating that the
        token is revoked. Otherwise, it returns `False`, indicating that the token is not revoked.
        
        .-.-.-.
        
        
        """
        token_hash = self.get_token_hash()
        result = await self.redis_client.exists(f"revoked_token:{token_hash}")
        return bool(result > 0)

    def get_jwks(self) -> Dict[str, Dict[str, str]]:
        """
        This Python function retrieves and returns a JSON Web Key Set (JWKS) from a specified URL.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/19/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        
        
        @ returns The `get_jwks` method returns a dictionary where the keys are strings and the values
        are dictionaries with string keys and string values. The method fetches JSON Web Key Set (JWKS)
        from a specified URL and assigns it to `self.known_jwks` attribute before returning it.
        
        .-.-.-.
        
        
        """
        jwks_url = f"https://{self.auth0_domain}/.well-known/jwks.json"
        self.known_jwks = httpx.get(jwks_url).json()
        return self.known_jwks

    def decode_jwt(self) -> Dict[str, Any]:
        """
        The function `decode_jwt` decodes a JSON Web Token (JWT) using RSA key from JWKS and verifies it
        with specified algorithms, audience, and issuer.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/19/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        
        
        @ returns The `decode_jwt` method is returning the decoded payload from the JWT token if the
        verification is successful. If the JWT verification fails due to any reason, it will raise an
        HTTPException with a status code of 401 and provide details about the failure. If no valid key
        is found in the JWKS, it will also raise an HTTPException with a status code of 401 indicating
        the issue.
        
        .-.-.-.
        
        
        """
        jwks = self.get_jwks()

        try:
            unverified_header = jwt.get_unverified_header(self.token)
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Invalid token format: {str(e)}")

        rsa_key: Dict[str, str] = {}
        for key in jwks["keys"]:
            if isinstance(key, dict) and isinstance(unverified_header, dict) and key.get("kid") == unverified_header.get("kid"):
                rsa_key = {k: key.get(k) for k in ["kty", "kid", "use", "n", "e"]}
                break

        if rsa_key:
            try:
                self.payload = jwt.decode(
                    self.token,
                    rsa_key,
                    algorithms=["RS256"],
                    audience=self.auth0_audience, 
                    issuer=f'https://{self.auth0_domain}/'
                )
                return self.payload
            except Exception as e:
                raise HTTPException(status_code=401, detail=f"JWT verification failed: {str(e)}")
        else:
            raise HTTPException(status_code=401, detail="No valid key found in JWKS")

    async def verify_session(self) -> Dict[str, Any]:
        """
        The function `verify_session` checks the validity of a token by ensuring it is not missing,
        revoked, or expired.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/19/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        
        
        @ returns The `verify_session` method returns a dictionary containing the decoded payload of the
        JWT token after performing various checks such as ensuring the presence of a token, checking if
        the token has been revoked, and verifying if the token has expired.
        
        .-.-.-.
        
        
        """
        if not self.token:
            raise HTTPException(status_code=401, detail="Missing token in request headers")
        
        if self.token.startswith("Bearer "):
            self.token = self.token.replace("Bearer ", "").strip()

        if self.is_token_revoked():
            raise HTTPException(status_code=401, detail="Token has been revoked")

        self.payload = self.decode_jwt()
        exp = self.payload.get("exp", 0)
        

        if exp < time.time():
            raise HTTPException(status_code=401, detail="Token has expired")

        return self.payload

    async def get_auth0_management_token(self) -> str:
        """
        The function `get_auth0_management_token` retrieves and returns an Auth0 management token using
        client credentials.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/19/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        
        
        @ returns The `get_auth0_management_token` method returns the Auth0 management token as a
        string.
        
        .-.-.-.
        
        
        """
        if not self.auth0_mgmt_token or self.auth0_mgmt_token_expiry < time.time():
            url = f"https://{self.auth0_domain}/oauth/token"
            data = {
                "client_id": self.auth0_mgmt_client_id,
                "client_secret": self.auth0_mgmt_client_secret,
                "audience": self.auth0_mgmt_audience,
                "grant_type": "client_credentials"
            }

            resp = httpx.post(url, json=data)
            if resp.status_code != 200:
                raise Exception("Failed to retrieve Auth0 management token")

            token_data = resp.json()
            self.auth0_mgmt_token = token_data["access_token"]
            self.auth0_mgmt_token_expiry = time.time() + token_data["expires_in"] - 60

        return self.auth0_mgmt_token