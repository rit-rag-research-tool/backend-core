from typing import Dict

from fastapi import Header, HTTPException, Request

from lib.database.mysql import MySQLClient
from lib.database.redis import RedisClient
from lib.database.s3_pool import S3Pool
from lib.database.croma import CromaDBClient
from lib.user import User
from lib.llm import LLMClient
from lib.embed import EmbeddingClient



def get_mysql_client(request: Request) -> MySQLClient:
    """
    The function `get_mysql_client` returns the MySQL client from the state of the request application.
    
    .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
    
    Author - Liam Scott
    Last update - 02/23/2025
    
    .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
    
    @ param request (Request)  - The `request` parameter in the `get_mysql_client` function is of type
    `Request`, which likely represents an HTTP request object. It is used to access the application
    state to retrieve the MySQL client instance.
    
    .-.-.-.
    
    
    
    @ returns The function `get_mysql_client` is returning the MySQL client stored in the state of the
    FastAPI application that is passed in the request object.
    
    .-.-.-.
    
    
    """
    if "mysql_client" not in request.app.state:
        raise HTTPException(status_code=500, detail="MySQL client not initialized")
    if isinstance(request.app.state.mysql_client, MySQLClient):
        return request.app.state.mysql_client
    raise HTTPException(status_code=500, detail="Error with MySQL client initialization")

def get_general_cache_client(request: Request) -> RedisClient:
    """
    The function `get_general_cache_client` returns the Redis client from the general cache client
    stored in the request's application state.
    
    .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
    
    Author - Liam Scott
    Last update - 02/23/2025
    
    .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
    
    @ param request (Request)  - The `request` parameter in the `get_general_cache_client` function is
    of type `Request`, which is likely an object representing an HTTP request in a web application
    framework. It is used to access the application state where the `general_cache_client` is stored.
    
    .-.-.-.
    
    
    
    @ returns The function `get_general_cache_client` is returning the Redis client associated with the
    general cache from the application state in the request.
    
    .-.-.-.
    
    
    """
    if "general_cache_client" not in request.app.state:
        raise HTTPException(status_code=500, detail="General cache client not initialized")
    if isinstance(request.app.state.general_cache_client, RedisClient):
        return request.app.state.general_cache_client
    raise HTTPException(status_code=500, detail="Error with general cache client initialization")

def get_file_cache_client(request: Request) -> RedisClient:
    """
    The function `get_file_cache_client` returns the Redis client stored in the state of the request
    application.
    
    .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
    
    Author - Liam Scott
    Last update - 02/23/2025
    
    .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
    
    @ param request (Request)  - Request object containing information about the incoming HTTP request.
    
    .-.-.-.
    
    
    
    @ returns The function `get_file_cache_client` is returning the Redis client stored in the
    `file_cache_client` attribute of the application state in the request object.
    
    .-.-.-.
    
    
    """
    if "file_cache_client" not in request.app.state:
        raise HTTPException(status_code=500, detail="File cache client not initialized")
    if isinstance(request.app.state.file_cache_client, RedisClient):
        return request.app.state.file_cache_client
    raise HTTPException(status_code=500, detail="Error with file cache client initialization")

def get_s3_pool(request: Request) -> S3Pool:
    """
    The function `get_s3_pool` returns the S3 connection pool from the application state based on the
    provided request.
    
    .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
    
    Author - Liam Scott
    Last update - 02/23/2025
    
    .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
    
    @ param request (Request)  - Request object containing information about the incoming HTTP request.
    It typically includes data such as headers, body, and query parameters.
    
    .-.-.-.
    
    
    
    @ returns The function `get_s3_pool` is returning the S3Pool object from the state of the
    application's request.
    
    .-.-.-.
    
    
    """
    if "s3_pool" not in request.app.state:
        raise HTTPException(status_code=500, detail="S3 pool not initialized")
    if isinstance(request.app.state.s3_pool, S3Pool):
        return request.app.state.s3_pool
    raise HTTPException(status_code=500, detail="Error with pool initialization")

def get_env(request: Request) -> Dict[str, str]:
    """
    The function `get_env` returns the environment variables stored in the state of the application from
    the provided request.
    
    .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
    
    Author - Liam Scott
    Last update - 02/23/2025
    
    .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
    
    @ param request (Request)  - Request object containing information about the incoming HTTP request.
    It typically includes details such as headers, query parameters, and body content.
    
    .-.-.-.
    
    
    
    @ returns A dictionary containing environment variables is being returned.
    
    .-.-.-.
    
    
    """
    if "env" not in request.app.state:
        raise HTTPException(status_code=500, detail="Environment variables not initialized")
    if isinstance(request.app.state.env, dict):
        return request.app.state.env
    raise HTTPException(status_code=500, detail="Error with environment variables initialization")

async def get_current_user( request: Request, authorization: str = Header(..., alias="Authorization") ) -> User:
    """
    The `get_current_user` function extracts the token from the Authorization header, creates a User
    object, loads user data, and verifies the session before returning the user.
    
    .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
    
    Author - Liam Scott
    Last update - 02/23/2025
    
    .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
    
    @ param request (Request)  - The `request` parameter is of type `Request`, which likely represents
    an HTTP request object. It contains information about the incoming request such as headers, query
    parameters, and more.
    
    .-.-.-.
    
    @ param authorization (str)  - The `authorization` parameter in the `get_current_user` function is
    used to extract the token from the request headers. The token is expected to be passed in the
    `Authorization` header using the format `Bearer <token>`. The function then creates a `User` object
    using the extracted token,
    
    .-.-.-.
    
    
    
    @ returns The `get_current_user` function returns a `User` object after loading user data and
    verifying the session. If the user is not valid or the token is invalid or expired, it raises an
    HTTPException with the appropriate status code and detail message.
    
    .-.-.-.
    
    
    """

    #api keys are not supported in this version
    token = authorization.split("Bearer ")[-1]
    user = User(
        token=token,
        env=request.app.state.env,
        redis_client=request.app.state.general_cache_client.client
    )
    await user.load_user_data()
    if not user.user_id:
        raise HTTPException(status_code=401, detail="Invalid user")
    
    if not await user.verify_session():
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user

def get_croma_client(request: Request) -> CromaDBClient:
    """
    The function `get_croma_client` retrieves the CromaDBClient from the request if it has been
    initialized, otherwise raises an HTTPException.
    
    .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
    
    Author - Liam Scott
    Last update - 02/26/2025
    
    .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
    
    @ param request (Request)  - The `request` parameter in the `get_croma_client` function is of type
    `Request`, which is likely an object representing an HTTP request in a web application framework.
    This parameter is used to access the application state where the `CromaDBClient` instance is stored.
    
    .-.-.-.
    
    
    
    @ returns The function `get_croma_client` returns the CromaDBClient instance stored in the
    `request.app.state` if it exists and is of the correct type. If the client is not initialized or
    there is an error with the initialization, it raises an HTTPException with a status code of 500 and
    an appropriate error message.
    
    .-.-.-.
    
    
    """
    if "croma_client" not in request.app.state:
        raise HTTPException(status_code=500, detail="CromaDB client not initialized")
    if isinstance(request.app.state.croma_client, CromaDBClient):
        return request.app.state.croma_client
    raise HTTPException(status_code=500, detail="Error with CromaDB client initialization")

def get_llm_client(request: Request) -> LLMClient:
    """
    The function `get_llm_client` retrieves the LLMClient object from the request's application state.
    
    .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
    
    Author - Liam Scott
    Last update - 02/26/2025
    
    .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
    
    @ param request (Request)  - The `request` parameter in the `get_llm_client` function is of type
    `Request`, which is likely an object representing an HTTP request in a web application framework. It
    is used to access information about the incoming request such as headers, parameters, and body
    content.
    
    .-.-.-.
    
    
    
    @ returns The function `get_llm_client` is returning the LLMClient object stored in the
    `request.app.state.llm_client` if it is an instance of `LLMClient`. If the `llm_client` is not found
    in the request's app state or if it is not an instance of `LLMClient`, the function raises an
    HTTPException with a status code of 500 and
    
    .-.-.-.
    
    
    """

    if "llm_client" not in request.app.state:
        raise HTTPException(status_code=500, detail="llm client not initialized")
    if isinstance(request.app.state.llm_client, LLMClient):
        return request.app.state.llm_client
    raise HTTPException(status_code=500, detail="Error with llm client initialization")

def get_embedding_client(request: Request) -> EmbeddingClient:
    """
    The function `get_embedding_client` retrieves an EmbeddingClient from the request's application
    state, raising an exception if not found or if the client is not properly initialized.
    
    .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
    
    Author - Liam Scott
    Last update - 02/26/2025
    
    .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
    
    @ param request (Request)  - The `request` parameter in the `get_embedding_client` function is of
    type `Request`, which is likely an object representing an HTTP request in a web application
    framework. It is used to access information about the incoming request, such as headers, query
    parameters, and request body.
    
    .-.-.-.
    
    
    
    @ returns the `EmbeddingClient` object stored in the `embedding_client` key of the
    `request.app.state` dictionary. If the `embedding_client` key is not found in the
    `request.app.state`, it raises an HTTPException with a status code of 500 and the detail message
    "Embedding client not initialized". If the `embedding_client` is not an instance of `
    
    .-.-.-.
    
    
    """

    if "embedding_client" not in request.app.state:
        raise HTTPException(status_code=500, detail="Embedding client not initialized")
    if isinstance(request.app.state.embedding_client, EmbeddingClient):
        return request.app.state.embedding_client
    raise HTTPException(status_code=500, detail="Error with embedding client initialization")