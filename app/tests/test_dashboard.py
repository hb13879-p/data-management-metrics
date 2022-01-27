import unittest
from app.profiler.tabular_readers import SQLTableReader, CSVReader
from app.profiler.data_sources import InMemoryDataSource, SQLDataSource
from app.profiler.metrics import (
    BasicProfile,
    ExtractDataRules,
    ClassifyClientNotes,
    ExtractPIIAttributes,
    TotalBlankCells,
    TotalRowsCols,
    DuplicateRows,
    DetectBadAddress,
    ExtractBadPostcode,
    GroupedZScore,
    SupervisedAnomalyDetection,
)
from app.profiler.dashboards import Dashboard, StandardDashboard
import pandas as pd
from pandas.testing import assert_frame_equal


class BasicCustomDashboardTest(unittest.TestCase):

    def test_custom_dashboard(self):
        demo_data_source = InMemoryDataSource(CSVReader(r'app/files','demo_csv.csv'))
        custom_dash = Dashboard()
        custom_dash.add_metrics([BasicProfile(demo_data_source,{'incl_graph':False}),TotalRowsCols(demo_data_source),TotalBlankCells(demo_data_source,{'pc':True})])
        custom_dash.calculate_dashboard()
        bp,trc,tb = custom_dash.get_all_results()
        exp_results = pd.DataFrame({
                "01. Column Name": ["a", "b", "c"],
                "02. Data Type" : ["int64", "int64", "object"],
                "03. Row Count" : [3,3,3],
                "04. Nulls" : [0,0,0],
                "05. Non-Nulls" : [3,3,3],
                "06. No. Unique Values" : [3,3,3],
                "07. Average Value" : [2.0,5.0,None],
                "08. Standard Deviation" : [1.0,1.0,None],
                "09. Minimum" : [1,4,None],
                "10. Maximum" : [3.0,6.0,None],
                "11. 25%" : [1.5,4.5,None],
                "12. 50%" : [2.0,5.0,None],
                "13. 75%" : [2.5,5.5,None],
                "count" : [3,3,None],
            })
        assert_frame_equal(exp_results, bp)
        self.assertEqual(trc, (3,3))
        self.assertEqual(tb, 0)



class StandardDashboardTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        bcm_data_source = InMemoryDataSource(
            CSVReader(r"app/files", "mortgage_data_v4.csv")
        )
        cls.dashboard = StandardDashboard(
            BasicProfile(bcm_data_source),
            ExtractDataRules(bcm_data_source),
            GroupedZScore(
                bcm_data_source,
                {
                    "id_col": "user_id",
                    "group_key": "card_type",
                    "group_value": "credit_rate",
                },
            ),
            ExtractBadPostcode(
                bcm_data_source, {"id_col": "user_id", "postcd_col": "PostCode"}
            ),
            DetectBadAddress(
                bcm_data_source,
                {"id_col": "user_id", "address_col": ["address", "city"]},
            ),
            [
                TotalBlankCells(bcm_data_source, {"pc": True}),
                TotalRowsCols(bcm_data_source),
                DuplicateRows(bcm_data_source),
                ExtractPIIAttributes(bcm_data_source),
            ],
            ClassifyClientNotes(
                bcm_data_source, {"id_col": "user_id", "notes_col": "client_notes"}
            ),
        )
        cls.dashboard.calculate_dashboard()

    def test_get_columnview(self):
        columnview = self.dashboard.get_columnwise_view("mortgage_rate")
        self.assertIsInstance(columnview, str)
