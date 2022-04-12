# This file will consist of some wrapper for using MySQL
# It is mainly used for preparing and calling mysql cli
import logging
from dataclasses import dataclass

from mysql_autoxtrabackup.configs.generalops import GeneralClass
from mysql_autoxtrabackup.process_runner.process_runner import ProcessRunner

logger = logging.getLogger(__name__)


@dataclass
class MySQLClientHelper:
    options: GeneralClass

    def __post_init__(self):
        self.mysql_options = self.options.mysql_options

    def create_mysql_client_command(self, statement: str) -> str:
        command_connection = (
            f'{self.mysql_options.get("mysql")} --defaults-file={self.mysql_options.get("mycnf")} '
            f'-u{self.mysql_options.get("mysql_user")} '
            f'--password={self.mysql_options.get("mysql_password")}'
        )

        command_connection += (
            f" --socket={self.mysql_options.get('mysql_socket')}"
            if self.mysql_options.get("mysql_socket")
            else f" --host={self.mysql_options.get('mysql_host')} "
            f" --port={self.mysql_options.get('mysql_port')}"
        )

        return f"{command_connection} -e '{statement}'"

    def mysql_run_command(self, statement: str) -> bool:
        command = self.create_mysql_client_command(statement=statement)
        return ProcessRunner.run_command(command)
