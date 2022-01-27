# Data Management Tool
This package implements a tool allowing users to examine and monitor the structure, content and relationships present in their data. As well as focusing on traditional metrics such as counts of values, distinct values, means, medians etc, this tool also provides the flexibility to add bespoke more advanced metrics.

The tool is presented as a Flask application. Screenshots below:

## Example Metrics
### Headline Metrics
Customise which metrics are most important to you and have them appear at the top of the dashboard
![headline_metrics](https://user-images.githubusercontent.com/97685851/149484416-5fb3bbb0-08af-465e-a294-d4cd6f0b97d1.PNG)

### Column View
Clickable graphs which show and display as graphs basic statistics and distributions of each column
![col_views](https://user-images.githubusercontent.com/97685851/149484393-5228f115-026a-48ca-a6e7-aa3b6a87ac18.PNG)
![col_views2](https://user-images.githubusercontent.com/97685851/149484396-e27f4b0c-485a-4bbd-a92d-26c8f23584dd.PNG)
![col_views3](https://user-images.githubusercontent.com/97685851/149484400-d2b3c9cb-9bb4-48b4-996f-3a2a854cbfd2.PNG)
![col_views4](https://user-images.githubusercontent.com/97685851/149484405-0afbffdb-e317-4ded-8625-7e770f109733.PNG)


### Anomaly Detection
2 methods for identifying anomalous values in structurally-valid data, one based on Gaussian features, the other using a regression model to pick out anomalies given a set of features.

![anom_dt](https://user-images.githubusercontent.com/97685851/149484382-36bf746d-4044-4e25-a3c8-9cbcff82239b.PNG)

### Extracting Data Rules
Automatic extraction of patterns that the existing data conforms to (eg uniqueness, data ranges, transformations between columns)
![data_rules](https://user-images.githubusercontent.com/97685851/149484410-07797726-46f7-4278-8b48-8d93f3ae34fe.PNG)

### ML Insights
Association rule mining to pick out relationships between columns (eg 'Rows with X in Column 1 are 90% likely to have Y in Column 2')
![ml_insights](https://user-images.githubusercontent.com/97685851/149484419-f8f67be9-956e-49a0-a1da-d62464f85b15.PNG)


### Standard Data Format Cleaning
Use of Regexes to clean Postcodes, phone numbers, NI numbers, email addresses etc

![postcode](https://user-images.githubusercontent.com/97685851/149484426-986984fe-2334-4922-a87d-0eef255b4e8f.PNG)


## Running the code
Clone, pip install requirements.txt, place data into app/files and run. Can either run the flask app (`python runserver.py`), run the `debug.py` script, or run the tests with `./run_tests.sh`.

## Code Structure Overview
The main backend code is in the 'profiler' folder:
 ### dashboards.py
 Dashboard classes. Dashboards are made up of customisable collections of Metrics

 ### data_sources.py
 data sources. In Memory or SQL.

 #### In memory data sources
 Defined with any form of tabular data reader.
 Attribute self.data holds data in memory. A given metric is run by passing this data to the metric function code.

 ### metrics.py
 Metrics - each can be defined as required. Code to calculate given metrics can be supplied for a range of data sources (eg code for in memory calculation, code for calculation of metric in SQL database etc)

 Metrics are designed to be defined on a data source (which itself is defined as either in mem or as SQL). So for example you can define a metric like bcm_inmem_data_basic_profile up front, then calculate it only when you need to. Underlying data source is therefore abstracted from both how it is calculated and functional calculation code. eg you could have an row count metric where processing is done in memory and change the underlying data between csv, json etc 

 first argument of a metric is always the data source. Second is any kw args needed for the underlying function code

 Example of custom metrics - import your own trained bad address model

 Metric passes function to data source. Data source, responsible for running hte function on the data, runs the function on its data (in mem) or runs the function on the SQL connector.

 SQL connectors have a method called run query. The config for this is handled by the SQLViewConnector object. The SQL data source object just has to call 

 calculate sql_tbl actually calls run_query 

 NB Dashboards don't depend on data sources - so can have one dashboard conatining metrics from multiple data sources

 The Backend lives in the profiler section

 For both in mem and sql metrics can calculate by m().  

 ### sql_connectors.py
 Various classes for connecting to different SQL dialects (MySQL, Postgres etc)

 ### tabular_readers.py
 Classes for reading different forms of tabular data into memory (CSV, Json, SQL result that fits in memory etc)
