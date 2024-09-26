#!/usr/bin/env python
from google.cloud import bigquery
import re
from tabulate import tabulate
import warnings

# Establish BigQuery connection using service account or default credentials
def connect_bigquery():
    print("Connecting to BigQuery...\n")
    warnings.filterwarnings("ignore", category=UserWarning)
    client = bigquery.Client()
    return client

# Fetch QA tests from the BigQuery table, ordered by code
def fetch_qa_tests(client, project_id, dataset_name):
    print("Fetching QA tests from BigQuery table...\n")
    query = f"""
    SELECT code, description, enabled, parameter, test_sql, exp_result
    FROM `{project_id}.{dataset_name}.qa_tests2`
    WHERE enabled = 'Y'
    ORDER BY code
    """
    query_job = client.query(query)
    return query_job.result()

# Replace parameters with runtime values (env and date) from the parameter column
def replace_parameters(test_sql, parameters, target_project_id, target_dataset_name):
    print(f"Original SQL: {test_sql}\n")

    # Check if parameters contain valid comma-separated values
    if parameters:
        param_list = parameters.split(',')
        print(f"Parameter list: {param_list}")  # Print the parsed parameter list for debugging

        # Extract env and date values from the parameters (if they exist)
        env_value = param_list[0].strip() if len(param_list) > 0 else None
        date_value = param_list[1].strip() if len(param_list) > 1 else None
    else:
        # Handle cases where parameters might be null or empty
        env_value = None
        date_value = None

    # Print env_value and date_value for debugging
    print(f"env_value: {env_value}")
    print(f"date_value: {date_value}")

    # Replace 'env' and 'date' placeholders in the SQL
    if env_value:
        print(f"Replacing 'env' with value '{env_value}'")
        test_sql = test_sql.replace('env', env_value)

    if date_value:
        print(f"Replacing 'date' with value '{date_value}'")
        test_sql = test_sql.replace(' = date', f" = '{date_value}'")  # Ensure date is enclosed in quotes
    else:
        print(f"No 'date' provided, skipping date replacement.")
        test_sql = test_sql.replace(' = date', "''")  # Replace with an empty string if date is not provided

    # Replace project and dataset placeholders
    test_sql = test_sql.replace('projectid', target_project_id)
    test_sql = test_sql.replace('datasetname', target_dataset_name)

    print(f"Modified SQL: {test_sql}\n")
    return test_sql

# Execute the SQL and get the result from BigQuery
def run_sql(client, sql):
    print(f"Executing SQL: {sql}\n")

    query_job = client.query(sql)
    result = query_job.result()

    # Print result for debugging
    for row in result:
        print(f"Query Result: {row[0]}\n")
        return row[0]  # Assuming the result is a single value (like a count)

# Insert results into the audit table
def insert_audit_log(client, test_code, executed_sql, expected_result, actual_result, test_sql, project_id, dataset_name):
    print(f"Inserting audit log for test '{test_code}'...\n")
    audit_table = f'{project_id}.{dataset_name}.qa_audit'  # Adjust table name as needed
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

    formatted_sql += current_line  # Add the last line
    return formatted_sql.strip()

# Display results in a tabular format using tabulate
def display_results(results):
    headers = ['Code', 'Executed SQL', 'Result']
    # Prepare the table with formatted SQL
    table = [(result[0], format_executed_sql(result[1]), result[2]) for result in results]

    # Aligning the columns with 'Executed SQL' left aligned
    print(tabulate(table, headers, tablefmt="grid", stralign="left", numalign="center"))

