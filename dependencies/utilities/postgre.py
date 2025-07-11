#####################################################
# Packages                                          #
#####################################################

import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from typing import Any, Dict, Final, Optional
from sqlalchemy.sql.elements import TextClause
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.engine.cursor import CursorResult
from sqlalchemy.engine.base import RootTransaction
from dependencies.utilities.credential import Credential
from dependencies.utilities.environment import Environment


#####################################################
# Main Class                                        #
#####################################################

class PGConnection:
    
    """
    Context manager and executor for PostgreSQL database connections using SQLAlchemy.
    Provides engine-level execution and pandas reading support.
    """

    SQL_PATH : Final[str] = os.path.join(os.path.dirname(Environment.get_main_path()), "dependencies", "sql")

    def __init__(self):
        
        """
        Initializes the PGConnection with SQLAlchemy engine.
        """
        
        self.engine: Optional[Engine] = None
        self.connection: Optional[Connection] = None
        self.transaction: Optional[RootTransaction] = None
        self.application_name: Final[str] = Environment.get_main_path()


    def __enter__(self) -> Connection:

        """
        Creates and returns a SQLAlchemy connection.
        """

        db_credentials: Final[Dict[str, str]] = Credential.get_db_credential()

        db_username: Final[str] = quote_plus(db_credentials["username"])
        db_password: Final[str] = quote_plus(db_credentials["password"])
        db_hostname: Final[str] = db_credentials["hostname"]
        db_port: Final[str] = db_credentials["port"]
        db_database: Final[str] = db_credentials["database"]
        db_uri: Final[str] = f"postgresql+psycopg2://{db_username}:{db_password}@{db_hostname}:{db_port}/{db_database}"

        self.engine = create_engine(db_uri, connect_args = {"application_name": self.application_name})
        self.connection = self.engine.connect()
        self.transaction = self.connection.begin()
    
        return self.connection


    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[Any]):
        
        """
        Commits or rolls back transaction, and closes the connection and engine.
        """

        if hasattr(self, "transaction") and self.transaction:
            try:
                if exc_type is None:
                    self.transaction.commit()
                else:
                    self.transaction.rollback()
                    raise RuntimeError(f"Transaction rolled back due to exception: {exc_val}") from exc_val
            finally:
                self.transaction = None

        if self.connection:
            self.connection.close()
            self.connection = None

        if self.engine:
            self.engine.dispose()
            self.engine = None


    @staticmethod
    def execute_sql(sql: str, params: Optional[Dict[str, Any]] = None) -> int:
        
        """
        Executes a SQL statement using SQLAlchemy within a managed context.
        """
        
        sql_statement: TextClause = text(sql)
        print(f"  - [SQL] {sql_statement}")
        print(f"  - [PARAM] {params}")

        with PGConnection() as conn:
            result: CursorResult[Any] = conn.execute(sql_statement, params or {})
            print(f"  - [DONE]")

            return result.rowcount


    @staticmethod
    def execute_file(file_name: str, params: Optional[Dict[str, Any]] = None) -> int:
        
        """
        Executes a SQL file using SQLAlchemy within a managed context.
        """
        
        with open(os.path.join(PGConnection.SQL_PATH, file_name), "r") as fin:
            return PGConnection.execute_sql(fin.read(), params)