import logging
import os
from dataclasses import dataclass
from typing import Optional, Tuple

from mysql_autoxtrabackup.general_conf.generalops import GeneralClass

logger = logging.getLogger(__name__)


@dataclass
class BackupPrepareBuilderChecker:

    options: GeneralClass

    def __post_init__(self):
        self.backup_options = self.options.backup_options

    @staticmethod
    def parse_backup_tags(
        backup_dir: Optional[str], tag_name: Optional[str]
    ) -> Optional[Tuple[str, str]]:
        """
        Static Method for returning the backup directory name and backup type
        :param: backup_dir: The backup directory path
        :param: tag_name: The tag name to search
        :return: Tuple of (backup directory, backup type) (2017-11-09_19-37-16, Full).
        :raises: RuntimeError if there is no such tag inside backup_tags.txt
        """
        if os.path.isfile(f"{backup_dir}/backup_tags.txt"):
            with open(f"{backup_dir}/backup_tags.txt", "r") as backup_tags:
                f = backup_tags.readlines()

            for i in f:
                split_ = i.split("\t")
                if tag_name == split_[-1].rstrip("'\n\r").lstrip("'"):
                    return split_[0], split_[1]
            raise RuntimeError("There is no such tag for backups")
        return None

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
        # Base prepare command
        xtrabackup_prepare_cmd = (
            f'{self.backup_options.get("backup_tool")} --prepare '
            f'--target-dir={self.backup_options.get("full_dir")}/{full_backup}'
        )

        xtrabackup_prepare_cmd += (
            f" --incremental-dir={self.backup_options.get('inc_dir')}/{incremental}"
            if incremental
            else ""
        )

        xtrabackup_prepare_cmd += (
            f" {self.backup_options.get('xtra_options')}"
            if self.backup_options.get("xtra_options")
            else ""
        )
        xtrabackup_prepare_cmd += (
            f" {self.backup_options.get('xtra_prepare_options')}"
            if self.backup_options.get("xtra_prepare_options")
            else ""
        )

        return f"{xtrabackup_prepare_cmd} --apply-log-only" if apply_log_only else ""
