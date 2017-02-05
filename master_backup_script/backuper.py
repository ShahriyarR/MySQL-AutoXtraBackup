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
from os.path import join
from os import makedirs

import logging
logger = logging.getLogger(__name__)


# Creating Backup class



class Backup(GeneralClass):
    def __init__(self, config='/etc/bck.conf'):
        self.conf = config
        #Call GeneralClass for storing configuration
        GeneralClass.__init__(self, self.conf)

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
        new_backup_dir = join(directory, datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
        try:
            # Creating backup directory
            makedirs(new_backup_dir)
            return new_backup_dir
        except Exception as err:
            logger.error("Something went wrong in create_backup_directory(): {}".format(err))

    def recent_full_backup_file(self):
        # Return last full backup dir name

        if len(os.listdir(self.full_dir)) > 0:
            return max(os.listdir(self.full_dir))
        else:
            return 0

    def recent_inc_backup_file(self):
        # Return last increment backup dir name

        if len(os.listdir(self.inc_dir)) > 0:
            return max(os.listdir(self.inc_dir))
        else:
            return 0

    def mysql_connection_flush_logs(self):
        """
        It is highly recomended to flush binary logs before each full backup for easy maintenance.
        That's why we will execute "flush logs" command before each full backup!
        Also for security purposes you must create a MySQL user with only RELOAD privilege.
        I provide eg. create user statement:

        """

        # ############################################################
        # create user 'test_backup'@'127.0.0.1' identified by '12345';
        # grant all on bck.* to 'test_backup'@'127.0.0.1';
        # grant reload on *.* to 'test_backup'@'127.0.0.1';
        # ############################################################

        # Also create a test database for connection
        # create database bck;


        config = {

            'user': self.mysql_user,
            'password': self.mysql_password,
            # 'database': 'bck',
            'raise_on_warnings': True,
        }

        if hasattr(self, 'mysql_socket'):
            config['unix_socket'] = self.mysql_socket
        elif hasattr(self, 'mysql_host') and hasattr(self, 'mysql_port'):
            config['host'] = self.mysql_host
            config['port'] = self.mysql_port
        else:
            logger.critical("Neither mysql_socket nor mysql_host and mysql_port are defined in config!")

        # Open connection
        try:
            cnx = mysql.connector.connect(**config)
            cursor = cnx.cursor()
            query = "flush logs"
            logger.debug("Flushing Binary Logs")
            time.sleep(2)
            cursor.execute(query)
            cursor.close()
            cnx.close()
            return True
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                logger.error(err)
                logger.error("Something is wrong with your user name or password!!!!!")
                return False
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                logger.error(err)
                logger.error("Database does not exists")
                return False
            else:
                logger.debug(err)
                return False

    def create_backup_archives(self):

        # Creating .tar.gz archive files of taken backups
        for i in os.listdir(self.full_dir):
            rm_dir = self.full_dir + '/' + i
            if len(os.listdir(self.full_dir)) == 1 or i != max(os.listdir(self.full_dir)):
                run_tar = "/usr/bin/tar -zcf %s %s %s" % (self.archive_dir+'/'+i+'.tar.gz', self.full_dir, self.inc_dir)

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
            archive_date = datetime.strptime(archive, "%Y-%m-%d_%H-%M-%S.tar.gz")
            now = datetime.now()

            # Finding if last full backup older than the interval or more from now!

            if (now - archive_date).total_seconds() >= self.max_archive_duration:
                logger.debug("Removing archive: " + self.archive_dir+"/"+archive + " due to max archive age")
                os.remove(self.archive_dir+"/"+archive)
            elif self.get_directory_size(self.archive_dir) > self.max_archive_size:
                logger.debug("Removing archive: " + self.archive_dir + "/" + archive +
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
        logger.debug("########################################################################")
        logger.debug("Copying backups to remote server")
        logger.debug("########################################################################")
        copy_it = 'scp -r %s %s:%s' % (self.backupdir, self.remote_conn, self.remote_dir)
        copy_it = shlex.split(copy_it)
        cp = subprocess.Popen(copy_it, stdout=subprocess.PIPE)
        logger.debug(str(cp.stdout.read()))

    def full_backup(self):

        full_backup_dir = self.create_backup_directory(self.full_dir)

        # Taking Full backup with MySQL (Oracle)
        args = "%s --defaults-file=%s --user=%s --password='%s' " \
               " --target-dir=%s --backup" % (self.backup_tool,
                                              self.mycnf,
                                              self.mysql_user,
                                              self.mysql_password,
                                              full_backup_dir)

        if hasattr(self, 'mysql_socket'):
            args += " --socket=%s" %(self.mysql_socket)
        elif hasattr(self, 'mysql_host') and hasattr(self, 'mysql_port'):
            args += " --host=%s" % self.mysql_host
            args += " --port=%s" % self.mysql_port
        else:
            logger.critical("Neither mysql_socket nor mysql_host and mysql_port are defined in config!")
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

        logger.debug("The following backup command will be executed %s", args)

        logger.debug("Starting %s", self.backup_tool)
        status, output = subprocess.getstatusoutput(args)
        if status == 0:
            logger.debug(output[-27:])
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

        check_env_obj = CheckEnv()
        product_type = check_env_obj.check_mysql_product()

        # Creating time-stamped incremental backup directory
        inc_backup_dir = self.create_backup_directory(self.inc_dir)

        # Checking if there is any incremental backup

        if recent_inc == 0: # If there is no incremental backup

            # If you have a question why we check whether MariaDB or MySQL installed?
            # See BUG -> https://bugs.launchpad.net/percona-xtrabackup/+bug/1444541

            if product_type == 2:

                # Taking incremental backup with MariaDB. (--incremental-force-scan option will be added for BUG workaround)

                args = "%s --defaults-file=%s --user=%s --password='%s' " \
                       "--incremental-force-scan --incremental %s --incremental-basedir %s/%s" % \
                       (self.backup_tool,
                        self.mycnf,
                        self.mysql_user,
                        self.mysql_password,
                        self.inc_dir,
                        self.full_dir,
                        recent_bck)

            elif product_type == 3:
                # Taking incremental backup with MySQL.
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
                logger.critical("Neither mysql_socket nor mysql_host and mysql_port are defined in config!")
                return False

            # Adding compression support for incremental backup
            if hasattr(self, 'compress'):
                args += " --compress=%s" % (self.compress)
            if hasattr(self, 'compress_chunk_size'):
                args += " --compress-chunk-size=%s" % (self.compress_chunk_size)
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


            if 'encrypt' in args:
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
                logger.debug("The following xbcrypt command will be executed %s", xbcrypt_command)
                status, output = subprocess.getstatusoutput(xbcrypt_command)
                if status == 0:
                    logger.debug(output[-27:])
                else:
                    logger.error("XBCRYPT COMMAND FAILED!")
                    time.sleep(5)
                    logger.error(output)
                    return False

            logger.debug("The following backup command will be executed %s", args)
            status, output = subprocess.getstatusoutput(args)
            if status == 0:
                logger.debug(output[-27:])
                return True
            else:
                logger.error("INCREMENT BACKUP FAILED!")
                time.sleep(5)
                logger.error(output)
                return False

        else: # If there is already existing incremental backup

            if product_type == 2:

                # Taking incremental backup with MariaDB. (--incremental-force-scan option will be added for BUG workaround)

                args = "%s --defaults-file=%s  --user=%s --password='%s' " \
                       "--incremental-force-scan --incremental %s --incremental-basedir %s/%s" % \
                       (self.backup_tool,
                        self.mycnf,
                        self.mysql_user,
                        self.mysql_password,
                        self.inc_dir,
                        self.inc_dir,
                        recent_inc)

            elif product_type == 3:

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
                logger.critical("Neither mysql_socket nor mysql_host and mysql_port are defined in config!")
                return False

            # Adding compression support for incremental backup
            if hasattr(self, 'compress'):
                args += " --compress=%s" % (self.compress)
            if hasattr(self, 'compress_chunk_size'):
                args += " --compress_chunk_size=%s" % (self.compress_chunk_size)
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


            if 'encrypt' in args:
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
                logger.debug("The following xbcrypt command will be executed %s", xbcrypt_command)
                status, output = subprocess.getstatusoutput(xbcrypt_command)
                if status == 0:
                    logger.debug(output[-27:])
                else:
                    logger.error("XBCRYPT COMMAND FAILED!")
                    time.sleep(5)
                    logger.error(output)
                    return False

            logger.debug("The following backup command will be executed %s", args)

            status, output = subprocess.getstatusoutput(args)
            if status == 0:
                logger.debug(output[-27:])
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
                logger.debug("###############################################################")
                logger.debug("#You have no backups : Taking very first Full Backup! - - - - #")
                logger.debug("###############################################################")

                time.sleep(3)

                # Flushing Logs
                if self.mysql_connection_flush_logs():

                    # Taking fullbackup
                    if self.full_backup():
                        # Removing old inc backups
                        self.clean_inc_backup_dir()

                # Copying backups to remote server
                if hasattr(self, 'remote_conn') and hasattr(self,'remote_dir') and self.remote_conn and self.remote_dir:
                    self.copy_backup_to_remote_host()

                # Exiting after taking full backup
                exit(0)

            elif self.last_full_backup_date() == 1:
                logger.debug("################################################################")
                logger.debug("Your full backup is timeout : Taking new Full Backup!- - - - - #")
                logger.debug("################################################################")

                time.sleep(3)

                # Archiving backups
                if self.archive_dir:
                    if (hasattr(self, 'max_archive_duration') and self.max_archive_duration) or (
                                hasattr(self, 'max_archive_size') and self.max_archive_size):
                        self.clean_old_archives()
                    if not self.create_backup_archives():
                        exit(0)

                # Flushing logs
                if self.mysql_connection_flush_logs():

                    # Taking fullbackup
                    if self.full_backup():
                        # Removing full backups
                        self.clean_full_backup_dir()

                        # Removing inc backups
                        self.clean_inc_backup_dir()

                # Copying backups to remote server
                if hasattr(self, 'remote_conn') and hasattr(self,'remote_dir') and self.remote_conn and self.remote_dir:
                    self.copy_backup_to_remote_host()

                # Exiting after taking NEW full backup
                exit(0)

            else:
                logger.debug("################################################################")
                logger.debug("You have a full backup that is less than %d seconds old. - -#", self.full_backup_interval)
                logger.debug("We will take an incremental one based on recent Full Backup - -#")
                logger.debug("################################################################")

                time.sleep(3)

                # Taking incremental backup
                self.inc_backup()

                # Copying backups to remote server
                if hasattr(self, 'remote_conn') and hasattr(self,'remote_dir') and self.remote_conn and self.remote_dir:
                    self.copy_backup_to_remote_host()

                # Exiting after taking Incremental backup
                exit(0)

# b = Backup()
# b.all_backup()
