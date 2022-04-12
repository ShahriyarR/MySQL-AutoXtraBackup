import logging
import os
import time
from dataclasses import dataclass
from typing import List, Optional, Tuple

from mysql_autoxtrabackup.common import helpers
from mysql_autoxtrabackup.configs.generalops import GeneralClass
from mysql_autoxtrabackup.prepare.prepare_builder import BackupPrepareBuilderChecker
from mysql_autoxtrabackup.process_runner.process_runner import ProcessRunner

logger = logging.getLogger(__name__)


def _set_apply_log_only_found_backups(
    dir_: str, found_backups: Optional[Tuple[str, str]]
):
    apply_log_only = None
    if dir_ != found_backups[0]:
        logger.info(f"Preparing inc backups in sequence. inc backup dir/name is {dir_}")
        apply_log_only = True
    else:
        logger.info(f"Preparing last incremental backup, inc backup dir/name is {dir_}")
    return apply_log_only


def _ask_input() -> str:
    x = "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -"
    print(x)
    print("")
    print("Preparing full/inc backups!")
    answer = input("Are you sure? [Y/n]: ")
    print("")
    print(x)
    return answer


@dataclass
class Prepare:
    options: GeneralClass
    dry_run: Optional[bool] = None

    def __post_init__(self):

        self.prepare_options = BackupPrepareBuilderChecker(options=self.options)

        self.recent_bck = helpers.get_latest_dir_name(
            str(self.prepare_options.backup_options.get("full_dir"))
        )
        self.inc_dir = str(self.prepare_options.backup_options.get("inc_dir"))

    def prepare_backup(self) -> None:
        answer = _ask_input()

        time.sleep(3)

        self._handle_prompt(answer)

    def _handle_prompt(self, answer) -> None:
        if answer.lower() == "y":
            self._prepare_inc_and_full_backups()
        else:
            print("Please type Y or n!")

    def _run_prepare_command(self, cmd: Optional[str]) -> Optional[bool]:
        logger.info(f"Running prepare command -> {cmd}")
        if self.dry_run:
            return True
        return ProcessRunner.run_command(cmd)

    def _prepare_run_incremental_backups(
        self, found_backups: Optional[Tuple[str, str]]
    ) -> None:
        logger.info("Preparing Incs: ")
        self._iterate_and_run_found_backups(
            found_backups, helpers.sorted_ls(self.inc_dir)
        )

    def _prepare_only_full_backup(self) -> Optional[bool]:
        if self.recent_bck:
            apply_log_only = self._set_apply_log_only()

            self._prepare_and_run(
                recent_bck=self.recent_bck, apply_log_only=apply_log_only
            )

        return True

    def _prepare_inc_and_full_backups(self) -> Optional[bool]:
        if not os.listdir(self.inc_dir):
            logger.info(
                "- - - - You have no Incremental backups. So will prepare only latest Full backup - - - -"
            )
            return self._prepare_only_full_backup()
        else:
            logger.info("- - - - You have Incremental backups. - - - -")

            if self._prepare_only_full_backup():
                logger.info("Preparing Incs: ")
                list_of_dir = sorted(os.listdir(self.inc_dir))
                self._iterate_and_run_sequential_increment_backups(list_of_dir)

            logger.info("- - - - The end of the Prepare Stage. - - - -")
            return True

    def _iterate_and_run_sequential_increment_backups(self, dir_: List[str]) -> None:
        for inc_backup_dir in dir_:
            apply_log_only = self._set_apply_log_only_exclude_recent(inc_backup_dir)

            self._prepare_and_run(
                recent_bck=self.recent_bck,
                dir_=inc_backup_dir,
                apply_log_only=apply_log_only,
            )

    def _prepare_and_run(
        self,
        recent_bck: str,
        apply_log_only: Optional[bool] = None,
        dir_: Optional[str] = None,
    ) -> None:
        backup_prepare_cmd = self.prepare_options.prepare_command_builder(
            full_backup=recent_bck,
            incremental=dir_,
            apply_log_only=apply_log_only,
        )
        self._run_prepare_command(backup_prepare_cmd)

    def _iterate_and_run_found_backups(
        self, found_backups: Optional[Tuple[str, str]], list_of_dir: List[str]
    ) -> None:
        # Limit the iteration until this found backup
        for dir_ in list_of_dir[: list_of_dir.index(found_backups[0]) + 1]:
            apply_log_only = _set_apply_log_only_found_backups(dir_, found_backups)

            self._prepare_and_run(
                recent_bck=self.recent_bck, apply_log_only=apply_log_only, dir_=dir_
            )

    def _set_apply_log_only(self) -> bool:
        apply_log_only = None
        if os.listdir(self.inc_dir):
            logger.info("- - - - Preparing Full backup for incrementals - - - -")
            logger.info(
                "- - - - Final prepare,will occur after preparing all inc backups - - - -"
            )
            time.sleep(3)

            apply_log_only = True
        return apply_log_only

    def _set_apply_log_only_exclude_recent(self, inc_backup_dir: str) -> bool:
        apply_log_only = None
        if inc_backup_dir != max(os.listdir(self.inc_dir)):
            logger.info(
                f"Preparing Incremental backups in sequence. Incremental backup dir/name is {inc_backup_dir}"
            )

            apply_log_only = True
        else:
            logger.info(
                f"Preparing last Incremental backup, inc backup dir/name is {inc_backup_dir}"
            )
        return apply_log_only
