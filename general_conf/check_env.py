#!/opt/Python-3.3.2/bin/python3

import shlex
import subprocess
import os
import time
from general_conf.generalops import GeneralClass

import logging
logger = logging.getLogger(__name__)


class CheckEnv(GeneralClass):

    def __init__(self, config='/etc/bck.conf'):
        self.conf = config
        GeneralClass.__init__(self, self.conf)

    def check_mysql_uptime(self):

        statusargs = '%s --user=%s --password=%s status' % (
            self.mysqladmin, self.mysql_user, self.mysql_password)

        if hasattr(self, 'mysql_socket'):
            statusargs += " --socket=%s" % (self.mysql_socket)
        elif hasattr(self, 'mysql_host') and hasattr(self, 'mysql_port'):
            statusargs += " --host=%s" % self.mysql_host
            statusargs += " --port=%s" % self.mysql_port
        else:
            logger.critical(
                "Neither mysql_socket nor mysql_host and mysql_port are defined in config!")
            return False

        statusargs = shlex.split(statusargs)
        myadmin = subprocess.Popen(statusargs, stdout=subprocess.PIPE)

        if not ('Uptime' in str(myadmin.stdout.read())):
            logger.error(
                'Server is NOT Up+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+')
            return False
        else:
            logger.debug(
                'Server is Up and running+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+OK')
            return True

    def check_mysql_conf(self):
        if not os.path.exists(self.mycnf):
            # Testing with MariaDB Galera Cluster
            # if not os.path.exists(self.maria_cluster_cnf):
            logger.error(
                'MySQL configuration file path does NOT exist+-+-+-+-+-+-+-+-+-+')
            return False
        else:
            logger.debug(
                'MySQL configuration file exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+OK')
            return True

    def check_mysql_mysql(self):
        if not os.path.exists(self.mysql):
            logger.error(
                '/usr/bin/mysql NOT exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-+')
            return False
        else:
            logger.debug(
                '/usr/bin/mysql exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-++-OK')
            return True

    def check_mysql_mysqladmin(self):
        if not os.path.exists(self.mysqladmin):
            logger.error(
                '/usr/bin/mysqladmin NOT exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-')
            return False
        else:
            logger.debug(
                '/usr/bin/mysqladmin exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK')
            return True

    def check_mysql_backuptool(self):
        if not os.path.exists(self.backup_tool):
            logger.error(
                'Xtrabackup/Innobackupex NOT exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-')
            return False
        else:
            logger.debug(
                'Xtrabackup/Innobackupex exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-OK')
            return True

    def check_mysql_backupdir(self):

        if not (os.path.exists(self.backupdir)):
            try:
                logger.debug(
                    'Main backup directory does not exist+-+-+-+-+-+-+-+-+-++-+-+-+-')
                logger.debug(
                    'Creating Main Backup folder+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+')
                os.makedirs(self.backupdir)
                logger.debug(
                    'Created+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK')
                return True
            except Exception as err:
                logger.error(err)
                return False
        else:
            logger.debug(
                'Main backup directory exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-OK')
            return True

    def check_mysql_archive_dir(self):

        if not (os.path.exists(self.archive_dir)):
            try:
                logger.debug(
                    'Archive backup directory does not exist+-+-+-+-+-+-+-+-+-++-+-+-+-')
                logger.debug(
                    'Creating archive folder+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+')
                os.makedirs(self.archive_dir)
                logger.debug(
                    'Created+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK')
                return True
            except Exception as err:
                logger.error(err)
                return False
        else:
            logger.debug(
                'Archive folder directory exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-OK')
            return True

    def check_mysql_fullbackupdir(self):

        if not (os.path.exists(self.full_dir)):
            try:
                logger.debug(
                    'Full Backup directory does not exist.+-+-+-+-+-+-+-+-+-+-+-+-OK')
                logger.debug(
                    'Creating full backup directory...+-+-+-+-+-+-+-+-+-++-+-+-+-+OK')
                os.makedirs(self.backupdir + '/full')
                logger.debug(
                    'Created+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK')
                return True
            except Exception as err:
                logger.error(err)
                return False
        else:
            logger.debug(
                "Full Backup directory exists.+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+OK")
            return True

    def check_mysql_incbackupdir(self):

        if not (os.path.exists(self.inc_dir)):
            try:
                logger.debug(
                    'Increment directory does not exist.+-+-+-+-+-+-+-+-+-++-+-+-+OK')
                logger.debug(
                    'Creating increment backup directory.+-+-+-+-+-+-+-+-+-++-+-+-OK')
                os.makedirs(self.backupdir + '/inc')
                logger.debug('Created')
                return True
            except Exception as err:
                logger.error(err)
                return False
        else:
            logger.debug(
                'Increment directory exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK')
            return True

    # def check_mysql_flush_log_user(self):
    #
    #     # Creating test Database and user for flushing binary logs.
    #
    #     # Connection Settings
    #
    #
    #
    #     config = {
    #
    #         'user': self.user,
    #         'password': self.password,
    #         'host': 'localhost',
    #         'database': 'mysql',
    #         'raise_on_warnings': True,
    #
    #     }
    #
    #     # Open connection
    #     try:
    #         cnx = mysql.connector.connect(**config)
    #         cursor = cnx.cursor()
    #         query1 = "create database if not exists bck"
    #         logger.debug("Creating Test User (test_backup)+-+-+-+-+-+-+-+-+-++-+-+-+-+-OK")
    #         self.check_mysql_user_exists(cursor=cursor)
    #         time.sleep(2)
    #         logger.debug("Creating Test Database (bck)+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-OK")
    #         cursor.execute(query1)
    #         cursor.close()
    #         cnx.close()
    #
    #         return True
    #     except mysql.connector.Error as err:
    #         if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    #             #logger.debug("Something is wrong with your user name or password!!!")
    #             logger.debug(err)
    #             return False
    #         elif err.errno == errorcode.ER_BAD_DB_ERROR:
    #             logger.debug("Database does not exists")
    #             return False
    #         elif err.errno == errorcode.ER_DB_CREATE_EXISTS:
    #             logger.debug("Database Already exists")
    #             return True
    #         else:
    #             logger.debug(err)
    #             return False

    # def check_mysql_user_exists(self, cursor):
    #     query = "SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = 'test_backup')"
    #     grant_query = "grant reload,usage on *.* to 'test_backup'@'127.0.0.1'"
    #     try:
    #         cursor.execute(query)
    #         for i in cursor:
    #             if i[0] == 1:
    #                 cursor.execute(grant_query)
    #             else:
    #                 if self.check_mysql_valpass_plugin(cursor=cursor):
    #                     passwd = self.generate_mysql_password(cursor=cursor)
    #                     create_query = "create user 'test_backup'@'127.0.0.1' identified by '%s'" % passwd
    #                     try:
    #                         cursor.execute(create_query)
    #                         self.test_backup_user_passwd = passwd
    #                         cursor.execute(grant_query)
    #                     except mysql.connector.Error as err:
    #                         logger.debug(err)
    #                         exit(0)
    #                 else:
    #                     create_query2 = "create user 'test_backup'@'127.0.0.1' identified by '12345'"
    #                     try:
    #                         cursor.execute(create_query2)
    #                         cursor.execute(grant_query)
    #                     except mysql.connector.Error as err:
    #                         logger.debug(err)
    #                         exit(0)
    #     except mysql.connector.Error as err:
    #         logger.debug(err)
    #         exit(0)

    # def random_password_generator(self, length):
    #     """
    #     Random Password Generator based on given password length value
    #     :param length: Length of generated password.
    #     :return: Random Generated Password
    #     """
    #     import random
    #
    #     alphabet = "abcdefghijklmnopqrstuvwxyz!@#$%?"
    #     upperalphabet = alphabet.upper()
    #     pw_len = 8
    #     pwlist = []
    #
    #     for i in range(pw_len//3):
    #         pwlist.append(alphabet[random.randrange(len(alphabet))])
    #         pwlist.append(upperalphabet[random.randrange(len(upperalphabet))])
    #         pwlist.append(str(random.randrange(10)))
    #     for i in range(pw_len-len(pwlist)):
    #         pwlist.append(alphabet[random.randrange(len(alphabet))])
    #
    #     random.shuffle(pwlist)
    #     pwstring = "".join(pwlist)
    #
    #     return pwstring

    # def check_mysql_valpass_plugin(self, cursor):
    #     """
    #     Check if MySQL has password policy via official validate_password plugin.
    #     :param: cursor: cursor from mysql connector
    #     :return: True/False.
    #     """
    #     query_plugin = "select plugin_status from information_schema.plugins where plugin_name='validate_password'"
    #
    #     try:
    #         cursor.execute(query_plugin)
    #         for i in cursor:
    #             if i[0] == 'ACTIVE':
    #                 return True
    #             else:
    #                 return False
    #     except mysql.connector.Error as err:
    #         logger.debug(err)
    #         return False

    # def generate_mysql_password(self, cursor):
    #     """
    #     Check if MySQL has password policy via official validate_password plugin.
    #     If it has enabled validate_password plugin learn, password length etc. information for generating random password.
    #     :param cursor: cursor from mysql connector
    #     :return: Integer (Password Length information) / False if there is no active plugin.
    #     """
    #     query_password_length = "select @@validate_password_length"
    #     try:
    #         cursor.execute(query_password_length)
    #         for i in cursor:
    #             return self.random_password_generator(i[0])
    #     except mysql.connector.Error as err:
    #         logger.debug(err)
    #         return False

    def check_mysql_product(self):
        """
        Check if MariaDB or MySQL installed. We will apply a workaround for MariaDB
        See related BUG report -> https://bugs.launchpad.net/percona-xtrabackup/+bug/1444541
        :return: 2 if server is MariaDB / 3 if server is MySQL(other)
        """

        check_version = "%s --user=%s --password='%s' ver" % (
            self.mysqladmin, self.mysql_user, self.mysql_password)

        if hasattr(self, 'mysql_socket'):
            check_version += " --socket=%s" % (self.mysql_socket)
        elif hasattr(self, 'mysql_host') and hasattr(self, 'mysql_port'):
            check_version += " --host=%s" % self.mysql_host
            check_version += " --port=%s" % self.mysql_port
        else:
            logger.critical(
                "Neither mysql_socket nor mysql_host and mysql_port are defined in config!")
            return False

        status, output = subprocess.getstatusoutput(check_version)

        if status == 0:
            if 'MARIADB' in output.upper():
                logger.debug("!!!!!!!!")
                logger.debug(
                    "Installed Server is MariaDB, will use a workaround for LP BUG 1444541.")
                logger.debug("!!!!!!!!")
                return 2
            else:
                logger.debug(
                    "Installed Server is MySQL, will continue as usual.")
                return 3
        else:
            logger.error("mysqladmin ver command Failed")
            time.sleep(5)
            logger.error(output)
            return False

    def check_systemd_init(self):
        """
        Check if systemd support available for server
        :return:
        3 - if server is MariaDB and systemd available.
        4 - if server is MariaDB and systemd NOT available.
        5 - if server is MySQL and systemd available.
        6- is server is MySQL and systemd NOT available.
        """
        product_result = self.check_mysql_product()
        systemd_dir = '/usr/lib/systemd/system'

        list_dir = []

        if os.path.isdir(systemd_dir):

            for i in os.listdir(systemd_dir):
                list_dir.append(i)
        else:
            logger.error(
                "There is no /usr/lib/systemd/system folder, Continue")

        if product_result == 2:
            if 'mariadb.service' in list_dir:
                return 3
            else:
                return 4

        elif product_result == 3:
            if 'mysqld.service' in list_dir:
                return 5
            else:
                return 6

    def check_all_env(self):

        env_result = False

        if self.check_mysql_uptime():
            if self.check_mysql_mysql():
                if self.check_mysql_mysqladmin():
                    if self.check_mysql_conf():
                        if self.check_mysql_backuptool():
                            if self.check_mysql_backupdir():
                                if self.check_mysql_fullbackupdir():
                                    if self.check_mysql_incbackupdir():
                                        if hasattr(
                                                self, 'archive_dir') and self.check_mysql_archive_dir():
                                            # if
                                            # self.check_mysql_flush_log_user():
                                            env_result = True
                                        else:
                                            env_result = True

            if env_result:
                logger.debug(
                    "Check status: STATUS+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-+-+-OK")
                return env_result
            else:
                logger.critical(
                    "Check status: STATUS+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-FAILED")
                return env_result


#
# x = CheckEnv()
# x.check_all_env()
