# MySQL Backuper Script using Percona Xtrabackup
# Originally Developed by
# Shahriyar Rzayev -> http://www.mysql.az
# / rzayev.sehriyar@gmail.com / rzayev.shahriyar@yandex.com


import logging
import os
import subprocess
import shlex
import shutil
import time

from datetime import datetime
from os.path import join, isfile
from os import makedirs

from general_conf import path_config
from general_conf.generalops import GeneralClass
from general_conf.check_env import CheckEnv
from backup_prepare.prepare import Prepare
from process_runner.process_runner import ProcessRunner

logger = logging.getLogger(__name__)


class Backup(GeneralClass):

    def __init__(self, config=path_config.config_path_file, dry_run=0, tag=None):
        self.conf = config
        self.dry = dry_run
        self.tag = tag
        # Call GeneralClass for storing configuration options
        super().__init__(self.conf)

    def add_tag(self, backup_type: str, backup_size: str, backup_status: str):
        """
        Method for adding backup tags
        :param backup_type: The backup type - Full/Inc
        :param backup_size: The size of the backup in human readab
        le format
        :param backup_status: Status: OK or Status: Failed
        :return: True if no exception
        """
        # skip tagging unless self.tag
        if not self.tag:
            logger.info("TAGGING SKIPPED")
            return True

        # Currently only support Inc and Full types, calculate name based on this
        assert backup_type in ('Full', 'Inc'), "add_tag(): backup_type {}: must be 'Full' or 'Inc'".format(backup_type)
        backup_name = self.recent_full_backup_file() if backup_type == 'Full' else self.recent_inc_backup_file()

        # Calculate more tag fields, create string
        backup_timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        backtag_str = "{bk_name}\t{bk_type}\t{bk_status}\t{bk_timestamp}\t{bk_size}\t'{bk_tag}'\n"

        # Apply tag
        with open('{}/backup_tags.txt'.format(self.backupdir), 'a') as backtags_file:
            backtag_final = backtag_str.format(bk_name=backup_name,
                                               bk_type=backup_type,
                                               bk_status=backup_status,
                                               bk_timestamp=backup_timestamp,
                                               bk_size=backup_size,
                                               bk_tag=self.tag)

            backtags_file.write(backtag_final)
        return True

    @staticmethod
    def get_folder_size(path):
        """
        Static method to calculate given folder size. Using 'du' command here.
        :param path: The full path to be calculated
        :return: String with human readable size info, for eg, 5.3M
        """
        du_cmd = 'du -hs {}'.format(path)
        status, output = subprocess.getstatusoutput(du_cmd)
        if status == 0:
            return output.split()[0]
        else:
            logger.error("Failed to get the folder size")
            return False

    @staticmethod
    def show_tags(backup_dir):
        if os.path.isfile("{}/backup_tags.txt".format(backup_dir)):
            with open('{}/backup_tags.txt'.format(backup_dir), 'r') as bcktags:
                from_file = bcktags.read()
            column_names = "{0}\t{1}\t{2}\t{3}\t{4}\tTAG\n".format(
                "Backup".ljust(19),
                "Type".ljust(4),
                "Status".ljust(2),
                "Completion_time".ljust(19),
                "Size")
            extra_str = "{}\n".format("-"*(len(column_names)+21))
            print(column_names + extra_str + from_file)
            logger.info(column_names + extra_str + from_file)
        else:
            logger.warning("Could not find backup_tags.txt inside given backup directory. Can't print tags.")
            print("WARNING: Could not find backup_tags.txt inside given backup directory. Can't print tags.")

    @staticmethod
    def sorted_ls(path):
        """
        Static Method for sorting given path
        :param path: Directory path
        :return: The list of sorted directories
        """
        mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
        return list(sorted(os.listdir(path), key=mtime))

    @staticmethod
    def get_directory_size(path):
        """
        Calculate total size of given directory path
        :param path: Directory path
        :return: Total size of directory
        """
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size

    def last_full_backup_date(self):
        """
        Check if last full backup date retired or not.
        :return: 1 if last full backup date older than given interval, 0 if it is newer.
        """
        # Finding last full backup date from dir/folder name

        max_dir = self.recent_full_backup_file()
        dir_date = datetime.strptime(max_dir, "%Y-%m-%d_%H-%M-%S")
        now = datetime.now()

        # Finding if last full backup older than the interval or more from now!

        if (now - dir_date).total_seconds() >= self.full_backup_interval:
            return 1
        else:
            return 0

    @staticmethod
    def create_backup_directory(directory):
        """
        Static method for creating timestamped directory on given path
        :param directory: Directory path
        :return: Created new directory path
        """
        new_backup_dir = join(directory, datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
        try:
            # Creating backup directory
            makedirs(new_backup_dir)
            return new_backup_dir
        except Exception as err:
            logger.error("Something went wrong in create_backup_directory(): {}".format(err))
            raise RuntimeError("Something went wrong in create_backup_directory(): {}".format(err))

    def recent_full_backup_file(self):
        # Return last full backup dir name

        if len(os.listdir(self.full_dir)) > 0:
            return max(os.listdir(self.full_dir))
        return 0

    def recent_inc_backup_file(self):
        # Return last increment backup dir name

        if len(os.listdir(self.inc_dir)) > 0:
            return max(os.listdir(self.inc_dir))
        return 0

    def mysql_connection_flush_logs(self):
        """
        It is highly recommended to flush binary logs before each full backup for easy maintenance.
        That's why we will execute "flush logs" command before each full backup!
        :return: True on success.
        :raise: RuntimeError on error.
        """
        if hasattr(self, 'mysql_socket'):
            command_connection = "{} --defaults-file={} -u{} --password='{}' "
            command_execute = ' -e "flush logs"'
        else:
            command_connection = "{} --defaults-file={} -u{} --password='{}' --host={}"
            command_execute = ' -e "flush logs"'

        # Open connection

        if hasattr(self, 'mysql_socket'):
            command_connection += ' --socket={}'
            command_connection += command_execute
            new_command = command_connection.format(
                self.mysql,
                self.mycnf,
                self.mysql_user,
                self.mysql_password,
                self.mysql_socket)
        else:
            command_connection += ' --port={}'
            command_connection += command_execute
            new_command = command_connection.format(
                self.mysql,
                self.mycnf,
                self.mysql_user,
                self.mysql_password,
                self.mysql_host,
                self.mysql_port)
        logger.info("Trying to flush logs")
        status, output = subprocess.getstatusoutput(new_command)

        if status == 0:
            logger.info("OK: Log flushing completed")
            return True
        else:
            logger.error("FAILED: Log flushing")
            logger.error(output)
            raise RuntimeError("FAILED: Log flushing -> {}".format(output))

    def create_backup_archives(self):
        # Creating .tar.gz archive files of taken backups
        for i in os.listdir(self.full_dir):
            if len(os.listdir(self.full_dir)) == 1 or i != max(os.listdir(self.full_dir)):
                logger.info("Preparing backups prior archiving them...")

                if hasattr(self, 'prepare_archive'):
                    logger.info("Started to prepare backups, prior archiving!")
                    prepare_obj = Prepare(config=self.conf, dry_run=self.dry, tag=self.tag)
                    status = prepare_obj.prepare_inc_full_backups()
                    if status:
                        logger.info("Backups Prepared successfully...".format(status))

                if hasattr(self, 'move_archive') and (int(self.move_archive) == 1):
                    dir_name = self.archive_dir + '/' + i + '_archive'
                    logger.info("move_archive enabled. Moving {} to {}".format(self.backupdir, dir_name))
                    try:
                        shutil.copytree(self.backupdir, dir_name)
                    except Exception as err:
                        logger.error("FAILED: Move Archive")
                        logger.error(err)
                        raise
                    else:
                        return True
                else:
                    logger.info("move_archive is disabled. archiving / compressing current_backup.")
                    # Multi-core tar utilizing pigz.

                    # Pigz default to number of cores available, or 8 if cannot be read.

                    # Test if pigz is available.
                    logger.info("testing for pigz...")
                    status = ProcessRunner.run_command("pigz --version")
                    archive_file = self.archive_dir + '/' + i + '.tar.gz'
                    if status:
                        logger.info("Found pigz...")
                        # run_tar = "tar cvvf - {} {} | pigz -v > {}" \
                        run_tar = "tar --use-compress-program=pigz -cvf {} {} {}" \
                            .format(archive_file, self.full_dir, self.inc_dir)
                    else:
                        # handle file not found error.
                        logger.warning("pigz executeable not available. Defaulting to singlecore tar")
                        run_tar = "tar -zcf {} {} {}"\
                            .format(archive_file, self.full_dir, self.inc_dir)
                    status = ProcessRunner.run_command(run_tar)
                    if status:
                        logger.info("OK: Old full backup and incremental backups archived!")
                        return True
                    else:
                        logger.error("FAILED: Archiving ")
                        raise RuntimeError("FAILED: Archiving -> {}".format(run_tar))

    def clean_old_archives(self):
        logger.info("Starting cleaning of old archives")
        for archive in self.sorted_ls(self.archive_dir):
            if '_archive' in archive:
                archive_date = datetime.strptime(
                    archive, "%Y-%m-%d_%H-%M-%S_archive")
            else:
                archive_date = datetime.strptime(
                    archive, "%Y-%m-%d_%H-%M-%S.tar.gz")

            now = datetime.now()

            # Finding if last full backup older than the interval or more from
            # now!
            cleanup_msg = "Removing archive {}/{} due to {}"
            if hasattr(self, 'archive_max_duration') and (now - archive_date).total_seconds() >= self.archive_max_duration:
                logger.info(cleanup_msg.format(self.archive_dir, archive, 'archive_max_duration exceeded.'))
                if os.path.isdir(self.archive_dir + "/" + archive):
                    shutil.rmtree(self.archive_dir + "/" + archive)
                else:
                    os.remove(self.archive_dir + "/" + archive)
            elif hasattr(self, 'archive_max_size') and self.get_directory_size(self.archive_dir) > self.archive_max_size:
                logger.info(cleanup_msg.format(self.archive_dir, archive, 'archive_max_size exceeded.'))
                if os.path.isdir(self.archive_dir + "/" + archive):
                    shutil.rmtree(self.archive_dir + "/" + archive)
                else:
                    os.remove(self.archive_dir + "/" + archive)

    def clean_full_backup_dir(self):
        # Deleting old full backup after taking new full backup.
        logger.info("starting clean_full_backup_dir")
        for i in os.listdir(self.full_dir):
            rm_dir = self.full_dir + '/' + i
            if i != max(os.listdir(self.full_dir)):
                shutil.rmtree(rm_dir)
                logger.info("DELETING {}".format(rm_dir))
            else:
                logger.info("KEEPING {}".format(rm_dir))

    def clean_inc_backup_dir(self):
        # Deleting incremental backups after taking new fresh full backup.
        for i in os.listdir(self.inc_dir):
            rm_dir = self.inc_dir + '/' + i
            shutil.rmtree(rm_dir)

    def copy_backup_to_remote_host(self):
        # Copying backup directory to remote server
        logger.info("- - - - Copying backups to remote server - - - -")

        copy_it = 'scp -r {} {}:{}'.format(self.backupdir, self.remote_conn, self.remote_dir)
        copy_it = shlex.split(copy_it)
        cp = subprocess.Popen(copy_it, stdout=subprocess.PIPE)
        logger.info(str(cp.stdout.read()))

    def general_command_builder(self):
        """
        Method for building general options for backup command.
        :return: String of constructed options.
        """
        args = ""

        if hasattr(self, 'mysql_socket'):
            args += " --socket={}".format(self.mysql_socket)
        elif hasattr(self, 'mysql_host') and hasattr(self, 'mysql_port'):
            args += " --host={}".format(self.mysql_host)
            args += " --port={}".format(self.mysql_port)
        else:
            logger.critical("Neither mysql_socket nor mysql_host and mysql_port are defined in config!")
            raise RuntimeError("Neither mysql_socket nor mysql_host and mysql_port are defined in config!")

        # Adding compression support for backup
        try:
            args += " --compress={}" \
                    " --compress-chunk-size={}" \
                    " --compress-threads={}".format(self.compress,
                                                    self.compress_chunk_size,
                                                    self.compress_threads)
        except AttributeError:
            pass

        # Adding encryption support for full backup
        try:
            args += " --encrypt={}" \
                    " --encrypt-key={}" \
                    " --encrypt-key-file={}" \
                    " --encrypt-threads={}" \
                    " --encrypt-chunk-size={}".format(self.encrypt,
                                                      self.encrypt_key,
                                                      self.encrypt_key_file,
                                                      self.encrypt_threads,
                                                      self.encrypt_chunk_size)
        except AttributeError:
            pass

        # Checking if extra options were passed:
        try:
            args += " {}".format(self.xtra_options)
        except AttributeError:
            pass

        # Checking if extra backup options were passed:
        try:
            args += " {}".format(self.xtra_backup)
        except AttributeError:
            pass

        # Checking if partial recovery list is available
        try:
            args += ' --databases="{}"'.format(self.partial_list)
            logger.warning("Partial Backup is enabled!")
        except AttributeError:
            pass

        return args

    def full_backup(self):
        """
        Method for taking full backups. It will construct the backup command based on config file.
        :return: True on success.
        :raise:  RuntimeError on error.
        """
        logger.info("starting full backup to {}".format(self.full_dir))
        full_backup_dir = self.create_backup_directory(self.full_dir)

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

        # Checking if streaming enabled for backups
        if hasattr(self, 'stream') and self.stream == 'xbstream':
            xtrabackup_cmd += " "
            xtrabackup_cmd += '--stream="{}"'.format(self.stream)
            xtrabackup_cmd += " > {}/full_backup.stream".format(full_backup_dir)
            logger.warning("Streaming xbstream is enabled!")
        elif hasattr(self, 'stream') and self.stream == 'tar' and \
                (hasattr(self, 'encrypt') or hasattr(self, 'compress')):
            logger.error("xtrabackup: error: compressed and encrypted backups are "
                         "incompatible with the 'tar' streaming format. Use --stream=xbstream instead.")
            raise RuntimeError("xtrabackup: error: compressed and encrypted backups are "
                               "incompatible with the 'tar' streaming format. Use --stream=xbstream instead.")
        elif hasattr(self, 'stream') and self.stream == 'tar':
            xtrabackup_cmd += " "
            xtrabackup_cmd += '--stream="{}"'.format(self.stream)
            xtrabackup_cmd += " > {}/full_backup.tar".format(full_backup_dir)
            logger.warning("Streaming tar is enabled!")

        if self.dry == 1:
            # If it's a dry run, skip running & tagging
            return True

        # do the xtrabackup
        logger.debug("Starting {}".format(self.backup_tool))
        status = ProcessRunner.run_command(xtrabackup_cmd)
        status_str = 'OK' if status is True else 'FAILED'
        self.add_tag(backup_type='Full',
                     backup_size=self.get_folder_size(full_backup_dir),
                     backup_status=status_str)
        return status

    def inc_backup(self):
        """
        Method for taking incremental backups.
        :return: True on success.
        :raise: RuntimeError on error.
        """
        # Get the recent full backup path
        recent_bck = self.recent_full_backup_file()
        # Get the recent incremental backup path
        recent_inc = self.recent_inc_backup_file()

        # Creating time-stamped incremental backup directory
        inc_backup_dir = self.create_backup_directory(self.inc_dir)

        # Checking if there is any incremental backup

        if recent_inc == 0:  # If there is no incremental backup

            # Taking incremental backup.
            xtrabackup_inc_cmd = "{} --defaults-file={} --user={} --password={} " \
                   "--target-dir={} --incremental-basedir={}/{} --backup".format(
                    self.backup_tool,
                    self.mycnf,
                    self.mysql_user,
                    self.mysql_password,
                    inc_backup_dir,
                    self.full_dir,
                    recent_bck)

            # Calling general options/command builder to add extra options
            xtrabackup_inc_cmd += self.general_command_builder()

            # Check here if stream=tar enabled.
            # Because it is impossible to take incremental backup with streaming tar.
            # raise RuntimeError.
            if hasattr(self, 'stream') and self.stream == 'tar':
                logger.error("xtrabackup: error: streaming incremental backups are incompatible with the "
                             "'tar' streaming format. Use --stream=xbstream instead.")
                raise RuntimeError("xtrabackup: error: streaming incremental backups are incompatible with the "
                                   "'tar' streaming format. Use --stream=xbstream instead.")

            # Extract and decrypt streamed full backup prior to executing incremental backup
            if hasattr(self, 'stream') and self.stream == 'xbstream' \
                    and hasattr(self, 'encrypt') and hasattr(self, 'xbs_decrypt'):
                logger.info("Using xbstream to extract and decrypt from full_backup.stream!")
                xbstream_command = "{} {} --decrypt={} --encrypt-key={} --encrypt-threads={} " \
                                   "< {}/{}/full_backup.stream -C {}/{}".format(
                                    self.xbstream,
                                    self.xbstream_options,
                                    self.decrypt,
                                    self.encrypt_key,
                                    self.encrypt_threads,
                                    self.full_dir,
                                    recent_bck,
                                    self.full_dir,
                                    recent_bck)

                logger.info("The following xbstream command will be executed {}".format(xbstream_command))
                if self.dry == 0 and isfile("{}/{}/full_backup.stream".format(self.full_dir, recent_bck)):
                    status, output = subprocess.getstatusoutput(xbstream_command)
                    if status == 0:
                        logger.info("OK: XBSTREAM command succeeded.")
                    else:
                        logger.error("FAILED: XBSTREAM COMMAND")
                        logger.error(output)
                        raise RuntimeError("FAILED: XBSTREAM COMMAND")

            # Extract streamed full backup prior to executing incremental backup
            elif hasattr(self, 'stream') and self.stream == 'xbstream':
                logger.info("Using xbstream to extract from full_backup.stream!")
                xbstream_command = "{} {} < {}/{}/full_backup.stream -C {}/{}".format(
                    self.xbstream,
                    self.xbstream_options,
                    self.full_dir,
                    recent_bck,
                    self.full_dir,
                    recent_bck)

                logger.info("The following xbstream command will be executed {}".format(xbstream_command))

                if self.dry == 0 and isfile("{}/{}/full_backup.stream".format(self.full_dir, recent_bck)):
                    status, output = subprocess.getstatusoutput(xbstream_command)
                    if status == 0:
                        logger.info("OK: XBSTREAM command succeeded.")
                    else:
                        logger.error("FAILED: XBSTREAM command")
                        logger.error(output)
                        raise RuntimeError("FAILED: XBSTREAM command")

            elif 'encrypt' in xtrabackup_inc_cmd:
                logger.info("Applying workaround for LP #1444255")
                xbcrypt_command = "{} -d -k {} -a {} -i {}/{}/xtrabackup_checkpoints.xbcrypt " \
                                  "-o {}/{}/xtrabackup_checkpoints".format(
                                   self.xbcrypt,
                                   self.encrypt_key,
                                   self.encrypt,
                                   self.full_dir,
                                   recent_bck,
                                   self.full_dir,
                                   recent_bck)
                logger.info("The following xbcrypt command will be executed {}".format(xbcrypt_command))

                if self.dry == 0:
                    status, output = subprocess.getstatusoutput(xbcrypt_command)
                    if status == 0:
                        logger.info(output[-27:])
                    else:
                        logger.error("FAILED: XBCRYPT command")
                        logger.error(output)
                        raise RuntimeError("FAILED: XBCRYPT command")

            # Checking if streaming enabled for backups
            if hasattr(self, 'stream') and self.stream == 'xbstream':
                xtrabackup_inc_cmd += " "
                xtrabackup_inc_cmd += '--stream="{}"'.format(self.stream)
                xtrabackup_inc_cmd += " > {}/inc_backup.stream".format(inc_backup_dir)
                logger.warning("Streaming xbstream is enabled!")
            elif hasattr(self, 'stream') and self.stream == 'tar':
                logger.error("xtrabackup: error: streaming incremental backups are incompatible with the "
                             "'tar' streaming format. Use --stream=xbstream instead.")
                raise RuntimeError("xtrabackup: error: streaming incremental backups are incompatible with the "
                                   "'tar' streaming format. Use --stream=xbstream instead.")

            if self.dry == 0:
                logger.info("Starting {}".format(self.backup_tool))
                status = ProcessRunner.run_command(xtrabackup_inc_cmd)
                status_str = 'OK' if status is True else 'FAILED'
                self.add_tag(backup_type='Inc',
                             backup_size=self.get_folder_size(inc_backup_dir),
                             backup_status=status_str)
                return status

        else:  # If there is already existing incremental backup

            xtrabackup_inc_cmd = "{} --defaults-file={} --user={} --password={}  " \
                   "--target-dir={} --incremental-basedir={}/{} --backup".format(
                    self.backup_tool,
                    self.mycnf,
                    self.mysql_user,
                    self.mysql_password,
                    inc_backup_dir,
                    self.inc_dir,
                    recent_inc)

            # Calling general options/command builder to add extra options
            xtrabackup_inc_cmd += self.general_command_builder()

            # Check here if stream=tar enabled.
            # Because it is impossible to take incremental backup with streaming tar.
            # raise RuntimeError.
            if hasattr(self, 'stream') and self.stream == 'tar':
                logger.error("xtrabackup: error: streaming incremental backups are incompatible with the "
                             "'tar' streaming format. Use --stream=xbstream instead.")
                raise RuntimeError("xtrabackup: error: streaming incremental backups are incompatible with the "
                                   "'tar' streaming format. Use --stream=xbstream instead.")

            # Extract and decrypt streamed full backup prior to executing incremental backup
            if hasattr(self, 'stream') \
                    and hasattr(self, 'encrypt') \
                    and hasattr(self, 'xbs_decrypt'):
                logger.info("Using xbstream to extract and decrypt from inc_backup.stream!")
                xbstream_command = "{} {} --decrypt={} --encrypt-key={} --encrypt-threads={} " \
                                   "< {}/{}/inc_backup.stream -C {}/{}".format(
                                       self.xbstream,
                                       self.xbstream_options,
                                       self.decrypt,
                                       self.encrypt_key,
                                       self.encrypt_threads,
                                       self.inc_dir,
                                       recent_inc,
                                       self.inc_dir,
                                       recent_inc)

                logger.info("The following xbstream command will be executed {}".format(xbstream_command))
                if self.dry == 0 and isfile("{}/{}/inc_backup.stream".format(self.inc_dir, recent_inc)):
                    status, output = subprocess.getstatusoutput(xbstream_command)
                    if status == 0:
                        logger.info("OK: XBSTREAM command succeeded.")
                    else:
                        logger.error("FAILED: XBSTREAM command.")
                        logger.error(output)
                        raise RuntimeError("FAILED: XBSTREAM command.")

            # Extracting streamed incremental backup prior to executing new incremental backup

            elif hasattr(self, 'stream'):
                logger.info("Using xbstream to extract from inc_backup.stream!")
                xbstream_command = "{} {} < {}/{}/inc_backup.stream -C {}/{}".format(
                    self.xbstream,
                    self.xbstream_options,
                    self.inc_dir,
                    recent_inc,
                    self.inc_dir,
                    recent_inc)

                logger.info("The following xbstream command will be executed {}".format(xbstream_command))

                if self.dry == 0 and isfile("{}/{}/inc_backup.stream".format(self.full_dir, recent_bck)):
                    status, output = subprocess.getstatusoutput(xbstream_command)
                    if status == 0:
                        logger.info("OK: XBSTREAM command succeeded.")
                    else:
                        logger.error("FAILED: XBSTREAM command.")
                        logger.error(output)
                        raise RuntimeError("FAILED: XBSTREAM command.")

            elif 'encrypt' in xtrabackup_inc_cmd:
                logger.info("Applying workaround for LP #1444255")
                xbcrypt_command = "{} -d -k {} -a {} -i {}/{}/xtrabackup_checkpoints.xbcrypt " \
                                  "-o {}/{}/xtrabackup_checkpoints".format(
                                   self.xbcrypt,
                                   self.encrypt_key,
                                   self.encrypt,
                                   self.inc_dir,
                                   recent_inc,
                                   self.inc_dir,
                                   recent_inc)
                logger.info("The following xbcrypt command will be executed {}".format(xbcrypt_command))
                if self.dry == 0:
                    status, output = subprocess.getstatusoutput(xbcrypt_command)
                    if status == 0:
                        logger.info(output[-27:])
                    else:
                        logger.error("FAILED: XBCRYPT command")
                        logger.error(output)
                        raise RuntimeError("FAILED: XBCRYPT command")

            # Checking if streaming enabled for backups
            if hasattr(self, 'stream'):
                xtrabackup_inc_cmd += " "
                xtrabackup_inc_cmd += '--stream="{}"'.format(self.stream)
                xtrabackup_inc_cmd += " > {}/inc_backup.stream".format(inc_backup_dir)
                logger.warning("Streaming is enabled!")

            if self.dry == 0:
                logger.debug("Starting {}".format(self.backup_tool))
                status = ProcessRunner.run_command(xtrabackup_inc_cmd)
                status_str = 'OK' if status is True else 'FAILED'
                self.add_tag(backup_type='Inc',
                             backup_size=self.get_folder_size(inc_backup_dir),
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
        if self.recent_full_backup_file() == 0:
            logger.info("- - - - You have no backups : Taking very first Full Backup! - - - -")

            # Flushing Logs
            if self.mysql_connection_flush_logs():

                # Taking fullbackup
                if self.full_backup():
                    # Removing old inc backups
                    self.clean_inc_backup_dir()

            # Copying backups to remote server
            if hasattr(self, 'remote_conn') and hasattr(self, 'remote_dir') \
                    and self.remote_conn and self.remote_dir:
                self.copy_backup_to_remote_host()

            return True

        elif self.last_full_backup_date() == 1:
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

            # Flushing logs
            if self.mysql_connection_flush_logs():

                # Taking fullbackup
                if self.full_backup():
                    # Removing full backups
                    self.clean_full_backup_dir()

                    # Removing inc backups
                    self.clean_inc_backup_dir()

            # Copying backups to remote server
            if hasattr(self, 'remote_conn') and hasattr(self, 'remote_dir') \
                    and self.remote_conn and self.remote_dir:
                self.copy_backup_to_remote_host()

            return True
        else:

            logger.info("- - - - You have a full backup that is less than {} seconds old. - - - -".format(
                self.full_backup_interval))
            logger.info("- - - - We will take an incremental one based on recent Full Backup - - - -")

            time.sleep(3)

            # Taking incremental backup
            self.inc_backup()

            # Copying backups to remote server
            if hasattr(self, 'remote_conn') and hasattr(self, 'remote_dir') \
                    and self.remote_conn and self.remote_dir:
                self.copy_backup_to_remote_host()

            return True
