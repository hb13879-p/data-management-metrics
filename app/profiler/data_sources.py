from abc import ABC, abstractmethod
import pandas as pd
import os
from typing import Callable
from .tabular_readers import TabularDataReader
from .sql_connectors import SQLViewConnector


class DataSource(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def run_metric(self, func: Callable, **kwargs):
        pass


class InMemoryDataSource(DataSource):
    def __init__(self, data_reader: TabularDataReader):
        self.data_reader = data_reader
        self.data = self.data_reader.get_data()

    def get_column_names(self):
        return self.data.columns

    def run_metric(self, func: Callable, **kwargs):
        if kwargs:
            return func(self.data, **kwargs)
        else:
            return func(self.data)


class SQLDataSource(DataSource):
    def __init__(self, sql_view_connector: SQLViewConnector):
        self.sql_view_connector = sql_view_connector

    def get_column_names(self):
        return self.sql_view_connector.column_names

    def run_metric(self, func: Callable, **kwargs):
        if kwargs:
            return func(self.sql_view_connector, **kwargs)
        else:
            return func(self.sql_view_connector)
