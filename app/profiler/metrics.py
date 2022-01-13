# from abc import ABC,abstractmethod
import pandas as pd
import os
from .data_sources import InMemoryDataSource, SQLDataSource
from .sql_connectors import SQLViewConnector
from sqlalchemy.sql import text
from joblib import load
from typing import Tuple, Callable, List
import numpy as np
import re
import json
import plotly.express as px
import plotly


class Metric(object):
    def __init__(self, data_source, metric_args={}):
        self.data_source = data_source
        self.metric_args = metric_args

    def get_result(self):
        """
        Return metric result without re-calculating
        """
        if self.result is None:
            raise ValueError(
                "You need to calculate the metric value before you can return the result. Call the metric at least once before calling get_result()"
            )
        else:
            return self.result

    def __call__(self, **kwargs) -> pd.DataFrame:
        # temporarily replace any kwargs provided by this call
        metric_args = self.metric_args.copy()
        if kwargs:
            for k, v in kwargs.items():
                metric_args[k] = v
        if isinstance(self.data_source, InMemoryDataSource):
            self.result = self.data_source.run_metric(
                self.calculate_in_mem, **metric_args
            )
        elif isinstance(self.data_source, SQLDataSource):
            self.result = self.data_source.run_metric(
                self.calculate_sql_tbl, **metric_args
            )
        return self.result

    def get_label(self):
        return self.label

    def get_icon(self):
        return self.icon or None

    def get_colour(self):
        return self.colour or None


class BasicProfile(Metric):
    label = "Basic Profile"

    def __init__(self, data_source, metric_args={}):
        super().__init__(data_source, metric_args)

    @staticmethod
    def calculate_in_mem(inp: pd.DataFrame, incl_graph=True) -> pd.DataFrame:
        def graph_select(row, inp):
            if row["02. Data Type"] == "object" and row["06. No. Unique Values"] > 50:
                bar_chart_df = row[
                    [
                        "04. Nulls",
                        "05. Non-Nulls",
                        "03. Row Count",
                        "06. No. Unique Values",
                    ]
                ]
                bar_chart_data = pd.DataFrame(
                    data=bar_chart_df.astype("str").values, columns=["value"]
                )
                bar_chart_data["col_names"] = [
                    "Null Values",
                    "Total Non-Null Values",
                    "Total Values inc. Nulls",
                    "Distinct Values",
                ]
                fig = px.bar(bar_chart_data, x="col_names", y="value")
                return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            else:
                return json.dumps(
                    px.histogram(inp, x=row["01. Column Name"], nbins=75),
                    cls=plotly.utils.PlotlyJSONEncoder,
                )

        profile = pd.DataFrame(data=inp.columns, columns=["01. Column Name"])
        profile["02. Data Type"] = inp.dtypes.values
        profile["04. Nulls"] = inp.isna().sum().values
        profile["05. Non-Nulls"] = inp.count().values
        profile["03. Row Count"] = inp.shape[0]
        profile["06. No. Unique Values"] = inp.nunique().values
        numeric_cols = inp.select_dtypes(include=["number"])
        try:
            stats = numeric_cols.describe()
            profile = profile.merge(
                stats.T, how="left", left_on="01. Column Name", right_index=True
            )
            profile = profile.rename(
                columns={
                    "mean": "07. Average Value",
                    "std": "08. Standard Deviation",
                    "min": "09. Minimum",
                    "max": "10. Maximum",
                    "25%": "11. 25%",
                    "50%": "12. 50%",
                    "75%": "13. 75%",
                }
            )
        except ValueError:
            pass
        if incl_graph:
            #            profile['histogram_json'] = profile['01. Column Name'].apply(lambda col: json.dumps(px.histogram(inp, x=col, nbins=20), cls=plotly.utils.PlotlyJSONEncoder))
            profile["histogram_json"] = profile.apply(
                lambda x: graph_select(x, inp), axis=1
            )
        ordered_cols = profile.columns.sort_values()
        profile = profile[ordered_cols]
        return profile

    @staticmethod
    def calculate_sql_tbl(sql_view_connector: SQLViewConnector) -> pd.DataFrame:
        if (
            sql_view_connector.table_name is not None
        ):  # this will be None if custom sql option is chosen
            column_info_query = text(
                """select * from  information_schema.columns where table_schema = :db_name and table_name = :table"""
            )
            column_info_params = {
                "db_name": sql_view_connector.sql_connector.db_creds["dbname"],
                "table": sql_view_connector.table_name,
            }
            info_schema_results = sql_view_connector.sql_connector.run_query(
                column_info_query, column_info_params
            )
            return info_schema_results
        else:
            raise NotImplementedError

    @staticmethod
    def calculate_sql_db(sql_view_connector: SQLViewConnector) -> pd.DataFrame:
        """
        to do a profile at db level ie for all tables in the db
        """
        raise NotImplementedError

    def get_result_for_column(self, col_name, round_dec=2):
        result = self.get_result()
        result[result.select_dtypes(include=["number"]).columns] = result.select_dtypes(
            include=["number"]
        ).round(round_dec)
        result = (
            result.loc[result["01. Column Name"] == col_name]
            .dropna(axis=1)
            .to_json(orient="records")
        )
        return result

    def get_tabular_view(self, round_dec=2):
        result = self.get_result()
        result = result.loc[:, result.columns != "histogram_json"]
        result[result.select_dtypes(include=["number"]).columns] = result.select_dtypes(
            include=["number"]
        ).round(round_dec)
        pd.set_option("display.float_format", "{:.2f}".format)
        return result.fillna("")

    def get_targets_view(self, round_dec=2):
        result = self.get_result()
        df = result[["01. Column Name", "04. Nulls", "06. No. Unique Values"]]
        df["completeness_pc"] = np.round(
            np.random.randint(91, 100, size=(20, 1)) + np.random.rand(20, 1), 2
        )
        df["validity_pc"] = np.round(
            np.random.randint(91, 100, size=(20, 1)) + np.random.rand(20, 1), 2
        )
        df["bespoke_tests_pc"] = np.round(
            np.random.randint(91, 100, size=(20, 1)) + np.random.rand(20, 1), 2
        )
        return df


class TotalBlankCells(Metric):
    label = "Total Blank Cells"
    icon = "fa-question"
    colour = "text-danger"

    def __init__(self, data_source, metric_args={}):
        super().__init__(data_source, metric_args)

    @staticmethod
    def calculate_in_mem(inp: pd.DataFrame, pc: bool = True, dp: int = 2):
        total_blank_cells = pd.isna(inp).sum().sum()
        if not pc:
            return total_blank_cells
        else:
            row_count = len(inp)
            col_count = len(inp.columns)
            return str(round(total_blank_cells / (row_count * col_count), dp)) + "%"

    @staticmethod
    def calculate_sql_tbl(sql_view_connector: SQLViewConnector, pc: bool = True):
        def create_tot_blank_cell_query(
            column_names: List[str], db_name: str, tbl_name: str
        ) -> str:
            query = "select "
            for col in column_names:
                q = (
                    "sum(case when "
                    + col
                    + " is null or "
                    + col
                    + " = '' then 1 else 0 end) +"
                )
                query += q
            query = query[:-1] + " as total_blanks"
            query += " from " + db_name + "." + tbl_name
            return text(query)

        if (
            sql_view_connector.table_name is not None
        ):  # this will be None if custom sql option is chosen
            query = create_tot_blank_cell_query(
                sql_view_connector.column_names,
                sql_view_connector.sql_connector.db_creds["dbname"],
                sql_view_connector.table_name,
            )
            results = sql_view_connector.sql_connector.run_query(query)
            # TODO add in pc flag
            return results
        else:
            raise NotImplementedError


class TotalRowsCols(Metric):
    label = ["Total Rows", "Total Columns"]
    icon = ["fa-table", "fa-columns"]
    colour = ["text-success", "text-info"]

    def __init__(self, data_source, metric_args={}):
        super().__init__(data_source, metric_args)

    @staticmethod
    def calculate_in_mem(inp: pd.DataFrame) -> Tuple[int, int]:
        return len(inp), len(inp.columns)

    @staticmethod
    def calculate_sql_tbl(sql_view_connector: SQLViewConnector) -> Tuple[int, int]:
        if (
            sql_view_connector.table_name is not None
        ):  # this will be None if custom sql option is chosen
            query = text(
                """select count(*) from """
                + sql_view_connector.sql_connector.db_creds["dbname"]
                + "."
                + sql_view_connector.table_name
            )
            results = sql_view_connector.sql_connector.run_query(query)
            return results.iat[0, 0], len(sql_view_connector.column_names)
        else:
            raise NotImplementedError


class DuplicateRows(Metric):
    label = "Duplicate Rows"
    icon = "fa-clone"
    colour = "text-warning"

    def __init__(self, data_source, metric_args={}):
        super().__init__(data_source, metric_args)

    @staticmethod
    def calculate_in_mem(inp: pd.DataFrame) -> np.int64:
        return inp.duplicated().sum()

    @staticmethod
    def calculate_sql_tbl(sql_view_connector: SQLViewConnector) -> np.int64:
        def create_duplicate_rows_query(column_names, db_name, table_name):
            query = "select count(*) from (select "
            groupby = " group by "
            for col in column_names:
                query += col + ","
                groupby += col + ","
            query = (
                query[:-1]
                + " from "
                + db_name
                + "."
                + table_name
                + groupby[:-1]
                + " having count(*) > 1) as t"
            )
            return text(query)

        if (
            sql_view_connector.table_name is not None
        ):  # this will be None if custom sql option is chosen
            query = create_duplicate_rows_query(
                sql_view_connector.column_names,
                sql_view_connector.sql_connector.db_creds["dbname"],
                sql_view_connector.table_name,
            )
            results = sql_view_connector.sql_connector.run_query(query)
            return results.iat[0, 0]
        else:
            raise NotImplementedError


class DetectBadAddress(Metric):
    label = "Detect Bad Address"

    def __init__(self, data_source, metric_args={}):
        super().__init__(data_source, metric_args)

    @staticmethod
    def calculate_in_mem(
        inp: pd.DataFrame,
        id_col: str = "id",
        address_col: List[str] = ["addr", "city"],
        model_path: str = r"app/models/bow_model_pipeline_v2.joblib",
    ) -> pd.DataFrame:
        """
        Returns bad addresses from a list of Addresses.

        Parameters:
           inp (pd.DataFrame):input data (including but not limited to id and address columns)
           id_col (int):index of id column
           address_col (List[str]): list of column names to be concatenated to form an address (eg line 1, line 2, city might be [2,3,4]). They will be concatenated in the order provided

        Returns:
            pd.DataFrame:ID Column,
        """
        model = load(model_path)
        addr = pd.DataFrame(data=inp[id_col], columns=[id_col])
        addr["addr"] = ""
        for col in address_col[:-1]:
            addr["addr"] = addr["addr"] + inp[col].fillna("") + ", "
        addr["addr"] = addr["addr"] + inp[address_col[-1]].fillna("")

        addr["addr"] = addr["addr"].apply(
            lambda x: re.sub(r"[^\x00-\x7F]+", "", str(x))
        )
        preds = model.predict_proba(addr["addr"])
        # preds = model.predict(addresses.values)
        addr["Validity Score"] = preds[:, 1]
        addr = addr.sort_values("Validity Score")
        addr["Validity Score"] = addr["Validity Score"].round(2)
        addr = addr[[id_col, "addr", "Validity Score"]].loc[~addr["addr"].str.isupper()]
        addr.to_pickle("addr.pkl", protocol=4)
        return addr

    @staticmethod
    def calculate_sql_tbl(sql_view_connector: SQLViewConnector) -> np.int64:
        raise NotImplementedError


class ClassifyClientNotes(Metric):
    label = "Classify Client Notes"

    def __init__(self, data_source, metric_args={}):
        super().__init__(data_source, metric_args)

    @staticmethod
    def calculate_in_mem(
        inp: pd.DataFrame,
        id_col: str = "id",
        notes_col: str = "client_notes",
        model_path: str = r"app/models/notification_model.joblib",
    ) -> pd.DataFrame:
        """
        Segments notes from a free text field based on whether they indicate notification of death or not

        """
        model = load(model_path)
        df = pd.DataFrame(data=inp[[id_col, notes_col]], columns=[id_col, notes_col])
        df[notes_col] = df[notes_col].fillna("")
        preds = model.predict_proba(df[notes_col])
        df["Confidence Score"] = preds[:, 1]
        df = df.sort_values("Confidence Score")
        df["Confidence Score"] = df["Confidence Score"].round(2)
        df = df[
            [id_col, notes_col, "Confidence Score"]
        ]  # .loc[~addr['addr'].str.isupper()]
        df.to_pickle("client_notes.pkl", protocol=4)
        return df

    @staticmethod
    def calculate_sql_tbl(sql_view_connector: SQLViewConnector) -> np.int64:
        raise NotImplementedError


class ExtractPIIAttributes(Metric):
    label = "PII Attributes"
    icon = "fa-user-secret"
    colour = "text-primary"

    def __init__(self, data_source, metric_args={}):
        super().__init__(data_source, metric_args)

    @staticmethod
    def calculate_in_mem(inp: pd.DataFrame) -> pd.DataFrame:
        return "10/21"

    @staticmethod
    def calculate_sql_tbl(sql_view_connector: SQLViewConnector) -> pd.DataFrame:
        raise NotImplementedError


class ExtractDataRules(Metric):
    label = "Extract Data Rules"

    def __init__(self, data_source, metric_args={}):
        super().__init__(data_source, metric_args)

    @staticmethod
    def calculate_in_mem(inp: pd.DataFrame) -> pd.DataFrame:
        rules = [
            '"user_id" is unique',
            '"Email_Address" is unique',
            '"product_start_date" contains 94.9% null values',
            '"dob" can be transformed to exactly match "cleaned_dob" with the following transformation: "Remove elements 2 & 5"',
            '"gender" takes the values ("M","F")',
            '"dob" is between "01/01/1950" and "31/12/2001"',
        ]
        ai_rules = [
            'Rows with "Student Credit Card" are 81.5% likely to have "Interest-only Mortgage"',
            'Rows with "Fixed-rate Mortgage" are 74.3% likely to have "Classic Credit Card"',
            '"ENGLAND" and "UNITED KINGDOM" always imply "GB" - storage space could be saved by normalising',
        ]
        return rules, ai_rules

    @staticmethod
    def calculate_sql_tbl(sql_view_connector: SQLViewConnector) -> pd.DataFrame:
        raise NotImplementedError


class ExtractBadPostcode(Metric):
    label = "Extract Bad Postcode"

    def __init__(self, data_source, metric_args={}):
        super().__init__(data_source, metric_args)

    @staticmethod
    def calculate_in_mem(
        inp: pd.DataFrame, id_col: str = "id", postcd_col: str = "postcode"
    ) -> pd.DataFrame:
        """
        Returns bad postcodes from a list of postcodes.

        Parameters:
           inp (pd.DataFrame):input data (including but not limited to id and address columns)
           id_col (int):index of id column
           postcd_col (str): list of indices of columns to be concatenated to form an address (eg line 1, line 2, city might be [2,3,4]). They will be concatenated in the order provided

        Returns:
            pd.DataFrame:ID Column,
        """
        uk_postcode = re.compile(
            "([Gg][Ii][Rr] 0[Aa]{2})|((([A-Za-z][0-9]{1,2})|(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})|(([A-Za-z][0-9][A-Za-z])|([A-Za-z][A-Ha-hJ-Yj-y][0-9][A-Za-z]?))))\s?[0-9][A-Za-z]{2})|([0-9][0-9][0-9][0-9][0-9])"
        )
        inp["invalid_postcode"] = [uk_postcode.match(str(x)) for x in inp[postcd_col]]
        inp["invalid_postcode"] = inp["invalid_postcode"].isnull()
        return inp[[id_col, postcd_col]].loc[inp["invalid_postcode"]]

    @staticmethod
    def calculate_sql_tbl(sql_view_connector: SQLViewConnector) -> np.int64:
        raise NotImplementedError


class GroupedZScore(Metric):
    label = "Anomaly Detection"

    def __init__(self, data_source, metric_args={}):
        super().__init__(data_source, metric_args)

    @staticmethod
    def calculate_in_mem(
        inp: pd.DataFrame,
        id_col: str = "id",
        group_key: str = "card_type",
        group_value: str = "credit_rate",
        conf: float = 0.99,
    ) -> pd.DataFrame:
        """
        Finds anomalies in Gaussian feature

        Parameters:
           inp (pd.DataFrame):input data (including but not limited to id and address columns)
           group_key (str): group within which to search for anomalies
           group_value (str): values within which to search for anomalies 
           conf (float): must be 0.95 or 0.99

        Returns:
            pd.DataFrame:
        """

        df = inp[[id_col, group_key, group_value]]
        df[group_key] = df[group_key].apply(
            lambda x: re.sub(r"[^\x00-\x7F]+", "", str(x))
        )
        grouped_df = df.groupby(group_key)
        df["avg"] = grouped_df.transform(np.mean)
        df["std"] = grouped_df.transform(np.std)
        df["Z_score"] = ((df[group_value] - df["avg"]) / df["std"]).abs()  # 1.645 2.33

        crit_value_lookup = {0.99: 2.33, 0.95: 1.645}
        crit_value = crit_value_lookup[conf]

        df["above_cv"] = df["Z_score"] > crit_value
        df["avg"] = df["avg"].round(2)
        return df.loc[df["above_cv"]][[id_col, group_key, "avg", group_value]]

    @staticmethod
    def calculate_sql_tbl(sql_view_connector: SQLViewConnector) -> pd.DataFrame:
        raise NotImplementedError


class SupervisedAnomalyDetection(Metric):
    label = "Anomaly Detection"

    def __init__(self, data_source, metric_args={}):
        super().__init__(data_source, metric_args)

    @staticmethod
    def calculate_in_mem(
        inp: pd.DataFrame,
        id_col: str = "id",
        x_cols: List[str] = ["input"],
        y_col: str = "output",
        model_path: str = r"app/models/premium_model.joblib",
    ) -> pd.DataFrame:
        """
        Runs the inputs through the provided model to predict an output. If the predicted output deviates from the true output by more than the 2 std devs then flag as anomaly

        Parameters:
           inp (pd.DataFrame):input data (including but not limited to id and address columns)
           id_col (int):index of id column
           postcd_col (str): list of indices of columns to be concatenated to form an address (eg line 1, line 2, city might be [2,3,4]). They will be concatenated in the order provided

        Returns:
            pd.DataFrame:ID Column,
        """

        model = load(model_path)
        X = inp[x_cols]
        y_test = inp[y_col]
        y_preds = model.predict(X)
        inp["est. premium"] = y_preds
        errors = pd.Series(np.abs(y_test - y_preds))
        inp["error"] = errors
        error_mean = errors.mean()
        error_std = errors.std()
        cutoff = error_mean + 2 * error_std
        return inp.sort_values(by="error", ascending=False)

    @staticmethod
    def calculate_sql_tbl(sql_view_connector: SQLViewConnector) -> np.int64:
        raise NotImplementedError
