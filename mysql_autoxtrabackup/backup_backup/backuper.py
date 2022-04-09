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

from mysql_autoxtrabackup.backup_backup.backup_builder import BackupBuilderChecker
from mysql_autoxtrabackup.backup_backup.backup_tags import BackupTags
from mysql_autoxtrabackup.general_conf import path_config
from mysql_autoxtrabackup.general_conf.check_env import CheckEnv
from mysql_autoxtrabackup.process_runner.process_runner import ProcessRunner
from mysql_autoxtrabackup.utils import helpers, mysql_cli

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


def _get_inc_dir(builder_obj: BackupBuilderChecker):
    return str(builder_obj.backup_options.get("inc_dir"))


def _get_full_dir(builder_obj: BackupBuilderChecker):
    return str(builder_obj.backup_options.get("full_dir"))


def _create_bck_dir(path: str):
    return helpers.create_backup_directory(path)


def _get_recent_bck(path: str):
    return helpers.get_latest_dir_name(path)


@dataclass
class Backup:
    builder_obj: BackupBuilderChecker
    tagger: BackupTags
    mysql_cli: mysql_cli.MySQLClientHelper
    config: str = path_config.config_path_file
    dry_run: Optional[bool] = None
    tag: Optional[str] = None
    _full_dir: str = field(init=False)
    _inc_dir: str = field(init=False)

    def __post_init__(self):
        self._full_dir = _get_full_dir(self.builder_obj)
        self._inc_dir = _get_inc_dir(self.builder_obj)

    def last_full_backup_date(
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
    def clean_full_backup_dir(
        self,
        full_dir: Optional[str] = None,
        remove_all: Optional[bool] = None,
    ) -> Optional[bool]:
        # Deleting old full backup after taking new full backup.
        # Keeping the latest in order not to lose everything.
        logger.info("starting clean_full_backup_dir")

        for i in os.listdir(full_dir):
            rm_dir = f"{full_dir}/{i}"
            if (i != max(os.listdir(full_dir)) and not remove_all) or remove_all:
                logger.info(f"DELETING {rm_dir}")
                shutil.rmtree(rm_dir)
            else:
                logger.info(f"KEEPING {rm_dir}")
        return True

    @_is_inc_path_exists
    def clean_inc_backup_dir(self, inc_dir: Optional[str] = None) -> Optional[bool]:
        # Deleting incremental backups after taking new fresh full backup.
        inc_dir = inc_dir or self._inc_dir

        for i in os.listdir(inc_dir):
            rm_dir = f"{inc_dir}/{i}"
            shutil.rmtree(str(rm_dir))
        return True

    @_is_dry_run
    def full_backup(self) -> bool:
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

        return self._get_status("Full", full_backup_dir, xtrabackup_cmd)

    @_is_dry_run
    def inc_backup(self) -> bool:
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

        return self._get_status("Inc", inc_backup_dir, xtrabackup_inc_cmd)

    def all_backup(self) -> bool:
        """
        This method at first checks full backup directory, if it is empty takes full backup.
        If it is not empty then checks for full backup time.
        If the recent full backup  is taken 1 day ago, it takes full backup.
        In any other conditions it takes incremental backup.
        """
        # Workaround for circular import dependency error in Python

        # Creating object from CheckEnv class
        check_env_obj = CheckEnv(
            self.config,
            full_dir=self._full_dir,
            inc_dir=self._inc_dir,
        )

        assert check_env_obj.check_all_env() is True, "environment checks failed!"
        if not _get_recent_bck(self._full_dir):
            logger.info(
                "- - - - You have no backups : Taking very first Full Backup! - - - -"
            )

            if self.mysql_cli.mysql_run_command("flush logs") and self.full_backup():
                # Removing old inc backups
                self.clean_inc_backup_dir()

        elif self.last_full_backup_date():
            logger.info(
                "- - - - Your full backup is timeout : Taking new Full Backup! - - - -"
            )

            if self.mysql_cli.mysql_run_command("flush logs") and self.full_backup():
                # Removing full backups
                self.clean_full_backup_dir()

                # Removing inc backups
                self.clean_inc_backup_dir()

        else:

            logger.info(
                f"- - - - You have a full backup that is less than "
                f'{self.builder_obj.backup_options.get("full_backup_interval")} seconds old. - - - -'
            )

            logger.info(
                "- - - - We will take an incremental one based on recent Full Backup - - - -"
            )

            time.sleep(3)

            # Taking incremental backup
            self.inc_backup()

        return True

    def _get_status(self, backup_type: str, backup_dir: str, xtrabackup_cmd: str):
        logger.debug(f'Starting {self.builder_obj.backup_options.get("backup_tool")}')
        status = ProcessRunner.run_command(xtrabackup_cmd)
        status_str = "OK" if status is True else "FAILED"
        self.tagger.add_tag(
            backup_type=backup_type,
            backup_size=helpers.get_folder_size(backup_dir),
            backup_status=status_str,
        )
        return status
