#####################################################
# Packages                                          #
#####################################################

import os
from dotenv import load_dotenv
from typing import Dict, Optional, Literal
from dependencies.utilities.environment import Environment


#####################################################
# Class                                             #
#####################################################


# Load .env variables once when the module is imported
load_dotenv()


class Credential:

    # Class Private Variables
    __ENV: Literal["DEV", "PROD"] = "DEV" if Environment.is_dev() else "PROD" 


    @classmethod
    def getenv(cls, p_key: str, raise_expection: bool = True) -> Optional[str]:

        value: Optional[str] = os.getenv(p_key, None)

        if not value and raise_expection:
            raise Exception(f"Environment value can't be empty for {p_key}: {value}, please check `.env` or `.bashrc` file.")

        return value
    
    
    @classmethod
    def get_smtp_credential(cls) -> Dict[str, str]:
        
        return {
            "smtp_port"      : cls.getenv("SMTP_PORT"),
            "smtp_address"   : cls.getenv("SMTP_ADDRESS"),
            "sender_login"   : cls.getenv("SMTP_SENDER_LOGIN"),
            "sender_password": cls.getenv("SMTP_SENDER_PASSWORD"),
        } # type: ignore
    
    
    @classmethod
    def get_ssh_credential(cls) -> Dict[str, Optional[str]]:
        
        return {
            "username": cls.getenv(f"EC2_USER_{cls.__ENV}"),
            "hostname": cls.getenv(f"EC2_HOST_{cls.__ENV}"),
            "pem_file": cls.getenv(f"EC2_PEM_FILE_{cls.__ENV}"),
        }
    

    @classmethod
    def get_db_credential(cls) -> Dict[str, str]:
        
        return {
            "database": cls.getenv(f"POSTGRE_DB_{cls.__ENV}"),
            "username": cls.getenv(f"POSTGRE_USER_{cls.__ENV}"),
            "password": cls.getenv(f"POSTGRE_PASS_{cls.__ENV}"),
            "hostname": cls.getenv(f"POSTGRE_HOST_{cls.__ENV}"),
            "port"    : cls.getenv(f"POSTGRE_PORT_{cls.__ENV}")
        } # type: ignore