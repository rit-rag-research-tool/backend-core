import io
from typing import Any, Dict, List, Optional
from minio import Minio
from minio.error import S3Error
from minio.datatypes import Bucket

class S3Client:
    def __init__(self, server_url: str, access_key: str, secret_key: str, verify_ssl: bool = False) -> None:
        """
        The function initializes a Minio client with specified server URL, access key, secret key, and
        SSL verification option.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/19/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param server_url (str)  - The `server_url` parameter is a string that represents the URL of
        the server where the Minio client will connect to. This URL typically includes the protocol
        (http:// or https://) and the domain or IP address of the server.
        
        .-.-.-.
        
        @ param access_key (str)  - The `access_key` parameter in the `__init__` method is used to store
        the access key required for authentication when connecting to a server. This access key is
        typically provided by the server administrator and is used along with the secret key to
        authenticate and authorize access to resources on the server.
        
        .-.-.-.
        
        @ param secret_key (str)  - The `secret_key` parameter in the `__init__` method is used to store
        the secret key required for authentication when connecting to a server. This key is typically
        used along with the `access_key` to authenticate the client with the server. It should be kept
        confidential and not shared publicly.
        
        .-.-.-.
        
        @ param verify_ssl (bool) False - The `verify_ssl` parameter in the `__init__` method is a
        boolean parameter that is set to `False` by default. It is used to determine whether SSL
        certificate verification should be performed when making requests to the server URL. If
        `verify_ssl` is set to `True`, SSL
        
        .-.-.-.
        
        
        """

        self.server_url = server_url
        self.access_key = access_key
        self.secret_key = secret_key
        self.verify_ssl = verify_ssl

        self.client = Minio(
            endpoint=server_url,
            access_key=access_key,
            secret_key=secret_key,
            secure=verify_ssl
        )

    def list_buckets(self) -> Optional[List[Bucket]]:
        """
        The function `list_buckets` attempts to list buckets using an S3 client and handles errors by
        printing a message and returning None.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/19/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        
        
        @ returns The `list_buckets` method is returning a list of Bucket objects, or `None` if an
        S3Error occurs during the operation.
        
        .-.-.-.
        
        
        """
        try:
            return self.client.list_buckets()
        except S3Error as e:
            print(f"Error listing buckets on {self.server_url}: {e}")
            return None

    def list_objects(self, bucket_name: str) -> Optional[List[Any]]:
        """
        The function `list_objects` retrieves a list of objects from a specified S3 bucket, handling any
        potential errors that may occur.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/19/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param bucket_name (str)  - The `bucket_name` parameter in the `list_objects` method is a
        string that represents the name of the S3 bucket from which you want to list objects. This
        method attempts to list all objects within the specified bucket and returns a list of objects if
        successful. If an error occurs during the process
        
        .-.-.-.
        
        
        
        @ returns The function `list_objects` is returning a list of objects in the specified S3 bucket.
        If an error occurs during the listing process, it will print an error message and return `None`.
        
        .-.-.-.
        
        
        """
        try:
            objects = self.client.list_objects(bucket_name, recursive=True)
            return list(objects)
        except S3Error as e:
            print(f"Error listing objects in bucket {bucket_name}: {e}")
            return None

    def upload_file(self, bucket_name: str, file_name: str, file_content: bytes) -> bool:
        """
        The `upload_file` function uploads a file to an S3 bucket using the provided file content.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/19/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param bucket_name (str)  - The `bucket_name` parameter in the `upload_file` method refers to
        the name of the Amazon S3 bucket where you want to upload the file. Amazon S3 is a cloud storage
        service provided by Amazon Web Services (AWS) where you can store and retrieve any amount of
        data at any time
        
        .-.-.-.
        
        @ param file_name (str)  - The `file_name` parameter in the `upload_file` method refers to the
        name of the file that you want to upload to the specified S3 bucket. It is a string that
        represents the name of the file, for example, "example.txt" or "image.jpg".
        
        .-.-.-.
        
        @ param file_content (bytes)  - The `file_content` parameter in the `upload_file` function
        represents the content of the file that you want to upload. It should be provided as a bytes
        object containing the actual data of the file you wish to upload to the specified S3 bucket.
        
        .-.-.-.
        
        
        
        @ returns The `upload_file` method returns a boolean value - `True` if the file was successfully
        uploaded to the specified S3 bucket, and `False` if an error occurred during the upload process.
        
        .-.-.-.
        
        
        """
        try:
            data_stream = io.BytesIO(file_content)
            self.client.put_object(bucket_name, file_name, data_stream, length=len(file_content))
            return True
        except S3Error as e:
            print(f"Error uploading file {file_name} to bucket {bucket_name}: {e}")
            return False

    def check_bucket_exists(self, bucket_name: str) -> bool:
        """
        The function `check_bucket_exists` checks if a bucket exists in an S3 server and returns a
        boolean value.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/19/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param bucket_name (str)  - The `bucket_name` parameter is a string that represents the name of
        the bucket you want to check for existence in an S3 storage service. The `check_bucket_exists`
        method is a function that takes the `bucket_name` as input and returns a boolean value
        indicating whether the bucket exists or not
        
        .-.-.-.
        
        
        
        @ returns The function `check_bucket_exists` is returning a boolean value. It returns `True` if
        the bucket with the specified `bucket_name` exists, and `False` if there is an error or the
        bucket does not exist.
        
        .-.-.-.
        
        
        """
        try:
            return self.client.bucket_exists(bucket_name)
        except S3Error as e:
            print(f"Error checking bucket {bucket_name} on {self.server_url}: {e}")
            return False

    def create_bucket(self, bucket_name: str) -> None:
        """
        The function `create_bucket` checks if a bucket exists and creates it if it doesn't.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/19/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param bucket_name (str)  - The `create_bucket` method takes a `bucket_name` parameter, which is a
        string representing the name of the bucket that you want to create in an S3 storage service. The
        method first checks if the bucket already exists using `self.client.bucket_exists(bucket_name)`. If
        the bucket does not
        
        .-.-.-.
        
        
        
        @ returns The `create_bucket` method is returning `None`.
        
        .-.-.-.
        
        
        """
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                print(f"Bucket {bucket_name} created successfully.")
            else:
                print(f"Bucket {bucket_name} already exists.")
        except S3Error as e:
            print(f"Error creating bucket {bucket_name}: {e}")
            return None