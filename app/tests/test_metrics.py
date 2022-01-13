import unittest
from app.profiler.tabular_readers import SQLTableReader, CSVReader
from app.profiler.data_sources import InMemoryDataSource, SQLDataSource
from app.profiler.metrics import BasicProfile, TotalBlankCells, TotalRowsCols, DuplicateRows, DetectBadAddress, ExtractBadPostcode, GroupedZScore, SupervisedAnomalyDetection, ClassifyClientNotes
from app.profiler.sql_connectors import SQLViewConnector
from typing import Tuple
import pandas as pd
import numpy as np

class CSVMetricTestsBCM(unittest.TestCase):
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
    
