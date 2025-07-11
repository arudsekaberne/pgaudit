#####################################################
# Packages                                          #
#####################################################

import pandas as pd
from typing import Any
from tabulate import tabulate
from dependencies.utilities.postgre import PGConnection


#####################################################
# Class                                             #
#####################################################


class Dataframe:

    """A utility class for handling data operations with Pandas DataFrames."""

    @classmethod
    def select_query_all(cls, query: str) -> pd.DataFrame:
        
        """
        Fetches a table records into a pandas DataFrame using SQLAlchemy engine and context manager.
        """
        
        with PGConnection() as conn:
            return pd.read_sql(sql = query, con = conn) # type: ignore
        

    @classmethod
    def select_query_one(cls, query: str) -> Any:
        
        """
        Fetches first cell table records into a pandas DataFrame using SQLAlchemy engine and context manager.
        """
        
        return cls.select_query_all(query).values[0][0]
    

    @staticmethod
    def print(df: pd.DataFrame) -> None:
        
        """
        Pretty print a pandas DataFrame using the tabulate library.
        """

        # Apply repr() to every element so that pd.NA, None, NaN show as literal.

        safe_df: pd.DataFrame = df.applymap(repr) # type: ignore

        print(f"\n{tabulate(safe_df, headers='keys', tablefmt='psql', showindex=False)}") # type: ignore