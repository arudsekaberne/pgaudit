#####################################################
# Packages                                          #
#####################################################

import paramiko
from paramiko import SSHClient, RSAKey
from typing import Any, Dict, Final, List, Optional
from dependencies.utilities.credential import Credential
from dependencies.utilities.environment import Environment


#####################################################
# Main Class                                        #
#####################################################

class SSHConnection:
    
    """
    Context manager and executor for SSH connections, specifically for executing commands on a remote server.
    """

    def __init__(self):

        self.ssh_client: Optional[SSHClient] = None


    def __enter__(self) -> SSHClient:

        """
        Establishes a connection to the PostgreSQL server when entering the context.
        """

        ssh_credentials: Dict[str, Optional[str]] = Credential.get_ssh_credential()

        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(hostname = ssh_credentials["hostname"], username = ssh_credentials["username"], pkey = RSAKey.from_private_key_file(ssh_credentials["pem_file"])) # type: ignore

        return self.ssh_client


    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[Any]):
        
        """
        Closes the instance connection when exiting the context.
        """
                
        if self.ssh_client:
            self.ssh_client.close()


    def execute_command(self, command: str) -> str:
        
        """
        Executes a bash command over the established SSH connection.
        """

        with self as ssh:
            _, stdout, stderr = ssh.exec_command(command)
            exit_status: int = stdout.channel.recv_exit_status()

            stdout_decoded: str = stdout.read().decode().strip()
            stderr_decoded: str = stderr.read().decode().strip()

            if exit_status != 0 or stderr_decoded:
                raise RuntimeError(f"Command failed '{command}' -> Exit Code: {exit_status}, and Stderr: {stderr_decoded}")

            return stdout_decoded
        

    def execute_psql(self, sql_statement: str) -> str:

        """
        Executes a SQL query inside a Docker container using the psql client.
        """
        
        db_credential: Dict[str, str] = Credential.get_db_credential()

        db_username: Final[str] = db_credential["username"]
        db_database: Final[str] = db_credential["database"]
        application_name: Final[str] = Environment.get_main_path()

        exec_command: str = f"sudo docker exec -u postgres {db_username} psql 'postgresql://postgres@localhost/{db_database}?application_name={application_name}' -c '{sql_statement}'"
        print(f"  - [SQL] {sql_statement}")

        exec_output: str = self.execute_command(exec_command)
        print(f"  - [DONE]")
        
        return exec_output
    

    def print_files(self, heading: str, file_paths: List[str]) -> None:

        """
        Prints a titled list of log file paths.
        """

        print(f"{heading}:")
        
        if file_paths:
            print("\n".join(f"  • {path}" for path in file_paths))
        else:
            print("(No files found)")

        print("***")