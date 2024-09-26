
#!/usr/bin/env python
# functions.py

from google.cloud import bigquery
import re
from tabulate import tabulate
import warnings

# Establish BigQuery connection using service account or default credentials
def connect_bigquery():
    print("Connecting to BigQuery...\n")
    warnings.filterwarnings("ignore", category=UserWarning)  # Suppress UserWarning
    client = bigquery.Client()
    return client

# Fetch QA tests from the BigQuery table, ordered by code
def fetch_qa_tests(client, project_id, dataset_name):
    print("Fetching QA tests from BigQuery table...\n")
    query = f"""
    SELECT code, description, enabled, parameter, test_sql, exp_result
    FROM `{project_id}.{dataset_name}.qa_tests`
    WHERE enabled = 'Y'
    ORDER BY code
    """
    query_job = client.query(query)
    return query_job.result()

# Replace parameters with runtime values (avoid replacing column names containing 'date')
def replace_parameters(test_sql, parameters, runtime_values, target_project_id, target_dataset_name):
    print(f"Original SQL: {test_sql}\n")

    # Substitute target project ID and dataset name in the test SQL
    test_sql = test_sql.replace('projectid', target_project_id)
    test_sql = test_sql.replace('datasetname', target_dataset_name)

    param_list = parameters.split(',')

    if 'env' in test_sql:
        test_sql = test_sql.replace('env', runtime_values[0])
        print(f"Replacing 'env' with value '{runtime_values[0]}'")

    for param, value in zip(param_list, runtime_values):
        if 'date' in param.lower():
            value = f"'{value.strip()}'"
        print(f"Replacing parameter '{param}' with value '{value}'")
        param_pattern = r"(?<![a-zA-Z_])" + re.escape(param.strip()) + r"(?![a-zA-Z_])"
        test_sql = re.sub(param_pattern, value, test_sql)

    print(f"Modified SQL: {test_sql}\n")
    return test_sql

# Execute the SQL and get the result from BigQuery
def run_sql(client, sql):
    print(f"Executing SQL: {sql}\n")
    query_job = client.query(sql)
    result = query_job.result()

    for row in result:
        print(f"Query Result: {row[0]}\n")
        return row[0]

# Insert results into the audit table
def insert_audit_log(client, test_code, executed_sql, expected_result, actual_result, test_sql, project_id, dataset_name):
    print(f"Inserting audit log for test '{test_code}'...\n")
    audit_table = f'{project_id}.{dataset_name}.qa_audit'
    query = f"""
    INSERT INTO {audit_table} (test_code, executed_sql, expected_result, actual_result, test_sql)
    VALUES (@test_code, @executed_sql, @expected_result, @actual_result, @test_sql)
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("test_code", "STRING", test_code),
            bigquery.ScalarQueryParameter("executed_sql", "STRING", executed_sql),
            bigquery.ScalarQueryParameter("expected_result", "STRING", expected_result),
            bigquery.ScalarQueryParameter("actual_result", "STRING", actual_result),
            bigquery.ScalarQueryParameter("test_sql", "STRING", test_sql),
        ]
    )

    client.query(query, job_config=job_config).result()
    print("Audit log inserted successfully.\n")

# Format executed SQL for fixed width and line breaks
def format_executed_sql(sql, max_length=150):
    words = sql.split()
    formatted_sql = ""
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + 1 <= max_length:
            current_line += " " + word if current_line else word
        else:
            formatted_sql += current_line + "\n"
            current_line = word

    formatted_sql += current_line
    return formatted_sql.strip()

# Display results in a tabular format using tabulate
def display_results(results):
    headers = ['Code', 'Executed SQL', 'Result']
    table = [(result[0], format_executed_sql(result[1]), result[2]) for result in results]
    print(tabulate(table, headers, tablefmt="grid", stralign="left", numalign="center"))
