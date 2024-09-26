## main.py
The main.py script acts as the entry point for running the QA tests. Its key responsibilities include:

## Prompting for User Input: When you run the script, it prompts you to enter values for:
The Google Cloud project ID
The BigQuery dataset name
The target project ID
The target dataset name
## BigQuery Connection:
It connects to BigQuery using the default credentials on the environment.
## Fetching and Executing Tests:
The script fetches all enabled QA tests from a specific table in BigQuery. It reads the test_sql field from the table and dynamically replaces placeholders (such as env and date) based on values from the parameter field in the table.
## Result Verification:
After executing the SQL queries, the actual result is compared with the expected result (exp_result field), and any discrepancies are logged.
Logging in Audit Table: It records all test executions in an audit log table, including the test code, executed SQL query, expected result, and actual result.

## functions.py
This file contains the core functions that support main.py. The key functionality is as follows:

## connect_bigquery():
Establishes a connection to BigQuery using the default credentials.

## fetch_qa_tests(client, project_id, dataset_name):
Fetches the enabled QA tests from the qa_tests table within the specified BigQuery project and dataset.

## replace_parameters(test_sql, parameters, target_project_id, target_dataset_name):
This function dynamically replaces placeholders in the SQL query (test_sql).

## The parameter column contains comma-separated values where:
The first value (env_value) is used to replace the env placeholder in the SQL query.
The second value (date_value) is used to replace the date placeholder.
If date_value is missing, it substitutes an empty string to avoid errors.
It also replaces placeholders for the targetProjectId and targetDatasetName with the provided values.
## run_sql(client, sql):
Executes the SQL query in BigQuery and returns the result. It assumes the SQL query performs an operation like a COUNT() to return a single value.

## insert_audit_log(client, test_code, executed_sql, expected_result, actual_result, test_sql, project_id, dataset_name):
Logs the details of the executed test, including the test code, the SQL that was run, expected result, and actual result, into an audit table for review.

## format_executed_sql(sql, max_length):
Formats the executed SQL query for easier readability, wrapping long lines for better display in reports.

## display_results(results):
Outputs the test results in a tabular format using the tabulate library for a clear and structured view.

## Summary of How the Scripts Work Together:
main.py prompts for input, fetches the QA tests, and manages the workflow.
functions.py contains reusable functions that handle database connections, query execution, and logging.
The parameters in the SQL queries are replaced dynamically from values provided in the parameter column in the BigQuery table, and the results of the tests are logged in an audit table for review.

## Execution Details
(venv) % python main1.py
Please enter the environment (e.g., 'stg'): stg. This could be any values within the target dataset name provided that table should present in that region
Please enter the date (YYYY-MM-DD): 2024-09-24
Please enter the Google Cloud project ID: GCP ProjectID which should have access to insert records as part of audit log. This is project where qa_tests table created
Please enter the BigQuery dataset name: Dataset name which has the qa_tests table
Please enter the target project ID: TargetProject Name against the test scripts to be executed
Please enter the target dataset name: TargetDateset Name against the test scripts to be executed, which has the tables mentioned in the ft scripts

+----------+-----------------------------------------------------------------------------------------------------------------------------------------------------+----------+
| Code     | Executed SQL                                                                                                                                        |  Result  |
+==========+=====================================================================================================================================================+==========+
| qa_ch_01 | SELECT count(*) FROM (SELECT channel_code,count(*) FROM `gcp-project-id.datasetname.channel_table_dev` GROUP BY channel_code HAVING count(*) > 1) |    1     |
+----------+-----------------------------------------------------------------------------------------------------------------------------------------------------+----------+
| qa_ch_02 | select count(*) from `gcp-project-id.datasetname.channel_transaction_dev` A left join `gcp-project-id.datasetname.channel_table_dev` B on       |    1     |
|          | (A.channel_code = B.channel_code) where B.channel_code is null and A.transaction_date = '2024-09-26'                                                |          |
+----------+-----------------------------------------------------------------------------------------------------------------------------------------------------+----------+


(venv) % python main2.py
Please enter the Google Cloud project ID: gcp-project-id
Please enter the BigQuery dataset name: datasetname
Please enter the target project ID: gcp-project-id
Please enter the target dataset name: datasetname


+----------+------------------------------------------------------------------------------------------------------------------------------------------------------+----------+
| Code     | Executed SQL                                                                                                                                         |  Result  |
+==========+======================================================================================================================================================+==========+
| qa_ch_01 | SELECT count(*) FROM (SELECT channel_code,count(*) FROM `gcp-project-id.datasetname.channel_table_dev` GROUP BY channel_code HAVING count(*) > 1)  |    1     |
+----------+------------------------------------------------------------------------------------------------------------------------------------------------------+----------+
| qa_ch_02 | select count(*) from `gcp-project-id.datasetname.channel_transaction_dev` A left join `gcp-project-id.datasetname.channel_table_dev` B on        |    1     |
|          | (A.channel_code = B.channel_code) where B.channel_code is null and A.transaction_date = '2024-09-26'                                                 |          |
+----------+------------------------------------------------------------------------------------------------------------------------------------------------------+----------+
| qa_ch_04 | SELECT count(*) FROM (SELECT channel_code,count(*) FROM `gcp-project-id.datasetname.channel_table_prod` GROUP BY channel_code HAVING count(*) > 1) |    0     |
+----------+------------------------------------------------------------------------------------------------------------------------------------------------------+----------+
| qa_ch_05 | select count(*) from `gcp-project-id.datasetname.channel_transaction_prod` A left join `gcp-project-id.datasetname.channel_table_prod` B on      |    0     |
|          | (A.channel_code = B.channel_code) where B.channel_code is null and A.transaction_date = '2024-09-28'                                                 |          |
+----------+------------------------------------------------------------------------------------------------------------------------------------------------------+----------+