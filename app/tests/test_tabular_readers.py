import unittest
from app.profiler.tabular_readers import SQLTableReader, CSVReader


class DataFileReadInTest(unittest.TestCase):
    # def test_mysql(self):
    #     db_creds = {'user':'root','password':'henryI&D123','server':'localhost','port':3306,'dbname':'demo_db'}
    #     table_name = 'DPR_Mortgage_Data'
    #     mysql_reader = SQLTableReader('mysql', db_creds, table_name=table_name)
    #     self.assertIsInstance(mysql_reader, SQLTableReader)
        #print(mysql_reader.get_data())

    def test_read_csv(self):
        csv_reader = CSVReader(r'app/files','TrackMyTrace_inputFile.csv')
        self.assertIsInstance(csv_reader, CSVReader)
        #print(csv_reader.get_data())
        
if __name__ == '__main__':
    unittest.main()