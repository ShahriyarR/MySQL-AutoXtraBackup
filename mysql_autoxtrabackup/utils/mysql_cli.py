# This file will consist of some wrapper for using MySQL
# It is mainly used for preparing and calling mysql cli
import logging

from mysql_autoxtrabackup.general_conf import path_config
from mysql_autoxtrabackup.general_conf.generalops import GeneralClass
from mysql_autoxtrabackup.process_runner.process_runner import ProcessRunner

logger = logging.getLogger(__name__)


class MySQLClientHelper:
    def __init__(self, config: str = path_config.config_path_file):
        self.conf = config
        # Using Composition instead of Inheritance here
        options_obj = GeneralClass(config=self.conf)
        self.mysql_options = options_obj.mysql_options

    def create_mysql_client_command(self, statement: str) -> str:
        command_connection = "{} --defaults-file={} -u{} --password={}".format(
            self.mysql_options.get("mysql"),
            self.mysql_options.get("mycnf"),
            self.mysql_options.get("mysql_user"),
            self.mysql_options.get("mysql_password"),
        )
        command_execute = ' -e "{}"'
        if self.mysql_options.get("mysql_socket"):
            command_connection += " --socket={}"
            new_command = command_connection.format(
                self.mysql_options.get("mysql_socket")
            )
        else:
            command_connection += " --host={} --port={}"
            new_command = command_connection.format(
                self.mysql_options.get("mysql_host"),
                self.mysql_options.get("mysql_port"),
            )
        new_command += command_execute
        return new_command.format(statement)

    def mysql_run_command(self, statement: str) -> bool:
        command = self.create_mysql_client_command(statement=statement)
        return ProcessRunner.run_command(command)
