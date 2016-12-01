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
import re

import logging
logger = logging.getLogger(__name__)


# Creating Backup class



class Backup(GeneralClass):
    def __init__(self, *args, **kwargs):
        #Call GeneralClass for storing configuration
        GeneralClass.__init__(self, *args, **kwargs)

    def last_full_backup_date(self):
        # Finding last full backup date from dir/folder name

        max = self.recent_full_backup_file()
        dir_date_str = max[:4] + '-' + max[5:7] + '-' + max[8:10] + ' ' + max[11:13] + ':' + max[14:16]
        dir_date = datetime.strptime(dir_date_str, "%Y-%m-%d %H:%M")
        now = datetime.now().replace(second=0, microsecond=0)

        # Defining variables for comparison.

        a = '2013-09-04 15:29'
        b = '2013-09-03 15:29'
        a = datetime.strptime(a, "%Y-%m-%d %H:%M")
        b = datetime.strptime(b, "%Y-%m-%d %H:%M")
        diff = a - b

        # Finding if last full backup is 1 day or more from now!

        if now - dir_date >= diff:
            return 1
        else:
            return 0

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
            #'host': '127.0.0.1',
            # 'database': 'bck',
            'raise_on_warnings': True,
            'unix_socket': self.mysql_socket,
            #'port' : self.mysql_port,

        }

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
            if i != max(os.listdir(self.full_dir)):
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

        # Taking Full backup with MySQL (Oracle)

        args = "%s --defaults-file=%s  --port=%s --socket=%s --user=%s --password='%s'  %s" % (self.backup_tool,
                                                        self.mycnf,
                                                        self.mysql_port,
                                                        self.mysql_socket,
                                                        self.mysql_user,
                                                        self.mysql_password,
                                                        self.full_dir)

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

        # Workaround for circular import dependency error in Python
        from .check_env import CheckEnv
        check_env_obj = CheckEnv()
        product_type = check_env_obj.check_mysql_product()

        if recent_inc == 0:

            # If you have a question why we check whether MariaDB or MySQL installed?
            # See BUG -> https://bugs.launchpad.net/percona-xtrabackup/+bug/1444541

            if product_type == 2:

                # Taking incremental backup with MariaDB. (--incremental-force-scan option will be added for BUG workaround)

                args = "%s --defaults-file=%s  --port=%s --socket=%s --user=%s --password='%s' --incremental-force-scan --incremental %s --incremental-basedir %s/%s" % \
                       (self.backup_tool,
                        self.mycnf,
                        self.mysql_port,
                        self.mysql_socket,
                        self.mysql_user,
                        self.mysql_password,
                        self.inc_dir,
                        self.full_dir,
                        recent_bck)

            elif product_type == 3:

                args = "%s --defaults-file=%s  --port=%s --socket=%s --user=%s --password='%s' --incremental %s --incremental-basedir %s/%s" % \
                       (self.backup_tool,
                        self.mycnf,
                        self.mysql_port,
                        self.mysql_socket,
                        self.mysql_user,
                        self.mysql_password,
                        self.inc_dir,
                        self.full_dir,
                        recent_bck)

            status, output = subprocess.getstatusoutput(args)
            if status == 0:
                logger.debug(output[-27:])
                return True
            else:
                logger.error("INCREMENT BACKUP FAILED!")
                time.sleep(5)
                logger.error(output)
                return False

        else:

            if product_type == 2:

                # Taking incremental backup with MariaDB. (--incremental-force-scan option will be added for BUG workaround)

                args = "%s --defaults-file=%s  --port=%s --socket=%s --user=%s --password='%s' --incremental-force-scan --incremental %s --incremental-basedir %s/%s" % \
                       (self.backup_tool,
                        self.mycnf,
                        self.mysql_port,
                        self.mysql_socket,
                        self.mysql_user,
                        self.mysql_password,
                        self.inc_dir,
                        self.inc_dir,
                        recent_inc)

            elif product_type == 3:

                args = "%s --defaults-file=%s  --port=%s --socket=%s --user=%s --password='%s'  --incremental %s --incremental-basedir %s/%s" % \
                       (self.backup_tool,
                        self.mycnf,
                        self.mysql_port,
                        self.mysql_socket,
                        self.mysql_user,
                        self.mysql_password,
                        self.inc_dir,
                        self.inc_dir,
                        recent_inc)

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
        from .check_env import CheckEnv

        # Creating object from CheckEnv class
        check_env_obj = CheckEnv()

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
                # self.copy_backup_to_remote_host()

                # Exiting after taking full backup
                exit(0)

            elif self.last_full_backup_date() == 1:
                logger.debug("################################################################")
                logger.debug("Your full backup is timeout : Taking new Full Backup!- - - - - #")
                logger.debug("################################################################")

                time.sleep(3)

                # Flushing logs
                if self.mysql_connection_flush_logs():

                    # Taking fullbackup
                    if self.full_backup():
                        # Archiving backups
                        if self.archive_dir:
                            if not self.create_backup_archives():
                                exit(0)
                        # Removing full backups
                        self.clean_full_backup_dir()

                        # Removing inc backups
                        self.clean_inc_backup_dir()

                # Copying backups to remote server
                # self.copy_backup_to_remote_host()

                # Exiting after taking NEW full backup
                exit(0)

            else:
                logger.debug("################################################################")
                logger.debug("You have a full backup. - - - - - - - - - - - - - - - - - - - -#")
                logger.debug("We will take an incremental one based on recent Full Backup - -#")
                logger.debug("################################################################")

                time.sleep(3)

                # Taking incremental backup
                self.inc_backup()

                # Copying backups to remote server
                # self.copy_backup_to_remote_host()

                # Exiting after taking Incremental backup
                exit(0)

# b = Backup()
# b.all_backup()
