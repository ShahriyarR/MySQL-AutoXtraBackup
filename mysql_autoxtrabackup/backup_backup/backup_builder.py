# Will store necessary checks and command building actions here
import logging
from typing import Optional

from mysql_autoxtrabackup.general_conf import path_config
from mysql_autoxtrabackup.general_conf.generalops import GeneralClass

logger = logging.getLogger(__name__)


class BackupBuilderChecker:
    def __init__(
        self,
        config: str = path_config.config_path_file,
        dry_run: Optional[bool] = None,
    ) -> None:
        self.conf = config
        self.dry = dry_run
        options_obj = GeneralClass(config=self.conf)
        self.mysql_options = options_obj.mysql_options
        self.backup_options = options_obj.backup_options

    def general_command_builder(self) -> str:
        """
        Method for building general options for backup command.
        :return: String of constructed options.
        """
        args = (
            f" --socket={self.mysql_options.get('mysql_socket')}"
            if self.mysql_options.get("mysql_socket")
            else f" --host={self.mysql_options.get('mysql_host')} --port={self.mysql_options.get('mysql_port')}"
        )

        return (
            f"{args} {self.backup_options.get('xtra_options')}"
            if self.backup_options.get("xtra_options")
            else ""
        )

    def full_backup_command_builder(self, full_backup_dir: str) -> str:
        """
        Method for creating Full Backup command.
        :param: full_backup_dir the path of backup directory
        :return: generated command string
        """
        return (
            f"{self.backup_options.get('backup_tool')} --defaults-file={self.mysql_options.get('mycnf')} "
            f"--user={self.mysql_options.get('mysql_user')} --password={self.mysql_options.get('mysql_password')} "
            f"--target-dir={full_backup_dir} --backup"
        ) + self.general_command_builder()

    def inc_backup_command_builder(
        self,
        recent_full_bck: Optional[str],
        inc_backup_dir: Optional[str],
        recent_inc_bck: Optional[str] = None,
    ) -> str:
        xtrabackup_inc_cmd_base = (
            f'{self.backup_options.get("backup_tool")} '
            f'--defaults-file={self.mysql_options.get("mycnf")} '
            f'--user={self.mysql_options.get("mysql_user")} '
            f'--password={self.mysql_options.get("mysql_password")} '
            f"--target-dir={inc_backup_dir}"
        )

        xtrabackup_inc_cmd_base += (
            f' --incremental-basedir={self.backup_options.get("inc_dir")}/{recent_inc_bck}'
            if recent_inc_bck
            else f' --incremental-basedir={self.backup_options.get("full_dir")}/{recent_full_bck}'
        )

        return f"{xtrabackup_inc_cmd_base} --backup {self.general_command_builder()}"
