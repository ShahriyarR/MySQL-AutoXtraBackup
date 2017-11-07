import os
import shutil
import subprocess
from general_conf.generalops import GeneralClass
import re
from general_conf import check_env
import sys

import logging
logger = logging.getLogger(__name__)


class PartialRecovery(GeneralClass):

    def __init__(self, config='/etc/bck.conf'):
        self.conf = config
        GeneralClass.__init__(self, self.conf)
        if shutil.which('mysqlfrm') is None:
            logger.critical("Could not find mysqlfrm! Please install it or check if it is in PATH")
            raise RuntimeError("Could not find mysqlfrm! Please install it or check if it is in PATH")

    def create_mysql_client_command(self, statement):
        command_connection = '{} --defaults-file={} -u{} --password={}'
        command_execute = ' -e "{}"'

        if hasattr(self, 'mysql_socket'):
            command_connection += ' --socket={}'
            command_connection += command_execute
            new_command = command_connection.format(
                self.mysql,
                self.mycnf,
                self.mysql_user,
                self.mysql_password,
                self.mysql_socket,
                statement)
            return new_command
        else:
            command_connection += ' --port={}'
            command_connection += command_execute
            new_command = command_connection.format(
                self.mysql,
                self.mycnf,
                self.mysql_user,
                self.mysql_password,
                self.mysql_host,
                self.mysql_port,
                statement)
            return new_command

    def check_innodb_file_per_table(self):
        """
        Function for checking MySQL innodb_file_per_table option.
        It is needed for "Transportable Tablespace" concept.
        :return: True/False
        """
        statement = "select @@global.innodb_file_per_table"
        run_command = self.create_mysql_client_command(statement=statement)

        logger.debug("Checking if innodb_file_per_table is enabled")
        status, output = subprocess.getstatusoutput(run_command)

        if status == 0 and int(output[-1]) == 1:
            logger.debug("OK: innodb_file_per_table is enabled!")
            return True
        elif status == 0 and int(output[-1]) == 0:
            logger.debug("OK: innodb_file_per_table is disabled!")
            return False
        else:
            logger.error("FAILED: InnoDB file per-table Check")
            logger.error(output)
            raise RuntimeError("FAILED: InnoDB file per-table Check")

    def check_mysql_version(self):
        """
        Function for checking MySQL version.
        Version must be >= 5.6 for using "Transportable Tablespace" concept.
        :return: True/False
        """
        statement = "select @@version"
        run_command = self.create_mysql_client_command(statement=statement)

        logger.debug("Checking MySQL version")
        status, output = subprocess.getstatusoutput(run_command)

        if status == 0 and ('5.6' in output):
            logger.debug("You have correct version of MySQL")
            return True
        elif status == 0 and ('5.7' in output):
            logger.debug("You have correct version of MySQL")
            return True
        elif status == 0 and ('5.7' not in output) and ('5.6' not in output):
            logger.error("Your MySQL server is not supported. MySQL version must be >= 5.6")
            raise RuntimeError("Your MySQL server is not supported. MySQL version must be >= 5.6")
        else:
            logger.error("FAILED: MySQL version check")
            logger.error(output)
            raise RuntimeError("FAILED: MySQL version check")

    def check_database_exists_on_mysql(self, database_name):
        """
        Function check if this database already exists in MySQL Server.(.frm and .ibd files are exist)
        In other words database is not dropped. If there is no such database, there is an input for creation.
        :param database_name: Specified database name
        :return: True/False
        """
        statement = "SELECT count(*) FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '%s'" % database_name
        run_command = self.create_mysql_client_command(statement=statement)

        logger.debug("Checking if database exists in MySQL")
        status, output = subprocess.getstatusoutput(run_command)
        if status == 0 and int(output[-1]) == 1:
            logger.debug("Database exists!")
            return True
        if status == 0 and int(output[-1]) == 0:
            logger.debug("There is no such database!")
            logger.debug("Create Specified Database in MySQL Server, before restoring single table")
            answer = input("We can create it for you do you want? (yes/no): ")
            if answer == 'yes':
                create_db = "create database %s" % database_name
                run_command = self.create_mysql_client_command(statement=create_db)
                logger.debug("Creating specified database")
                status, output = subprocess.getstatusoutput(run_command)
                if status == 0:
                    logger.debug("OK: {} database created".format(database_name))
                    return True
                else:
                    logger.error("FAILED: to create database!")
                    logger.error(output)
                    raise RuntimeError("FAILED: to create database!")
            else:  # if you type non-yes word
                logger.error("Exited!")
                return False

        else:
            logger.error("FAILED: Check for database")
            logger.error(output)
            raise RuntimeError("FAILED: Check for database")

    def check_table_exists_on_mysql(
            self,
            path_to_frm_file,
            database_name,
            table_name):
        """
        Function to check if table exists on MySQL.
        If it is dropped, we will try to extract table create statement from .frm file from backup file.
        :param path_to_frm_file: Path for .frm file
        :param database_name: Specified database name
        :param table_name: Specified table name
        :return: True/False
        """

        statement = "select count(*) from INFORMATION_SCHEMA.tables " \
                "where table_schema = '%s'" \
                "and table_name =  '%s'" % (database_name, table_name)

        run_command = self.create_mysql_client_command(statement=statement)
        logger.debug("Checking if table exists in MySQL Server")
        status, output = subprocess.getstatusoutput(run_command)
        if status == 0 and int(output[-1]) == 1:
            logger.debug("Table exists in MySQL Server.")
            return True
        elif status == 0 and int(output[-1]) == 0:
            logger.debug("Table does not exist in MySQL Server.")
            logger.debug("You can not restore table, with not existing tablespace file(.ibd)!")
            logger.debug("We will try to extract table create statement from .frm file, from backup folder")
            create = self.run_mysqlfrm_utility(path_to_frm_file=path_to_frm_file)
            regex = re.compile(r'((\n)CREATE((?!#).)*ENGINE=\w+)', re.DOTALL)
            matches = [m.groups() for m in regex.finditer(create)]
            for m in matches:
                create_table = m[0]
                new_create_table = create_table.replace("`", "")
                run_command = self.create_mysql_client_command(statement=new_create_table)
                status, output = subprocess.getstatusoutput(run_command)
                if status == 0:
                    logger.debug("Table Created from .frm file!")
                    return True
                else:
                    logger.error("Failed to create table from .frm file!")
                    logger.error(output)
                    raise RuntimeError("Failed to create table from .frm file!")
        else:
            logger.error("FAILED: Check if table exists")
            logger.error(output)
            raise RuntimeError("FAILED: Check if table exists")

    @staticmethod
    def run_mysqlfrm_utility(path_to_frm_file):
        command = '/usr/bin/mysqlfrm --diagnostic %s' % path_to_frm_file
        logger.debug("Running mysqlfrm tool")
        status, output = subprocess.getstatusoutput(command)
        if status == 0:
            logger.debug("OK: Success to run mysqlfrm")
            return output
        else:
            logger.error("FAILED: run mysqlfrm")
            logger.error(output)
            raise RuntimeError("FAILED: run mysqlfrm")

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
            for x in os.listdir(self.full_dir + "/" + i):
                if os.path.isdir(
                    self.full_dir +
                    "/" +
                    i +
                    "/" +
                        x) and x == database_name:
                    for z in os.listdir(self.full_dir + "/" + i + "/" + x):
                        database_dir_list.append(z)
                        database_objects_full_path.append(
                            self.full_dir + "/" + i + "/" + x + "/" + z)

        # If database directory exists find already provided table in database
        # directory
        if len(database_dir_list) > 0:
            for i in database_dir_list:
                base_file = os.path.splitext(i)[0]
                ext = os.path.splitext(i)[1]

                if table_name == base_file:
                    table_dir_list.append(i)

        # If table name from input is valid and it is located in database
        # directory return .ibd file name
        if len(database_dir_list) > 0 and len(
                table_dir_list) == 2:  # Why 2? because every InnoDB table must have .frm and .ibd file
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
            logger.error("Sorry, There is no such Database or Table in backup directory")
            logger.error("Or maybe table storage engine is not InnoDB")
            raise RuntimeError("Sorry, There is no such Database or Table in backup directory "
                               "Or maybe table storage engine is not InnoDB ")

    def lock_table(self, database_name, table_name):
        # Executing lock tables write on specified table
        statement = "LOCK TABLES %s.%s WRITE" % (database_name, table_name)
        run_command = self.create_mysql_client_command(statement=statement)
        status, output = subprocess.getstatusoutput(run_command)
        logger.debug("Applying write lock!")
        if status == 0:
            logger.debug("OK: Table is locked")
            return True
        else:
            logger.error("FAILED: to LOCK!")
            logger.error(output)
            raise RuntimeError("FAILED: to LOCK!")

    def alter_tablespace(self, database_name, table_name):
        # Running alter table discard tablespace here
        statement = "ALTER TABLE %s.%s DISCARD TABLESPACE" % (
            database_name, table_name)
        run_command = self.create_mysql_client_command(statement=statement)
        status, output = subprocess.getstatusoutput(run_command)
        logger.debug("Discarding tablespace")
        if status == 0:
            logger.debug("OK: Tablespace discarded successfully")
            return True
        else:
            logger.error("FAILED: discard tablespace!")
            logger.error(output)
            raise RuntimeError("FAILED: discard tablespace!")

    @staticmethod
    def copy_ibd_file_back(path_of_ibd_file, path_to_mysql_database_dir):
        # Copy .ibd file back
        try:
            logger.debug("OK: Copying .ibd file back")
            shutil.copy(path_of_ibd_file, path_to_mysql_database_dir)
            return True
        except Exception as err:
            logger.error("FAILED: copy .ibd file back")
            logger.error(err)
            raise RuntimeError("FAILED: copy .ibd file back")

    def give_chown(self, path_to_mysql_database_dir):
        # run chown command
        comm = '%s %s' % (self.chown_command, path_to_mysql_database_dir)
        status, output = subprocess.getstatusoutput(comm)
        logger.debug("Running chown command!")
        if status == 0:
            logger.debug("OK: Chown command completed")
            return True
        else:
            logger.error("FAILED: Chown Command")
            raise RuntimeError("FAILED: Chown Command")

    def import_tablespace(self, database_name, table_name):
        # Running alter table import tablespace
        statement = "ALTER TABLE %s.%s IMPORT TABLESPACE" % (
            database_name, table_name)
        run_command = self.create_mysql_client_command(statement=statement)
        status, output = subprocess.getstatusoutput(run_command)
        logger.debug("Importing Tablespace!")
        if status == 0:
            logger.debug("OK: Tablespace imported")
            return True
        else:
            logger.error("FAILED: Tablespace import")
            logger.error(output)
            raise RuntimeError("FAILED: Tablespace import")

    def unlock_tables(self):
        # Run unlock tables command
        statement = "unlock tables"
        run_command = self.create_mysql_client_command(statement=statement)
        status, output = subprocess.getstatusoutput(run_command)
        logger.debug("Unlocking tables!")
        if status == 0:
            logger.debug("OK: Unlocked!")
            return True
        else:
            logger.error("FAILED: Unlocking")
            logger.error(output)
            raise RuntimeError("FAILED: Unlocking")

    def final_actions(self):
        # Type Database name of table which you want to restore
        database_name = input("Type Database name: ")
        # Type name of table which you want to restore
        table_name = input("Type Table name: ")
        path = self.get_table_ibd_file(
            database_name=database_name,
            table_name=table_name)
        path_to_mysql_datadir = self.datadir + "/" + database_name

        if path:
            path_to_frm_file = path[:-3] + 'frm'

        obj_check_env = check_env.CheckEnv(self.conf)

        if path:
            try:
                obj_check_env.check_mysql_uptime()
                self.check_innodb_file_per_table()
                self.check_mysql_version()
                self.check_database_exists_on_mysql(
                                    database_name=database_name)
                self.check_table_exists_on_mysql(
                                    path_to_frm_file=path_to_frm_file,
                                    database_name=database_name,
                                    table_name=table_name)
                self.lock_table(database_name=database_name, table_name=table_name)
                self.alter_tablespace(database_name=database_name, table_name=table_name)
                self.copy_ibd_file_back(path_of_ibd_file=path, path_to_mysql_database_dir=path_to_mysql_datadir)
                self.give_chown(path_to_mysql_database_dir=path_to_mysql_datadir)
                self.import_tablespace(database_name=database_name, table_name=table_name)
                self.unlock_tables()
            except Exception as err:
                logger.error("FAILED: Table is not recovered")
                logger.error(err)
                raise RuntimeError("FAILED: Table is not recovered")
            else:
                logger.debug("OK: Table Recovered! ...")
                return True
