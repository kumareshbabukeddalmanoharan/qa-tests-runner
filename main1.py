
#!/usr/bin/env python
# main.py

from functions1 import connect_bigquery, fetch_qa_tests, replace_parameters, run_sql, insert_audit_log, display_results

def run_qa_checks(runtime_values, project_id, dataset_name, target_project_id, target_dataset_name):
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
        executed_sql = replace_parameters(test_sql, parameters, runtime_values, target_project_id, target_dataset_name)
        result = run_sql(client, executed_sql)

        insert_audit_log(client, code, executed_sql, exp_result, result, test_sql, project_id, dataset_name)
        results.append((code, executed_sql, result))

    display_results(results)

# Prompt user for runtime values
if __name__ == "__main__":
    env = input("Please enter the environment (e.g., 'env'): ")
    date = input("Please enter the date (YYYY-MM-DD): ")
    project_id = input("Please enter the Google Cloud project ID: ")
    dataset_name = input("Please enter the BigQuery dataset name: ")
    target_project_id = input("Please enter the target project ID: ")
    target_dataset_name = input("Please enter the target dataset name: ")

    runtime_values = [env, date]
    run_qa_checks(runtime_values, project_id, dataset_name, target_project_id, target_dataset_name)
