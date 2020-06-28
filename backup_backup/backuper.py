# MySQL Backuper Script using Percona Xtrabackup
# Originally Developed by
# Shahriyar Rzayev (Shako)-> https://mysql.az/ https://azepug.az/
# / rzayev.sehriyar@gmail.com / rzayev.shahriyar@yandex.com


import logging
import os
import shutil
import time
from datetime import datetime

from general_conf import path_config
from general_conf.generalops import GeneralClass
from general_conf.check_env import CheckEnv
from process_runner.process_runner import ProcessRunner
from utils import helpers, mysql_cli

logger = logging.getLogger(__name__)


class Backup:

    def __init__(self, config: str = path_config.config_path_file, dry_run: int = 0, tag: str = None) -> None:
        self.conf = config
        self.dry = dry_run
        self.tag = tag
        self.mysql_cli = mysql_cli.MySQLClientHelper(config=self.conf)
        options_obj = GeneralClass(config=self.conf)
        self.backup_options = options_obj.backup_options

    def add_tag(self, backup_type: str, backup_size: str, backup_status: str) -> bool:
        """
        Method for adding backup tags
        :param backup_type: The backup type - Full/Inc
        :param backup_size: The size of the backup in human readable format
        :param backup_status: Status: OK or Status: Failed
        :return: True if no exception
        """
        # skip tagging unless self.tag
        if not self.tag:
            logger.info("TAGGING SKIPPED")
            return True

        # Currently only support Inc and Full types, calculate name based on this
        assert backup_type in ('Full', 'Inc'), "add_tag(): backup_type {}: must be 'Full' or 'Inc'".format(backup_type)
        backup_name = helpers.get_latest_dir_name(self.backup_options.get('full_dir')) if backup_type == 'Full' else \
            helpers.get_latest_dir_name(self.backup_options.get('inc_dir'))

        # Calculate more tag fields, create string
        backup_timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        backup_tag_str = "{bk_name}\t{bk_type}\t{bk_status}\t{bk_timestamp}\t{bk_size}\t'{bk_tag}'\n"

        # Apply tag
        with open('{}/backup_tags.txt'.format(self.backup_options.get('backup_dir')), 'a') as backup_tags_file:
            backup_tag_final = backup_tag_str.format(bk_name=backup_name,
                                                     bk_type=backup_type,
                                                     bk_status=backup_status,
                                                     bk_timestamp=backup_timestamp,
                                                     bk_size=backup_size,
                                                     bk_tag=self.tag)

            backup_tags_file.write(backup_tag_final)
        return True

    @staticmethod
    def show_tags(backup_dir: str) -> None:
        if os.path.isfile("{}/backup_tags.txt".format(backup_dir)):
            with open('{}/backup_tags.txt'.format(backup_dir), 'r') as backup_tags:
                from_file = backup_tags.read()
            column_names = "{0}\t{1}\t{2}\t{3}\t{4}\tTAG\n".format(
                "Backup".ljust(19),
                "Type".ljust(4),
                "Status".ljust(2),
                "Completion_time".ljust(19),
                "Size")
            extra_str = "{}\n".format("-" * (len(column_names) + 21))
            print(column_names + extra_str + from_file)
            logger.info(column_names + extra_str + from_file)
        else:
            logger.warning("Could not find backup_tags.txt inside given backup directory. Can't print tags.")
            print("WARNING: Could not find backup_tags.txt inside given backup directory. Can't print tags.")

    def last_full_backup_date(self) -> bool:
        """
        Check if last full backup date retired or not.
        :return: 1 if last full backup date older than given interval, 0 if it is newer.
        """
        # Finding last full backup date from dir/folder name
        max_dir = helpers.get_latest_dir_name(self.backup_options.get('full_dir'))
        dir_date = datetime.strptime(max_dir, "%Y-%m-%d_%H-%M-%S")
        now = datetime.now()
        return (now - dir_date).total_seconds() >= self.backup_options.get('full_backup_interval')

    def clean_full_backup_dir(self):
        # Deleting old full backup after taking new full backup.
        # Keeping the latest in order not to lose everything.
        logger.info("starting clean_full_backup_dir")
        full_dir = self.backup_options.get('full_dir')
        if not os.path.isdir(full_dir):
            return
        for i in os.listdir(full_dir):
            rm_dir = full_dir + '/' + i
            if i != max(os.listdir(full_dir)):
                shutil.rmtree(rm_dir)
                logger.info("DELETING {}".format(rm_dir))
            else:
                logger.info("KEEPING {}".format(rm_dir))

    def clean_inc_backup_dir(self):
        # Deleting incremental backups after taking new fresh full backup.
        inc_dir = self.backup_options.get('inc_dir')
        for i in os.listdir(inc_dir):
            rm_dir = inc_dir + '/' + i
            shutil.rmtree(rm_dir)

    def full_backup(self):
        """
        Method for taking full backups. It will construct the backup command based on config file.
        :return: True on success.
        :raise:  RuntimeError on error.
        """
        logger.info("starting full backup to {}".format(self.full_dir))
        full_backup_dir = helpers.create_backup_directory(self.full_dir)

        # Taking Full backup
        xtrabackup_cmd = "{} --defaults-file={} --user={} --password={} " \
                         " --target-dir={} --backup".format(
                            self.backup_tool,
                            self.mycnf,
                            self.mysql_user,
                            self.mysql_password,
                            full_backup_dir)

        # Calling general options/command builder to add extra options
        xtrabackup_cmd += self.general_command_builder()
        # Extra checks
        self.stream_encrypt_compress_tar_checker()

        if hasattr(self, 'stream'):
            xtrabackup_cmd += ' --stream="{}"'.format(self.stream)
            if self.stream == 'xbstream':
                xtrabackup_cmd += " > {}/full_backup.stream".format(full_backup_dir)
                logger.warning("Streaming xbstream is enabled!")
            elif self.stream == 'tar':
                xtrabackup_cmd += " > {}/full_backup.tar".format(full_backup_dir)
                logger.warning("Streaming tar is enabled!")

        if self.dry == 1:
            # If it's a dry run, skip running & tagging
            return True

        logger.debug("Starting {}".format(self.backup_tool))
        status = ProcessRunner.run_command(xtrabackup_cmd)
        status_str = 'OK' if status is True else 'FAILED'
        self.add_tag(backup_type='Full',
                     backup_size=helpers.get_folder_size(full_backup_dir),
                     backup_status=status_str)
        return status

    def inc_backup(self):
        """
        Method for taking incremental backups.
        :return: True on success.
        :raise: RuntimeError on error.
        """
        # Get the recent full backup path
        recent_full_bck = helpers.get_latest_dir_name(self.full_dir)
        # Get the recent incremental backup path
        recent_inc_bck = helpers.get_latest_dir_name(self.inc_dir)

        # Creating time-stamped incremental backup directory
        inc_backup_dir = helpers.create_backup_directory(self.inc_dir)

        # Check here if stream=tar enabled.
        # Because it is impossible to take incremental backup with streaming tar.
        # raise RuntimeError.
        self.stream_tar_incremental_checker()

        # Checking if there is any incremental backup

        if not recent_inc_bck:  # If there is no incremental backup

            # Taking incremental backup.
            xtrabackup_inc_cmd = "{} --defaults-file={} --user={} --password={} " \
                                 "--target-dir={} --incremental-basedir={}/{} --backup".format(
                                    self.backup_tool,
                                    self.mycnf,
                                    self.mysql_user,
                                    self.mysql_password,
                                    inc_backup_dir,
                                    self.full_dir,
                                    recent_full_bck)

            # Calling general options/command builder to add extra options
            xtrabackup_inc_cmd += self.general_command_builder()

            self.extract_decrypt_from_stream_backup(recent_full_bck=recent_full_bck)

            # Deprecated workaround for LP #1444255
            # Disabled the call here but will keep in any case
            self.decrypter(recent_full_bck=recent_full_bck, xtrabackup_inc_cmd=xtrabackup_inc_cmd)

        else:  # If there is already existing incremental backup
            xtrabackup_inc_cmd = "{} --defaults-file={} --user={} --password={}  " \
                                 "--target-dir={} --incremental-basedir={}/{} --backup".format(
                                  self.backup_tool,
                                  self.mycnf,
                                  self.mysql_user,
                                  self.mysql_password,
                                  inc_backup_dir,
                                  self.inc_dir,
                                  recent_inc_bck)

            # Calling general options/command builder to add extra options
            xtrabackup_inc_cmd += self.general_command_builder()

            self.extract_decrypt_from_stream_backup(recent_inc_bck=recent_inc_bck)

            # Deprecated workaround for LP #1444255
            # Disabled the call here but will keep in any case
            self.decrypter(recent_full_bck=recent_full_bck, xtrabackup_inc_cmd=xtrabackup_inc_cmd,
                           recent_inc_bck=recent_inc_bck)

        # Checking if streaming enabled for backups
        # There is no need to check for 'tar' streaming type -> see the method: stream_tar_incremental_checker()
        if hasattr(self, 'stream') and self.stream == 'xbstream':
            xtrabackup_inc_cmd += '  --stream="{}"'.format(self.stream)
            xtrabackup_inc_cmd += " > {}/inc_backup.stream".format(inc_backup_dir)
            logger.warning("Streaming xbstream is enabled!")

        if self.dry == 1:
            # If it's a dry run, skip running & tagging
            return True

        logger.debug("Starting {}".format(self.backup_tool))
        status = ProcessRunner.run_command(xtrabackup_inc_cmd)
        status_str = 'OK' if status is True else 'FAILED'
        self.add_tag(backup_type='Inc',
                     backup_size=helpers.get_folder_size(inc_backup_dir),
                     backup_status=status_str)
        return status

    def all_backup(self):
        """
         This method at first checks full backup directory, if it is empty takes full backup.
         If it is not empty then checks for full backup time.
         If the recent full backup  is taken 1 day ago, it takes full backup.
         In any other conditions it takes incremental backup.
        """
        # Workaround for circular import dependency error in Python

        # Creating object from CheckEnv class
        check_env_obj = CheckEnv(self.conf, full_dir=self.full_dir, inc_dir=self.inc_dir)

        assert check_env_obj.check_all_env() is True, "environment checks failed!"
        if not helpers.get_latest_dir_name(self.full_dir):
            logger.info("- - - - You have no backups : Taking very first Full Backup! - - - -")

            if self.mysql_cli.mysql_run_command("flush logs") and self.full_backup():
                # Removing old inc backups
                self.clean_inc_backup_dir()

        elif self.last_full_backup_date():
            logger.info("- - - - Your full backup is timeout : Taking new Full Backup! - - - -")

            # Archiving backups
            if hasattr(self, 'archive_dir'):
                logger.info("Archiving enabled; cleaning archive_dir & archiving previous Full Backup")
                if (hasattr(self, 'archive_max_duration') and self.archive_max_duration) \
                        or (hasattr(self, 'archive_max_size') and self.archive_max_size):
                    self.clean_old_archives()
                self.create_backup_archives()
            else:
                logger.info("Archiving disabled. Skipping!")

            if self.mysql_cli.mysql_run_command("flush logs") and self.full_backup():
                # Removing full backups
                self.clean_full_backup_dir()

                # Removing inc backups
                self.clean_inc_backup_dir()

        else:

            logger.info("- - - - You have a full backup that is less than {} seconds old. - - - -".format(
                self.full_backup_interval))
            logger.info("- - - - We will take an incremental one based on recent Full Backup - - - -")

            time.sleep(3)

            # Taking incremental backup
            self.inc_backup()

        return True
