# Will store necessary checks and command building actions here
import logging
from os.path import isfile
from typing import Optional
from typing import Union

from mysql_autoxtrabackup.general_conf import path_config
from mysql_autoxtrabackup.general_conf.generalops import GeneralClass
from mysql_autoxtrabackup.process_runner.process_runner import ProcessRunner

logger = logging.getLogger(__name__)


class BackupBuilderChecker:
    # General pre-backup checking/extracting/untar/streaming etc. should happen here

    def __init__(
        self,
        config: str = path_config.config_path_file,
        dry_run: Union[bool, None] = None,
    ) -> None:
        self.conf = config
        self.dry = dry_run
        options_obj = GeneralClass(config=self.conf)
        self.mysql_options = options_obj.mysql_options
        self.compression_options = options_obj.compression_options
        self.encryption_options = options_obj.encryption_options
        self.backup_options = options_obj.backup_options
        self.xbstream_options = options_obj.xbstream_options

    def general_command_builder(self) -> str:
        """
        Method for building general options for backup command.
        :return: String of constructed options.
        """
        args = ""

        if self.mysql_options.get("mysql_socket"):
            args += " --socket={}".format(self.mysql_options.get("mysql_socket"))
        else:
            args += " --host={} --port={}".format(
                self.mysql_options.get("mysql_host"),
                self.mysql_options.get("mysql_port"),
            )
        # Adding compression support for backup
        if (
            self.compression_options.get("compress")
            and self.compression_options.get("compress_chunk_size")
            and self.compression_options.get("compress_threads")
        ):
            args += (
                " --compress={}"
                " --compress-chunk-size={}"
                " --compress-threads={}".format(
                    self.compression_options.get("compress"),
                    self.compression_options.get("compress_chunk_size"),
                    self.compression_options.get("compress_threads"),
                )
            )

        # Adding encryption support for full backup
        if self.encryption_options.get("encrypt"):
            args += (
                " --encrypt={}"
                " --encrypt-threads={}"
                " --encrypt-chunk-size={}".format(
                    self.encryption_options.get("encrypt"),
                    self.encryption_options.get("encrypt_threads"),
                    self.encryption_options.get("encrypt_chunk_size"),
                )
            )

        if self.encryption_options.get("encrypt_key"):
            if self.encryption_options.get("encrypt_key_file"):
                raise AttributeError(
                    "--encrypt-key and --encrypt-key-file are mutually exclusive"
                )
            args += " --encrypt-key={}".format(
                self.encryption_options.get("encrypt_key")
            )
        elif self.encryption_options.get("encrypt_key_file"):
            args += " --encrypt-key-file={}".format(
                self.encryption_options.get("encrypt_key_file")
            )

        # Checking if extra options were passed:
        if self.backup_options.get("xtra_options"):
            args += " {}".format(self.backup_options.get("xtra_options"))
        # Checking if extra backup options were passed:
        if self.backup_options.get("xtra_backup"):
            args += " {}".format(self.backup_options.get("xtra_backup"))

        # Checking if partial recovery list is available
        if self.backup_options.get("partial_list"):
            logger.warning("Partial Backup is enabled!")
            args += ' --databases="{}"'.format(self.backup_options.get("partial_list"))

        return args

    def extract_decrypt_from_stream_backup(
        self,
        recent_full_bck: Optional[str] = None,
        recent_inc_bck: Optional[str] = None,
        flag: Optional[bool] = None,
    ) -> None:
        """
        Method for extracting and if necessary decrypting from streamed backup.
        If the recent_full_bck passed then it means you want to extract the full backup.
        If the recent_int_bck passed then it means you want to extract the inc backup.
        """
        # Extract and decrypt streamed full backup prior to executing incremental backup
        file_name = "{}/{}/inc_backup.stream".format(
            self.backup_options.get("inc_dir"), recent_inc_bck
        )
        file_place_holder = "< {} -C {}/{}".format(
            file_name, self.backup_options.get("inc_dir"), recent_inc_bck
        )

        if not recent_inc_bck:
            file_name = "{}/{}/full_backup.stream".format(
                self.backup_options.get("full_dir"), recent_full_bck
            )
            file_place_holder = "< {} -C {}/{}".format(
                file_name, self.backup_options.get("full_dir"), recent_full_bck
            )

        xbstream_command = None

        if self.xbstream_options.get("stream") == "xbstream":
            xbstream_command = "{} {}".format(
                self.xbstream_options.get("xbstream"),
                self.xbstream_options.get("xbstream_options"),
            )
            if (
                self.encryption_options.get("encrypt")
                and self.xbstream_options.get("xbs_decrypt")
                and not flag
            ):
                logger.info(
                    "Using xbstream to extract and decrypt from {}".format(file_name)
                )
                xbstream_command += (
                    " --decrypt={} --encrypt-key={} --encrypt-threads={} ".format(
                        self.encryption_options.get("decrypt"),
                        self.encryption_options.get("encrypt_key"),
                        self.encryption_options.get("encrypt_threads"),
                    )
                )

        if xbstream_command:
            xbstream_command += file_place_holder
            logger.info(
                "The following xbstream command will be executed {}".format(
                    xbstream_command
                )
            )
            if self.dry == 0 and isfile(file_name):
                ProcessRunner.run_command(xbstream_command)

    def stream_encrypt_compress_tar_checker(self) -> None:
        if self.xbstream_options.get("stream") == "tar" and (
            self.encryption_options.get("encrypt")
            or self.compression_options.get("compress")
        ):
            logger.error(
                "xtrabackup: error: compressed and encrypted backups are "
                "incompatible with the 'tar' streaming format. Use --stream=xbstream instead."
            )
            raise RuntimeError(
                "xtrabackup: error: compressed and encrypted backups are "
                "incompatible with the 'tar' streaming format. Use --stream=xbstream instead."
            )

    def stream_tar_incremental_checker(self) -> None:
        if self.xbstream_options.get("stream") == "tar":
            logger.error(
                "xtrabackup: error: streaming incremental backups are incompatible with the "
                "'tar' streaming format. Use --stream=xbstream instead."
            )
            raise RuntimeError(
                "xtrabackup: error: streaming incremental backups are incompatible with the "
                "'tar' streaming format. Use --stream=xbstream instead."
            )

    def full_backup_command_builder(self, full_backup_dir: str) -> str:
        """
        Method for creating Full Backup command.
        :param full_backup_dir the path of backup directory
        """
        xtrabackup_cmd = (
            "{} --defaults-file={} --user={} --password={} "
            " --target-dir={} --backup".format(
                self.backup_options.get("backup_tool"),
                self.mysql_options.get("mycnf"),
                self.mysql_options.get("mysql_user"),
                self.mysql_options.get("mysql_password"),
                full_backup_dir,
            )
        )
        # Calling general options/command builder to add extra options
        xtrabackup_cmd += self.general_command_builder()

        stream = self.backup_options.get("stream")
        if stream:
            logger.warning("Streaming is enabled!")
            xtrabackup_cmd += ' --stream="{}"'.format(stream)
            if stream == "xbstream":
                xtrabackup_cmd += " > {}/full_backup.stream".format(full_backup_dir)
            elif stream == "tar":
                xtrabackup_cmd += " > {}/full_backup.tar".format(full_backup_dir)

        return xtrabackup_cmd

    def inc_backup_command_builder(
        self,
        recent_full_bck: Optional[str],
        inc_backup_dir: Optional[str],
        recent_inc_bck: Union[str, None] = None,
    ) -> str:
        xtrabackup_inc_cmd_base = (
            "{} --defaults-file={} --user={} --password={}".format(
                self.backup_options.get("backup_tool"),
                self.mysql_options.get("mycnf"),
                self.mysql_options.get("mysql_user"),
                self.mysql_options.get("mysql_password"),
            )
        )
        if not recent_inc_bck:
            xtrabackup_inc_cmd_base += (
                " --target-dir={} --incremental-basedir={}/{} --backup".format(
                    inc_backup_dir, self.backup_options.get("full_dir"), recent_full_bck
                )
            )
        else:
            xtrabackup_inc_cmd_base += (
                " --target-dir={} --incremental-basedir={}/{} --backup".format(
                    inc_backup_dir, self.backup_options.get("inc_dir"), recent_inc_bck
                )
            )

        # Calling general options/command builder to add extra options
        xtrabackup_inc_cmd_base += self.general_command_builder()

        # Checking if streaming enabled for backups
        # There is no need to check for 'tar' streaming type -> see the method: stream_tar_incremental_checker()
        if (
            hasattr(self, "stream")
            and self.xbstream_options.get("stream") == "xbstream"
        ):
            xtrabackup_inc_cmd_base += '  --stream="{}"'.format(
                self.xbstream_options.get("stream")
            )
            xtrabackup_inc_cmd_base += " > {}/inc_backup.stream".format(inc_backup_dir)
            logger.warning("Streaming xbstream is enabled!")

        return xtrabackup_inc_cmd_base

    def decrypter(
        self,
        recent_full_bck: Optional[str] = None,
        xtrabackup_inc_cmd: Optional[str] = None,
        recent_inc_bck: Optional[str] = None,
    ) -> None:
        logger.info("Applying workaround for LP #1444255")
        logger.info("See more -> https://jira.percona.com/browse/PXB-934")
        # With recent PXB 8 it seems to be there is no need for this workaround.
        # Due to this moving this feature to this method and keeping just in case.
        # Deprecated as hell.
        if "encrypt" not in xtrabackup_inc_cmd:  # type: ignore
            return
        if not isfile(
            "{}/{}/xtrabackup_checkpoints.xbcrypt".format(
                self.backup_options.get("full_dir"), recent_full_bck
            )
        ):
            logger.info("Skipping...")
            return

        xbcrypt_command = "{} -d -k {} -a {}".format(
            self.encryption_options.get("xbcrypt"),
            self.encryption_options.get("encrypt_key"),
            self.encryption_options.get("encrypt"),
        )
        xbcrypt_command_extra = (
            " -i {}/{}/xtrabackup_checkpoints.xbcrypt -o {}/{}/xtrabackup_checkpoints"
        )
        xbcrypt_command += xbcrypt_command_extra.format(
            self.backup_options.get("full_dir"),
            recent_full_bck,
            self.backup_options.get("full_dir"),
            recent_full_bck,
        )

        if recent_inc_bck:
            if not isfile(
                "{}/{}/xtrabackup_checkpoints.xbcrypt".format(
                    self.backup_options.get("inc_dir"), recent_inc_bck
                )
            ):
                logger.info("Skipping...")
                return
            xbcrypt_command += xbcrypt_command_extra.format(
                self.backup_options.get("inc_dir"),
                recent_inc_bck,
                self.backup_options.get("inc_dir"),
                recent_inc_bck,
            )
        logger.info(
            "The following xbcrypt command will be executed {}".format(xbcrypt_command)
        )
        if self.dry == 0:
            ProcessRunner.run_command(xbcrypt_command)
