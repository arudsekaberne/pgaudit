#####################################################
# Environment Setup                                 #
#####################################################

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


#####################################################
# Packages                                          #
#####################################################

import pytz
import traceback
from vault import Vault
from datetime import date, datetime
from typing import Final, List, Optional
from dependencies.utilities.ssh import SSHConnection
from dependencies.utilities.dataframe import Dataframe
from dependencies.utilities.postgre import PGConnection
from dependencies.utilities.environment import Environment
from argparse import ArgumentParser, Namespace, RawTextHelpFormatter


#####################################################
# Default Configs                                   #
#####################################################

EC2_TMP_LOG_DIR : Final[str] = "/tmp/pgaudit_log"
EC2_DOC_LOG_WNM : Final[str] = "postgresql_*.csv"
EC2_DOC_LOG_DIR : Final[str] = "/var/lib/postgresql/data/pgdata"
RUN_DATETIME_NAIVE: Final[datetime] = datetime.now(pytz.timezone("Asia/Kolkata")).replace(tzinfo = None)


#####################################################
# Pre - Execution                                   #
#####################################################

# Define input arguments
parser: ArgumentParser = ArgumentParser(
    formatter_class = RawTextHelpFormatter, description = "MGDB Postgre Audit Job Runner"
)

if Environment.enable_auto():
    parser.add_argument(
        "--auto", action = "store_true", required = False,
        help = (
            "Indicates that the job is being triggered automatically as part of a scheduled Airflow DAG run.\n\n"
            "Example:\n"
            "  $ python main.py --auto"
        )
    )

# Get input argument
args: Namespace = parser.parse_args()

args_run_type: str = "AUTO" if (args.auto if Environment.enable_auto() else False) else "MANUAL"


#####################################################
# Main Execution                                    #
#####################################################

if __name__ == "__main__":

    try:

        print(f"[INFO] Argument passed: {args}")
        print(f"[INFO] Run Type: {args_run_type}")
        print(f"[INFO] Batch Date Time (IST): {RUN_DATETIME_NAIVE}")
        

        # Initialize connections
        db_util : PGConnection  = PGConnection()
        ssh_util: SSHConnection = SSHConnection()        
    

        # Get most recent completed file date
        max_completed_file_date: Optional[date] = Dataframe.select_query_one("""
            SELECT MAX(log_file_date)::DATE FROM landing.postgre_log_run
            WHERE UPPER(TRIM(batch_status)) = 'COMPLETE'
            ;
        """)

        print("[INFO] Maximum completed log file date:", max_completed_file_date)


        # Find all CSV log files
        logs_found: List[str] = ssh_util.execute_command(f"sudo docker exec postgres find {EC2_DOC_LOG_DIR} -type f -name '{EC2_DOC_LOG_WNM}'").split()
        ssh_util.print_files("Logs Found", logs_found)


        # Filter only unprocessed or partial logs
        logs_selected: List[str] = Vault.filter_log_files(logs_found, max_completed_file_date)
        ssh_util.print_files("Logs Selected", logs_selected)


        # Load unprocessed logs
        for log_index, log_file_path in enumerate(logs_selected, start = 1):

            print(f"({log_index}) Working with {log_file_path}")

            log_file_date: date = Vault.fetch_date(log_file_path)

            db_util.execute_sql("TRUNCATE TABLE stg.postgre_log_copy;")

            ssh_util.execute_psql(fr"\COPY stg.postgre_log_copy FROM '{log_file_path}' WITH CSV;")            
            
            db_util.execute_sql("DELETE FROM stg.postgre_log_copy WHERE LOWER(TRIM(database_name)) != 'mgdb';")

            db_util.execute_file("1_stg_postgre_log.sql")
            
            db_util.execute_file("2_stg_pgaudit_session_log.sql")
            
            inserted_row_count: int = (
                db_util.execute_file("3_lnd_postgre_log.sql", {
                    "batch_time_ist": RUN_DATETIME_NAIVE,
                    "log_file_path": log_file_path
                })
            )

            db_util.execute_file("4_lnd_pgaudit_session_log.sql", {
                "batch_time_ist": RUN_DATETIME_NAIVE,
                "log_file_path": log_file_path
            })

            db_util.execute_file("5_lnd_postgre_log_run.sql", {
                "batch_time_ist": RUN_DATETIME_NAIVE,
                "batch_type": args_run_type,
                "log_file_path": log_file_path,
                "log_file_date": log_file_date,
                "inserted_rows": inserted_row_count,
                "batch_status": "ON-GOING" if RUN_DATETIME_NAIVE.date() == log_file_date else "COMPLETE"
            })

            print("***")

        Vault.send_email_notification(
            batch_run_datetime = RUN_DATETIME_NAIVE,
            batch_type = args_run_type
        )

        sys.exit(0)


    except Exception as error:

        Vault.send_email_notification(
            batch_run_datetime = RUN_DATETIME_NAIVE,
            batch_type = args_run_type,
            expection = error
        )

        traceback.print_exc()

        sys.exit(1)
        