import unittest
from app.profiler.tabular_readers import SQLTableReader, CSVReader, JSONReader, ExcelReader
import pandas as pd
from pandas.testing import assert_frame_equal

class DataFileReadInTest(unittest.TestCase):
    # def test_mysql(self):
    #     db_creds = {'user':'root','password':'henryI&D123','server':'localhost','port':3306,'dbname':'demo_db'}
    #     table_name = 'DPR_Mortgage_Data'
    #     mysql_reader = SQLTableReader('mysql', db_creds, table_name=table_name)
    #     self.assertIsInstance(mysql_reader, SQLTableReader)
        #print(mysql_reader.get_data())

    def test_read_csv(self):
        csv_reader = CSVReader(r'app/files','demo_csv.csv')
        exp_results  = pd.DataFrame({
                "a": [1, 2, 3],
                "b": [4, 5, 6],
                "c": ["cat", "dog", "apple"],
                })            
        assert_frame_equal(exp_results, csv_reader.get_data())

    def test_read_json(self):
        json_reader = JSONReader(r'app/files','demo_json.json')
        exp_results  = pd.DataFrame({
                "a": [1, 2, 3],
                "b": [4, 5, 6],
                "c": ["cat", "dog", "apple"],
                })   
        assert_frame_equal(exp_results, json_reader.get_data())

    def test_read_excel(self):
        excel_reader = ExcelReader(r'app/files','demo_xlsx.xlsx')
        exp_results  = pd.DataFrame({
                "a": [1, 2, 3],
                "b": [4, 5, 6],
                "c": ["cat", "dog", "apple"],
                })            
        assert_frame_equal(exp_results, excel_reader.get_data())
        
if __name__ == '__main__':
    unittest.main()