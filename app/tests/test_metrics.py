import unittest
from app.profiler.tabular_readers import SQLTableReader, CSVReader
from app.profiler.data_sources import InMemoryDataSource, SQLDataSource
from app.profiler.metrics import BasicProfile, TotalBlankCells, TotalRowsCols, DuplicateRows, DetectBadAddress, ExtractBadPostcode, GroupedZScore, SupervisedAnomalyDetection, ClassifyClientNotes
from app.profiler.sql_connectors import SQLViewConnector
from typing import Tuple
import pandas as pd
import numpy as np
from pandas.testing import assert_frame_equal

class StaticMetricTestsInMem(unittest.TestCase):
    ''' Test metrics on all in-memory readers with dummy data '''
    ''' Static methods used so class can be used to just give you the answer if needed '''
    def test_static_basic_profile(self):
        df = pd.DataFrame({
                "symbol": ["A", "B", "C", "A", "B", "C"],
                "price": [12, 24, 48, 14, 13, 20],
            })
        ans = BasicProfile.calculate_in_mem(df, False)
        exp_results = pd.DataFrame({
                "01. Column Name": ["symbol", "price"],
                "02. Data Type" : ["object", "int64"],
                "03. Row Count" : [6,6],
                "04. Nulls" : [0,0],
                "05. Non-Nulls" : [6,6],
                "06. No. Unique Values" : [3,6],
                "07. Average Value" : [None,21.833333],
                "08. Standard Deviation" : [None,13.629625],
                "09. Minimum" : [None,12.0],
                "10. Maximum" : [None,48.0],
                "11. 25%" : [None,13.25],
                "12. 50%" : [None,17.0],
                "13. 75%" : [None,23.0],
                "count" : [None,6.0],
            })
        assert_frame_equal(ans,exp_results)

    def test_static_blanks(self):
        df = pd.DataFrame({
                "symbol": ["A", "B", "C", "A", "B", "C"],
                "price": [12, 24, 48, 14, 13, 20],
            })
        ans = TotalBlankCells.calculate_in_mem(df, pc=False)
        self.assertEqual(ans,0)
        df = pd.DataFrame({
                "symbol": ["A", "B", "C", None, "B", None],
                "price": [12, 24, 48, 14, None, 20],
            })
        ans = TotalBlankCells.calculate_in_mem(df, pc=False)
        self.assertEqual(ans,3)
        # test as a percentage
        df = pd.DataFrame({
                "symbol": ["A", "B", "C", "A", "B", "C"],
                "price": [12, 24, 48, 14, 13, 20],
            })
        ans = TotalBlankCells.calculate_in_mem(df, pc=True)
        self.assertEqual(ans,0)
        df = pd.DataFrame({
                "symbol": ["A", "B", "C", None, "B", None],
                "price": [12, 24, 48, 14, None, 20],
            })
        ans = TotalBlankCells.calculate_in_mem(df, pc=True)
        self.assertEqual(ans,0.25)

    def test_static_tot_row_col(self):
        df = pd.DataFrame({
                "symbol": ["A", "B", "C", "A", "B", "C"],
                "price": [12, 24, 48, 14, 13, 20],
            })
        ans = TotalRowsCols.calculate_in_mem(df)
        self.assertEqual(ans,(6,2))

    def test_static_dupe_row(self):
        df = pd.DataFrame({
                "symbol": ["A", "B", "C", "A", "B", "C"],
                "price": [12, 24, 48, 12, 13, 20],
            })
        ans = DuplicateRows.calculate_in_mem(df)
        self.assertEqual(ans,1)  

    def test_static_bad_address(self):
        
        df = pd.DataFrame({
                "user_id": [1, 2, 3],
                "address": ['4 Mill Lane, London', '56 Cowper Street, Edinburgh', 'No address found for this customer'],
            })
        ans = DetectBadAddress.calculate_in_mem(df, **{'id_col':'user_id','address_col':['address']})
        ans = ans.loc[ans["Validity Score"] < 0.5].values
        ans = ans.tolist()[0][:2]
        self.assertEqual(ans,[3, 'No address found for this customer'])

    def test_static_bad_postcode(self):
        
        df = pd.DataFrame({
                "user_id": [1, 2, 3, 4, 5],
                "postcd": ['DDDDDD', 'SE210AA', 'RG44RF', '453', '@2BG'],
            })
        ans = ExtractBadPostcode.calculate_in_mem(df, **{'id_col':'user_id','postcd_col':'postcd'})
        ans = ans.values.tolist()
        self.assertEqual(ans,[[1, 'DDDDDD'],[4,'453'],[5,'@2BG']]) 
    



class CSVMetricTestsBCM(unittest.TestCase):
    ''' run basic tests for mortgage data with in-memory calcs '''
    @classmethod
    def setUpClass(cls):
        csv_reader = CSVReader(r'app/files','mortgage_data_v4.csv')
        cls.data_source = InMemoryDataSource(csv_reader)        

    def test_basic_profile_csv(self):
        csv_basic_profile = BasicProfile(self.data_source)
        x = csv_basic_profile()
        self.assertIsInstance(csv_basic_profile(), pd.DataFrame)

    def test_basic_profile_column_views_csv(self):
        csv_basic_profile = BasicProfile(self.data_source)
        csv_basic_profile()
#        print(csv_basic_profile.get_result_for_column('card_type'))
        self.assertIsInstance(csv_basic_profile.get_result_for_column('card_type'), str)

    def test_basic_profile_tabular_views_csv(self):
        csv_basic_profile = BasicProfile(self.data_source)
        csv_basic_profile()
        self.assertIsInstance(csv_basic_profile.get_tabular_view(), pd.DataFrame)


    def test_blanks_csv(self):
        csv_blanks = TotalBlankCells(self.data_source,{'pc':True})
        self.assertIsInstance(csv_blanks(), str)
        self.assertIsInstance(csv_blanks(pc=False), np.int64)

    def test_tot_rows_cols_csv(self):
        csv_tot_rows_cols = TotalRowsCols(self.data_source)
        #print(csv_tot_rows_cols())
        self.assertIsInstance(csv_tot_rows_cols(), tuple)

    def test_dup_rows_csv(self):
        csv_dup_rows = DuplicateRows(self.data_source)
        #print(csv_dup_rows())
        self.assertIsInstance(csv_dup_rows(), np.int64)

    def test_addr_classify(self):
        csv_addr = DetectBadAddress(self.data_source, {'id_col':'user_id','address_col':['address','city']})
        #print(csv_addr())
        self.assertIsInstance(csv_addr(), pd.DataFrame)

    def test_notes_classify(self):
        csv_addr = ClassifyClientNotes(self.data_source, {'id_col':'user_id','notes_col':'client_notes'})
        print(csv_addr())
        self.assertIsInstance(csv_addr(), pd.DataFrame)


    def test_postcd_classify_in_mem(self):
        csv_postcd = ExtractBadPostcode(self.data_source,{'id_col':'user_id','postcd_col':'PostCode'})
        #print(csv_postcd())
        self.assertIsInstance(csv_postcd(), pd.DataFrame)

    def test_grouped_z_in_mem(self):
        csv_groupz = GroupedZScore(self.data_source,{'id_col':'user_id','group_key':'card_type','group_value':'credit_rate'})
        #print(csv_groupz())
        self.assertIsInstance(csv_groupz(), pd.DataFrame)

class CSVMetricTestsIns(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        csv_reader = CSVReader(r'app/files','insurance_data.csv')
        cls.data_source = InMemoryDataSource(csv_reader)        

    def test_spv_anom_detect_in_mem(self):
        csv_anom_ins = SupervisedAnomalyDetection(self.data_source,{'id_col':'user_id','x_cols':['Age_days','Annual_Mileage','Vehicle_Value','Previous_Claims'],'y_col':'Premium'})
        csv_anom_ins()
        self.assertIsInstance(csv_anom_ins.get_result(), pd.DataFrame) 
        

# class MySQLInMemMetricTests(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):
#         db_creds = {'user':'root','password':'henryI&D123','server':'localhost','port':3306,'dbname':'demo_db'}
#         table_name = 'dpr_mortgage_data'
#         mysql_reader = SQLTableReader('mysql', db_creds, table_name=table_name)
#         cls.data_source = InMemoryDataSource(mysql_reader)

#     def test_basic_profile_mysql(self):
#         mysql_basic_profile = BasicProfile(self.data_source)
#         #print(mysql_basic_profile())
#         self.assertIsInstance(mysql_basic_profile(), pd.DataFrame)

#     def test_blanks_mysql(self):
#         mysql_blanks = TotalBlankCells(self.data_source, {'pc':True})
#         self.assertIsInstance(mysql_blanks(), float)
        
#     def test_tot_rows_cols_csv(self):
#         mysql_tot_rows_cols = TotalRowsCols(self.data_source)
#         #print(mysql_tot_rows_cols())
#         self.assertIsInstance(mysql_tot_rows_cols(), tuple)

#     def test_dup_rows_csv(self):
#         mysql_dup_rows = DuplicateRows(self.data_source)
#         #print(mysql_dup_rows())
#         self.assertIsInstance(mysql_dup_rows(), np.int64)

#     # TODO test custom sql

# class MySQLMetricTests(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):
#         db_creds = {'user':'root','password':'henryI&D123','server':'localhost','port':3306,'dbname':'demo_db'}
#         table_name = 'DPR_Mortgage_Data'
#         mysql_reader = SQLViewConnector('mysql', db_creds, table_name=table_name)
#         cls.data_source = SQLDataSource(mysql_reader)

#     def test_basic_profile_mysql(self):
#         mysql_basic_profile = BasicProfile(self.data_source)
#         self.assertIsInstance(mysql_basic_profile(), pd.DataFrame)

#     def test_tot_blank_cells_mysql(self):
#         mysql_blank_cells = TotalBlankCells(self.data_source)
#         #print(mysql_blank_cells())
#         self.assertIsInstance(mysql_blank_cells(), pd.DataFrame)

#     def test_tot_rows_cols_mysql(self):
#         mysql_tot_rows = TotalRowsCols(self.data_source)
#         #print(mysql_tot_rows())
#         self.assertIsInstance(mysql_tot_rows(), tuple)

#     def test_dup_rows_mysql(self):
#         mysql_dup_rows = DuplicateRows(self.data_source)
#         #print(mysql_dup_rows())
#         self.assertIsInstance(mysql_dup_rows(), np.int64)

if __name__ == '__main__':
    unittest.main()
    
