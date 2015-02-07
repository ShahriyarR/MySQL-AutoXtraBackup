# (#!/usr/bin/python3)

#!/usr/local/bin/python3

import shlex
import subprocess
import os
import mysql.connector
import time
from mysql.connector import errorcode


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
            print('Server is NOT Up------------------------------------')
            return False
        else:
            print('Server is Up and running--------------------------OK')
            return True


    def check_mysql_conf(self):
        #if not os.path.exists(self.backup_class_obj.mycnf):
        # Testing with MariaDB Galera Cluster
        if not os.path.exists(self.backup_class_obj.maria_cluster_cnf):
            print('MySQL configuration file path NOT exists------------')
            return False
        else:
            print('MySQL configuration file exists-------------------OK')
            return True


    def check_mysql_mysql(self):
        if not os.path.exists(self.backup_class_obj.mysql):
            print('/usr/bin/mysql NOT exists---------------------------')
            return False
        else:
            print('/usr/bin/mysql exists-----------------------------OK')
            return True


    def check_mysql_mysqladmin(self):
        if not os.path.exists(self.backup_class_obj.mysqladmin):
            print('/usr/bin/mysqladmin NOT exists----------------------')
            return False
        else:
            print('/usr/bin/mysqladmin exists------------------------OK')
            return True


    def check_mysql_backuptool(self):
        if not os.path.exists(self.backup_class_obj.backup_tool):
            print('Xtrabackup/Innobackupex NOT exists------------------')
            return False
        else:
            print('Xtrabackup/Innobackupex exists--------------------OK')
            return True


    def check_mysql_backupdir(self):

        if not (os.path.exists(self.backup_class_obj.backupdir)):
            print('Main backup directory NOT exists--------------------')
            return False
        else:
            print('Main backup directory exists----------------------OK')
            return True


    def check_mysql_fullbackupdir(self):

        if not (os.path.exists(self.backup_class_obj.full_dir)):
            try:
                print('Full Backup directory does not exist.---------OK')
                print('Creating full backup directory...-------------OK')
                os.makedirs(self.backup_class_obj.backupdir + '/full')
                print('Created---------------------------------------OK')
                return True
            except Exception as err:
                print(err)
                return False
        else:
            print("Full Backup directory exists.---------------------OK")
            return True


    def check_mysql_incbackupdir(self):

        if not (os.path.exists(self.backup_class_obj.inc_dir)):
            try:
                print('Increment directory does not exist.-----------OK')
                print('Creating increment backup directory.----------OK')
                os.makedirs(self.backup_class_obj.backupdir + '/inc')
                print('Created')
                return True
            except Exception as err:
                print(err)
                return False
        else:
            print('Increment directory exists------------------------OK')
            return True


    def check_mysql_flush_log_user(self):

       # Creating test Database and user for flushing binary logs.

        # Connection Settings

        config = {

            'user': 'root',
            'password': '12345',
            'host': '127.0.0.1',
            'database': 'mysql',
            'raise_on_warnings': True,

        }

        # Open connection
        try:
            cnx = mysql.connector.connect(**config)
            cursor = cnx.cursor()
            query1 = "create database if not exists bck"
            query2 = "grant all on bck.* to 'test_backup'@'127.0.0.1' identified by '12345'"
            query3 = "grant reload on *.* to 'test_backup'@'127.0.0.1'"
            time.sleep(2)
            print("Creating Test User (test_backup)------------------OK")
            cursor.execute(query2)
            time.sleep(2)
            print("Giving Grants to Test User------------------------OK")
            cursor.execute(query3)
            time.sleep(2)
            print("Creating Test Database (bck)----------------------OK")
            cursor.execute(query1)
            cursor.close()
            cnx.close()

            return True
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
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
                                        if self.check_mysql_flush_log_user():
                                            env_result = True



            if env_result:
                print("Check status: STATUS------------------------------OK")
                return env_result
            else:
                print("Check status: STATUS------------------------------FAILED")
                return env_result



#
# x = CheckEnv()
# x.check_all_env()