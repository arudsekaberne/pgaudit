INSERT INTO landing.postgre_log_run(batch_time_ist, batch_type, log_file_path, log_file_date, inserted_rows, batch_status)
VALUES (
    CAST(:batch_time_ist AS TIMESTAMP(3)),
    :batch_type,
    :log_file_path,
    CAST(:log_file_date AS DATE),
    :inserted_rows,
    :batch_status
);