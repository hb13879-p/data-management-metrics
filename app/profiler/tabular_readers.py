from abc import ABC, abstractmethod
from typing import Dict
import pandas as pd
import os
import logging
from .sql_connectors import SQLViewConnector


class TabularDataReader(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_data(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def read_in_data(self):
        pass


class SQLTableReader(SQLViewConnector, TabularDataReader):
    # can either provide table name or custom sql to return a table of results
    def __init__(
        self,
        sql_dialect: str,
        db_creds: Dict[str, str],
        table_name: str = None,
        custom_sql: str = None,
    ):
        super().__init__(
            sql_dialect, db_creds, table_name=table_name, custom_sql=custom_sql
        )
        self.read_in_data()

    def read_in_data(self):
        self.data = self.sql_connector.run_query(
            self.main_query_sql, params=self.main_query_params
        )

    def get_data(self) -> pd.DataFrame:
        return self.data


class DataFrameReader(TabularDataReader):
    def __init__(self, df):
        self.data = df
        self.read_in_data()

    def read_in_data(self):
        # TODO add validation checks
        pass

    def get_data(self) -> pd.DataFrame:
            return self.data

class CSVReader(TabularDataReader):
    def __init__(self, path: str, filename: str):
        self.path = path
        self.filename = filename
        self.read_in_data()

    def read_in_data(self):
        self.data = pd.read_csv(os.path.join(self.path, self.filename))

    def get_data(self) -> pd.DataFrame:
        return self.data


class ExcelReader(TabularDataReader):
    def __init__(self, path: str, filename: str):
        self.path = path
        self.filename = filename
        self.read_in_data()

    def read_in_data(self):
        self.data = pd.read_excel(os.path.join(self.path, self.filename), engine='openpyxl')

    def get_data(self) -> pd.DataFrame:
        return self.data


class JSONReader(TabularDataReader):
    def __init__(self, path: str, filename: str):
        self.path = path
        self.filename = filename
        self.read_in_data()

    def read_in_data(self):
        self.data = pd.read_json(os.path.join(self.path, self.filename))

    def get_data(self) -> pd.DataFrame:
        return self.data
