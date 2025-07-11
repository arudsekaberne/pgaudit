BEGIN;

TRUNCATE TABLE stg.pgaudit_session_log;

CREATE TEMP TABLE temp_pgaudit_session_log
ON COMMIT DROP AS
SELECT
	log_time_ist, session_id, session_line_num,
	SUBSTRING(message FROM '^[^,]*,(.*)') AS pgaudit_log
FROM stg.postgre_log
WHERE message LIKE 'AUDIT: SESSION,%'
;

CREATE TEMP TABLE temp_pgaudit_session_split_log
ON COMMIT DROP AS
SELECT
	log_time_ist,
	session_id,
	session_line_num,
	TRIM(SPLIT_PART(pgaudit_log, ',', 1))::INT AS statement_id,
	TRIM(SPLIT_PART(pgaudit_log, ',', 2))::INT AS substatement_id,
	TRIM(SPLIT_PART(pgaudit_log, ',', 3)) AS class,
	TRIM(SPLIT_PART(pgaudit_log, ',', 4)) AS command,
	TRIM(SPLIT_PART(pgaudit_log, ',', 5)) AS object_type,
	TRIM(SPLIT_PART(pgaudit_log, ',', 6)) AS object_name,
	TRIM(
        BOTH '"' FROM REGEXP_REPLACE(
            pgaudit_log,
            E'^(?:\"[^\"]*\"|[^,"]*)(?:,(?:\"[^\"]*\"|[^,"]*)){5},(.*),[^,]+,[^,]+$',
            E'\\1',
            'si'
        )
    ) AS statement,
	TRIM(SPLIT_PART(pgaudit_log, ',', -2)) AS parameters,
	TRIM(SPLIT_PART(pgaudit_log, ',', -1))::INT AS row_count
FROM temp_pgaudit_session_log
;

CREATE TEMP TABLE temp_pgaudit_session_parsed_log
ON COMMIT DROP AS
SELECT
	log_time_ist,
	session_id,
	session_line_num,
	statement_id,
	substatement_id,
	CASE WHEN class = '' THEN NULL ELSE class END,
    CASE WHEN command = '' THEN NULL ELSE command END,
    CASE WHEN object_type = '' THEN NULL ELSE object_type END,
    CASE WHEN object_name = '' THEN NULL ELSE object_name END,
    CASE WHEN statement = '' THEN NULL ELSE statement END,
    CASE WHEN parameters = '' OR parameters = '<none>' THEN NULL ELSE parameters END,		
	row_count
FROM temp_pgaudit_session_split_log
;

INSERT INTO stg.pgaudit_session_log
SELECT 
	log_time_ist,
	session_id,
	session_line_num,
	statement_id,
	substatement_id,
	class,
	command,
	CASE
		WHEN (log.command IN ('DROP VIEW') AND log.object_type IS NULL) THEN 'VIEW'
	    WHEN (log.command IN ('COPY', 'DROP TABLE', 'TRUNCATE TABLE') AND log.object_type IS NULL) THEN 'TABLE'
	    ELSE log.object_type
	END AS object_type,
	COALESCE(log.object_name, match.schema_name || '.' || match.table_name) AS object_name_match,
	statement,
	parameters,
	row_count
FROM temp_pgaudit_session_parsed_log AS log
LEFT JOIN LATERAL (
    SELECT 
        regexp_matches(
            log.statement,
            CASE
				WHEN log.command = 'COPY' THEN '(?i)\\?copy\s+([a-zA-Z_][\w]*)\.([a-zA-Z_][\w]*)\s+from'
				WHEN log.command = 'TRUNCATE TABLE' THEN '(?i)truncate\s+table\s+([a-zA-Z_][\w]*)\.([a-zA-Z_][\w]*)'
				WHEN log.command = 'DROP VIEW' THEN '(?i)drop\s+view(?:\s+if\s+exists)?\s+([a-zA-Z_][\w]*)\.([a-zA-Z_][\w]*)'
                WHEN log.command = 'DROP TABLE' THEN '(?i)drop\s+table(?:\s+if\s+exists)?\s+([a-zA-Z_][\w]*)\.([a-zA-Z_][\w]*)'
            END
        ) AS match
) AS raw_match
	ON log.command = 'TRUNCATE TABLE'
	OR (log.command = 'DROP TABLE' AND log.object_name IS NULL)
CROSS JOIN LATERAL (
    SELECT 
        raw_match.match[1] AS schema_name,
        raw_match.match[2] AS table_name
) AS match
;

COMMIT;