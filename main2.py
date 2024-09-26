#!/usr/bin/env python
from functions2 import connect_bigquery, fetch_qa_tests, replace_parameters, run_sql, insert_audit_log, display_results

# Main execution function
def run_qa_checks(project_id, dataset_name, target_project_id, target_dataset_name):
    client = connect_bigquery()
    qa_tests = fetch_qa_tests(client, project_id, dataset_name)

    results = []
    for test in qa_tests:
        code = test['code']
        description = test['description']
        parameters = test['parameter']
        test_sql = test['test_sql']
        exp_result = test['exp_result']

        print(f"Processing test '{code}': {description}\n")
        executed_sql = replace_parameters(test_sql, parameters, target_project_id, target_dataset_name)
        result = run_sql(client, executed_sql)

        # Insert the audit log
        insert_audit_log(client, code, executed_sql, exp_result, result, test_sql, project_id, dataset_name)

        results.append((code, executed_sql, result))

    display_results(results)

# Prompt user for runtime values
if __name__ == "__main__":
    project_id = input("Please enter the Google Cloud project ID: ")
    dataset_name = input("Please enter the BigQuery dataset name: ")
    target_project_id = input("Please enter the target project ID: ")
    target_dataset_name = input("Please enter the target dataset name: ")

    # Run the QA checks with the provided inputs
    run_qa_checks(project_id, dataset_name, target_project_id, target_dataset_name)
