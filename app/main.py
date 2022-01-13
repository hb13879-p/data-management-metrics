from profiler.data_sources import InMemoryDataSource
from profiler.tabular_readers import CSVReader
from profiler.metrics import BasicProfile, TotalBlankCells, TotalRowsCols, DuplicateRows, DetectBadAddress, ExtractBadPostcode, GroupedZScore, SupervisedAnomalyDetection
from profiler.dashboards import Dashboard, StandardDashboard


if __name__ == '__main__':
    bcm_data_source = InMemoryDataSource(CSVReader(r'C:\Users\hbinning\Documents\data_profiling_tool\app\files','mortgage_data_v4.csv'))
    dashboard = StandardDashboard(
                        BasicProfile(bcm_data_source)
                        ,GroupedZScore(bcm_data_source, {'id_col':'user_id','group_key':'card_type','group_value':'credit_rate'})
                        ,ExtractBadPostcode(bcm_data_source, {'id_col':'user_id','postcd_col':'PostCode'})
                        ,DetectBadAddress(bcm_data_source, {'id_col':'user_id','address_col':['address','city']})
                        ,[TotalBlankCells(bcm_data_source), TotalRowsCols(bcm_data_source)]
                        )
    dashboard.calculate_all_metrics()
    dashboard.print_all_results()