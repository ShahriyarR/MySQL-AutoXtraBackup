import logging
import os
import shutil
from datetime import datetime
from typing import Union

from mysql_autoxtrabackup.backup_backup.backup_builder import \
    BackupBuilderChecker
from mysql_autoxtrabackup.general_conf import path_config
from mysql_autoxtrabackup.general_conf.generalops import GeneralClass
from mysql_autoxtrabackup.process_runner.process_runner import ProcessRunner
from mysql_autoxtrabackup.utils import helpers

logger = logging.getLogger(__name__)


class BackupArchive:
    def __init__(
        self,
        config: str = path_config.config_path_file,
        dry_run: Union[bool, None] = None,
        tag: Union[str, None] = None,
    ) -> None:
        self.conf = config
        self.dry = dry_run
        self.tag = tag
        options_obj = GeneralClass(config=self.conf)
        self.backup_options = BackupBuilderChecker(
            config=self.conf, dry_run=self.dry
        ).backup_options
        self.backup_archive_options = options_obj.backup_archive_options

    def create_backup_archives(self) -> bool:
        # Creating .tar.gz archive files of taken backups
        file_list = os.listdir(str(self.backup_options.get("full_dir")))
        for i in file_list:
            if len(file_list) == 1 or i != max(file_list):
                logger.info("Preparing backups prior archiving them...")

                if self.backup_archive_options.get("prepare_archive"):
                    logger.info("Started to prepare backups, prior archiving!")
                    prepare_obj = Prepare(
                        config=self.conf, dry_run=self.dry, tag=self.tag
                    )
                    status = prepare_obj.prepare_inc_full_backups()
                    if status:
                        logger.info(
                            "Backups Prepared successfully... {}".format(status)
                        )

                if self.backup_archive_options.get("move_archive") and (
                    int(str(self.backup_archive_options.get("move_archive"))) == 1
                ):
                    dir_name = (
                        str(self.backup_archive_options.get("archive_dir"))
                        + "/"
                        + i
                        + "_archive"
                    )
                    logger.info(
                        "move_archive enabled. Moving {} to {}".format(
                            self.backup_options.get("backup_dir"), dir_name
                        )
                    )
                    try:
                        shutil.copytree(
                            str(self.backup_options.get("backup_dir")), dir_name
                        )
                    except Exception as err:
                        logger.error("FAILED: Move Archive")
                        logger.error(err)
                        raise
                    else:
                        return True
                else:
                    logger.info(
                        "move_archive is disabled. archiving / compressing current_backup."
                    )
                    # Multi-core tar utilizing pigz.

                    # Pigz default to number of cores available, or 8 if cannot be read.

                    # Test if pigz is available.
                    logger.info("testing for pigz...")
                    status = ProcessRunner.run_command("pigz --version")
                    archive_file = (
                        str(self.backup_archive_options.get("archive_dir"))
                        + "/"
                        + i
                        + ".tar.gz"
                    )
                    if status:
                        logger.info("Found pigz...")
                        # run_tar = "tar cvvf - {} {} | pigz -v > {}" \
                        run_tar = (
                            "tar --use-compress-program=pigz -cvf {} {} {}".format(
                                archive_file,
                                self.backup_options.get("full_dir"),
                                self.backup_options.get("inc_dir"),
                            )
                        )
                    else:
                        # handle file not found error.
                        logger.warning(
                            "pigz executeable not available. Defaulting to singlecore tar"
                        )
                        run_tar = "tar -zcf {} {} {}".format(
                            archive_file,
                            self.backup_options.get("full_dir"),
                            self.backup_options.get("inc_dir"),
                        )
                    status = ProcessRunner.run_command(run_tar)
                    if status:
                        logger.info(
                            "OK: Old full backup and incremental backups archived!"
                        )
                        return True

                    logger.error("FAILED: Archiving ")
                    raise RuntimeError("FAILED: Archiving -> {}".format(run_tar))
        return True

    def clean_old_archives(self) -> None:
        logger.info("Starting cleaning of old archives")
        archive_dir = str(self.backup_archive_options.get("archive_dir"))
        # Finding if last full backup older than the interval or more from now!
        cleanup_msg = "Removing archive {}/{} due to {}"
        for archive in helpers.sorted_ls(archive_dir):
            if "_archive" in archive:
                archive_date = datetime.strptime(archive, "%Y-%m-%d_%H-%M-%S_archive")
            else:
                archive_date = datetime.strptime(archive, "%Y-%m-%d_%H-%M-%S.tar.gz")

            now = datetime.now()

            if (
                self.backup_archive_options.get("archive_max_duration")
                or self.backup_archive_options.get("archive_max_size")
            ) and (
                float((now - archive_date).total_seconds())
                >= float(str(self.backup_archive_options.get("archive_max_duration")))
                or float(helpers.get_directory_size(archive_dir))
                > float(str(self.backup_archive_options.get("archive_max_size")))
            ):
                logger.info(
                    cleanup_msg.format(
                        archive_dir, archive, "archive_max_duration exceeded."
                    )
                )
                logger.info("OR")
                logger.info(
                    cleanup_msg.format(
                        archive_dir, archive, "archive_max_size exceeded."
                    )
                )
                full_archive_path = os.path.join(archive_dir, archive)
                if os.path.isdir(full_archive_path):
                    shutil.rmtree(full_archive_path)
                else:
                    os.remove(full_archive_path)
