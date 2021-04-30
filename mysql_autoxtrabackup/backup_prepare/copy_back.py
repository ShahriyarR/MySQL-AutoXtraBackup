import logging
import os
import shutil
from typing import Optional
from typing import Union

from mysql_autoxtrabackup.general_conf import path_config
from mysql_autoxtrabackup.general_conf.generalops import GeneralClass
from mysql_autoxtrabackup.process_runner.process_runner import ProcessRunner
from mysql_autoxtrabackup.utils import helpers

logger = logging.getLogger(__name__)


class CopyBack:
    def __init__(self, config: str = path_config.config_path_file) -> None:
        self.conf = config
        options_obj = GeneralClass(config=self.conf)
        self.command_options = options_obj.command_options
        self.mysql_options = options_obj.backup_options
        self.backup_options = options_obj.backup_options

    def shutdown_mysql(self) -> Union[None, bool, Exception]:
        # Shut Down MySQL
        logger.info("Shutting Down MySQL server:")
        args = self.command_options.get("stop_mysql_command")
        return ProcessRunner.run_command(args)

    def move_to_tmp_dir(self) -> None:
        try:
            shutil.move(
                str(self.mysql_options.get("data_dir")),
                str(self.backup_options.get("tmp_dir")),
            )
            logger.info(
                "Moved data_dir to {} ...".format(self.backup_options.get("tmp_dir"))
            )
        except shutil.Error as err:
            logger.error("Error occurred while moving data_dir")
            logger.error(err)
            raise RuntimeError(err)

    def create_empty_data_dir(self) -> Union[None, bool, Exception]:
        logger.info("Creating an empty data directory ...")
        makedir = "mkdir {}".format(self.mysql_options.get("data_dir"))
        return ProcessRunner.run_command(makedir)

    def move_data_dir(self) -> bool:
        # Move data_dir to new directory
        tmp_dir = self.backup_options.get("tmp_dir")
        logger.info("Moving MySQL data_dir to {}".format(tmp_dir))
        if os.path.isdir(str(self.backup_options.get("tmp_dir"))):
            rmdir_ = "rm -rf {}".format(tmp_dir)
            ProcessRunner.run_command(rmdir_)
        self.move_to_tmp_dir()
        self.create_empty_data_dir()
        return True

    def run_xtra_copyback(self, data_dir: Optional[str] = None) -> Optional[bool]:
        # Running Xtrabackup with --copy-back option
        copy_back = "{} --copy-back {} --target-dir={}/{} --data_dir={}".format(
            self.backup_options.get("backup_tool"),
            self.backup_options.get("xtra_options"),
            self.backup_options.get("full_dir"),
            helpers.get_latest_dir_name(str(self.backup_options.get("full_dir"))),
            self.mysql_options.get("data_dir") if data_dir is None else data_dir,
        )
        return ProcessRunner.run_command(copy_back)

    def giving_chown(self, data_dir: Optional[str] = None) -> Optional[bool]:
        # Changing owner of data_dir to given user:group
        give_chown = "{} {}".format(
            self.command_options.get("chown_command"),
            self.mysql_options.get("data_dir") if data_dir is None else data_dir,
        )
        return ProcessRunner.run_command(give_chown)

    def start_mysql_func(
        self, start_tool: Optional[str] = None, options: Optional[str] = None
    ) -> Union[None, bool, Exception]:
        # Starting MySQL
        logger.info("Starting MySQL server: ")
        args = (
            self.command_options.get("start_mysql_command")
            if start_tool is None
            else start_tool
        )
        start_command = "{} {}".format(args, options) if options is not None else args
        return ProcessRunner.run_command(start_command)

    @staticmethod
    def check_if_backup_prepared(
        full_dir: Optional[str], full_backup_file: Optional[str]
    ) -> Optional[bool]:
        """
        This method is for checking if the backup can be copied-back.
        It is going to check xtrabackup_checkpoints file inside backup directory for backup_type column.
        backup_type column must be equal to 'full-prepared'
        :return: True if backup is already prepared; RuntimeError if it is not.
        """
        with open(
            "{}/{}/xtrabackup_checkpoints".format(full_dir, full_backup_file), "r"
        ) as xchk_file:
            # This thing seems to be complicated bu it is not:
            # Trying to get 'full-prepared' from ['backup_type ', ' full-prepared\n']
            if (
                xchk_file.readline().split("=")[1].strip("\n").lstrip()
                == "full-prepared"
            ):
                return True
            raise RuntimeError(
                "This full backup is not fully prepared, not doing copy-back!"
            )

    def copy(
        self, options: Optional[str] = None, data_dir: Optional[str] = None
    ) -> bool:
        """
        Function for running:
          xtrabackup --copy-back
          giving chown to data_dir
          starting mysql
        :return: True if succeeded. Error if failed
        """
        logger.info("Copying Back Already Prepared Final Backup:")
        if (
            len(
                os.listdir(
                    str(self.mysql_options.get("data_dir"))
                    if data_dir is None
                    else data_dir
                )
            )
            > 0
        ):
            logger.info("MySQL data_dir is not empty!")
            return False
        else:
            self.run_xtra_copyback(data_dir=data_dir)
            self.giving_chown(data_dir=data_dir)
            self.start_mysql_func(options=options)
            return True

    def copy_back_action(self, options: Optional[str] = None) -> Optional[bool]:
        """
        Function for complete recover/copy-back actions
        :return: True if succeeded. Error if failed.
        """
        try:
            self.check_if_backup_prepared(
                str(self.backup_options.get("full_dir")),
                helpers.get_latest_dir_name(str(self.backup_options.get("full_dir"))),
            )
            self.shutdown_mysql()
            if self.move_data_dir() and self.copy(options=options):
                logger.info("All data copied back successfully. ")
                logger.info("Your MySQL server is UP again")
                return True
        except Exception as err:
            logger.error("{}: {}".format(type(err).__name__, err))
        return None
