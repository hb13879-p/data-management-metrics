import unittest
from app.profiler.tabular_readers import SQLTableReader, CSVReader, JSONReader, ExcelReader
from app.profiler.data_sources import InMemoryDataSource
import pandas as pd
from pandas.testing import assert_frame_equal

class InMemDataSource(unittest.TestCase):
    
    def test_cols_and_run_metric(self):
        csv_reader = CSVReader(r'app/files','demo_csv.csv')
        exp_results  = pd.DataFrame({
                "a": [1, 2, 3],
                "b": [4, 5, 6],
                "c": ["cat", "dog", "apple"],
                })            
        assert_frame_equal(exp_results, csv_reader.get_data())
        ds = InMemoryDataSource(csv_reader)
        self.assertListEqual(ds.get_column_names().tolist(), ['a','b','c'])

        def demoMetric(df):
            return df['a'].max()

        res = ds.run_metric(demoMetric)
        self.assertEqual(res, 3)

        
if __name__ == '__main__':
    unittest.main()