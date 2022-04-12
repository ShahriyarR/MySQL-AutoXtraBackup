import logging
import os
import re

from dataclasses import dataclass
from typing import Optional, Union
from mysql_autoxtrabackup.process_runner.process_runner import ProcessRunner
from mysql_autoxtrabackup.utils.helpers import create_directory

from .generalops import GeneralClass

logger = logging.getLogger(__name__)


def _mask_password(status_args: str) -> str:
    # filter out password from argument list
    return re.sub("--password='?\w+'?", "--password='*'", status_args)


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

    def _check_mysql_uptime(self, options: Optional[str] = None) -> Optional[bool]:
        """
        Method for checking if MySQL server is up or not.
        :param: options: Passed options to connect to MySQL server if None, then going to get it from conf file
        :return: True on success, raise RuntimeError on error.
        """
        status_args = f'{self.mysql_options.get("mysqladmin")} {options} status' \
            if options else self._build_status_check_command()

        logger.info(f"Running mysqladmin command -> {_mask_password(status_args)}")

        return ProcessRunner.run_command(status_args)

    def _build_status_check_command(self) -> str:
        status_args = f"""{self.mysql_options.get("mysqladmin")} 
            --defaults-file={self.mysql_options.get("mycnf")} 
            --user={self.mysql_options.get("mysql_user")} 
            --password='{self.mysql_options.get("mysql_password")}' 
            status"""
        if self.mysql_options.get("mysql_socket"):
            status_args += f' --socket={self.mysql_options.get("mysql_socket")}'
        elif self.mysql_options.get("mysql_host") and self.mysql_options.get(
                "mysql_port"
        ):
            status_args += f' --host={self.mysql_options.get("mysql_host")}'
            status_args += f' --port={self.mysql_options.get("mysql_port")}'
        else:
            logger.critical(
                "Neither mysql_socket nor mysql_host and mysql_port are defined in config!"
            )
            raise RuntimeError(
                "Neither mysql_socket nor mysql_host and mysql_port are defined in config!"
            )
        return status_args

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
            logger.error("FAILED: MySQL configuration file path does NOT exist")
            raise RuntimeError("FAILED: MySQL configuration file path does NOT exist")

        logger.info("OK: MySQL configuration file exists")
        return True

    def _check_mysql_mysql(self) -> Union[bool, Exception]:
        """
        Method for checking mysql client path
        :return: True on success, raise RuntimeError on error.
        """
        mysql = self.mysql_options.get("mysql")
        if os.path.exists(str(mysql)):
            logger.info(f"OK: {mysql} exists")
            return True

        logger.error(f"FAILED: {mysql} doest NOT exist")
        raise RuntimeError(f"FAILED: {mysql} doest NOT exist")

    def _check_mysql_mysqladmin(self) -> Union[bool, Exception]:
        """
        Method for checking mysqladmin path
        :return: True on success, raise RuntimeError on error.
        """
        mysqladmin = self.mysql_options.get("mysqladmin")
        if os.path.exists(str(mysqladmin)):
            logger.info(f"OK: {mysqladmin} exists")
            return True

        logger.error(f"FAILED: {mysqladmin} does NOT exist")
        raise RuntimeError(f"FAILED: {mysqladmin} does NOT exist")

    def _check_backup_tool(self) -> Union[bool, Exception]:
        """
        Method for checking if given backup tool path is there or not.
        :return: RuntimeError on failure, True on success
        """
        if os.path.exists(str(self.backup_options.get("backup_tool"))):
            logger.info("OK: XtraBackup exists")
            return True

        logger.error("FAILED: XtraBackup does NOT exist")
        raise RuntimeError("FAILED: XtraBackup does NOT exist")

    def _check_backup_dir(self) -> Optional[bool]:
        """
        Check for MySQL backup directory.
        If directory exists already then, return True. If not, try to create it.
        :return: True on success. RuntimeError on failure.
        """
        if os.path.exists(str(self.backup_options.get("backup_dir"))):
            logger.info("OK: Main backup directory exists")
            return True

        return create_directory(str(self.backup_options.get("backup_dir")))

    def _check_full_backup_dir(self) -> Optional[bool]:
        """
        Check full backup directory path.
        If this path exists return True if not try to create.
        :return: True on success.
        """
        if os.path.exists(str(self.backup_options.get("full_dir"))):
            logger.info("OK: Full Backup directory exists")
            return True

        return create_directory(str(self.backup_options.get("full_dir")))

    def _check_inc_backup_dir(self) -> Optional[bool]:
        """
        Check incremental backup directory path.
        If this path exists return True if not try to create.
        :return: True on success.
        """
        if os.path.exists(str(self.backup_options.get("inc_dir"))):
            logger.info("OK: Increment directory exists")
            return True

        return create_directory(str(self.backup_options.get("inc_dir")))

    def check_all_env(self) -> Union[bool, Exception]:
        """
        Method for running all checks
        :return: True on success, raise RuntimeError on error.
        """
        try:
            self._check_mysql_uptime()
            self._check_mysql_mysql()
            self._check_mysql_mysqladmin()
            self._check_mysql_conf()
            self._check_backup_tool()
            self._check_backup_dir()
            self._check_full_backup_dir()
            self._check_inc_backup_dir()
        except Exception as err:
            logger.critical("FAILED: Check status")
            logger.error(err)
            raise RuntimeError("FAILED: Check status") from err
        else:
            logger.info("OK: Check status")
            return True
