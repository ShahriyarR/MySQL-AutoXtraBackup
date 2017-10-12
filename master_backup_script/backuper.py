#!/opt/Python-3.3.2/bin/python3

# MySQL Backuper Script using Percona Xtrabackup
# Originally Developed by
# Shahriyar Rzayev -> http://www.mysql.az
# / rzayev.sehriyar@gmail.com / rzayev.shahriyar@yandex.com


import os
import subprocess
import shlex
import shutil
import mysql.connector
import time
from datetime import datetime
from mysql.connector import errorcode
from sys import exit
from general_conf.generalops import GeneralClass
from general_conf.check_env import CheckEnv
from os.path import join, isfile
from os import makedirs

import logging
logger = logging.getLogger(__name__)


# Creating Backup class


class Backup(GeneralClass):

    def __init__(self, config='/etc/bck.conf', dry_run=0):
        self.conf = config
        self.dry = dry_run
        # Call GeneralClass for storing configuration
        super().__init__(self.conf)
        #GeneralClass.__init__(self, self.conf)

    def sorted_ls(self, path):
        mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
        return list(sorted(os.listdir(path), key=mtime))

    def get_directory_size(self, path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size

    def last_full_backup_date(self):
        # Finding last full backup date from dir/folder name

        max = self.recent_full_backup_file()
        dir_date = datetime.strptime(max, "%Y-%m-%d_%H-%M-%S")
        now = datetime.now()

        # Finding if last full backup older than the interval or more from now!

        if (now - dir_date).total_seconds() >= self.full_backup_interval:
            return 1
        else:
            return 0

    def create_backup_directory(self, directory):
        new_backup_dir = join(
            directory, datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
        try:
            # Creating backup directory
            makedirs(new_backup_dir)
            return new_backup_dir
        except Exception as err:
            logger.error(
                "Something went wrong in create_backup_directory(): {}".format(err))

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
        It is highly recomended to flush binary logs before each full backup for easy maintenance.
        That's why we will execute "flush logs" command before each full backup!
        """
        if hasattr(self, 'mysql_socket'):
            command_connection = '{} --defaults-file={} -u{} --password={}'
            command_execute = ' -e "flush logs"'
        else:
            command_connection = '{} --defaults-file={} -u{} --password={} --host={}'
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
                #self.mysql_host,
                self.mysql_socket
            )
        else:
            command_connection += ' --port={}'
            command_connection += command_execute
            new_command = command_connection.format(
                self.mysql,
                self.mycnf,
                self.mysql_user,
                self.mysql_password,
                self.mysql_host,
                self.mysql_port
            )
        logger.debug("Trying to flush logs")
        status, output = subprocess.getstatusoutput(new_command)

        if status == 0:
            logger.debug("Log flushing completed")
            return True
        else:
            logger.error("Log flushing FAILED!")
            time.sleep(5)
            logger.error(output)
            return False


    def create_backup_archives(self):
        # Creating .tar.gz archive files of taken backups
        for i in os.listdir(self.full_dir):
            rm_dir = self.full_dir + '/' + i
            if len(
                os.listdir(
                    self.full_dir)) == 1 or i != max(
                os.listdir(
                    self.full_dir)):
                run_tar = "/usr/bin/tar -zcf %s %s %s" % (
                    self.archive_dir + '/' + i + '.tar.gz', self.full_dir, self.inc_dir)

        logger.debug("Start to archive previous backups")
        status, output = subprocess.getstatusoutput(run_tar)
        if status == 0:
            logger.debug("Old full backup and incremental backups archived!")
            return True
        else:
            logger.error("Archiving FAILED!")
            time.sleep(5)
            logger.error(output)
            return False

    def clean_old_archives(self):
        logger.debug("Starting cleaning of old archives")
        for archive in self.sorted_ls(self.archive_dir):
            archive_date = datetime.strptime(
                archive, "%Y-%m-%d_%H-%M-%S.tar.gz")
            now = datetime.now()

            # Finding if last full backup older than the interval or more from
            # now!

            if (now - archive_date).total_seconds() >= self.max_archive_duration:
                logger.debug(
                    "Removing archive: " +
                    self.archive_dir +
                    "/" +
                    archive +
                    " due to max archive age")
                os.remove(self.archive_dir + "/" + archive)
            elif self.get_directory_size(self.archive_dir) > self.max_archive_size:
                logger.debug(
                    "Removing archive: " +
                    self.archive_dir +
                    "/" +
                    archive +
                    " due to max archive size")
                os.remove(self.archive_dir + "/" + archive)

    def clean_full_backup_dir(self):
        # Deleting old full backup after taking new full backup.

        for i in os.listdir(self.full_dir):
            rm_dir = self.full_dir + '/' + i
            if i != max(os.listdir(self.full_dir)):
                shutil.rmtree(rm_dir)

    def clean_inc_backup_dir(self):
        # Deleting incremental backups after taking new fresh full backup.

        for i in os.listdir(self.inc_dir):
            rm_dir = self.inc_dir + '/' + i
            shutil.rmtree(rm_dir)

    def copy_backup_to_remote_host(self):
        # Copying backup directory to remote server
        logger.debug(
            "########################################################################")
        logger.debug("Copying backups to remote server")
        logger.debug(
            "########################################################################")
        copy_it = 'scp -r %s %s:%s' % (self.backupdir,
                                       self.remote_conn, self.remote_dir)
        copy_it = shlex.split(copy_it)
        cp = subprocess.Popen(copy_it, stdout=subprocess.PIPE)
        logger.debug(str(cp.stdout.read()))

    def full_backup(self):

        full_backup_dir = self.create_backup_directory(self.full_dir)

        # Taking Full backup
        args = "%s --defaults-file=%s --user=%s --password='%s' " \
               " --target-dir=%s --backup" % (self.backup_tool,
                                              self.mycnf,
                                              self.mysql_user,
                                              self.mysql_password,
                                              full_backup_dir)

        if hasattr(self, 'mysql_socket'):
            args += " --socket=%s" % (self.mysql_socket)
        elif hasattr(self, 'mysql_host') and hasattr(self, 'mysql_port'):
            args += " --host=%s" % self.mysql_host
            args += " --port=%s" % self.mysql_port
        else:
            logger.critical(
                "Neither mysql_socket nor mysql_host and mysql_port are defined in config!")
            return False

        # Adding compression support for full backup
        if hasattr(self, 'compress'):
            args += " --compress=%s" % (self.compress)
        if hasattr(self, 'compress_chunk_size'):
            args += " --compress-chunk-size=%s" % (self.compress_chunk_size)
        if hasattr(self, 'compress_threads'):
            args += " --compress-threads=%s" % (self.compress_threads)

        # Adding encryption support for full backup
        if hasattr(self, 'encrypt'):
            args += " --encrypt=%s" % (self.encrypt)
        if hasattr(self, 'encrypt_key'):
            args += " --encrypt-key=%s" % (self.encrypt_key)
        if hasattr(self, 'encrypt_key_file'):
            args += " --encrypt-key-file=%s" % (self.encrypt_key_file)
        if hasattr(self, 'encrypt_threads'):
            args += " --encrypt-threads=%s" % (self.encrypt_threads)
        if hasattr(self, 'encrypt_chunk_size'):
            args += " --encrypt-chunk-size=%s" % (self.encrypt_chunk_size)

        # Checking if extra options were passed:
        if hasattr(self, 'xtra_options'):
            args += " "
            args += self.xtra_options

        # Checking if extra backup options were passed:
        if hasattr(self, 'xtra_backup'):
            args += " "
            args += self.xtra_backup

        # Checking if partial recovery list is available
        if hasattr(self, 'partial_list'):
            args += " "
            args += '--databases="%s"' % self.partial_list
            logger.warning("Partial Backup is enabled!")

        # Checking if streaming enabled for backups
        if hasattr(self, 'stream'):
            args += " "
            args += '--stream="%s"' % self.stream
            args += " > %s/full_backup.stream" % full_backup_dir
            logger.warning("Streaming is enabled!")

        logger.debug("The following backup command will be executed %s", args)

        if self.dry == 0:
            logger.debug("Starting %s", self.backup_tool)
            status, output = subprocess.getstatusoutput(args)
            if status == 0:
                logger.debug(output)
                #logger.debug(output[-27:])
                return True
            else:
                logger.error("FULL BACKUP FAILED!")
                time.sleep(5)
                logger.error(output)
                return False


    def inc_backup(self):

        # Taking Incremental backup

        recent_bck = self.recent_full_backup_file()
        recent_inc = self.recent_inc_backup_file()

        check_env_obj = CheckEnv(self.conf)

        # Creating time-stamped incremental backup directory
        inc_backup_dir = self.create_backup_directory(self.inc_dir)

        # Checking if there is any incremental backup

        if recent_inc == 0:  # If there is no incremental backup

            # Taking incremental backup.
            args = "%s --defaults-file=%s --user=%s --password='%s' " \
                   "--target-dir=%s --incremental-basedir=%s/%s --backup" % \
                   (self.backup_tool,
                    self.mycnf,
                    self.mysql_user,
                    self.mysql_password,
                    inc_backup_dir,
                    self.full_dir,
                    recent_bck)

            if hasattr(self, 'mysql_socket'):
                args += " --socket=%s" % (self.mysql_socket)
            elif hasattr(self, 'mysql_host') and hasattr(self, 'mysql_port'):
                args += " --host=%s" % self.mysql_host
                args += " --port=%s" % self.mysql_port
            else:
                logger.critical(
                    "Neither mysql_socket nor mysql_host and mysql_port are not defined in config!")
                return False

            # Adding compression support for incremental backup
            if hasattr(self, 'compress'):
                args += " --compress=%s" % (self.compress)
            if hasattr(self, 'compress_chunk_size'):
                args += " --compress-chunk-size=%s" % (
                    self.compress_chunk_size)
            if hasattr(self, 'compress_threads'):
                args += " --compress-threads=%s" % (self.compress_threads)

            # Adding encryption support for incremental backup
            if hasattr(self, 'encrypt'):
                args += " --encrypt=%s" % (self.encrypt)
            if hasattr(self, 'encrypt_key'):
                args += " --encrypt-key=%s" % (self.encrypt_key)
            if hasattr(self, 'encrypt_key_file'):
                args += " --encrypt_key_file=%s" % (self.encrypt_key_file)
            if hasattr(self, 'encrypt_threads'):
                args += " --encrypt-threads=%s" % (self.encrypt_threads)
            if hasattr(self, 'encrypt_chunk_size'):
                args += " --encrypt-chunk-size=%s" % (self.encrypt_chunk_size)

            # Extract and decrypt streamed full backup prior to executing incremental backup
            if hasattr(self, 'stream') \
                                       and hasattr(self, 'encrypt') \
                                       and hasattr(self, 'xbs_decrypt'):
                logger.debug("Using xbstream to extract and decrypt from full_backup.stream!")
                xbstream_command = "%s %s --decrypt=%s --encrypt-key=%s --encrypt-threads=%s " \
                                   "< %s/%s/full_backup.stream -C %s/%s" % (
                                    self.xbstream,
                                    self.xbstream_options,
                                    self.decrypt,
                                    self.encrypt_key,
                                    self.encrypt_threads,
                                    self.full_dir,
                                    recent_bck,
                                    self.full_dir,
                                    recent_bck
                                )

                logger.debug(
                    "The following xbstream command will be executed %s",
                    xbstream_command)
                if self.dry == 0 and isfile(("%s/%s/full_backup.stream") % (self.full_dir, recent_bck)):
                    status, output = subprocess.getstatusoutput(xbstream_command)
                    if status == 0:
                        logger.debug("XBSTREAM command succeeded.")
                    else:
                        logger.error("XBSTREAM COMMAND FAILED!")
                        time.sleep(5)
                        logger.error(output)
                        return False

            # Extract streamed full backup prior to executing incremental backup
            elif hasattr(self, 'stream'):
                logger.debug("Using xbstream to extract from full_backup.stream!")
                xbstream_command = "%s %s < %s/%s/full_backup.stream -C %s/%s" % (
                    self.xbstream,
                    self.xbstream_options,
                    self.full_dir,
                    recent_bck,
                    self.full_dir,
                    recent_bck
                )

                logger.debug(
                    "The following xbstream command will be executed %s",
                xbstream_command)

                if self.dry == 0 and isfile(("%s/%s/full_backup.stream") % (self.full_dir, recent_bck)):
                    status, output = subprocess.getstatusoutput(xbstream_command)
                    if status == 0:
                        logger.debug("XBSTREAM command succeeded.")
                    else:
                        logger.error("XBSTREAM COMMAND FAILED!")
                        time.sleep(5)
                        logger.error(output)
                        return False

            elif 'encrypt' in args:
                logger.debug("Applying workaround for LP #1444255")
                xbcrypt_command = "%s -d -k %s -a %s -i %s/%s/xtrabackup_checkpoints.xbcrypt " \
                                  "-o %s/%s/xtrabackup_checkpoints" % \
                                  (self.xbcrypt,
                                   self.encrypt_key,
                                   self.encrypt,
                                   self.full_dir,
                                   recent_bck,
                                   self.full_dir,
                                   recent_bck)
                logger.debug(
                    "The following xbcrypt command will be executed %s",
                    xbcrypt_command)

                if self.dry == 0:
                    status, output = subprocess.getstatusoutput(xbcrypt_command)
                    if status == 0:
                        logger.debug(output[-27:])
                    else:
                        logger.error("XBCRYPT COMMAND FAILED!")
                        time.sleep(5)
                        logger.error(output)
                        return False

            # Checking if extra options were passed:
            if hasattr(self, 'xtra_options'):
                args += " "
                args += self.xtra_options

            # Checking if extra backup options were passed:
            if hasattr(self, 'xtra_backup'):
                args += " "
                args += self.xtra_backup

            # Checking if partial recovery list is available
            if hasattr(self, 'partial_list'):
               args += " "
               args += '--databases="%s"' % (self.partial_list)
               logger.warning("Partial Backup is enabled!")

            # Checking if streaming enabled for backups
            if hasattr(self, 'stream'):
               args += " "
               args += '--stream="%s"' % self.stream
               args += " > %s/inc_backup.stream" % inc_backup_dir
               logger.warning("Streaming is enabled!")

            logger.debug(
                "The following backup command will be executed %s", args)
            if self.dry == 0:
                status, output = subprocess.getstatusoutput(args)
                if status == 0:
                    logger.debug(output)
                    #logger.debug(output[-27:])
                    return True
                else:
                    logger.error("INCREMENT BACKUP FAILED!")
                    time.sleep(5)
                    logger.error(output)
                    return False

        else:  # If there is already existing incremental backup

            args = "%s --defaults-file=%s --user=%s --password='%s'  " \
                   "--target-dir=%s --incremental-basedir=%s/%s --backup" % \
                   (self.backup_tool,
                    self.mycnf,
                    self.mysql_user,
                    self.mysql_password,
                    inc_backup_dir,
                    self.inc_dir,
                    recent_inc)

            if hasattr(self, 'mysql_socket'):
                args += " --socket=%s" % (self.mysql_socket)
            elif hasattr(self, 'mysql_host') and hasattr(self, 'mysql_port'):
                args += " --host=%s" % self.mysql_host
                args += " --port=%s" % self.mysql_port
            else:
                logger.critical(
                    "Neither mysql_socket nor mysql_host and mysql_port are defined in config!")
                return False

            # Adding compression support for incremental backup
            if hasattr(self, 'compress'):
                args += " --compress=%s" % (self.compress)
            if hasattr(self, 'compress_chunk_size'):
                args += " --compress_chunk_size=%s" % (
                    self.compress_chunk_size)
            if hasattr(self, 'compress-threads'):
                args += " --compress_threads=%s" % (self.compress_threads)

            # Adding encryption support for incremental backup
            if hasattr(self, 'encrypt'):
                args += " --encrypt=%s" % (self.encrypt)
            if hasattr(self, 'encrypt_key'):
                args += " --encrypt-key=%s" % (self.encrypt_key)
            if hasattr(self, 'encrypt_key_file'):
                args += " --encrypt-key-file=%s" % (self.encrypt_key_file)
            if hasattr(self, 'encrypt_threads'):
                args += " --encrypt-threads=%s" % (self.encrypt_threads)
            if hasattr(self, 'encrypt_chunk_size'):
                args += " --encrypt-chunk-size=%s" % (self.encrypt_chunk_size)

            # Extract and decrypt streamed full backup prior to executing incremental backup
            if hasattr(self, 'stream') \
                    and hasattr(self, 'encrypt') \
                    and hasattr(self, 'xbs_decrypt'):
                logger.debug("Using xbstream to extract and decrypt from inc_backup.stream!")
                xbstream_command = "%s %s --decrypt=%s --encrypt-key=%s --encrypt-threads=%s " \
                                   "< %s/%s/inc_backup.stream -C %s/%s" % (
                                       self.xbstream,
                                       self.xbstream_options,
                                       self.decrypt,
                                       self.encrypt_key,
                                       self.encrypt_threads,
                                       self.inc_dir,
                                       recent_inc,
                                       self.inc_dir,
                                       recent_inc
                                   )

                logger.debug(
                    "The following xbstream command will be executed %s",
                    xbstream_command)
                if self.dry == 0 and isfile(("%s/%s/inc_backup.stream") % (self.inc_dir, recent_inc)):
                    status, output = subprocess.getstatusoutput(xbstream_command)
                    if status == 0:
                        logger.debug("XBSTREAM command succeeded.")
                    else:
                        logger.error("XBSTREAM COMMAND FAILED!")
                        time.sleep(5)
                        logger.error(output)
                        return False

            # Extracting streamed incremental backup prior to executing new incremental backup

            elif hasattr(self, 'stream'):
                logger.debug("Using xbstream to extract from inc_backup.stream!")
                xbstream_command = "%s %s < %s/%s/inc_backup.stream -C %s/%s" % (
                    self.xbstream,
                    self.xbstream_options,
                    self.inc_dir,
                    recent_inc,
                    self.inc_dir,
                    recent_inc
                )

                logger.debug(
                    "The following xbstream command will be executed %s",
                    xbstream_command)

                if self.dry == 0 and isfile(("%s/%s/inc_backup.stream") % (self.full_dir, recent_bck)):
                    status, output = subprocess.getstatusoutput(xbstream_command)
                    if status == 0:
                        logger.debug("XBSTREAM command succeeded.")
                    else:
                        logger.error("XBSTREAM COMMAND FAILED!")
                        time.sleep(5)
                        logger.error(output)
                        return False

            elif 'encrypt' in args:
                logger.debug("Applying workaround for LP #1444255")
                xbcrypt_command = "%s -d -k %s -a %s -i %s/%s/xtrabackup_checkpoints.xbcrypt " \
                                  "-o %s/%s/xtrabackup_checkpoints" % \
                                  (self.xbcrypt,
                                   self.encrypt_key,
                                   self.encrypt,
                                   self.inc_dir,
                                   recent_inc,
                                   self.inc_dir,
                                   recent_inc)
                logger.debug(
                    "The following xbcrypt command will be executed %s",
                    xbcrypt_command)
                if self.dry == 0:
                    status, output = subprocess.getstatusoutput(xbcrypt_command)
                    if status == 0:
                        logger.debug(output[-27:])
                    else:
                        logger.error("XBCRYPT COMMAND FAILED!")
                        time.sleep(5)
                        logger.error(output)
                        return False

            # Checking if extra options were passed:
            if hasattr(self, 'xtra_options'):
                args += " "
                args += self.xtra_options

            # Checking if extra backup options were passed:
            if hasattr(self, 'xtra_backup'):
                args += " "
                args += self.xtra_backup

            # Checking if partial recovery list is available
            if hasattr(self, 'partial_list'):
               args += " "
               args += '--databases="%s"' % (self.partial_list)
               logger.warning("Partial Backup is enabled!")

           # Checking if streaming enabled for backups
            if hasattr(self, 'stream'):
               args += " "
               args += '--stream="%s"' % self.stream
               args += " > %s/inc_backup.stream" % inc_backup_dir
               logger.warning("Streaming is enabled!")

            logger.debug(
                "The following backup command will be executed %s", args)

            if self.dry == 0:
                status, output = subprocess.getstatusoutput(args)
                if status == 0:
                    logger.debug(output)
                    #logger.debug(output[-27:])
                    return True
                else:
                    logger.error("INCREMENT BACKUP FAILED!")
                    time.sleep(5)
                    logger.error(output)
                    return False

    def all_backup(self):
        """
         This function at first checks full backup directory, if it is empty takes full backup.
         If it is not empty then checks for full backup time.
         If the recent full backup  is taken 1 day ago, it takes full backup.
         In any other conditions it takes incremental backup.
        """
        # Workaround for circular import dependency error in Python

        # Creating object from CheckEnv class
        check_env_obj = CheckEnv(self.conf)

        if check_env_obj.check_all_env():

            if self.recent_full_backup_file() == 0:
                logger.debug(
                    "###############################################################")
                logger.debug(
                    "#You have no backups : Taking very first Full Backup! - - - - #")
                logger.debug(
                    "###############################################################")

                time.sleep(3)

                # Flushing Logs
                if self.mysql_connection_flush_logs():

                    # Taking fullbackup
                    if self.full_backup():
                        # Removing old inc backups
                        self.clean_inc_backup_dir()

                # Copying backups to remote server
                if hasattr(
                        self,
                        'remote_conn') and hasattr(
                        self,
                        'remote_dir') and self.remote_conn and self.remote_dir:
                    self.copy_backup_to_remote_host()

                # Exiting after taking full backup
                #exit(0)

            elif self.last_full_backup_date() == 1:
                logger.debug(
                    "################################################################")
                logger.debug(
                    "Your full backup is timeout : Taking new Full Backup!- - - - - #")
                logger.debug(
                    "################################################################")

                time.sleep(3)

                # Archiving backups
                if (hasattr(self, 'archive_dir')):
                    if (hasattr(self, 'max_archive_duration') and self.max_archive_duration) or (
                            hasattr(self, 'max_archive_size') and self.max_archive_size):
                        self.clean_old_archives()
                    if not self.create_backup_archives():
                        exit(0)
                else:
                    logger.debug("Archiving disabled. Skipping!")

                # Flushing logs
                if self.mysql_connection_flush_logs():

                    # Taking fullbackup
                    if self.full_backup():
                        # Removing full backups
                        self.clean_full_backup_dir()

                        # Removing inc backups
                        self.clean_inc_backup_dir()

                # Copying backups to remote server
                if hasattr(
                        self,
                        'remote_conn') and hasattr(
                        self,
                        'remote_dir') and self.remote_conn and self.remote_dir:
                    self.copy_backup_to_remote_host()

                # Exiting after taking NEW full backup
                #exit(0)

            else:
                logger.debug(
                    "################################################################")
                logger.debug(
                    "You have a full backup that is less than %d seconds old. - -#",
                    self.full_backup_interval)
                logger.debug(
                    "We will take an incremental one based on recent Full Backup - -#")
                logger.debug(
                    "################################################################")

                time.sleep(3)

                # Taking incremental backup
                self.inc_backup()

                # Copying backups to remote server
                if hasattr(
                        self,
                        'remote_conn') and hasattr(
                        self,
                        'remote_dir') and self.remote_conn and self.remote_dir:
                    self.copy_backup_to_remote_host()

                # Exiting after taking Incremental backup
                #exit(0)

# b = Backup()
# b.all_backup()
