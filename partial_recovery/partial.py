import mysql.connector
import os
import shutil
import shlex
import subprocess
from general_conf.generalops import GeneralClass
from mysql.connector import errorcode
import re
from master_backup_script import check_env

class PartialRecovery(GeneralClass):

    def __init__(self):
        GeneralClass.__init__(self)

        # =================================
        # Connecting To MySQL
        # =================================

        self.password = re.search(r'\-\-password\=(.*)[\s]*', self.myuseroption)

        self.config = {

            'user': 'root',
            'password': self.password.group(1),
            'host': 'localhost',
            'database': 'bck',
            'raise_on_warnings': True,

        }

        self.cnx = mysql.connector.connect(**self.config)
        self.cur = self.cnx.cursor()


    def __del__(self):
        self.cnx.close()
        self.cur.close()



    def check_innodb_file_per_table(self):
        """
        Function for checking MySQL innodb_file_per_table option.
        It is needed for "Transportable Tablespace" concept.
        :return: True/False
        """

        query = "select @@global.innodb_file_per_table"
        try:
            self.cur.execute(query)
            for i in self.cur:
                if i[0] == 1:
                    print("MySQL per table space enabled!")
                    return True
                else:
                    print("MySQL per table space disabled!")
                    print("You can not use partial table recovery.")
                    return False
            return True
        except mysql.connector.Error as err:
            print(err)
            return False



    def check_mysql_version(self):
        """
        Function for checking MySQL version.
        Version must be >= 5.6 for using "Transportable Tablespace" concept.
        :return: True/False
        """

        query = "select @@version"
        try:
            self.cur.execute(query)
            for i in self.cur:
                if '5.6' in i[0]:
                    print("MySQL Version is, %s" % i[0])
                    print("You have correct version of MySQL")
                    return True
                else:
                    print("Your MySQL server is not supported")
                    print("MySQL version must be >= 5.6")
                    return False
            return True
        except mysql.connector.Error as err:
            print(err)
            return False



    def check_database_exists_on_mysql(self, database_name):
        """
        Function check if this table already exists in MySQL Server.(.frm and .ibd files are exist)
        In other words database is not dropped. If there is no such database, there is an input for creation.
        :param database_name: Specified database name
        :return: True/False
        """

        query = "SELECT count(*) FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '%s'" % database_name

        try:
            self.cur.execute(query)
            for i in self.cur:
                if i[0] == 1:
                    print("Database exists on MySQL")
                    return True
                else:
                    print("Database does not exist in MySQL Server, but there is backed up one on backup directory")
                    print("Create Specified Database in MySQL Server, before restoring single table.")
                    answer = input("We can create it for you do you want? (yes/no): ")
                    if answer == 'yes':
                        try:
                            create_db = "create database %s" % database_name
                            self.cur.execute(create_db)
                            print("%s database created" % database_name)
                            return True
                        except mysql.connector.Error as err:
                            print(err)
                            return False
                    else: #if you type non-yes word
                        print("Exited!")
                        return False

        except mysql.connector.Error as err:
            print(err)
            return False


    def check_table_exists_on_mysql(self,path_to_frm_file, database_name, table_name):
        """
        Function to check if table exists on MySQL.
        If it is dropped, we will try to extract table create statement from .frm file from backup file.
        :param database_name: Specified database name
        :param table_name: Specified table name
        :return: True/False
        """

        query = "select count(*) from INFORMATION_SCHEMA.tables " \
                "where table_schema = '%s'" \
                "and table_name =  '%s'" % (database_name, table_name)

        try:
            self.cur.execute(query)
            for i in self.cur:
                if i[0] == 1:
                    print("Table exists in MySQL Server.")
                    return True
                else:
                    print("Table does not exist in MySQL Server.")
                    print("You can not restore table, with not existing tablespace file(.ibd)!")
                    print("We will try to extract table create statement from .frm file, from backup folder")
                    create = self.run_mysqlfrm_utility(path_to_frm_file=path_to_frm_file)
                    regex = re.compile(r'((\n)CREATE((?!#).)*ENGINE=\w+)', re.DOTALL)
                    matches = [m.groups() for m in regex.finditer(create)]
                    for m in matches:
                        create_table = m[0]
                        try:
                            self.cur.execute(create_table)
                            print("Table Created from .frm file!")
                            return True
                        except mysql.connector.Error as err:
                            print(err)
                            return False
                    return False
        except mysql.connector.Error as err:
            print(err)
            return False


    def run_mysqlfrm_utility(self, path_to_frm_file):
        command = '/usr/bin/mysqlfrm --diagnostic %s' % path_to_frm_file

        status, output = subprocess.getstatusoutput(command)
        if status == 0:
            return output
            print("Success")
        else:
            print("Failed")
            print(output)


    def get_table_ibd_file(self, database_name, table_name):
        """
            Locate backed up database and table.
             Exactly we are looking for .ibd file.
             .ibd file is a tablespace file where table data located.
        :param database_name: Specified database name
        :param table_name: Specified table name
        :return .ibd file full path / False if not exists
        """


        database_dir_list = []
        database_objects_full_path = []
        find_objects_full_path = []
        table_dir_list = []


        # Look for all files in database directory
        for i in os.listdir(self.full_dir):
            for x in os.listdir(self.full_dir+"/"+i):
                if os.path.isdir(self.full_dir+"/"+i+"/"+x) and x == database_name:
                    for z in os.listdir(self.full_dir+"/"+i+"/"+x):
                        database_dir_list.append(z)
                        database_objects_full_path.append(self.full_dir+"/"+i+"/"+x+"/"+z)



        # If database directory exists find already provided table in database directory
        if len(database_dir_list) > 0:
            for i in database_dir_list:
                base_file = os.path.splitext(i)[0]
                ext = os.path.splitext(i)[1]

                if table_name == base_file:
                    table_dir_list.append(i)


        # If table name from input is valid and it is located in database directory return .ibd file name
        if len(database_dir_list) > 0 and len(table_dir_list) == 2: # Why 2? because every table must have .frm and .ibd file
            for i in table_dir_list:
                ext = os.path.splitext(i)[1]
                if ext == '.ibd':
                    for a in database_objects_full_path:
                        if i in a:
                            find_objects_full_path.append(a)

            if len(find_objects_full_path) > 0:
                for x in find_objects_full_path:
                    return x
        else:
            print("Sorry, There is no such Database or Table in backup directory")
            print("Or maybe table storage engine is not InnoDB")
            return False


    def lock_table(self,database_name, table_name):
        query = "LOCK TABLES %s.%s WRITE" % (database_name, table_name)
        try:
            self.cur.execute(query)
            return True
        except mysql.connector.Error as err:
            print(err)
            return False


    def alter_tablespace(self, database_name, table_name):
        query = "ALTER TABLE %s.%s DISCARD TABLESPACE" % (database_name, table_name)
        try:
            self.cur.execute(query)
            return True
        except mysql.connector.Error as err:
            print(err)
            return False


    def copy_ibd_file_back(self, path_of_ibd_file, path_to_mysql_database_dir):
        try:
            shutil.copy(path_of_ibd_file, path_to_mysql_database_dir)
            return True
        except Exception as err:
            print(err)
            return False

    def give_chown(self, path_to_mysql_database_dir):
        comm = '%s %s' % (self.chown_command, path_to_mysql_database_dir)
        status, output = subprocess.getstatusoutput(comm)

        if status == 0:
            return True
        else:
            print("Chown Command Failed!")
            return False




    def import_tablespace(self, database_name, table_name):
        query = "ALTER TABLE %s.%s IMPORT TABLESPACE" % (database_name, table_name)
        try:
            self.cur.execute(query)
            return True
        except mysql.connector.errors.DatabaseError as err:
            if err.errno == errorcode.ER_IO_READ_ERROR:
                return True
            else:
                False


    def unlock_tables(self):
        query = "unlock tables"
        try:
            self.cur.execute(query)
            return True
        except mysql.connector.Error as err:
            print(err)
            return False


    def final_actions(self):
        # Type Database name of table which you want to restore

        print("+-"*40)
        database_name = input("Type Database name: ")

        # Type name of table which you want to restore
        table_name = input("Type Table name: ")

        path = self.get_table_ibd_file(database_name=database_name, table_name=table_name)
        path_to_mysql_datadir = self.datadir+"/"+database_name
        path_to_frm_file = path[:-3]+'frm'
        obj_check_env = check_env.CheckEnv()

        if path:
            if obj_check_env.check_mysql_uptime():
                if self.check_innodb_file_per_table():
                    if self.check_mysql_version():
                        if self.check_database_exists_on_mysql(database_name=database_name):
                            if self.check_table_exists_on_mysql(path_to_frm_file=path_to_frm_file, database_name=database_name, table_name=table_name):
                                if self.lock_table(database_name=database_name, table_name=table_name):
                                    if self.alter_tablespace(database_name=database_name, table_name=table_name):
                                        if self.copy_ibd_file_back(path_of_ibd_file=path, path_to_mysql_database_dir=path_to_mysql_datadir):
                                            if self.give_chown(path_to_mysql_database_dir=path_to_mysql_datadir):
                                                if self.import_tablespace(database_name=database_name, table_name=table_name):
                                                    if self.unlock_tables():
                                                        print("+-"*40)

                                                        print("Table Recovered! ..."+'-+'*30)



# a = PartialRecovery()
# a.final_actions()

