#####################################################
# Packages                                          #
#####################################################

import smtplib
from email.mime.text import MIMEText
from typing import Dict, List, Optional
from email.mime.multipart import MIMEMultipart
from dependencies.utilities.credential import Credential
from dependencies.utilities.validation import Validation


#####################################################
# Class                                             #
#####################################################


class Outlook:
    
    """
    A utility class for sending email alerts using Outlook SMTP settings.
    """

    @staticmethod
    def send(recipients: List[str], subject: str, body: str, cc_recipients: Optional[List[str]] = None, is_html: bool = False) -> None:
        
        """
        Send an email using SMTP credentials from CredUtil.
        """

        # Retrieve SMTP credentials
        smtp_credentials: Dict[str, str] = Credential.get_smtp_credential()
        smtp_port: int = int(smtp_credentials["smtp_port"])
        smtp_server: str = smtp_credentials["smtp_address"]
        smtp_username: str = smtp_credentials["sender_login"]
        smtp_password: str = smtp_credentials["sender_password"]


        # Initialize the email message
        email_message = MIMEMultipart()
        email_message["Subject"] = subject
        email_message["From"] = smtp_username
        email_message["To"] = ", ".join(Validation.validate_email(recipients))
        email_message["Cc"] = ", ".join(Validation.validate_email(cc_recipients)) if cc_recipients else ""


        # Attach the email body
        email_message.attach(MIMEText(body, "html" if is_html else "plain"))


        # Connect to the SMTP server and send the email
        with smtplib.SMTP(smtp_server, smtp_port) as smtp_connection:

            smtp_connection.starttls()
            smtp_connection.login(smtp_username, smtp_password)

            # Combine TO and CC recipients for sending
            all_recipients = recipients + (cc_recipients or [])
            smtp_connection.sendmail(smtp_username, all_recipients, email_message.as_string())