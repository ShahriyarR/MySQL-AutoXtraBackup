import logging
import os
import re
from dataclasses import dataclass
from typing import Optional, Union

from mysql_autoxtrabackup.common.helpers import create_directory
from mysql_autoxtrabackup.process_runner.process_runner import ProcessRunner

from .generalops import GeneralClass

DOES_NOT_EXIST = "FAILED: MySQL configuration file path does NOT exist"

MYSQL_CONN_MSG = (
    "Neither mysql_socket nor mysql_host and mysql_port are defined in config!"
)

logger = logging.getLogger(__name__)


def _mask_password(status_args: str) -> str:
    # filter out password from argument list
    return re.sub("--password='?\w+'?", "--password='*'", status_args)


def _is_binary_exists(_binary_path: str):
    if os.path.exists(_binary_path):
        logger.info(f"OK: {_binary_path} exists")
        return True

    logger.error(f"FAILED: {_binary_path} does NOT exist")
    raise RuntimeError(f"FAILED: {_binary_path} does NOT exist")


def _is_path_exists(_path: str) -> Optional[bool]:
    if os.path.exists(_path):
        logger.info(f"OK: {_path} exists")
        return True
    return create_directory(_path)


@dataclass
class CheckEnv:
    options: GeneralClass
    full_dir: Optional[str] = None
    inc_dir: Optional[str] = None

    def __post_init__(self):
        self.backup_options = self.options.backup_options
        self.mysql_options = self.options.mysql_options

        if self.full_dir:
            self.backup_options["full_dir"] = self.full_dir
        if self.inc_dir:
            self.backup_options["ind_dir"] = self.inc_dir

        self._required_dirs = {
            "backup_dir": self.backup_options.get("backup_dir"),
            "full_dir": self.backup_options.get("full_dir"),
            "inc_dir": self.backup_options.get("inc_dir"),
        }
        self._required_binaries = {
            "mysql": self.mysql_options.get("mysql"),
            "mysqladmin": self.mysql_options.get("mysqladmin"),
            "backup_tool": self.backup_options.get("backup_tool"),
        }

    def check_all_env(self) -> Union[bool, Exception]:
        """
        Method for running all checks
        :return: True on success, raise RuntimeError on error.
        """
        try:
            self._check_mysql_uptime()
            self._check_mysql_conf()
            self._is_all_binaries_exist()
            self._is_all_paths_exist()
        except Exception as err:
            logger.critical("FAILED: Check status")
            logger.error(err)
            raise RuntimeError("FAILED: Check status") from err
        else:
            logger.info("OK: Check status")
            return True

    def _check_mysql_uptime(self, options: Optional[str] = None) -> Optional[bool]:
        """
        Method for checking if MySQL server is up or not.
        :param: options: Passed options to connect to MySQL server if None, then going to get it from conf file
        :return: True on success, raise RuntimeError on error.
        """
        status_args = (
            f'{self.mysql_options.get("mysqladmin")} {options} status'
            if options
            else self._build_status_check_command()
        )

        logger.info(f"Running mysqladmin command -> {_mask_password(status_args)}")

        return ProcessRunner.run_command(status_args)

    def _check_mysql_conf(self) -> Optional[bool]:
        """
        Method for checking passed MySQL my.cnf defaults file. If it is not passed then skip this check
        :return: True on success, raise RuntimeError on error.
        """
        my_cnf = self.mysql_options.get("mycnf")

        if not my_cnf or my_cnf == "":
            logger.info("Skipping my.cnf check, because it is not specified")
            return True
        elif not os.path.exists(my_cnf):
            logger.error(DOES_NOT_EXIST)
            raise RuntimeError(DOES_NOT_EXIST)

        logger.info("OK: MySQL configuration file exists")
        return True

    def _is_all_paths_exist(self) -> bool:
        return all(_is_path_exists(_path) for _path in self._required_dirs.values())

    def _is_all_binaries_exist(self) -> bool:
        return all(
            _is_binary_exists(_binary_path)
            for _binary_path in self._required_binaries.values()
        )

    def _is_mysql_conn_options_provided(self) -> None:
        if not self.mysql_options.get("mysql_socket") and not (
            self.mysql_options.get("mysql_host")
            and self.mysql_options.get("mysql_port")
        ):
            logger.critical(MYSQL_CONN_MSG)
            raise RuntimeError(MYSQL_CONN_MSG)

    def _build_status_check_command(self) -> str:
        self._is_mysql_conn_options_provided()

        status_args = f"""{self.mysql_options.get("mysqladmin")} 
            --defaults-file={self.mysql_options.get("mycnf")} 
            --user={self.mysql_options.get("mysql_user")} 
            --password='{self.mysql_options.get("mysql_password")}' 
            status"""

        return self._append_conn_string(status_args)

    def _append_conn_string(self, status_args) -> str:
        status_args += (
            f' --socket={self.mysql_options.get("mysql_socket")}'
            if self.mysql_options.get("mysql_socket")
            else ""
        )
        if self.mysql_options.get("mysql_host") and self.mysql_options.get(
            "mysql_port"
        ):
            status_args += f' --host={self.mysql_options.get("mysql_host")}'
            status_args += f' --port={self.mysql_options.get("mysql_port")}'
        return status_args
