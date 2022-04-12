# MySQL Backuper Script using Percona Xtrabackup
# Originally Developed by
# Shahriyar Rzayev (Shako)-> https://mysql.az/ https://azepug.az/
# / rzayev.sehriyar@gmail.com / rzayev.shahriyar@yandex.com
# This comment is from 2014 - keeping it here
import logging
import os
import shutil
import time
from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps
from typing import Optional

from mysql_autoxtrabackup.backup.backup_builder import BackupCommandBuilder
from mysql_autoxtrabackup.common import helpers, mysql_cli
from mysql_autoxtrabackup.configs.check_env import CheckEnv
from mysql_autoxtrabackup.configs.generalops import GeneralClass
from mysql_autoxtrabackup.process_runner.process_runner import ProcessRunner

logger = logging.getLogger(__name__)


def _is_dry_run(method):
    @wraps(method)
    def wrapped(_self, *args, **kwargs):
        return True if _self.dry_run else method(_self, *args, **kwargs)

    return wrapped


def _is_full_path_exists(method):
    @wraps(method)
    def wrapped(
        _self, full_dir: Optional[str] = None, remove_all: Optional[str] = None
    ):
        full_dir = full_dir or _self._full_dir
        if not os.path.isdir(full_dir):
            return
        return method(_self, full_dir, remove_all)

    return wrapped


def _is_inc_path_exists(method):
    @wraps(method)
    def wrapped(_self, inc_dir: Optional[str] = None):
        inc_dir = inc_dir or _self._inc_dir
        if not os.path.isdir(inc_dir):
            return
        return method(_self, inc_dir)

    return wrapped


def _get_inc_dir(builder_obj: BackupCommandBuilder) -> str:
    return str(builder_obj.backup_options.get("inc_dir"))


def _get_full_dir(builder_obj: BackupCommandBuilder) -> str:
    return str(builder_obj.backup_options.get("full_dir"))


def _create_bck_dir(path: str) -> str:
    return helpers.create_backup_directory(path)


def _get_recent_bck(path: str) -> str:
    return helpers.get_latest_dir_name(path)


@dataclass
class Backup:
    builder_obj: BackupCommandBuilder
    mysql_cli: mysql_cli.MySQLClientHelper
    options: GeneralClass
    dry_run: Optional[bool] = None
    _full_dir: str = field(init=False)
    _inc_dir: str = field(init=False)

    def __post_init__(self):
        self._full_dir = _get_full_dir(self.builder_obj)
        self._inc_dir = _get_inc_dir(self.builder_obj)

    def all_backup(self) -> bool:
        check_env_obj = CheckEnv(
            options=self.options,
            full_dir=self._full_dir,
            inc_dir=self._inc_dir,
        )

        assert check_env_obj.check_all_env() is True, "environment checks failed!"
        self._run_backup()

        return True

    def _last_full_backup_date(
        self, path: Optional[str] = None, full_backup_interval: Optional[float] = None
    ) -> bool:
        """
        Check if last full backup date retired or not.
        :return: True if last full backup date older than given interval, False if it is newer.
        """
        # Finding last full backup date from dir/folder name
        full_dir = path or self._full_dir
        backup_interval = full_backup_interval or str(
            self.builder_obj.backup_options.get("full_backup_interval")
        )
        max_dir = _get_recent_bck(full_dir)

        dir_date = datetime.strptime(str(max_dir), "%Y-%m-%d_%H-%M-%S")
        now = datetime.now()
        return float((now - dir_date).total_seconds()) >= float(backup_interval)

    @_is_full_path_exists
    def _clean_full_backup_dir(
        self,
        full_dir: Optional[str] = None,
        remove_all: Optional[bool] = None,
    ) -> Optional[bool]:
        # Deleting old full backup after taking new full backup.
        # Keeping the latest in order not to lose everything.
        logger.info("Starting _clean_full_backup_dir")

        for i in os.listdir(full_dir):
            rm_dir = f"{full_dir}/{i}"
            if (i != max(os.listdir(full_dir)) and not remove_all) or remove_all:
                logger.info(f"DELETING {rm_dir}")
                shutil.rmtree(rm_dir)
            else:
                logger.info(f"KEEPING {rm_dir}")
        return True

    @_is_inc_path_exists
    def _clean_inc_backup_dir(self, inc_dir: Optional[str] = None) -> Optional[bool]:
        # Deleting incremental backups after taking new fresh full backup.
        inc_dir = inc_dir or self._inc_dir

        for i in os.listdir(inc_dir):
            rm_dir = f"{inc_dir}/{i}"
            shutil.rmtree(str(rm_dir))
        return True

    @_is_dry_run
    def _take_full_backup(self) -> bool:
        """
        Method for taking full backups. It will construct the backup command based on config file.
        :return: True on success.
        :raise:  RuntimeError on error.
        """
        logger.info(
            f'starting full backup to {self.builder_obj.backup_options.get("full_dir")}'
        )

        full_backup_dir = _create_bck_dir(self._full_dir)

        # Creating Full Backup command.
        xtrabackup_cmd = self.builder_obj.full_backup_command_builder(
            full_backup_dir=full_backup_dir
        )

        return self._get_status(xtrabackup_cmd)

    @_is_dry_run
    def _take_inc_backup(self) -> bool:
        """
        Method for taking incremental backups.
        :return: True on success.
        :raise: RuntimeError on error.
        """
        # Get the recent full backup path
        recent_full_bck = _get_recent_bck(self._full_dir)
        if not recent_full_bck:
            raise RuntimeError(
                "Failed to get Full backup path. Are you sure you have one?"
            )

        # Get the recent incremental backup path
        recent_inc_bck = _get_recent_bck(self._inc_dir)

        # Creating time-stamped incremental backup directory
        inc_backup_dir = _create_bck_dir(self._inc_dir)

        xtrabackup_inc_cmd = self.builder_obj.inc_backup_command_builder(
            recent_full_bck=recent_full_bck,
            inc_backup_dir=inc_backup_dir,
            recent_inc_bck=recent_inc_bck,
        )

        return self._get_status(xtrabackup_inc_cmd)

    def _run_backup(self) -> None:
        if not _get_recent_bck(self._full_dir):
            self._take_fresh_full_backup()
        elif self._last_full_backup_date():
            self._take_new_full_backup_after_old_expired()
        else:
            self._take_incremental_backup()

    def _take_incremental_backup(self):
        logger.info(
            f"- - - - You have a full backup that is less than "
            f'{self.builder_obj.backup_options.get("full_backup_interval")} seconds old. - - - -'
        )
        logger.info(
            "- - - - We will take an incremental one based on recent Full Backup - - - -"
        )
        time.sleep(3)
        # Taking incremental backup
        self._take_inc_backup()

    def _take_new_full_backup_after_old_expired(self):
        logger.info(
            "- - - - Your full backup is timeout : Taking new Full Backup! - - - -"
        )
        self._flush_logs_backup_and_clean(clean_full=True)

    def _take_fresh_full_backup(self):
        logger.info(
            "- - - - You have no backups : Taking very first Full Backup! - - - -"
        )
        self._flush_logs_backup_and_clean()

    def _flush_logs_backup_and_clean(self, clean_full: bool = False) -> None:
        if self._flush_logs_and_take_backup():
            self._clean_backup_dirs(clean_full=clean_full)

    def _clean_backup_dirs(self, clean_full: bool = False) -> None:
        # Removing full backups
        if clean_full:
            self._clean_full_backup_dir()

        # Removing inc backups
        self._clean_inc_backup_dir()

    def _flush_logs_and_take_backup(self) -> bool:
        return (
            self.mysql_cli.mysql_run_command("flush logs") and self._take_full_backup()
        )

    def _get_status(self, xtrabackup_cmd: str) -> bool:
        logger.debug(f'Starting {self.builder_obj.backup_options.get("backup_tool")}')
        return ProcessRunner.run_command(xtrabackup_cmd)
