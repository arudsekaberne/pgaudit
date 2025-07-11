MERGE INTO landing.pgaudit_session_log AS target
USING stg.pgaudit_session_log AS source
    ON target.session_id = source.session_id
    AND target.session_line_num = source.session_line_num
WHEN NOT MATCHED THEN
INSERT (
    log_time_ist, session_id, session_line_num, statement_id, substatement_id, class,
    command, object_type, object_name, statement, parameters, row_count,
    batch_time_ist, log_file_path
)
VALUES (
    source.log_time_ist, source.session_id, source.session_line_num, source.statement_id,
    source.substatement_id, source.class, source.command, source.object_type,
    source.object_name, source.statement, source.parameters, source.row_count,
    CAST(:batch_time_ist AS TIMESTAMP(3)),
    :log_file_path
)
;