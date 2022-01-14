# Data Management Tool
This package implements a tool allowing users to examine and monitor the structure, content and relationships present in their data. As well as focusing on traditional metrics such as counts of values, distinct values, means, medians etc, this tool also provides the flexibility to add bespoke more advanced metrics.

The tool is presented as a Flask application. Screenshots below:

## Example Metrics
### Headline Metrics
Customise which metrics are most important to you and have them appear at the top of the dashboard

### Column View
Clickable graphs which show and display as graphs basic statistics and distributions of each column

### Anomaly Detection
2 methods for identifying anomalous values in structurally-valid data, one based on Gaussian features, the other using a regression model to pick out anomalies given a set of features.

### Extracting Data Rules
Automatic extraction of patterns that the existing data conforms to (eh uniqueness, data ranges, transformations between columns)

### ML Insights
Association rule mining to pick out relationships between columns (eg 'Rows with X in Column 1 are 90% likely to have Y in Column 2')

### Standard Data Format Cleaning
Use of Regexes to clean Postcodes, phone numbers, NI numbers, email addresses etc


## Running the code
Clone, pip install requirements.txt, combine with data source and run. Can either run the flask app (`python runserver.py`), run the debug.py script, or run the tests with `./run_tests.sh`.

## Code Structure Overview
The main backend code is in the 'profiler' folder:
 ### dashboards.py
 Dashboard classes. Dashboards are made up of customisable collections of Metrics

 ### metrics.py
 Metrics - each can be defined as required. Code to calculate given metrics can be supplied for a range of data sources (eg code for in memory calculation, code for calculation of metric in SQL database etc)

 ### sql_connectors.py
 Various classes for connecting to different SQL dialects (MySQL, Postgres etc)

 ### tabular_readers.py
 Classes for reading different forms of tabular data into memory (CSV, Json, SQL result that fits in memory etc)