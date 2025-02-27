import asyncio
import json
from typing import List, Tuple

import redis

from .s3 import S3Client


class S3Pool:
    def __init__( self,s3_servers: List[str], access_key: str, secret_key: str, bucket: str, redis_client: redis.StrictRedis) -> None:
        """
        This Python function initializes an object with parameters for S3 servers, access key, secret
        key, bucket name, and a Redis client.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/19/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param s3_servers (List[str])  - A list of strings representing the S3 server endpoints that
        the code will interact with.
        
        .-.-.-.
        
        @ param access_key (str)  - The `access_key` parameter in the `__init__` method is a string that
        represents the access key used for authentication to access the S3 servers. It is typically
        provided by the cloud service provider (such as AWS) to authorize access to resources in the S3
        buckets.
        
        .-.-.-.
        
        @ param secret_key (str)  - The `secret_key` parameter in the `__init__` method is a string that
        typically represents the secret key used for authentication when accessing resources like an S3
        server. It is a sensitive piece of information that should be kept secure and not shared
        publicly.
        
        .-.-.-.
        
        @ param bucket (str)  - The `bucket` parameter in the `__init__` method represents the name of
        the S3 bucket that will be used in the code. This bucket is where the files will be stored or
        retrieved from using the S3 clients created for each server in the `s3_servers` list.
        
        .-.-.-.
        
        @ param redis_client (redis.StrictRedis)  - The `redis_client` parameter in the `__init__`
        method is of type `redis.StrictRedis`. It is an instance of a Redis client that allows
        communication with a Redis server. This parameter is used to initialize the `self.redis_client`
        attribute of the class with the provided Redis client instance
        
        .-.-.-.
        
        
        """
        
        self.redis_client = redis_client
        self.s3_servers = s3_servers
        self.bucket = bucket
        self.s3_clients: dict[str, S3Client] = {
            server: S3Client(server, access_key, secret_key)
            for server in s3_servers
        }

    async def get_file_count(self, server: str) -> float:
        """
        The function `get_file_count` asynchronously retrieves the count of files in a specified server
        using `list_objects` offloaded to a separate thread.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/19/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param server (str)  - The `server` parameter in the `get_file_count` method represents the
        server from which you want to retrieve the file count. It is a string that specifies the server
        name or identifier.
        
        .-.-.-.
        
        
        
        @ returns The `get_file_count` method returns the number of files in the specified server's
        bucket as a float. If there is an error during the process, it returns infinity as a float.
        
        .-.-.-.
        
        
        """
        if server not in self.s3_clients:
            return float("inf")

        try:
            objects = await asyncio.to_thread(
                self.s3_clients[server].list_objects,
                self.bucket
            )
            if objects is None:
                return float("inf")
            return float(len(objects))
        except Exception as e:
            print(f"Error getting file count from {server}: {e}")
            return float("inf")

    async def get_least_loaded_server(self) -> str:
        """
        This Python async function retrieves the least loaded server by getting the file count from
        multiple servers and returning the server with the minimum file count.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/19/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        
        
        @ returns The `get_least_loaded_server` method returns the name of the S3 server with the least
        number of files stored on it.
        
        .-.-.-.
        
        
        """
        try:
            tasks = [self.get_file_count(server) for server in self.s3_servers]
            results = await asyncio.gather(*tasks)
            server_counts = dict(zip(self.s3_servers, results))
            self.redis_client.set("s3_server_file_count", json.dumps(server_counts))

            return min(server_counts, key=lambda k: server_counts[k])
        except Exception as e:
            print(f"Error determining least loaded S3 server: {e}")
            return self.s3_servers[0]

    async def upload_file(self,bucket_name: str, file_name: str, file_content: bytes) -> Tuple[str, bool]:
        """
        The function `upload_file` asynchronously uploads a file to the least loaded server using an S3
        client.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/19/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param bucket_name (str)  - The `bucket_name` parameter is a string that represents the name of
        the bucket in which you want to upload the file. In cloud storage services like Amazon S3, a
        bucket is a container for objects (files) stored in the cloud. When uploading a file, you
        specify the bucket where the
        
        .-.-.-.
        
        @ param file_name (str)  - The `file_name` parameter in the `upload_file` method is a string
        that represents the name of the file you want to upload to the specified bucket in the S3
        storage service. It is the name by which the file will be identified and stored in the bucket.
        
        .-.-.-.
        
        @ param file_content (bytes)  - The `file_content` parameter in the `upload_file` method is
        expected to be of type `bytes`, which represents the binary content of the file that you want to
        upload to the specified S3 bucket. This could be the actual content of a file that you have read
        from disk or received from
        
        .-.-.-.
        
        
        
        @ returns The function `upload_file` returns a tuple containing the `file_name` and a boolean
        value `result`.
        
        .-.-.-.
        
        
        """
        
        least_loaded_server = await self.get_least_loaded_server()

        result = await asyncio.to_thread(
            self.s3_clients[least_loaded_server].upload_file,
            bucket_name,
            file_name,
            file_content
        )

        return least_loaded_server, result

    async def upload_file_server(self, bucket_name: str, file_name: str, file_content: bytes, server: str) -> bool:
        """
        The function `upload_file_server` asynchronously uploads a file to a specified server using an
        S3 client.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param bucket_name (str)  - The `bucket_name` parameter is a string that represents the name of
        the bucket in the S3 storage service where you want to upload the file. It is used to specify
        the destination bucket for storing the file.
        
        .-.-.-.
        
        @ param file_name (str)  - The `file_name` parameter in the `upload_file_server` function
        represents the name of the file that you want to upload to the specified server. It is a string
        that should contain the name of the file including its extension (e.g., "example.txt").
        
        .-.-.-.
        
        @ param file_content (bytes)  - The `file_content` parameter in the `upload_file_server`
        function is expected to be of type `bytes`. This parameter should contain the content of the
        file that you want to upload to the specified server. When calling this function, you should
        pass the content of the file as a bytes object.
        
        .-.-.-.
        
        @ param server (str)  - The `server` parameter in the `upload_file_server` function represents
        the server where the file will be uploaded. It is a string that specifies the server's address
        or identifier where the file will be stored.
        
        .-.-.-.
        
        
        
        @ returns The `upload_file_server` function returns a boolean value indicating the success of
        the file upload operation.
        
        .-.-.-.
        
        
        """

        result = await asyncio.to_thread(
            self.s3_clients[server].upload_file,
            bucket_name,
            file_name,
            file_content
        )

        return result