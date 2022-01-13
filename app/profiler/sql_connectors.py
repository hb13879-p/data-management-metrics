import pandas as pd
from sqlalchemy import create_engine
from typing import Dict
from sqlalchemy.sql import text


class SQLConnector(object):
    @staticmethod
    def sql_connector_factory(prefix, db_creds):
        class MySQLConnector(SQLConnector):
            prefix = "mysql+pymysql"

            def __init__(self, db_creds: Dict[str, str]):
                super().__init__(db_creds)

        if prefix == "mysql":
            return MySQLConnector(db_creds)
        else:
            raise ValueError("Please specify desired SQL dialect...")

    def __init__(self, db_creds: Dict[str, str]):
        if self.prefix is None:
            raise ValueError(
                'Please instatiate subclass by choosing a sql dialect and using factory method eg SQLConnector.sql_connector_factory("mysql", db_creds)'
            )
        self.db_creds = db_creds
        self.create_db_engine()

    def create_conn_string(self, prefix: str, db_creds: Dict[str, str]):
        return "{0}://{1}:{2}@{3}:{4}/{5}?charset=utf8mb4".format(
            prefix,
            db_creds["user"],
            db_creds["password"],
            db_creds["server"],
            str(db_creds["port"]),
            db_creds["dbname"],
        )

    def create_db_engine(self):
        conn_str = self.create_conn_string(self.prefix, self.db_creds)
        self.engine = create_engine(conn_str, encoding="utf8")

    def run_query(self, query, params=None):
        with self.engine.connect() as conn:
            if params is None:
                results = conn.execute(query)
                keys = conn.execute(query).keys()
            else:
                results = conn.execute(query, params)
                keys = conn.execute(query, params).keys()
        return pd.DataFrame(results.fetchall(), columns=keys)

    def get_query_metadata(self, query, params=None):
        with self.engine.connect() as conn:
            if params is None:
                return conn.execute(query).keys()
            else:
                return conn.execute(query, params).keys()


class SQLViewConnector(object):
    def __init__(
        self,
        sql_dialect: str,
        db_creds: Dict[str, str],
        table_name: str = None,
        custom_sql: str = None,
        custom_sql_params: str = None,
    ):
        self.sql_connector = SQLConnector.sql_connector_factory(sql_dialect, db_creds)
        if table_name is not None and custom_sql is not None:
            logging.warning("Both table name and sql provided. Table name is used")
        elif custom_sql is None and table_name is None:
            raise ValueError(
                "Please provide either a table name or custom SQL returning a table"
            )
        if table_name is not None:
            self.main_query_sql = text(
                "select * from " + db_creds["dbname"] + "." + table_name
            )
            self.main_query_params = None
            self.table_name = table_name
        elif custom_sql is not None:
            self.main_query_sql = custom_sql
            self.main_query_params = custom_sql_params
        self.column_names = self.sql_connector.get_query_metadata(
            self.main_query_sql, params=self.main_query_params
        )
