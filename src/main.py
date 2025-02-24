import os
import asyncio
import uvicorn
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv

from typing import Any, Type, AsyncGenerator

from lib import MySQLClient, S3Pool, RedisClient
from routes import router as base_router

FILE_VERSION = "0.1.0"

# Load environment variables
load_dotenv()
def get_env(var: str, conv: Type[Any] = str) -> Any:
    value = os.getenv(var)
    if value is None:
        exit(f"ERROR: {var} is not set")
    return conv(value)

file_cache_client = RedisClient(
    host=get_env("FILE_CACHE_HOST"),
    port=int(get_env("FILE_CACHE_PORT")),
    db=0,
    decode_responses=True
)
general_cache_client = RedisClient(
    host=get_env("GENRAL_CACHE_HOST"),
    port=int(get_env("GENRAL_CACHE_PORT")),
    db=0,
    decode_responses=True
)


mysql_client = MySQLClient(
    host=get_env("MYSQL_HOST"),
    user=get_env("MYSQL_USER"),
    password=get_env("MYSQL_PASSWORD"),
    database=get_env("MYSQL_DATABASE"),
    port=int(get_env("MYSQL_PORT"))
)

s3_servers = get_env("S3_SERVERS").split(",")
s3_pool = S3Pool(
    s3_servers,
    get_env("S3_ACCESS_KEY"),
    get_env("S3_SECRET_KEY"),
    get_env("BUCKET_NAME"),
    general_cache_client.client  
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    try:
        if not general_cache_client.client.ping():
            raise ConnectionError("KeyDB is not reachable.")
        print("general_cache_client connection established.")
    except Exception as e:
        raise RuntimeError(f"Failed to connect to KeyDB: {str(e)}")

    try:
        if not file_cache_client.client.ping():
            raise ConnectionError("Redis is not reachable.")
        print("file_cache_client connection established.")
    except Exception as e:
        general_cache_client.close_connection()
        raise RuntimeError(f"Failed to connect to Redis: {str(e)}")

    await mysql_client.connect()
    if not mysql_client.is_connected():
        raise RuntimeError("MySQL is not reachable.")
    else:
        print("MySQL connection established.")

    try:
        results = await asyncio.gather(*(s3_pool.get_file_count(server) for server in s3_pool.s3_servers))
        print(results)
        if any(result == float('inf') for result in results):
            raise ConnectionError("Some or all S3 servers are not reachable.")
        print("S3 servers are reachable.")
    except Exception as e:
        general_cache_client.close_connection()
        file_cache_client.close_connection()
        await mysql_client.close()
        raise RuntimeError(f"Failed to connect to S3 servers: {str(e)}")

    app.state.mysql_client = mysql_client
    app.state.general_cache_client = general_cache_client
    app.state.file_cache_client = file_cache_client
    app.state.s3_pool = s3_pool
    app.state.env = dict(os.environ)

    print("-" * 20)
    print("Routes:")
    print("  /upload/")
    print("  /embedding-status/{embedding_id}")
    print("  /apikeys/new")
    print("  /apikeys")
    print("  /apikeys/remove")
    print("  /logout")
    print("-" * 20)

    yield

    # Shutdown: Close the connections
    general_cache_client.close_connection()
    file_cache_client.close_connection()
    await mysql_client.close()
    print("Connections closed.")


app = FastAPI(lifespan=lifespan, title="RagStack", description=f"Backend Version: {FILE_VERSION}", version=FILE_VERSION, root_path="/src",)
app.include_router(base_router)



# Uncomment for local development:
# if __name__ == "__main__":
#     uvicorn.run(app, host="localhost", port=8000)