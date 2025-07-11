-- DROP STATEMENT
DROP VIEW IF EXISTS landing.v_postgre_log;
DROP TABLE IF EXISTS landing.pgaudit_session_log;
DROP TABLE IF EXISTS landing.postgre_log;
DROP TABLE IF EXISTS stg.postgre_log_copy;
DROP TABLE IF EXISTS stg.postgre_log;
DROP TABLE IF EXISTS stg.pgaudit_session_log;
DROP TABLE IF EXISTS landing.postgre_log_run;


-- NATIVE LOGGING
CREATE TABLE stg.postgre_log_copy
(
  log_time_ist timestamp(3) WITHOUT TIME ZONE not null,
  user_name text,
  database_name text,
  process_id integer not null,
  connection_from text,
  session_id text not null,
  session_line_num bigint not null,
  command_tag text,
  session_start_time_ist timestamp(3) WITHOUT TIME ZONE not null,
  virtual_transaction_id text,
  transaction_id bigint not null,
  error_severity text not null,
  sql_state_code text not null,
  message text not null,
  detail text,
  hint text,
  internal_query text,
  internal_query_pos integer,
  context text,
  query text,
  query_pos integer,
  location text not null,
  application_name text,
  backend_type text not null,
  leader_pid integer,
  query_id bigint not null,
  PRIMARY KEY (session_id, session_line_num)
);

CREATE TABLE stg.postgre_log
(
  log_time_ist timestamp(3) WITHOUT TIME ZONE not null,
  user_name text,
  database_name text,
  process_id integer not null,
  connection_from text,
  session_id text not null,
  session_line_num bigint not null,
  command_tag text,
  session_start_time_ist timestamp(3) WITHOUT TIME ZONE not null,
  virtual_transaction_id text,
  transaction_id bigint not null,
  error_severity text not null,
  sql_state_code text not null,
  message text not null,
  detail text,
  hint text,
  internal_query text,
  internal_query_pos integer,
  context text,
  query text,
  query_pos integer,
  location text not null,
  application_name text,
  backend_type text not null,
  leader_pid integer,
  query_id bigint not null,
  PRIMARY KEY (session_id, session_line_num)
);

CREATE TABLE landing.postgre_log
(
  log_time_ist timestamp(3) WITHOUT TIME ZONE not null,
  user_name text,
  database_name text,
  process_id integer not null,
  connection_from text,
  session_id text not null,
  session_line_num bigint not null,
  command_tag text,
  session_start_time_ist timestamp(3) WITHOUT TIME ZONE not null,
  virtual_transaction_id text,
  transaction_id bigint not null,
  error_severity text not null,
  sql_state_code text not null,
  message text not null,
  detail text,
  hint text,
  internal_query text,
  internal_query_pos integer,
  context text,
  query text,
  query_pos integer,
  location text not null,
  application_name text,
  backend_type text not null,
  leader_pid integer,
  query_id bigint not null,
  duration interval not null,
  batch_time_ist timestamp(3) WITHOUT TIME ZONE NOT NULL,
  log_file_path text NOT NULL,
  PRIMARY KEY (session_id, session_line_num)
);

-- PGAUDIT LOGGING
CREATE TABLE stg.pgaudit_session_log
(
  log_time_ist     timestamp(3) WITHOUT TIME ZONE not null,
  session_id       text not null,
  session_line_num bigint not null,
  statement_id     integer not null,
  substatement_id  integer not null,
  class            text not null,
  command          text not null,
  object_type      text not null,
  object_name      text not null,
  statement        text not null,
  parameters       text,
  row_count        integer not null,
  PRIMARY KEY (session_id, session_line_num)
);

CREATE TABLE landing.pgaudit_session_log
(
  log_time_ist     timestamp(3) WITHOUT TIME ZONE not null,
  session_id       text not null,
  session_line_num bigint not null,
  statement_id     integer not null,
  substatement_id  integer not null,
  class            text not null,
  command          text not null,
  object_type      text not null,
  object_name      text not null,
  statement        text not null,
  parameters       text,
  row_count        integer not null,
  batch_time_ist timestamp(3) WITHOUT TIME ZONE NOT NULL,
  log_file_path text NOT NULL,
  PRIMARY KEY (session_id, session_line_num),
  CONSTRAINT fk_postgre_log_ref FOREIGN KEY (session_id, session_line_num)
    REFERENCES landing.postgre_log (session_id, session_line_num)
);

-- RUN LOG
CREATE TABLE landing.postgre_log_run (
  batch_id SERIAL PRIMARY KEY,
  batch_time_ist TIMESTAMP(3) WITHOUT TIME ZONE NOT NULL,
  batch_type TEXT NOT NULL, 
  log_file_path TEXT NOT NULL,
  log_file_date DATE NOT NULL,
  inserted_rows INT NOT NULL,
  batch_status TEXT NOT NULL
);

-- SUMMARY VIEW
CREATE VIEW landing.v_postgre_log AS (
	SELECT
		pg.session_id,
		pg.session_line_num,
		pg.session_start_time_ist,
		pg.log_time_ist,
		pg.error_severity,
		pg.user_name,
		pg.database_name,
		pga.statement_id,
		pga.substatement_id,
		pga.class,
		pga.command,
		pga.object_type,
		pga.object_name,
		pga.statement,
		pga.parameters,
		pga.row_count,
		pg.duration,
		CASE
      WHEN UPPER(TRIM(pg.error_severity)) IN ('ERROR') THEN pg.message
      ELSE NULL
    END AS error_message,
		pg.detail AS error_detail,
		pg.hint AS error_hint,
		pg.query AS error_query,
		pg.query_pos AS error_query_pos,
    	pg.application_name,
		pg.log_file_path,
		pg.batch_time_ist
	FROM landing.postgre_log AS pg
	LEFT JOIN landing.pgaudit_session_log AS pga
		ON  pg.session_id = pga.session_id
		AND pg.session_line_num = pga.session_line_num	
);