import time
import subprocess
import yaml
import mysql.connector
from minio import Minio
from dotenv import load_dotenv
import time
import boto3
from typing import Dict, Any, List

def load_docker_compose_config() -> Dict[Any, Any]:
    with open("docker-compose.yml", "r") as file:
        return yaml.safe_load(file) # type: ignore

def stop_docker_compose() -> None:
    subprocess.run(["docker-compose", "-f", "docker-compose.yml", "down"], check=True)

def run_docker_compose() -> None:
    """Runs docker-compose up to start the stack."""
    subprocess.run(["docker-compose", "-f", "docker-compose.yml", "up", "-d"], check=True)

def wait_for_mysql(host: str, port: int, user: str, password: str) -> None:
    """Waits until MySQL is ready to accept connections."""
    while True:
        try:
            conn = mysql.connector.connect(host=host, port=port, user=user, password=password)
            conn.close()
            print("MySQL is ready!")
            break
        except mysql.connector.Error:
            print("Waiting for MySQL to be ready...")
            time.sleep(5)

def create_mysql_databases(databases: List[str], host: str, port: int, user: str, password: str) -> None:
    """Creates MySQL databases from an array."""
    conn = mysql.connector.connect(host=host, port=port, user=user, password=password)
    cursor = conn.cursor()
    for db in databases:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db};")
        print(f"Database {db} created or already exists.")
    cursor.close()
    conn.close()

def wait_for_minio(server_url: str, access_key: str, secret_key: str) -> None:
    """Waits until MinIO server is ready."""
    while True:
        try:
            client = Minio(server_url, access_key=access_key, secret_key=secret_key, secure=False)
            client.list_buckets()
            print(f"MinIO at {server_url} is ready!")
            break
        except Exception as e:
            print(f"Waiting for MinIO at {server_url}..." +  str(e))
            time.sleep(5)

def create_minio_buckets(buckets: List[str], servers: List[str], access_key: str, secret_key: str) -> None:
    """Creates buckets in MinIO servers from an array."""
    for server in servers:
        client = Minio(server, access_key=access_key, secret_key=secret_key, secure=False)
        for bucket in buckets:
            if not client.bucket_exists(bucket):
                client.make_bucket(bucket)
                print(f"Bucket {bucket} created on {server}.")
            else:
                print(f"Bucket {bucket} already exists on {server}.")

def generate_env_file(config: Dict[Any, Any]) -> None:
    env_content = """
# File Cache Configuration
FILE_CACHE_HOST=localhost
FILE_CACHE_PORT=6379

# General Cache Configuration
GENRAL_CACHE_HOST=localhost
GENRAL_CACHE_PORT=6379

# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD={password}
MYSQL_DATABASE={database}

# S3 Servers Configuration
S3_SERVERS={servers}
S3_ACCESS_KEY={access_key}
S3_SECRET_KEY={secret_key}
BUCKET_NAME={bucket}
""".format(
        password=config['services']['mysql']['environment']['MYSQL_ROOT_PASSWORD'] if 'MYSQL_ROOT_PASSWORD' in config['services']['mysql']['environment'] else '123456',
        database=config['services']['mysql']['environment']['MYSQL_DATABASE'] if 'MYSQL_DATABASE' in config['services']['mysql']['environment'] else 'metadata',
        servers=','.join([f"localhost:{srv['ports'][0].split(':')[0]}" for srv in config['services'].values() if 'minio' in srv['image']]),
        access_key=config['services']['minio1']['environment']['MINIO_ROOT_USER'] if 'MINIO_ROOT_USER' in config['services']['minio1']['environment'] else 'default_access_key',
        secret_key=config['services']['minio1']['environment']['MINIO_ROOT_PASSWORD'] if 'MINIO_ROOT_PASSWORD' in config['services']['minio1']['environment'] else 'default_secret_key',
        bucket="uploads"
    )
    with open(".build.env", "w") as f:
        f.write(env_content)
    print(".build.env file created successfully.")

def main() -> None:
    start = time.time()
    load_dotenv()
    config = load_docker_compose_config()
    
    print("Stopping existing docker-compose stack if running...")
    stop_docker_compose()
    
    print("Starting docker-compose stack...")
    run_docker_compose()
    
    mysql_host = "localhost"
    mysql_port = 3306
    mysql_user = "root"
    mysql_password = config['services']['mysql']['environment']['MYSQL_ROOT_PASSWORD']
    mysql_databases = ["metadata"]
    
    wait_for_mysql(mysql_host, mysql_port, mysql_user, mysql_password)
    create_mysql_databases(mysql_databases, mysql_host, mysql_port, mysql_user, mysql_password)
    
    minio_servers = [f"localhost:{srv['ports'][0].split(':')[0]}" for srv in config['services'].values() if 'minio' in srv['image']]
    minio_access_key = config['services']['minio1']['environment']['MINIO_ROOT_USER']
    minio_secret_key = config['services']['minio1']['environment']['MINIO_ROOT_PASSWORD']
    minio_buckets = ["uploads"]
    
    for server in minio_servers:
        wait_for_minio(server, minio_access_key, minio_secret_key)
    create_minio_buckets(minio_buckets, minio_servers, minio_access_key, minio_secret_key)
    
    generate_env_file(config)
    print(f"Setup completed in {time.time() - start} seconds.")
    print("Setup completed successfully!")

if __name__ == "__main__":
    main()
