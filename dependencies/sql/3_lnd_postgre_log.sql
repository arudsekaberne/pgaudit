MERGE INTO landing.postgre_log AS target
USING stg.postgre_log AS source
    ON target.session_id = source.session_id
    AND target.session_line_num = source.session_line_num
WHEN NOT MATCHED THEN
INSERT (
    log_time_ist, user_name, database_name, process_id, connection_from, session_id, session_line_num,
    command_tag, session_start_time_ist, virtual_transaction_id, transaction_id, error_severity,
    sql_state_code, message, detail, hint, internal_query, internal_query_pos, context, query,
    query_pos, location, application_name, backend_type, leader_pid, query_id,
    duration, batch_time_ist, log_file_path
)
VALUES (
    source.log_time_ist, source.user_name, source.database_name, source.process_id, source.connection_from,
    source.session_id, source.session_line_num, source.command_tag, source.session_start_time_ist,
    source.virtual_transaction_id, source.transaction_id, source.error_severity, source.sql_state_code,
    source.message, source.detail, source.hint, source.internal_query, source.internal_query_pos,
    source.context, source.query, source.query_pos, source.location, source.application_name,
    source.backend_type, source.leader_pid, source.query_id,
    source.log_time_ist - source.session_start_time_ist,
    CAST(:batch_time_ist AS TIMESTAMP(3)),
    :log_file_path
)
;