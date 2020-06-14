# This file will consist of some wrapper for using MySQL
# It is mainly used for preparing and calling mysql cli
from general_conf import path_config
from general_conf.generalops import GeneralClass
import logging
import subprocess
logger = logging.getLogger(__name__)


class MySQLClientHelper(GeneralClass):
    def __init__(self, config=path_config.config_path_file):
        self.conf = config
        # Call GeneralClass for storing configuration options
        super().__init__(self.conf)

    def create_mysql_client_command(self, statement: str) -> str:
        command_connection = '{} --defaults-file={} -u{} --password={}'
        command_execute = ' -e "{}"'

        if hasattr(self, 'mysql_socket'):
            command_connection += ' --socket={}'
            command_connection += command_execute
            new_command = command_connection.format(
                self.mysql,
                self.mycnf,
                self.mysql_user,
                self.mysql_password,
                self.mysql_socket,
                statement)
        else:
            command_connection += ' --host={} --port={}'
            command_connection += command_execute
            new_command = command_connection.format(
                self.mysql,
                self.mycnf,
                self.mysql_user,
                self.mysql_password,
                self.mysql_host,
                self.mysql_port,
                statement)
        return new_command

    def mysql_run_command(self, statement):
        command = self.create_mysql_client_command(statement=statement)
        logger.info("Running command -> {}".format(command))
        status, output = subprocess.getstatusoutput(command)
        if status == 0:
            logger.info("OK: completed command -> {}".format(command))
            return True
        else:
            logger.error("FAILED: command -> {}".format(command))
            logger.error(output)
            raise RuntimeError("FAILED: command -> {}".format(command))
