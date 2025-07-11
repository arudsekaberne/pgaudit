TRUNCATE TABLE stg.postgre_log;

INSERT INTO stg.postgre_log
SELECT
	log_time_ist,
	CASE WHEN TRIM(user_name) = '' THEN NULL ELSE user_name END,
	CASE WHEN TRIM(database_name) = '' THEN NULL ELSE database_name END,
	process_id,
	CASE WHEN TRIM(connection_from) = '' THEN NULL ELSE connection_from END,
	CASE WHEN TRIM(session_id) = '' THEN NULL ELSE session_id END,
	session_line_num,
	CASE WHEN TRIM(command_tag) = '' THEN NULL ELSE command_tag END,
	session_start_time_ist,
	CASE WHEN TRIM(virtual_transaction_id) = '' THEN NULL ELSE virtual_transaction_id END,
	transaction_id,
	CASE WHEN TRIM(error_severity) = '' THEN NULL ELSE error_severity END,
	CASE WHEN TRIM(sql_state_code) = '' THEN NULL ELSE sql_state_code END,
	CASE WHEN TRIM(message) = '' THEN NULL ELSE message END,
    CASE WHEN TRIM(detail) = '' THEN NULL ELSE detail END,
	CASE WHEN TRIM(hint) = '' THEN NULL ELSE hint END,
	CASE WHEN TRIM(internal_query) = '' THEN NULL ELSE internal_query END,
	internal_query_pos,
	CASE WHEN TRIM(context) = '' THEN NULL ELSE context END,
	CASE WHEN TRIM(query) = '' THEN NULL ELSE query END,
	query_pos,
	CASE WHEN TRIM(location) = '' THEN NULL ELSE location END,
	CASE WHEN TRIM(application_name) = '' THEN NULL ELSE application_name END,
	CASE WHEN TRIM(backend_type) = '' THEN NULL ELSE backend_type END,
	leader_pid,
	query_id
FROM stg.postgre_log_copy
;