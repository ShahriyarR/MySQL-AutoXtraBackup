# Will store necessary checks and command building actions here
import logging
from dataclasses import dataclass
from typing import Optional

from mysql_autoxtrabackup.configs.generalops import GeneralClass

logger = logging.getLogger(__name__)


@dataclass
class BackupCommandBuilder:
    options: GeneralClass

    def __post_init__(self):
        self.mysql_options = self.options.mysql_options
        self.backup_options = self.options.backup_options

    def full_backup_command_builder(self, full_backup_dir: str) -> str:
        return (
            self._get_full_backup_command(full_backup_dir)
            + self._get_common_command_string()
        )

    def inc_backup_command_builder(
        self,
        recent_full_bck: Optional[str],
        inc_backup_dir: Optional[str],
        recent_inc_bck: Optional[str] = None,
    ) -> str:
        xtrabackup_inc_cmd_base = self._get_inc_backup_base_command(
            inc_backup_dir=inc_backup_dir
        )

        xtrabackup_inc_cmd_base += self._add_incremental_basedir(
            recent_inc_bck=recent_inc_bck, recent_full_bck=recent_full_bck
        )

        return f"{xtrabackup_inc_cmd_base} --backup {self._get_common_command_string()}"

    def _get_common_command(self) -> str:
        return (
            f" --socket={self.mysql_options.get('mysql_socket')}"
            if self.mysql_options.get("mysql_socket")
            else f" --host={self.mysql_options.get('mysql_host')} --port={self.mysql_options.get('mysql_port')}"
        )

    def _get_inc_backup_base_command(self, inc_backup_dir: str) -> str:
        return (
            f'{self.backup_options.get("backup_tool")} '
            f'--defaults-file={self.mysql_options.get("mycnf")} '
            f'--user={self.mysql_options.get("mysql_user")} '
            f'--password={self.mysql_options.get("mysql_password")} '
            f"--target-dir={inc_backup_dir}"
        )

    def _add_incremental_basedir(self, recent_inc_bck: str, recent_full_bck: str):
        return (
            f' --incremental-basedir={self.backup_options.get("inc_dir")}/{recent_inc_bck}'
            if recent_inc_bck
            else f' --incremental-basedir={self.backup_options.get("full_dir")}/{recent_full_bck}'
        )

    def _get_full_backup_command(self, full_backup_dir: str) -> str:
        return (
            f"{self.backup_options.get('backup_tool')} --defaults-file={self.mysql_options.get('mycnf')} "
            f"--user={self.mysql_options.get('mysql_user')} --password={self.mysql_options.get('mysql_password')} "
            f"--target-dir={full_backup_dir} --backup"
        )

    def _get_extra_options(self, option: str) -> str:
        _option = self.backup_options.get(option)
        return f" {_option}" if _option else ""

    def _get_common_command_string(self) -> str:
        return f"{self._get_common_command()} {self._get_extra_options('xtra_options')}"
