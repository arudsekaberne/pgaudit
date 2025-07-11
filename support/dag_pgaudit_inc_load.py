#####################################################
# Packages                                          #
#####################################################

import pendulum
from airflow import DAG
from typing import Any, Dict
from datetime import datetime, timedelta
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash_operator import BashOperator


#####################################################
# Constants                                         #
#####################################################

DAG_TIMEZONE: str = "Asia/Kolkata"

DEFAULT_ARGS: Dict[str, Any] = {
    "owner": "arudsekabs",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes = 5)
}


#####################################################
# DAG                                               #
#####################################################

with DAG(
    dag_id = "dag_pgaudit_inc_load",
    description = "This DAG loads PostgreSQL pgAudit logs into an audit table for compliance and activity tracking. It supports both scheduled incremental loads and manual triggers for on-demand.",
    default_args = DEFAULT_ARGS,
    start_date = datetime(2025, 7, 9, tzinfo = pendulum.timezone(DAG_TIMEZONE)),
    schedule_interval = "0 5 * * *",
    catchup = False,
    tags = ["#Prod"]
) as dag:


    # Start Task
    start = EmptyOperator(task_id = "start")

    # Tasks
    pgaudit_inc_load = BashOperator(
        task_id = "pgaudit_inc_load",
        bash_command = (
            "python3 -u /opt/airflow/jobs/pgaudit/main.py "
            "{% if not dag_run.external_trigger %} --auto {% endif %}"
        )
    )

    # End Task
    end = EmptyOperator(task_id = "end")

    # Tasks Dependency
    start >> pgaudit_inc_load >> end