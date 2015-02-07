import mysql.connector
import time
import configparser
import os
import shutil
import shlex
import subprocess
from general_conf.generalops import GeneralClass


class PartialRecovery(GeneralClass):

    def __init__(self):
        GeneralClass.__init__(self)

        # ===========================
        #  Reading Config File      #
        # ===========================

        # con = configparser.ConfigParser()
        # con.read(conf)
        # bolme = con.sections()
        #
        # DB = bolme[0]
        # self.datadir = con[DB]['datadir']
        #
        #
        # BCK = bolme[1]
        # self.backupdir = con[BCK]['backupdir']
        # self.full_dir = self.backupdir + '/full'
        # self.inc_dir = self.backupdir + '/inc'
        #
        #
        # CM = bolme[2]
        # self.chown_command = con[CM]['chown_command']


        # =================================
        # Connecting To MySQL
        # =================================

        self.config = {

            'user': 'root',
            'password': '12345',
            'host': '127.0.0.1',
            'database': 'bck',
            'raise_on_warnings': True,

        }

        self.cnx = mysql.connector.connect(**self.config)
        self.cur = self.cnx.cursor()


    def __del__(self):
        self.cnx.close()
        self.cur.close()


    def get_table_ibd_file(self, database_name, table_name):
        """
            This function purpose to locate backed up database and table.
             Exactly we are looking for .ibd file.
             .ibd file is a tablespace where table data located.
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
            print("There is no such Database or Table")


    def lock_table(self,database_name, table_name):
        #query = "select 1 from dual"
        query = "LOCK TABLES %s.%s WRITE" % (database_name, table_name)
        try:
            self.cur.execute(query)
            # for i in self.cur:
            #     print(i)
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
        comm2 = shlex.split(comm)
        try:
            fb2 = subprocess.Popen(comm2, stdout=subprocess.PIPE)
            print(str(fb2.stdout.read()))
            return True
        except Exception as err:
            print(err)
            return False



    def import_tablespace(self, database_name, table_name):
        query = "ALTER TABLE %s.%s IMPORT TABLESPACE" % (database_name, table_name)
        try:
            self.cur.execute(query)
            return True
        except mysql.connector.Error as err:
            print(err)
            return False

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
        database_name = input("Type Database name: ")

        # Type name of table which you want to restore
        table_name = input("Type Table name: ")

        path = self.get_table_ibd_file(database_name=database_name, table_name=table_name)
        path_to_mysql_datadir = self.datadir+"/"+database_name

        if self.lock_table(database_name=database_name, table_name=table_name):
            if self.alter_tablespace(database_name=database_name, table_name=table_name):
                if self.copy_ibd_file_back(path_of_ibd_file=path, path_to_mysql_database_dir=path_to_mysql_datadir):
                    if self.give_chown(path_to_mysql_database_dir=path_to_mysql_datadir):
                        if self.import_tablespace(database_name=database_name, table_name=table_name):
                            self.unlock_tables()



# a = PartialRecovery()
# a.final_actions()

