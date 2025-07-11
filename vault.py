#####################################################
# Packages                                          #
#####################################################

import pandas as pd
from pathlib import Path
from jinja2 import Template
from dependencies import assets
from datetime import date, datetime
import importlib.resources as pkg_resources
from typing import Dict, Final, List, Optional
from dependencies.utilities.outlook import Outlook
from dependencies.utilities.dataframe import Dataframe
from dependencies.utilities.environment import Environment



#####################################################
# Main Class                                        #
#####################################################


class Vault:

    """
    This module provides utility methods to support PostgreSQL audit log processing and reporting.
    """

    SMTP_RECEIVERS: List[str] = ["arudsekabs@altimetrik.com"]
    SMTP_RECEIVERS_CC: Optional[List[str]] = None


    @classmethod
    def fetch_date(cls, log_file_path: str) -> date:

        """
        Extracts the date from a log file path based on the expected file name pattern.
        """

        log_file_name: str = Path(log_file_path).stem
        log_file_date_str: str = log_file_name.split("_")[1]
        log_file_date_parsed: date = datetime.strptime(log_file_date_str, "%Y%m%d").date()

        return log_file_date_parsed


    @classmethod
    def filter_log_files(cls, log_files: List[str], max_completed_file_date: Optional[date]) -> List[str]:

        """
        Filters a list of log file paths to include only those with a date newer than the given max completed date.
        """

        def _sort_log_files(_log_files: List[str]) -> List[str]:

            """
            Sorts a list of PostgreSQL log file paths based on the date embedded in each filename.
            """
            
            return [
                _file_path for _file_path in sorted(_log_files, key = lambda _file_path: cls.fetch_date(_file_path))
            ]
        

        # Return original list if empty input or no date to filter by
        if (not log_files) or (not max_completed_file_date):
            return _sort_log_files(log_files)

        selected_files: List[str] = []

        for log_file_path in log_files:

            log_file_name: str = Path(log_file_path).stem
            log_file_date: date = cls.fetch_date(log_file_name)
            
            if log_file_date > max_completed_file_date:
                selected_files.append(log_file_path)

        return _sort_log_files(selected_files)


    @classmethod
    def send_email_notification(cls, batch_run_datetime: datetime, batch_type: str, expection: Optional[Exception] = None) -> None:

        """
        Sends a email notification via Outlook email using a pre-defined HTML template.
        """

        def __style_task_status(batch_status: str) -> str:

            """
            Apply HTML styling to batch status for use in the email template.
            """
            
            # Mapping from bacth status to styled HTML span
            batch_status_style_map: Final[Dict[str, str]] = {
                "ON-GOING": f"<span class='status-ongoing'>ON-GOING</span>",
                "COMPLETE": f"<span class='status-success'>COMPLETE</span>"
            }
            
            return batch_status_style_map[batch_status]
            

        # Define column renaming mapping for readability in the email
        SELECTED_COLUMNS_CONFIG: Final[Dict[str, str]] = {
            "batch_id": "Batch ID",
            "log_file_date": "Log File Date",
            "log_file_path": "Log File Name",
            "inserted_rows": "Inserted Rows",
            "batch_status_styled": "Log Status"
        }


        # Parse run logs
        log_df: Optional[pd.DataFrame] = Dataframe.select_query_all(f""" 
            SELECT
                batch_id, log_file_path, log_file_date::text, inserted_rows, batch_status
            FROM landing.postgre_log_run
            WHERE batch_time_ist = CAST('{batch_run_datetime}' AS TIMESTAMP(3))
            ORDER BY batch_id
            ;
        """)


        # Create a working copy of the log DataFrame and apply styling
        log_work_df: Optional[pd.DataFrame] = log_df.copy()
        log_work_df["batch_status_styled"] = log_work_df["batch_status"].apply(func = __style_task_status) # type: ignore


        # Select and rename relevant columns
        log_selected_df: Optional[pd.DataFrame] = log_work_df[SELECTED_COLUMNS_CONFIG.keys()]
        log_renamed_df: Optional[pd.DataFrame] = log_selected_df.rename(columns = SELECTED_COLUMNS_CONFIG)

        
        # Convert the styled DataFrame to HTML for embedding into the email
        log_table_html: str = log_renamed_df.to_html(index = False, escape = False) # type: ignore


        # Load the HTML template from the assets
        with pkg_resources.open_text(assets, "pgaudit_email_template.html", encoding="utf-8") as html_obj:
            email_html_object: str = html_obj.read()


        # Render the email template with actual values
        rendered_html_template = Template(email_html_object).render(
            ph_run_datetime = batch_run_datetime.strftime("%Y-%m-%d %I:%M:%S %p"),
            ph_log_table_html = log_table_html if not log_df.empty else None,
            ph_exception_message = expection,
            ph_batch_type = batch_type
        )


        # TODO: Remove the below statement in production
        # print(rendered_html_template)


        # Send the rendered email using Outlook
        Outlook.send(
            recipients = cls.SMTP_RECEIVERS,
            cc_recipients = cls.SMTP_RECEIVERS_CC,
            subject = f"{'TEST' if Environment.is_dev() else 'LIVE'} [PgAudit] {'❌' if expection else '✅'} MGDB Database Log Insert Run",
            body = rendered_html_template,
            is_html = True
        )

        print("Email notification sent.")

