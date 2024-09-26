# QA Tests Runner

This project consists of a Big Query PL/SQL that executes in Google BigQuery UI, fetches QA tests, runs them, and logs the results.

Before running the scripts, ensure you created the qa_tests table

## Prerequisites
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

## Creating sample table with data (Dev to fail test case and prod to pass as it have correct data)
drop TABLE if exists
  `GCPProjectId.GCPDatasetName.channel_table_dev`;
CREATE TABLE
  `GCPProjectId.GCPDatasetName.channel_table_dev` ( code STRING,
    channel_code STRING);

INSERT INTO
  `GCPProjectId.GCPDatasetName.channel_table_dev` (channel_code)
VALUES
  ('CH_01'),
  ('CH_01'),
  ('CH_02'),
  ('CH_03');

drop TABLE if exists
  `GCPProjectId.GCPDatasetName.channel_table_prod`;
CREATE TABLE
  `GCPProjectId.GCPDatasetName.channel_table_prod` ( code STRING,
    channel_code STRING);

INSERT INTO
  `GCPProjectId.GCPDatasetName.channel_table_prod` (channel_code)
VALUES
  ('CH_01'),
  ('CH_02'),
  ('CH_03'),
  ('CH_04');

drop TABLE if exists
  `GCPProjectId.GCPDatasetName.channel_transaction_dev`;
CREATE TABLE
  `GCPProjectId.GCPDatasetName.channel_transaction_dev` (
    channel_code STRING,
    transaction_date DATE,
    transaction_amount NUMERIC
    );

INSERT INTO
  `GCPProjectId.GCPDatasetName.channel_transaction_dev` (channel_code,transaction_date,transaction_amount)
VALUES
  ('CH_01', CURRENT_DATE() -4, 100),
  ('CH_02', CURRENT_DATE() -3, 200),
  ('CH_03', CURRENT_DATE() -2, 300),
  ('CH_04', CURRENT_DATE() , 400);


drop TABLE if exists
  `GCPProjectId.GCPDatasetName.channel_transaction_prod`;
CREATE TABLE
  `GCPProjectId.GCPDatasetName.channel_transaction_prod` (
    channel_code STRING,
    transaction_date DATE,
    transaction_amount NUMERIC);

INSERT INTO
  `GCPProjectId.GCPDatasetName.channel_transaction_prod` (channel_code,transaction_date,transaction_amount)
VALUES
  ('CH_01', CURRENT_DATE() -4, 100),
  ('CH_02', CURRENT_DATE() -3, 200),
  ('CH_03', CURRENT_DATE() -2, 300),
  ('CH_04', CURRENT_DATE() , 400);

