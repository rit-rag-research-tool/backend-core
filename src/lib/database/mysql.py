import aiomysql
from typing import List, Tuple, Optional, Any, Dict



class MySQLClient:
    def __init__(self, host: str, user: str, password: str, database: str,port: int = 3306) -> None:
        """
        This Python function initializes connection parameters for a database using aiomysql.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/20/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param host (str)  - The `host` parameter in the `__init__` method represents the hostname or
        IP address of the database server to which you want to connect. This is where your database is
        located and where your application will send its database queries.
        
        .-.-.-.
        
        @ param user (str)  - The `user` parameter in the `__init__` method is a string that represents
        the username used to connect to the database server. It is typically used for authentication
        purposes to identify the user who is accessing the database.
        
        .-.-.-.
        
        @ param password (str)  - The `password` parameter in the `__init__` method is a string type
        parameter. It is used to store the password required for connecting to a database server. In
        this case, it seems to be used for establishing a connection to a MySQL database server.
        
        .-.-.-.
        
        @ param database (str)  - The `database` parameter in the `__init__` method represents the name
        of the database you want to connect to. It is a required parameter for establishing a connection
        to a specific database on the MySQL server.
        
        .-.-.-.
        
        @ param port (int) 3306 - The `port` parameter in the `__init__` method is used to specify the
        port number for the database connection. In this case, the default port is set to 3306 for MySQL
        databases. However, you can override this default value by providing a different port number
        when creating an instance
        
        .-.-.-.
        
        
        """

        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port

        self.pool: Optional[aiomysql.Pool] = None

    async def connect(self) -> None:
        """
        The `connect` function establishes a MySQL connection pool using aiomysql in Python asyncio.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/20/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        
        """
        if not self.pool:
            try:
                self.pool = await aiomysql.create_pool(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    db=self.database,
                    port=self.port,
                    autocommit=True,
                    cursorclass=aiomysql.cursors.DictCursor
                )
                print("MySQL connection pool established successfully.")
            except aiomysql.Error as e:
                print(f"MySQL connection error: {str(e)}")
                self.pool = None

    def is_connected(self) -> bool:
        """
        The function `is_connected` returns a boolean value indicating whether the pool is not None.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/19/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        
        
        @ returns The method `is_connected` is returning a boolean value indicating whether the `pool`
        attribute of the object is not `None`.
        
        .-.-.-.
        
        
        """
        return self.pool is not None

    async def execute_query(self, query: str, params: Optional[Tuple[Any, ...]] = None ) -> List[Dict[str, Any]]:
        """
        This Python async function executes a query using aiomysql, handling connection, execution, and
        error cases.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/19/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param query (str)  - The `query` parameter in the `execute_query` method is a string that
        represents the SQL query that you want to execute. This query will be sent to the database for
        execution.
        
        .-.-.-.
        
        @ param params (Optional[Tuple[Any, ...]])  - The `params` parameter in the `execute_query`
        method is used to pass any parameters that need to be substituted into the SQL query. These
        parameters are typically used in query placeholders to prevent SQL injection attacks and to
        provide dynamic values to the query. The `params` parameter is optional and is a
        
        .-.-.-.
        
        
        
        @ returns A list of dictionaries containing the results of the query is being returned. If there
        are no results, an empty list is returned. If there is an error during the execution of the
        query, an empty list is also returned.
        
        .-.-.-.
        
        
        """
        if not self.is_connected():
            await self.connect()
        if not self.pool:
            return []

        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, params)
                    results = await cursor.fetchall()
                    return results if results else []
        except aiomysql.Error as e:
            print(f"MySQL query error: {str(e)}")
            return []

    async def execute_commit(self,query: str, params: Optional[Tuple[Any, ...]] = None) -> bool:
        """
        This function executes a SQL query with optional parameters and commits the transaction in an
        asynchronous manner using aiomysql in Python.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/19/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param query (str)  - The `query` parameter in the `execute_commit` method is a string that
        represents the SQL query that you want to execute. This query can be any valid SQL statement
        such as INSERT, UPDATE, DELETE, or even SELECT.
        
        .-.-.-.
        
        @ param params (Optional[Tuple[Any, ...]])  - The `params` parameter in the `execute_commit`
        method is used to pass a tuple of parameters that will be used in the query. These parameters
        will be safely interpolated into the query to prevent SQL injection attacks. If the query
        contains placeholders (usually represented by `?` or `%s`),
        
        .-.-.-.
        
        
        
        @ returns The `execute_commit` method returns a boolean value. It returns `True` if the query
        execution and commit were successful, and `False` if there was an error during the process.
        
        .-.-.-.
        
        
        """
        if not self.is_connected():
            await self.connect()
        if not self.pool:
            return False

        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, params)
                    # autocommit=True (set in pool) typically handles commits, this is redundant for now may remove later (conn.commit())
                    await conn.commit()
                    return True
        except aiomysql.Error as e:
            print(f"MySQL commit error: {str(e)}")
            return False

    async def keep_alive(self) -> None:
        """
        The `keep_alive` function checks and maintains the MySQL connection status in an asynchronous
        Python program.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/19/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        
        
        @ returns If the `self.pool` is empty (falsy), the function will return without performing any
        further actions.
        
        .-.-.-.
        
        
        """
        if not self.is_connected():
            await self.connect()
        if not self.pool:
            return

        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT 1")
                    await cursor.fetchone()
            print("MySQL connection is alive.")
        except aiomysql.Error as e:
            print(f"MySQL connection error: {str(e)}")
            self.pool = None
            await self.connect()

    async def close(self) -> None:
        """
        This Python async function closes a MySQL connection pool if it exists.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 02/19/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        
        """
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            self.pool = None
            print("MySQL connection pool closed.")
