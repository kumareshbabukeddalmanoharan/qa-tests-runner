DROP TABLE IF EXISTS `localprojectid.localdatasetname.qa_test_results`;

CREATE OR REPLACE PROCEDURE `localprojectid.localdatasetname.run_qa_tests`(
  localprojectid STRING,
  localdatasetname STRING,
  projectid STRING,
  datasetname STRING
)

BEGIN
  DECLARE test_query STRING;
  DECLARE executed_query STRING;
  DECLARE exp_result STRING;
  DECLARE actual_result STRING;
  DECLARE test_code STRING;
  DECLARE temp_result INT64; -- Temporary variable to hold actual result
  DECLARE error_message STRING;
  DECLARE qa_tests_table STRING;
  DECLARE qa_test_results_table STRING;
  DECLARE query1 STRING;
  DECLARE param1 STRING DEFAULT '';
  DECLARE param2 STRING DEFAULT '';
  DECLARE param_array ARRAY<STRING>;
  DECLARE test_cases ARRAY<STRUCT<code STRING, parameter STRING,test_sql STRING, exp_result STRING>>; -- Update type here

  -- Dynamically construct the table names using projectid and datasetname
  SET qa_tests_table = CONCAT("`", localprojectid, ".", localdatasetname, ".qa_tests2`");
  SET qa_test_results_table = CONCAT("`", localprojectid, ".", localdatasetname, ".qa_test_results`");

  -- Create the qa_test_results table if it doesn't exist
  EXECUTE IMMEDIATE CONCAT(
    "CREATE TABLE IF NOT EXISTS ", qa_test_results_table, " (code STRING, test_sql STRING, executed_sql STRING, exp_result STRING, actual_result STRING, error_message STRING, execution_time TIMESTAMP)"
  );

  -- Build the query to retrieve test cases
  SET query1 = FORMAT("""
    SELECT ARRAY_AGG(STRUCT(code, parameter, test_sql, exp_result))
    FROM %s
    WHERE enabled = 'Y'
  """, qa_tests_table);

  -- Execute the dynamic query and store the result in the array
  EXECUTE IMMEDIATE query1 INTO test_cases;

  -- Loop through each test in the qa_tests table where enabled = 'Y'
  FOR test_row IN (SELECT * FROM UNNEST(test_cases))
  DO
    -- Initialize variables
    SET test_query = test_row.test_sql;
    SET test_code = test_row.code;
    SET exp_result = test_row.exp_result;
    SET param_array = SPLIT(test_row.parameter, ',');

    -- Check the size of the split array and assign param1 and param2
    SET param1 = param_array[OFFSET(0)]; -- Always assign param1
    IF ARRAY_LENGTH(param_array) > 1 THEN
      SET param2 = param_array[OFFSET(1)]; -- Assign param2 if it exists
    ELSE
      SET param2 = ''; -- Default to empty if param2 does not exist
    END IF;

    -- Replace 'env' and other variables in the dynamic SQL query
    SET executed_query = REPLACE(REPLACE(REPLACE(test_query, 'env', param1), 'projectid', projectid), 'datasetname', datasetname);
    SET executed_query = REPLACE(executed_query, '= date', CONCAT('= "', CAST(param2 AS STRING), '"'));

    -- Default values
    SET actual_result = NULL;
    SET error_message = NULL;

    -- Try executing the dynamically resolved query
    BEGIN
      EXECUTE IMMEDIATE executed_query INTO temp_result;

      -- Convert the result to STRING
      SET actual_result = CAST(temp_result AS STRING);
    EXCEPTION
      WHEN ERROR THEN
        -- Capture the actual error message from the exception
        SET error_message = FORMAT("Error executing query: %s", executed_query);
    END;

    -- Insert the result into qa_test_results table
    EXECUTE IMMEDIATE CONCAT(
      "INSERT INTO ", qa_test_results_table, "(code, test_sql, executed_sql, exp_result, actual_result, error_message, execution_time) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP())"
    ) USING test_code, test_query, executed_query, exp_result, actual_result, error_message;

  END FOR;
END;

CALL `localprojectid.localdatasetname.run_qa_tests`('localprojectid', 'localdatasetname','projectid', 'datasetname');

SELECT * FROM `localprojectid.localdatasetname.qa_test_results` ORDER BY code;
