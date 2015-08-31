#!/opt/Python-3.3.2/bin/python3

import shlex
import subprocess
import os
import mysql.connector
import time
from mysql.connector import errorcode
import re


class CheckEnv:

    def __init__(self):

        # Workaround for circular import dependency error in Python

        from .backuper import Backup

        self.backup_class_obj = Backup()

        


    def check_mysql_uptime(self):

        statusargs = '%s %s status' % (self.backup_class_obj.mysqladmin, self.backup_class_obj.myuseroption)
        statusargs = shlex.split(statusargs)
        myadmin = subprocess.Popen(statusargs, stdout=subprocess.PIPE)

        if not ('Uptime' in str(myadmin.stdout.read())):
            print('Server is NOT Up+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+')
            return False
        else:
            print('Server is Up and running+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+OK')
            return True


    def check_mysql_conf(self):
        if not os.path.exists(self.backup_class_obj.mycnf):
        # Testing with MariaDB Galera Cluster
        #if not os.path.exists(self.backup_class_obj.maria_cluster_cnf):
            print('MySQL configuration file path does NOT exist+-+-+-+-+-+-+-+-+-+')
            return False
        else:
            print('MySQL configuration file exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+OK')
            return True


    def check_mysql_mysql(self):
        if not os.path.exists(self.backup_class_obj.mysql):
            print('/usr/bin/mysql NOT exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-+')
            return False
        else:
            print('/usr/bin/mysql exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-++-OK')
            return True


    def check_mysql_mysqladmin(self):
        if not os.path.exists(self.backup_class_obj.mysqladmin):
            print('/usr/bin/mysqladmin NOT exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-')
            return False
        else:
            print('/usr/bin/mysqladmin exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK')
            return True


    def check_mysql_backuptool(self):
        if not os.path.exists(self.backup_class_obj.backup_tool):
            print('Xtrabackup/Innobackupex NOT exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-')
            return False
        else:
            print('Xtrabackup/Innobackupex exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-OK')
            return True


    def check_mysql_backupdir(self):

        if not (os.path.exists(self.backup_class_obj.backupdir)):
            try:
                print('Main backup directory does not exist+-+-+-+-+-+-+-+-+-++-+-+-+-')
                print('Creating Main Backup folder+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+')
                os.makedirs(self.backup_class_obj.backupdir)
                print('Created+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK')
                return True
            except Exception as err:
                print(err)
                return False
        else:
            print('Main backup directory exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-OK')
            return True


    def check_mysql_archive_dir(self):

        if not (os.path.exists(self.backup_class_obj.archive_dir)):
            try:
                print('Archive backup directory does not exist+-+-+-+-+-+-+-+-+-++-+-+-+-')
                print('Creating archive folder+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+')
                os.makedirs(self.backup_class_obj.archive_dir)
                print('Created+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK')
                return True
            except Exception as err:
                print(err)
                return False
        else:
            print('Archive folder directory exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-OK')
            return True


    def check_mysql_fullbackupdir(self):

        if not (os.path.exists(self.backup_class_obj.full_dir)):
            try:
                print('Full Backup directory does not exist.+-+-+-+-+-+-+-+-+-+-+-+-OK')
                print('Creating full backup directory...+-+-+-+-+-+-+-+-+-++-+-+-+-+OK')
                os.makedirs(self.backup_class_obj.backupdir + '/full')
                print('Created+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK')
                return True
            except Exception as err:
                print(err)
                return False
        else:
            print("Full Backup directory exists.+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+OK")
            return True


    def check_mysql_incbackupdir(self):

        if not (os.path.exists(self.backup_class_obj.inc_dir)):
            try:
                print('Increment directory does not exist.+-+-+-+-+-+-+-+-+-++-+-+-+OK')
                print('Creating increment backup directory.+-+-+-+-+-+-+-+-+-++-+-+-OK')
                os.makedirs(self.backup_class_obj.backupdir + '/inc')
                print('Created')
                return True
            except Exception as err:
                print(err)
                return False
        else:
            print('Increment directory exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK')
            return True


    def check_mysql_flush_log_user(self):

        # Creating test Database and user for flushing binary logs.

        # Connection Settings


        
        password = re.search(r'\-\-password\=(.*)[\s]*', self.backup_class_obj.myuseroption)
        user = re.search(r'\-\-user\=(.*)[\s]--', self.backup_class_obj.myuseroption)

        config = {

            'user': user.group(1),
            'password': password.group(1),
            'host': '127.0.0.1',
            'database': 'mysql',
            'raise_on_warnings': True,

        }

        # Open connection
        try:
            cnx = mysql.connector.connect(**config)
            cursor = cnx.cursor()
            query1 = "create database if not exists bck"
            print("Creating Test User (test_backup)+-+-+-+-+-+-+-+-+-++-+-+-+-+-OK")
            self.check_mysql_user_exists(cursor=cursor)
            time.sleep(2)
            print("Creating Test Database (bck)+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-OK")
            cursor.execute(query1)
            cursor.close()
            cnx.close()

            return True
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password!!!")
                return False
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exists")
                return False
            elif err.errno == errorcode.ER_DB_CREATE_EXISTS:
                print("Database Already exists")
                return True
            else:
                print(err)
                return False


    def check_mysql_user_exists(self, cursor):
        query = "SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = 'test_backup')"
        grant_query = "grant reload,usage on *.* to 'test_backup'@'127.0.0.1'"
        try:
            cursor.execute(query)
            for i in cursor:
                if i[0] == 1:
                    cursor.execute(grant_query)
                else:
                    if self.check_mysql_valpass_plugin(cursor=cursor):
                        passwd = self.generate_mysql_password(cursor=cursor)
                        create_query = "create user 'test_backup'@'127.0.0.1' identified by %s" % passwd
                        try:
                            cursor.execute(create_query)
                            cursor.execute(grant_query)
                        except mysql.connector.Error as err:
                            print(err)
                            exit(0)
                    else:
                        create_query2 = "create user 'test_backup'@'127.0.0.1' identified by '12345'"
                        try:
                            cursor.execute(create_query2)
                            cursor.execute(grant_query)
                        except mysql.connector.Error as err:
                            print(err)
                            exit(0)
        except mysql.connector.Error as err:
            print(err)
            exit(0)






    def random_password_generator(self, length):
        """
        Random Password Generator based on given password length value
        :param length: Length of generated password.
        :return: Random Generated Password
        """
        import random

        alphabet = "abcdefghijklmnopqrstuvwxyz!@#$%?"
        upperalphabet = alphabet.upper()
        pw_len = 8
        pwlist = []

        for i in range(pw_len//3):
            pwlist.append(alphabet[random.randrange(len(alphabet))])
            pwlist.append(upperalphabet[random.randrange(len(upperalphabet))])
            pwlist.append(str(random.randrange(10)))
        for i in range(pw_len-len(pwlist)):
            pwlist.append(alphabet[random.randrange(len(alphabet))])

        random.shuffle(pwlist)
        pwstring = "".join(pwlist)

        return pwstring



    def check_mysql_valpass_plugin(self, cursor):
        """
        Check if MySQL has password policy via official validate_password plugin.
        :param: cursor: cursor from mysql connector
        :return: True/False.
        """
        query_plugin = "select plugin_status from information_schema.plugins where plugin_name='validate_password'"

        try:
            cursor.execute(query_plugin)
            for i in cursor:
                if i[0] == 'ACTIVE':
                    return True
                else:
                    return False
        except mysql.connector.Error as err:
            print(err)
            return False



    def generate_mysql_password(self, cursor):
        """
        Check if MySQL has password policy via official validate_password plugin.
        If it has enabled validate_password plugin learn, password length etc. information for generating random password.
        :param cursor: cursor from mysql connector
        :return: Integer (Password Length information) / False if there is no active plugin.
        """
        query_password_length = "select @@validate_password_length"
        try:
            cursor.execute(query_password_length)
            for i in cursor:
                return self.random_password_generator(i[0])
        except mysql.connector.Error as err:
            print(err)
            return False


    def check_mysql_product(self):
        """
        Check if MariaDB or MySQL installed. We will apply a workaround for MariaDB
        See related BUG report -> https://bugs.launchpad.net/percona-xtrabackup/+bug/1444541
        :return: 2 if server is MariaDB / 3 if server is MySQL(other)
        """
        check_version = '%s %s ver' % (self.backup_class_obj.mysqladmin, self.backup_class_obj.myuseroption)
        status, output = subprocess.getstatusoutput(check_version)

        if status == 0:
            if 'MARIADB' in output.upper():
                print("!!!!!!!!")
                print("Installed Server is MariaDB, will use a workaround for LP BUG 1444541.")
                print("!!!!!!!!")
                return 2
            else:
                print("Installed Server is MySQL, will continue as usual.")
                return 3
        else:
            print("mysqladmin ver command Failed")
            time.sleep(5)
            print(output)
            return False






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
                                        if self.check_mysql_archive_dir():
                                            if self.check_mysql_flush_log_user():
                                                env_result = True



            if env_result:
                print("Check status: STATUS+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-+-+-OK")
                return env_result
            else:
                print("Check status: STATUS+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-FAILED")
                return env_result



#
# x = CheckEnv()
# x.check_all_env()