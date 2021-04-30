import logging
import os
from typing import Optional
from typing import Tuple

from mysql_autoxtrabackup.general_conf import path_config
from mysql_autoxtrabackup.general_conf.generalops import GeneralClass
from mysql_autoxtrabackup.process_runner.process_runner import ProcessRunner

logger = logging.getLogger(__name__)


class BackupPrepareBuilderChecker:
    def __init__(
        self, config: str = path_config.config_path_file, dry_run: Optional[bool] = None
    ) -> None:
        self.conf = config
        self.dry = dry_run

        options_obj = GeneralClass(config=self.conf)
        self.backup_options = options_obj.backup_options
        self.compression_options = options_obj.compression_options
        self.encryption_options = options_obj.encryption_options
        self.xbstream_options = options_obj.xbstream_options

    @staticmethod
    def parse_backup_tags(
        backup_dir: Optional[str], tag_name: Optional[str]
    ) -> Optional[Tuple[str, str]]:
        """
        Static Method for returning the backup directory name and backup type
        :param backup_dir: The backup directory path
        :param tag_name: The tag name to search
        :return: Tuple of (backup directory, backup type) (2017-11-09_19-37-16, Full).
        :raises: RuntimeError if there is no such tag inside backup_tags.txt
        """
        if os.path.isfile("{}/backup_tags.txt".format(backup_dir)):
            with open("{}/backup_tags.txt".format(backup_dir), "r") as backup_tags:
                f = backup_tags.readlines()

            for i in f:
                split_ = i.split("\t")
                if tag_name == split_[-1].rstrip("'\n\r").lstrip("'"):
                    return split_[0], split_[1]
            else:
                raise RuntimeError("There is no such tag for backups")
        return None

    def decompress_backup(
        self, path: Optional[str], dir_name: Optional[str]
    ) -> Optional[bool]:
        """
        Method for backup decompression.
        Check if decompression enabled, if it is, decompress
        backup prior prepare.
        :param path: the basedir path i.e full backup dir or incremental dir.
        :param dir_name: the exact name backup folder(likely timestamped folder name).
        :return: None or RuntimeError
        """
        if self.compression_options.get("decompress"):
            # The base decompression command
            dec_cmd = "{} --decompress={} --target-dir={}/{}".format(
                self.backup_options.get("backup_tool"),
                self.compression_options.get("decompress"),
                path,
                dir_name,
            )
            if self.compression_options.get("remove_original_comp"):
                dec_cmd += " --remove-original"

            logger.info("Trying to decompress backup")
            logger.info("Running decompress command -> {}".format(dec_cmd))
            if self.dry:
                return None
            return ProcessRunner.run_command(dec_cmd)
        return None

    def decrypt_backup(
        self, path: Optional[str], dir_name: Optional[str]
    ) -> Optional[bool]:
        """
        Method for decrypting backups.
        If you use crypted backups it should be decrypted prior preparing.
        :param path: the basedir path i.e full backup dir or incremental dir.
        :param dir_name: the exact name backup folder(likely timestamped folder name).
        :return: None or RuntimeError
        """
        if self.encryption_options.get("decrypt"):
            # The base decryption command
            decr_cmd = "{} --decrypt={} --encrypt-key={} --target-dir={}/{}".format(
                self.backup_options.get("backup_tool"),
                self.encryption_options.get("decrypt"),
                self.encryption_options.get("encrypt_key"),
                path,
                dir_name,
            )
            if self.encryption_options.get("remove_original_comp"):
                decr_cmd += " --remove-original"
            logger.info("Trying to decrypt backup")
            logger.info("Running decrypt command -> {}".format(decr_cmd))
            if self.dry:
                return None
            return ProcessRunner.run_command(decr_cmd)
        return None

    def prepare_command_builder(
        self,
        full_backup: Optional[str],
        incremental: Optional[str] = None,
        apply_log_only: Optional[bool] = None,
    ) -> str:
        """
        Method for building prepare command as it is repeated several times.
        :param full_backup: The full backup directory name
        :param incremental: The incremental backup directory name
        :param apply_log_only: The flag to add --apply-log-only
        :return: The prepare command string
        """
        # Base prepare command
        xtrabackup_prepare_cmd = "{} --prepare --target-dir={}/{}".format(
            self.backup_options.get("backup_tool"),
            self.backup_options.get("full_dir"),
            full_backup,
        )

        if incremental:
            xtrabackup_prepare_cmd += " --incremental-dir={}/{}".format(
                self.backup_options.get("inc_dir"), incremental
            )
        if apply_log_only:
            xtrabackup_prepare_cmd += " --apply-log-only"

        # Checking if extra options were passed:
        if self.backup_options.get("xtra_options"):
            xtrabackup_prepare_cmd += "  {}".format(
                self.backup_options.get("xtra_options")
            )

        # Checking of extra prepare options were passed:
        if self.backup_options.get("xtra_prepare_options"):
            xtrabackup_prepare_cmd += "  {}".format(
                self.backup_options.get("xtra_prepare_options")
            )

        return xtrabackup_prepare_cmd

    def untar_backup(self, recent_bck: str) -> Optional[bool]:
        if self.xbstream_options.get("stream") == "tar":
            full_dir = self.backup_options.get("full_dir")
            untar_cmd = "tar -xf {}/{}/full_backup.tar -C {}/{}".format(
                full_dir, recent_bck, full_dir, recent_bck
            )
            logger.info(
                "The following tar command will be executed -> {}".format(untar_cmd)
            )
            if self.dry == 0 and os.path.isfile(
                "{}/{}/full_backup.tar".format(full_dir, recent_bck)
            ):
                return ProcessRunner.run_command(untar_cmd)
        return None
