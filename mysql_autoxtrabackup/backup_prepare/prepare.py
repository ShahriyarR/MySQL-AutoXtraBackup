import logging
import os
import time
from typing import Optional
from typing import Union

from mysql_autoxtrabackup.backup_backup.backup_builder import \
    BackupBuilderChecker
from mysql_autoxtrabackup.backup_prepare.copy_back import CopyBack
from mysql_autoxtrabackup.backup_prepare.prepare_builder import \
    BackupPrepareBuilderChecker
from mysql_autoxtrabackup.general_conf import path_config
from mysql_autoxtrabackup.process_runner.process_runner import ProcessRunner
from mysql_autoxtrabackup.utils import helpers

logger = logging.getLogger(__name__)


class Prepare:
    def __init__(
        self,
        config: str = path_config.config_path_file,
        dry_run: Optional[bool] = None,
        tag: Optional[str] = None,
    ) -> None:
        self.conf = config
        self.dry = dry_run
        self.tag = tag
        self.prepare_options = BackupPrepareBuilderChecker(
            config=self.conf, dry_run=self.dry
        )
        # If prepare_tool option enabled in config, make backup_tool to use this.
        # The reason is maybe you have backup taken with 2.4 version but your are going to prepare
        # with newer version. It is somehow unlike to do this but still.
        if self.prepare_options.backup_options.get("prepare_tool"):
            self.prepare_options.backup_options["backup_tool"] = str(
                self.prepare_options.backup_options.get("prepare_tool")
            )

        if self.tag and not os.path.isfile(
            "{}/backup_tags.txt".format(
                self.prepare_options.backup_options.get("backup_dir")
            )
        ):
            raise RuntimeError(
                "Could not find backup_tags.txt inside backup directory. "
                "Please run without --tag option"
            )

    def run_prepare_command(
        self, base_dir: Optional[str], actual_dir: Optional[str], cmd: Optional[str]
    ) -> Optional[bool]:
        # Decrypt backup
        self.prepare_options.decrypt_backup(base_dir, actual_dir)

        # Decompress backup
        self.prepare_options.decompress_backup(base_dir, actual_dir)

        logger.info("Running prepare command -> {}".format(cmd))
        if self.dry:
            return True
        return ProcessRunner.run_command(cmd)

    def prepare_with_tags(self) -> Optional[bool]:
        # Method for preparing backups based on passed backup tags
        found_backups = BackupPrepareBuilderChecker.parse_backup_tags(
            backup_dir=str(self.prepare_options.backup_options.get("backup_dir")),
            tag_name=self.tag,
        )
        recent_bck = helpers.get_latest_dir_name(
            str(self.prepare_options.backup_options.get("full_dir"))
        )
        # I am not going to initialize this object in Prepare class constructor as I thin there is no need.
        backup_builder = BackupBuilderChecker(self.conf, dry_run=self.dry)

        if found_backups[1] == "Full":  # type: ignore
            if recent_bck:
                logger.info("- - - - Preparing Full Backup - - - -")

                # Extracting/decrypting from streamed backup and extra checks goes here.
                backup_builder.extract_decrypt_from_stream_backup(
                    recent_full_bck=recent_bck
                )

                # Prepare command
                backup_prepare_cmd = self.prepare_options.prepare_command_builder(
                    full_backup=recent_bck
                )

                self.run_prepare_command(
                    str(self.prepare_options.backup_options.get("full_dir")),
                    recent_bck,
                    backup_prepare_cmd,
                )

        elif found_backups[1] == "Inc":  # type: ignore
            if not os.listdir(str(self.prepare_options.backup_options.get("inc_dir"))):
                logger.info(
                    "- - - - You have no Incremental backups. So will prepare only latest Full backup - - - -"
                )
                self.prepare_only_full_backup()
            else:
                logger.info("- - - - You have Incremental backups. - - - -")
                if self.prepare_only_full_backup():
                    logger.info("Preparing Incs: ")
                    list_of_dir = helpers.sorted_ls(
                        str(self.prepare_options.backup_options.get("inc_dir"))
                    )
                    # Find the index number inside all list for backup(which was found via tag)
                    index_num = list_of_dir.index(found_backups[0])  # type: ignore
                    # Limit the iteration until this found backup
                    for dir_ in list_of_dir[: index_num + 1]:
                        apply_log_only = None
                        if dir_ != found_backups[0]:  # type: ignore
                            logger.info(
                                "Preparing inc backups in sequence. inc backup dir/name is {}".format(
                                    dir_
                                )
                            )
                            apply_log_only = True

                        else:
                            logger.info(
                                "Preparing last incremental backup, inc backup dir/name is {}".format(
                                    dir_
                                )
                            )

                            # Extracting/decrypting from streamed backup and extra checks goes here
                            backup_builder.extract_decrypt_from_stream_backup(
                                recent_inc_bck=dir_, flag=True
                            )

                        # Prepare command
                        backup_prepare_cmd = (
                            self.prepare_options.prepare_command_builder(
                                full_backup=recent_bck,
                                incremental=dir_,
                                apply_log_only=apply_log_only,
                            )
                        )

                        self.run_prepare_command(
                            str(self.prepare_options.backup_options.get("inc_dir")),
                            dir_,
                            backup_prepare_cmd,
                        )

        logger.info("- - - - The end of the Prepare Stage. - - - -")
        return True

    def prepare_only_full_backup(self) -> Union[None, bool, Exception]:
        recent_bck = helpers.get_latest_dir_name(
            str(self.prepare_options.backup_options.get("full_dir"))
        )
        backup_builder = BackupBuilderChecker(self.conf, dry_run=self.dry)
        if recent_bck:
            apply_log_only = None
            if not os.listdir(str(self.prepare_options.backup_options.get("inc_dir"))):
                logger.info("- - - - Preparing Full Backup - - - -")
                self.prepare_options.untar_backup(recent_bck=recent_bck)
                # Extracting/decrypting from streamed backup and extra checks goes here
                backup_builder.extract_decrypt_from_stream_backup(
                    recent_full_bck=recent_bck
                )

            else:
                logger.info("- - - - Preparing Full backup for incrementals - - - -")
                logger.info(
                    "- - - - Final prepare,will occur after preparing all inc backups - - - -"
                )
                time.sleep(3)

                apply_log_only = True
                # Prepare command

            backup_prepare_cmd = self.prepare_options.prepare_command_builder(
                full_backup=recent_bck, apply_log_only=apply_log_only
            )

            self.run_prepare_command(
                str(self.prepare_options.backup_options.get("full_dir")),
                recent_bck,
                backup_prepare_cmd,
            )
        return True

    def prepare_inc_full_backups(self) -> Union[None, bool, Exception]:
        backup_builder = BackupBuilderChecker(self.conf, dry_run=self.dry)
        if not os.listdir(str(self.prepare_options.backup_options.get("inc_dir"))):
            logger.info(
                "- - - - You have no Incremental backups. So will prepare only latest Full backup - - - -"
            )
            return self.prepare_only_full_backup()
        else:
            logger.info("- - - - You have Incremental backups. - - - -")
            recent_bck = helpers.get_latest_dir_name(
                str(self.prepare_options.backup_options.get("full_dir"))
            )

            if self.prepare_only_full_backup():
                logger.info("Preparing Incs: ")
                list_of_dir = sorted(
                    os.listdir(str(self.prepare_options.backup_options.get("inc_dir")))
                )
                for inc_backup_dir in list_of_dir:
                    apply_log_only = None
                    if inc_backup_dir != max(
                        os.listdir(
                            str(self.prepare_options.backup_options.get("inc_dir"))
                        )
                    ):
                        logger.info(
                            "Preparing Incremental backups in sequence. Incremental backup dir/name is {}".format(
                                inc_backup_dir
                            )
                        )
                        apply_log_only = True
                    else:
                        logger.info(
                            "Preparing last Incremental backup, inc backup dir/name is {}".format(
                                inc_backup_dir
                            )
                        )

                        # Extracting/decrypting from streamed backup and extra checks goes here
                        backup_builder.extract_decrypt_from_stream_backup(
                            recent_inc_bck=inc_backup_dir, flag=True
                        )
                    # Prepare command
                    backup_prepare_cmd = self.prepare_options.prepare_command_builder(
                        full_backup=recent_bck,
                        incremental=inc_backup_dir,
                        apply_log_only=apply_log_only,
                    )

                    self.run_prepare_command(
                        str(self.prepare_options.backup_options.get("inc_dir")),
                        inc_backup_dir,
                        backup_prepare_cmd,
                    )

            logger.info("- - - - The end of the Prepare Stage. - - - -")
            return True

    def prepare_backup_and_copy_back(self) -> None:
        copy_back_obj = CopyBack(config=self.conf)
        # Recovering/Copying Back Prepared Backup
        x = "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -"

        print(x)
        print("")
        print("Preparing full/inc backups!")
        print("What do you want to do?")
        print(
            "1. Prepare Backups and keep for future usage. NOTE('Once Prepared Backups Can not be prepared Again')"
        )
        print("2. Prepare Backups and restore/recover/copy-back immediately")
        print("3. Just copy-back previously prepared backups")

        prepare = int(input("Please Choose one of options and type 1 or 2 or 3: "))
        print("")
        print(x)

        time.sleep(3)

        if prepare == 1:
            if not self.tag:
                self.prepare_inc_full_backups()
            else:
                logger.info("Backup tag will be used to prepare backups")
                self.prepare_with_tags()
        elif prepare == 2:
            if not self.tag:
                self.prepare_inc_full_backups()
            else:
                self.prepare_with_tags()
            if not self.dry:
                copy_back_obj.copy_back_action()
            else:
                logger.critical(
                    "Dry run is not implemented for copy-back/recovery actions!"
                )
        elif prepare == 3:
            if not self.dry:
                copy_back_obj.copy_back_action()
            else:
                logger.critical(
                    "Dry run is not implemented for copy-back/recovery actions!"
                )
        else:
            print("Please type 1 or 2 or 3 and nothing more!")
