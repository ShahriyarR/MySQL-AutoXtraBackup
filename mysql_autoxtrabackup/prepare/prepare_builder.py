import logging
import os
from dataclasses import dataclass
from typing import Optional, Tuple

from mysql_autoxtrabackup.configs.generalops import GeneralClass

logger = logging.getLogger(__name__)


@dataclass
class BackupPrepareBuilderChecker:
    options: GeneralClass

    def __post_init__(self):
        self.backup_options = self.options.backup_options

    def prepare_command_builder(
        self,
        full_backup: Optional[str],
        incremental: Optional[str] = None,
        apply_log_only: Optional[bool] = None,
    ) -> str:
        """
        Method for building prepare command as it is repeated several times.
        :param: full_backup: The full backup directory name
        :param: incremental: The incremental backup directory name
        :param: apply_log_only: The flag to add --apply-log-only
        :return: The prepare command string
        """
        xtrabackup_prepare_cmd = self._base_prepare_command(full_backup)

        xtrabackup_prepare_cmd = self._append_incremental_option(
            incremental, xtrabackup_prepare_cmd
        )

        xtrabackup_prepare_cmd = self._append_extra_options(xtrabackup_prepare_cmd)

        return (
            f"{xtrabackup_prepare_cmd} --apply-log-only"
            if apply_log_only
            else xtrabackup_prepare_cmd
        )

    def _base_prepare_command(self, full_backup):
        xtrabackup_prepare_cmd = (
            f'{self.backup_options.get("backup_tool")} --prepare '
            f'--target-dir={self.backup_options.get("full_dir")}/{full_backup}'
        )
        return xtrabackup_prepare_cmd

    def _append_incremental_option(self, incremental, xtrabackup_prepare_cmd):
        xtrabackup_prepare_cmd += (
            f" --incremental-dir={self.backup_options.get('inc_dir')}/{incremental}"
            if incremental
            else ""
        )
        return xtrabackup_prepare_cmd

    def _append_extra_options(self, xtrabackup_prepare_cmd):
        xtrabackup_prepare_cmd += (
            f" {self._get_extra_options('xtra_options')}"
            f" {self._get_extra_options('xtra_prepare_options')}"
        )
        return xtrabackup_prepare_cmd

    def _get_extra_options(self, option: str):
        _option = self.backup_options.get(option)
        return f" {_option}" if _option else ""
