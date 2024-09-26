# QA Tests Runner

This project consists of a Python script that connects to Google BigQuery, fetches QA tests, runs them, and logs the results.

Before running the scripts, ensure you have the following:

## Prerequisites

- **Python**: Ensure Python 3.6 or higher is installed. You can download it from [python.org](https://www.python.org/downloads/).

- **Google Cloud SDK**: Install the Google Cloud SDK for access to the BigQuery API. Follow the instructions on the [Google Cloud SDK documentation](https://cloud.google.com/sdk/docs/install).

- **Google Cloud Project**: You need a Google Cloud project with BigQuery enabled. Make sure you have the necessary permissions to run queries and access datasets.

You can also create a virtual environment (recommended) and activate it:

```bash
# Create a virtual environment (optional)
python -m venv venv

# Activate the virtual environment (Windows)
venv\Scripts\activate

# Activate the virtual environment (macOS/Linux)
source venv/bin/activate

## Required Packages
google-cloud-bigquery
tabulate

You can install the above two packages individually by pip install package_ name or put the above two packages inside requirements.txt file and install both packages by using the command pip install -r requirements.txt

Install the required Python packages using `pip`.

## Big Query Tables Creation

 Create the qa_tests table and insert the test cases.  Replace the projectId your GCP ProjectId and datasetName with your datasetName. Note, you should have access to create table in that dataset.


DROP TABLE IF EXISTS
  `GCPProjectId.GCPDatasetName.qa_tests`;
CREATE TABLE
  `GCPProjectId.GCPDatasetName.qa_tests` ( code STRING,
    description STRING,
    enabled STRING,
    parameter STRING,
    test_sql STRING,
    exp_result STRING );

INSERT INTO
  `GCPProjectId.GCPDatasetName.qa_tests` (code,
    description,
    enabled,
    parameter,
    test_sql,
    exp_result)
VALUES
  ('qa_ch_01', 'Runs the SQL against the Channel table to count', 'Y', 'env', 'SELECT count(*) FROM (SELECT channel_code,count(*) FROM `projectid.datasetname.channel_table_env` GROUP BY channel_code HAVING count(*) > 1)', '0'),
  ('qa_ch_02', 'Check the FK between channel_code and channel_transaction to identify orphans', 'Y', 'env, date', 'select count(*) from `projectid.datasetname.channel_transaction_env` A left join `projectid.datasetname.channel_table_env` B on (A.channel_code = B.channel_code) where B.channel_code is null and A.transaction_date = date', '0'),
  ('qa_ch_03', 'Counts the records in channel_transaction where amount is null', 'N', 'env,date', 'select count(*) from `projectid.datasetname.channel_transaction_env` where transaction_date = date and transaction_amount is null', '0');

 DROP TABLE IF EXISTS
  `GCPProjectId.GCPDatasetName.qa_tests2`;
CREATE TABLE
  `GCPProjectId.GCPDatasetName.qa_tests2` ( code STRING,
    description STRING,
    enabled STRING,
    parameter STRING,
    test_sql STRING,
    exp_result STRING );

INSERT INTO
  `GCPProjectId.GCPDatasetName.qa_tests2` (code,
    description,
    enabled,
    parameter,
    test_sql,
    exp_result)
VALUES
  ('qa_ch_01', 'Runs the SQL against the Channel table to count', 'Y', 'dev', 'SELECT count(*) FROM (SELECT channel_code,count(*) FROM `projectid.datasetname.channel_table_env` GROUP BY channel_code HAVING count(*) > 1)', '0'),
  ('qa_ch_02', 'Check the FK between channel_code and channel_transaction to identify orphans', 'Y', 'dev,2024-09-26', 'select count(*) from `projectid.datasetname.channel_transaction_env` A left join `projectid.datasetname.channel_table_env` B on (A.channel_code = B.channel_code) where B.channel_code is null and A.transaction_date = date', '0'),
  ('qa_ch_03', 'Counts the records in channel_transaction table at a given date that have amount null', 'N', 'dev,2024-09-28', 'select count(*) from `projectid.datasetname.channel_transaction_env` where transaction_date = date and transaction_amount is null', '0'),
  ('qa_ch_04', 'Runs the SQL against the Channel table to count', 'Y', 'prod', 'SELECT count(*) FROM (SELECT channel_code,count(*) FROM `projectid.datasetname.channel_table_env` GROUP BY channel_code HAVING count(*) > 1)', '0'),
  ('qa_ch_05', 'Check the FK between channel_code and channel_transaction to identify orphans', 'Y', 'prod,2024-09-28', 'select count(*) from `projectid.datasetname.channel_transaction_env` A left join `projectid.datasetname.channel_table_env` B on (A.channel_code = B.channel_code) where B.channel_code is null and A.transaction_date = date', '0'),
  ('qa_ch_06', 'Counts the records in channel_transaction table at a given date that have amount null', 'N', 'prod,2024-09-28', 'select count(*) from `projectid.datasetname.channel_transaction_env` where transaction_date = date and transaction_amount is null', '0');

Create the empty qa_audit table.This will store the run execution details. Replace the projectId your GCP ProjectId and datasetName with your datasetName. Note, you should have access to create table in that dataset.

DROP TABLE IF EXISTS
  `projectId.datasetName.qa_audit`;
CREATE TABLE
  `projectId.datasetName.qa_audit` ( test_code STRING,
    test_sql STRING,
    executed_sql STRING,
    expected_result STRING,
    actual_result STRING );

##Running the python script
