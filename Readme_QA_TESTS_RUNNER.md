# QA Tests Procedure Logic

This document outlines the logic behind the `QA_TESTS_RUNNER` stored procedure implemented in Google BigQuery. The purpose of this procedure is to execute quality assurance (QA) tests defined in a specified table and log the results into a designated results table.

## Procedure Logic Overview

1. **Dropping Previous Results**
   - The procedure begins by ensuring that any previous results from past QA runs are removed. This step is crucial for maintaining an accurate and up-to-date results table.

2. **Variable Declarations**
   - Several variables are declared to hold various components necessary for executing the tests, including SQL strings, expected results, actual results, error messages, and temporary result holders.

3. **Dynamic Table Name Construction**
   - The names of the QA tests and results tables are constructed dynamically based on the provided project ID and dataset name. This allows for flexibility in targeting different datasets and projects.

4. **Creating the Results Table**
   - The procedure checks for the existence of the results table and creates it if it does not already exist. This ensures there is a proper destination for logging the results of the executed tests.

5. **Retrieving Enabled Test Cases**
   - The procedure queries the tests table to retrieve all test cases that are marked as enabled. These tests are stored in an array for further processing.

6. **Iterating Through Test Cases**
   - A loop is employed to iterate through each enabled test case. For each test, the SQL query is prepared by replacing placeholders with actual parameters, such as environment variables and date values.

7. **Executing the Test Query**
   - The dynamically constructed SQL query is executed. If the execution is successful, the actual result is captured. In case of an error, the error message is logged for troubleshooting.

8. **Logging Results**
   - After executing each test, the procedure logs the results, including the test code, original SQL query, executed SQL, expected result, actual result, and any error messages into the results table.

## Procedure Execution
- The stored procedure can be executed with specified parameters, allowing it to run tests for different environments and dates.

## Conclusion
The `QA_TESTS_RUNNER` procedure provides a systematic approach to executing and logging QA tests, ensuring data quality and facilitating quality assurance processes in data workflows.
