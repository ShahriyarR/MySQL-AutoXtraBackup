from prepare_env_test_mode.clone_build_start_server import CloneBuildStartServer
from prepare_env_test_mode.config_generator import ConfigGenerator
from prepare_env_test_mode.take_backup import WrapperForBackupTest
from prepare_env_test_mode.prepare_backup import WrapperForPrepareTest
from prepare_env_test_mode.run_benchmark import RunBenchmark
from general_conf.generalops import GeneralClass
from general_conf.check_env import CheckEnv
import socket
import os
import shutil
import logging
import subprocess
from time import sleep
from random import randint
logger = logging.getLogger(__name__)


class RunnerTestMode(GeneralClass):

    def __init__(self, config='/etc/bck.conf'):
        self.conf = config
        super().__init__(config=self.conf)

        self.clone_obj = CloneBuildStartServer(config=self.conf)
        self.basedirs = self.clone_obj.get_basedir()
        self.df_mysql_options = " ".join(self.default_mysql_options.split(','))

    @staticmethod
    def get_free_tcp_port():
        # Method to generate random ports
        tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp.bind(('', 0))
        addr, port = tcp.getsockname()
        tcp.close()
        return port

    def prepare_start_slave_options(self, basedir, slave_number, options):
        '''

        :param basedir: PS basedir path
        :param slave_number: Slave count 0, 1, 2 (node0 node1 node2 etc.)
        :param options: Generated combination of PS options passed here.
        :return: String of options
        '''
        tmpdir="--tmpdir={}/node{}".format(basedir, slave_number)
        datadir = "--datadir={}/node{}".format(basedir, slave_number)
        socket = "--socket={}/sock{}.sock".format(basedir, slave_number)
        port = "--port={}".format(self.get_free_tcp_port())
        log_error = "--log-error={}/log/node{}".format(basedir, slave_number)
        server_id = "--server_id={}".format(randint(10, 99))
        return " ".join([tmpdir, datadir, socket, port, log_error, options, server_id])

    @staticmethod
    def run_pt_table_checksum(basedir, conn_options=None):
        '''
        Method for running pt-table-checksum method. Should be run on master server.
        :param basedir: PS basedir path
        :param conn_options: pass this only for Slave
        :return:
        '''
        rb_obj = RunBenchmark()
        sock_file = rb_obj.get_sock(basedir=basedir)
        if conn_options is None:
            command = "pt-table-checksum --user={} --socket={}".format("root", sock_file)
        else:
            command = "pt-table-checksum {}".format(conn_options)
        status, output = subprocess.getstatusoutput(command)
        if status == 0:
            logger.debug("pt-table-checksum succeeded on master")
            return True
        else:
            logger.error("pt-table-checksum command failed")
            logger.error(output)
            raise RuntimeError("pt-table-checksum command failed")

    @staticmethod
    def create_dsns_table(sql_conn):
        '''
        This method will create dsns table for pt-table-checksum
        :param sql_conn: The mysql client connection command
        :return: True if success or raise RuntimeError from run_sql_command()
        '''
        create_table = """CREATE TABLE `dsns` (
                          `id` int(11) NOT NULL AUTO_INCREMENT,
                          `parent_id` int(11) DEFAULT NULL,
                          `dsn` varchar(255) NOT NULL,
                          PRIMARY KEY (`id`))
                        """

        cmd = "{} -e \'{}\'".format(sql_conn, create_table)
        RunnerTestMode.run_sql_command(cmd)

        return True

    @staticmethod
    def populate_dsns_table(sql_conn, slave_socket):
        '''
        Method for inserting slave info into dsns table
        :param sql_conn: MySQl client connection string
        :param slave_socket: Socket file of slave
        :return: True or RuntimError from run_sql_command()
        '''

        dsns_id = randint(10, 99)
        dsns_parent_id = randint(1, 99)
        dsn='"h=localhost,u=root,p=,s={}"'.format(slave_socket)
        insert_into = "{} -e 'insert into dsns(id, parent_id, dsn) values({}, {}, {})'".format(sql_conn,
                                                                                               dsns_id,
                                                                                               dsns_parent_id,
                                                                                               dsn)
        RunnerTestMode.run_sql_command(insert_into)

        return True



    @staticmethod
    def run_sql_command(sql_command):
        '''
        General method for running SQL using mysql client connection
        :param sql_command: Passed runnable mysql client sql command
        :return: The output/result of running SQL or raise RuntimError
        '''
        logger.debug("Running -> {}".format(sql_command))
        status, output = subprocess.getstatusoutput(sql_command)
        if status == 0:
            return output
        else:
            raise RuntimeError("Failed to run SQL command -> {}".format(output))

    @staticmethod
    def check_slave_status(sql_command):
        '''
        Checks Slave's status output for fails
        :param sql_command: The formulated SQL command to be passed to run_sql_command()
        :return: True if Slave up and running properly
        :return: Raise a RuntimeError is something wrong with slave
        '''

        output = RunnerTestMode.run_sql_command(sql_command=sql_command)
        list_output = output.splitlines()
        for i, j in enumerate(list_output[2:], start=1):
            splitted = j.split(":")

            if 'Slave_IO_Running' == splitted[0].lstrip():
                if splitted[1].lstrip() != 'Yes':
                    raise RuntimeError("Slave_IO_Running is not Yes")

            if 'Slave_SQL_Running' == splitted[0].lstrip():
                if splitted[1].lstrip() != 'Yes':
                    raise RuntimeError("Slave_SQL_Running is not Yes")

            if 'Last_IO_Error' == splitted[0].lstrip():
                if splitted[1].lstrip() != '':
                    raise RuntimeError("It seems to be IO Error: {}".format(splitted[1]))

            if 'Last_SQL_Error' == splitted[0].lstrip():
                if splitted[1].lstrip() != '':
                    raise RuntimeError("It seems to be SQL Error: {}".format(splitted[1]))




    @staticmethod
    def drop_blank_mysql_users(sql_conn):
        '''
        Method for dropping blank PS users(for 5.6 version). In PS 5.7 there are no blank users created.
        :param sql_conn: MySQL Client connection string
        :return: True if success or raise RuntimeError exception from run_sql_command() method
        '''
        select_blank_users = '{} -e \"select user, host from mysql.user where user like \'\'\"'
        logger.debug("Running -> {}".format(select_blank_users.format(sql_conn)))
        users = RunnerTestMode.run_sql_command(sql_command=select_blank_users.format(sql_conn))
        # Getting host names for blank users:
        for i in users.splitlines()[1:]:
            drop_user = '{} -e "drop user \'\'@\'{}\'"'
            logger.debug("Running -> {}".format(drop_user.format(sql_conn, i.lstrip())))
            RunnerTestMode.run_sql_command(drop_user.format(sql_conn, i.lstrip()))

        return True

    @staticmethod
    def get_gtid_address(full_backup_dir):
        '''
        This method is going to open xtrabackup_binlog_info file inside full backup dir.
        :param full_backup_dir: The full backup directory path
        :return: The GTID position
        '''
        file_name = "{}/{}".format(full_backup_dir, 'xtrabackup_binlog_info')
        with open(file_name, 'r') as binlog_file:
            return binlog_file.readline().split('\t')[2][:-1]


    def run_change_master(self, basedir, full_backup_dir, file_name=None):
        '''
        Method for making ordinary server as slave
        :param basedir: PS basedir path
        :param file_name: MySQL client connections stored file name; It is passed for slave server
        :return: True if succes or raise RuntimeError exception fom run_sql_command()
        '''

        logger.debug("Started to make this new server as slave...")
        sql_port = "{} -e 'select @@port'"
        sql_create_user = '{} -e "CREATE USER \'repl\'@\'%\' IDENTIFIED BY \'Baku12345\'"'
        sql_grant = '{} -e "GRANT REPLICATION SLAVE ON *.* TO \'repl\'@\'%\'"'
        sql_change_master = '{} -e "CHANGE MASTER TO MASTER_HOST=\'{}\', MASTER_USER=\'{}\', MASTER_PASSWORD=\'{}\', MASTER_PORT={}, MASTER_AUTO_POSITION=1"'
        start_slave = "{} -e 'start slave'"
        show_slave_status = "{} -e 'show slave status\G'"
        mysql_slave_client_cmd = RunBenchmark(config=self.conf).get_mysql_conn(basedir=basedir, file_name=file_name)
        mysql_master_client_cmd = RunBenchmark(config=self.conf).get_mysql_conn(basedir=basedir)
        # Getting port from master
        port = self.run_sql_command(sql_port.format(mysql_master_client_cmd))
        # Create user
        self.run_sql_command(sql_create_user.format(mysql_master_client_cmd))
        # Grant user
        self.run_sql_command(sql_grant.format(mysql_master_client_cmd))
        # Drop blank users if PS version is 5.6
        if '5.6' in basedir:
            self.drop_blank_mysql_users(mysql_master_client_cmd)

        # Run SET GLOBAL gtid_purged= here
        gtid_pos = self.get_gtid_address(full_backup_dir)
        gtid_purged = '{} -e \'set global gtid_purged=\"{}\"\''.format(mysql_slave_client_cmd, gtid_pos)
        self.run_sql_command(gtid_purged)

        # Change master
        self.run_sql_command(
            sql_change_master.format(mysql_slave_client_cmd, '127.0.0.1', 'repl', 'Baku12345', port[7:]))
        # Start Slave
        self.run_sql_command(start_slave.format(mysql_slave_client_cmd))
        # Check Slave output for errors
        sleep(20)
        self.check_slave_status(show_slave_status.format(mysql_slave_client_cmd))

        return True

    def wipe_backup_prepare_copyback(self, basedir):
        '''
        Method Backup + Prepare and Copy-back actions.
        It is also going to create slave server from backup of master and start.
        :param basedir: The basedir path of MySQL
        :return: Success if no exception raised from methods
        '''
        c_count = 0
        for options in ConfigGenerator(config=self.conf).options_combination_generator(self.mysql_options):
            c_count = c_count + 1
            options = " ".join(options)
            options = options + " " + self.df_mysql_options.format(c_count)
            logger.debug("Will start MySQL with {}".format(options))
            if self.clone_obj.wipe_server_all(basedir_path=basedir, options=options):
                logger.debug("Starting cycle{}".format(c_count))
                full_dir = self.backupdir + "/cycle{}".format(c_count) + "/full"
                inc_dir = self.backupdir + "/cycle{}".format(c_count) + "/inc"
                backup_obj = WrapperForBackupTest(config=self.conf, full_dir=full_dir, inc_dir=inc_dir, basedir=basedir)
                # Take backups
                logger.debug("Started to run run_all_backup()")
                if backup_obj.run_all_backup():
                    prepare_obj = WrapperForPrepareTest(config=self.conf, full_dir=full_dir, inc_dir=inc_dir)
                    # Prepare backups
                    logger.debug("Started to run run_prepare_backup()")
                    if prepare_obj.run_prepare_backup():
                        if hasattr(self, 'slave_count'):
                            logger.debug("slave_count is defined so will create slaves!")
                            for i in range(int(self.slave_count)):
                                slave_datadir = "{}/node{}".format(basedir, i)
                                if os.path.exists(slave_datadir):
                                    try:
                                        logger.debug("Removing old slave datadir...")
                                        shutil.rmtree(slave_datadir)
                                    except Exception as err:
                                        logger.error("An error while removing directory {}".format(slave_datadir))
                                        logger.error(err)

                                try:
                                    logger.debug("Creating slave datadir...")
                                    os.makedirs("{}/node{}".format(basedir, i))
                                except Exception as err:
                                    logger.error("An error while creating directory {}".format(slave_datadir))
                                    logger.error(err)
                                # Doing some stuff for creating slave server env
                                if prepare_obj.run_xtra_copyback(datadir=slave_datadir):
                                    if prepare_obj.giving_chown(datadir=slave_datadir):
                                        slave_full_options = self.prepare_start_slave_options(basedir=basedir, slave_number=i, options=options)
                                        if prepare_obj.start_mysql_func(start_tool="{}/start_dynamic".format(basedir), options=slave_full_options):
                                            # Creating connection file for new node
                                            with open("{}/cl_node{}".format(basedir, i), 'w+') as clfile:
                                                conn = "{}/bin/mysql -A -uroot -S{}/sock{}.sock --force test".format(basedir, basedir, i)
                                                clfile.write(conn)
                                                # give u+x to this file
                                                chmod = "chmod u+x {}/cl_node{}".format(basedir, i)
                                                status, output = subprocess.getstatusoutput(chmod)

                                                if status == 0:
                                                    logger.debug("chmod succeeded for {}/cl_node{}".format(basedir, i))
                                                else:
                                                    raise RuntimeError("Failed to chmod {}/cl_node{}".format(basedir, i))

                                            with open("{}/stop_node{}".format(basedir, i), 'w+') as stop_file:
                                                shutdown_slave = "{}/bin/mysqladmin -uroot -S{}/sock{}.sock shutdown".format(basedir, basedir, i)
                                                stop_file.write(shutdown_slave)
                                                # give u+x to this file
                                                chmod = "chmod u+x {}/stop_node{}".format(basedir, i)
                                                status, output = subprocess.getstatusoutput(chmod)

                                                if status == 0:
                                                    logger.debug("chmod succeeded for {}/stop_node{}".format(basedir, i))
                                                else:
                                                    raise RuntimeError("Failed to chmod {}/stop_node{}".format(basedir, i))



                                            # Checking if node is up
                                            chk_obj = CheckEnv(config=self.conf)
                                            check_options = "--user={} --socket={}/sock{}.sock".format('root', basedir, i)
                                            slave_socket_file = "{}/sock{}.sock".format(basedir, i)
                                            if chk_obj.check_mysql_uptime(options=check_options):
                                                # Make this node to be slave
                                                full_backup_dir = prepare_obj.recent_full_backup_file()
                                                if self.run_change_master(basedir=basedir,
                                                                          full_backup_dir="{}/{}".format(full_dir, full_backup_dir),
                                                                          file_name="cl_node{}".format(i)):
                                                    sleep(10)
                                                    #Running on master
                                                    if self.run_pt_table_checksum(basedir=basedir):
                                                        break
                        else:
                            prepare_obj.copy_back_action(options=options)