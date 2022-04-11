import logging
import os
import time
from dataclasses import dataclass
from typing import List, Optional, Tuple

from mysql_autoxtrabackup.backup_prepare.prepare_builder import (
    BackupPrepareBuilderChecker,
)
from mysql_autoxtrabackup.general_conf.generalops import GeneralClass
from mysql_autoxtrabackup.process_runner.process_runner import ProcessRunner
from mysql_autoxtrabackup.utils import helpers

logger = logging.getLogger(__name__)


@dataclass
class Prepare:
    options: GeneralClass
    dry_run: Optional[bool] = None
    tag: Optional[str] = None

    def __post_init__(self):

        self.prepare_options = BackupPrepareBuilderChecker(options=self.options)

        if self.tag and not os.path.isfile(
            f'{self.prepare_options.backup_options.get("backup_dir")}/backup_tags.txt'
        ):
            raise RuntimeError(
                "Could not find backup_tags.txt inside backup directory. "
                "Please run without --tag option"
            )

        self.recent_bck = helpers.get_latest_dir_name(
            str(self.prepare_options.backup_options.get("full_dir"))
        )
        self.inc_dir = str(self.prepare_options.backup_options.get("inc_dir"))

    def run_prepare_command(self, cmd: Optional[str]) -> Optional[bool]:

        logger.info(f"Running prepare command -> {cmd}")
        if self.dry_run:
            return True
        return ProcessRunner.run_command(cmd)

    def prepare_with_tags(self) -> Optional[bool]:
        # Method for preparing backups based on passed backup tags
        found_backups = BackupPrepareBuilderChecker.parse_backup_tags(
            backup_dir=str(self.prepare_options.backup_options.get("backup_dir")),
            tag_name=self.tag,
        )

        self._prepare_and_run_using_tags(found_backups)

        logger.info("- - - - The end of the Prepare Stage. - - - -")
        return True

    def prepare_run_incremental_backups(self, found_backups: Optional[Tuple[str, str]]) -> None:
        logger.info("Preparing Incs: ")
        self._iterate_and_run_found_backups(
            found_backups, helpers.sorted_ls(self.inc_dir)
        )

    def prepare_only_full_backup(self) -> Optional[bool]:
        if self.recent_bck:
            apply_log_only = None
            if os.listdir(self.inc_dir):
                logger.info("- - - - Preparing Full backup for incrementals - - - -")
                logger.info(
                    "- - - - Final prepare,will occur after preparing all inc backups - - - -"
                )
                time.sleep(3)

                apply_log_only = True

            self._prepare_and_run(
                recent_bck=self.recent_bck, apply_log_only=apply_log_only
            )

        return True

    def prepare_inc_full_backups(self) -> Optional[bool]:
        if not os.listdir(self.inc_dir):
            logger.info(
                "- - - - You have no Incremental backups. So will prepare only latest Full backup - - - -"
            )
            return self.prepare_only_full_backup()
        else:
            logger.info("- - - - You have Incremental backups. - - - -")

            if self.prepare_only_full_backup():
                logger.info("Preparing Incs: ")
                list_of_dir = sorted(os.listdir(self.inc_dir))
                self._iterate_and_run_sequential_increment_backups(list_of_dir)

            logger.info("- - - - The end of the Prepare Stage. - - - -")
            return True

    def _prepare_and_run_using_tags(
        self, found_backups: Optional[Tuple[str, str]]
    ) -> None:
        if found_backups[1] == "Full":
            if self.recent_bck:
                logger.info("- - - - Preparing Full Backup - - - -")
                self._prepare_and_run(recent_bck=self.recent_bck)

        elif found_backups[1] == "Inc":
            if not os.listdir(self.inc_dir):
                logger.info(
                    "- - - - You have no Incremental backups. So will prepare only latest Full backup - - - -"
                )
                self.prepare_only_full_backup()
            else:
                logger.info("- - - - You have Incremental backups. - - - -")
                if self.prepare_only_full_backup():
                    self.prepare_run_incremental_backups(found_backups)

    def _iterate_and_run_sequential_increment_backups(self, dir_: List[str]) -> None:
        for inc_backup_dir in dir_:
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
        # Prepare command
        backup_prepare_cmd = self.prepare_options.prepare_command_builder(
            full_backup=recent_bck,
            incremental=dir_,
            apply_log_only=apply_log_only,
        )
        self.run_prepare_command(backup_prepare_cmd)

    def _iterate_and_run_found_backups(
        self, found_backups: Optional[Tuple[str, str]], list_of_dir: List[str]
    ) -> None:
        # Limit the iteration until this found backup
        for dir_ in list_of_dir[: list_of_dir.index(found_backups[0]) + 1]:
            apply_log_only = None
            if dir_ != found_backups[0]:
                logger.info(
                    f"Preparing inc backups in sequence. inc backup dir/name is {dir_}"
                )
                apply_log_only = True
            else:
                logger.info(
                    f"Preparing last incremental backup, inc backup dir/name is {dir_}"
                )

            self._prepare_and_run(
                recent_bck=self.recent_bck, apply_log_only=apply_log_only, dir_=dir_
            )

    def prepare_backup_and_copy_back(self) -> None:
        x = "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -"

        print(x)
        print("")
        print("Preparing full/inc backups!")
        answer = input("Are you sure? [Y/n]: ")
        print("")
        print(x)

        time.sleep(3)

        if answer.lower() == "y":
            if not self.tag:
                self.prepare_inc_full_backups()
            else:
                logger.info("Backup tag will be used to prepare backups")
                self.prepare_with_tags()
        else:
            print("Please type Y or n!")
