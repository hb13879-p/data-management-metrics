import unittest
from profiler.tabular_readers import SQLTableReader, CSVReader
from profiler.data_sources import InMemoryDataSource, SQLDataSource
from profiler.metrics import BasicProfile, TotalBlankCells, TotalRowsCols, DuplicateRows, DetectBadAddress, ExtractBadPostcode, GroupedZScore, SupervisedAnomalyDetection
from profiler.dashboards import StandardDashboard

class StandardDashboardTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        bcm_data_source = InMemoryDataSource(CSVReader(r'C:/Users/hbinning/Documents/data_profiling_tool/app/files','mortgage_data_v4.csv'))
        cls.dashboard = StandardDashboard(
                        BasicProfile(bcm_data_source)
                        ,GroupedZScore(bcm_data_source, {'id_col':'user_id','group_key':'card_type','group_value':'credit_rate'})
                        ,ExtractBadPostcode(bcm_data_source, {'id_col':'user_id','postcd_col':'PostCode'})
                        ,DetectBadAddress(bcm_data_source, {'id_col':'user_id','address_col':['address','city']})
                        ,[TotalBlankCells(bcm_data_source,{'pc':False}), TotalRowsCols(bcm_data_source), DuplicateRows(bcm_data_source)]
                        )
        cls.dashboard.calculate_dashboard()

    def test_get_columnview(self):
        columnview = self.dashboard.get_columnwise_view('mortgage_rate')
        self.assertIsInstance(columnview, dict)
