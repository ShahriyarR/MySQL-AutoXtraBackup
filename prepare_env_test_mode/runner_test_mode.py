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

    @staticmethod
    def prepare_start_slave_options(basedir, slave_number, options):
        """
        Method for preparing slave start options
        :param basedir: PS basedir path
        :param slave_number: Slave count 0, 1, 2 (node0 node1 node2 etc.)
        :param options: Generated combination of PS options passed here.
        :return: String of options
        """
        tmpdir = "--tmpdir={}/node{}".format(basedir, slave_number)
        datadir = "--datadir={}/node{}".format(basedir, slave_number)
        socket_file = "--socket={}/sock{}.sock".format(basedir, slave_number)
        port = "--port={}".format(RunnerTestMode.get_free_tcp_port())
        log_error = "--log-error={}/log/node{}".format(basedir, slave_number)
        server_id = "--server_id={}".format(randint(1111, 9999))
        return " ".join([tmpdir, datadir, socket_file, port, log_error, options, server_id])

    @staticmethod
    def run_pt_table_checksum(basedir, conn_options=None):
        """
        Method for running pt-table-checksum method. Should be run on master server.
        :param basedir: PS basedir path
        :param conn_options: pass this only for Slave
        :return:
        """
        rb_obj = RunBenchmark()
        sock_file = rb_obj.get_sock(basedir=basedir)
        if conn_options is None:
            # TODO: Temporarily disable check due to https://jira.percona.com/browse/PT-225
            # --no-check-slave-tables
            command = "pt-table-checksum --user={} --socket={} " \
                      "--recursion-method dsn=h=localhost,D=test,t=dsns " \
                      "--no-check-binlog-format --no-check-slave-tables".format("root", sock_file)
        else:
            command = "pt-table-checksum {} " \
                      "--recursion-method dsn=h=localhost,D=test,t=dsns " \
                      "--no-check-binlog-format --no-check-slave-tables".format(conn_options)
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
        """
        This method will create dsns table for pt-table-checksum
        :param sql_conn: The mysql client connection command
        :return: True if success or raise RuntimeError from run_sql_command()
        """
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
    def populate_dsns_table(sql_conn, slave_port):
        """
        Method for inserting slave info into dsns table
        :param sql_conn: MySQl client connection string
        :param slave_port: The port number for slave
        :return: True or RuntimError from run_sql_command()
        """
        dsns_id = randint(10, 999)
        dsns_parent_id = randint(1, 999)
        dsn = '"h=127.0.0.1,u=root,P={}"'.format(slave_port)
        insert_into = "{} -e 'insert into dsns(id, parent_id, dsn) values({}, {}, {})'".format(sql_conn,
                                                                                               dsns_id,
                                                                                               dsns_parent_id,
                                                                                               dsn)
        RunnerTestMode.run_sql_command(insert_into)

        return True

    @staticmethod
    def run_sql_command(sql_command):
        """
        General method for running SQL using mysql client connection
        :param sql_command: Passed runnable mysql client sql command
        :return: The output/result of running SQL
        :raise: RuntimeError on fail
        """
        logger.debug("Running -> {}".format(sql_command))
        status, output = subprocess.getstatusoutput(sql_command)
        if status == 0:
            return output
        else:
            raise RuntimeError("Failed to run SQL command -> {}".format(output))

    @staticmethod
    def check_slave_status(sql_command):
        """
        Checks Slave's status output for fails
        :param sql_command: The formulated SQL command to be passed to run_sql_command()
        :return: True if Slave up and running properly
        :return: Raise a RuntimeError is something wrong with slave
        """

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
        """
        Method for dropping blank PS users(for 5.6 version). In PS 5.7 there are no blank users created.
        :param sql_conn: MySQL Client connection string
        :return: True if success or raise RuntimeError exception from run_sql_command() method
        """
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
    def run_sql_create_user(mysql_master_client_cmd):
        sql_create_user = '{} -e "CREATE USER \'repl\'@\'%\' IDENTIFIED BY \'Baku12345\'"'
        sql_grant = '{} -e "GRANT REPLICATION SLAVE ON *.* TO \'repl\'@\'%\'"'
        # Create user
        RunnerTestMode.run_sql_command(sql_create_user.format(mysql_master_client_cmd))
        # Grant user
        RunnerTestMode.run_sql_command(sql_grant.format(mysql_master_client_cmd))

    @staticmethod
    def create_slave_datadir(basedir, num):
        """
        Static method for creating slave datadir
        :param basedir: Basedir path
        :param num: The number for slave
        :return: created slave datadir path
        """
        slave_datadir = "{}/node{}".format(basedir, num)
        if os.path.exists(slave_datadir):
            try:
                logger.debug("Removing old slave datadir...")
                shutil.rmtree(slave_datadir)
            except Exception as err:
                logger.error("An error while removing directory {}".format(slave_datadir))
                logger.error(err)

        try:
            logger.debug("Creating slave datadir...")
            os.makedirs("{}/node{}".format(basedir, num))
        except Exception as err:
            logger.error("An error while creating directory {}".format(slave_datadir))
            logger.error(err)
        else:
            return slave_datadir

    @staticmethod
    def create_slave_connection_file(basedir, num):
        """
        Static method for creating slave mysql client connection file
        :param basedir: Basedir path
        :param num: The number for slave
        :return: True on success
        :raise: RuntimeError on fail
        """
        with open("{}/cl_node{}".format(basedir, num), 'w+') as clfile:
            conn = "{}/bin/mysql -A -uroot -S{}/sock{}.sock --force test".format(basedir, basedir, num)
            clfile.write(conn)
            # give u+x to this file
            chmod = "chmod u+x {}/cl_node{}".format(basedir, num)
            status, output = subprocess.getstatusoutput(chmod)

            if status == 0:
                logger.debug("chmod succeeded for {}/cl_node{}".format(basedir, num))
                return True
            else:
                raise RuntimeError("Failed to chmod {}/cl_node{}".format(basedir, num))

    @staticmethod
    def create_slave_shutdown_file(basedir, num):
        """
        Static method for creating shutdown file for slave
        :param basedir: Basedir path
        :param num: The number for slave
        :return: True on success
        :raise: RuntimeError on fail
        """
        with open("{}/stop_node{}".format(basedir, num), 'w+') as stop_file:
            shutdown_slave = "{}/bin/mysqladmin -uroot -S{}/sock{}.sock shutdown".format(basedir, basedir, num)
            stop_file.write(shutdown_slave)
            # give u+x to this file
            chmod = "chmod u+x {}/stop_node{}".format(basedir, num)
            status, output = subprocess.getstatusoutput(chmod)

            if status == 0:
                logger.debug("chmod succeeded for {}/stop_node{}".format(basedir, num))
                return True
            else:
                raise RuntimeError("Failed to chmod {}/stop_node{}".format(basedir, num))

    @staticmethod
    def slave_shutdown(basedir, num):
        shutdown_cmd = "{}/stop_node{}".format(basedir, num)
        status, output = subprocess.getstatusoutput(shutdown_cmd)
        if status == 0:
            logger.debug("OK: Slave shutdown")
            return True
        else:
            raise RuntimeError("FAILED: Slave shutdown")

    @staticmethod
    def get_gtid_address(full_backup_dir):
        """
        This method is going to open xtrabackup_binlog_info file inside full backup dir.
        :param full_backup_dir: The full backup directory path
        :return: The GTID position
        """
        file_name = "{}/{}".format(full_backup_dir, 'xtrabackup_binlog_info')
        with open(file_name, 'r') as binlog_file:
            return binlog_file.readline().split('\t')[2][:-1]

    @staticmethod
    def get_gtid_xtrabackup_slave_info(full_backup_dir):
        """
        Parsing xtrabackup_slave_info
        :param full_backup_dir: Full backup directory path
        :return: String of SET GLOBAL gtid_purged=
        :raise: I/O Error if failed
        """
        file_name = "{}/{}".format(full_backup_dir, 'xtrabackup_slave_info')
        with open(file_name, 'r') as slave_info:
            return slave_info.readline()[:-1]

    @staticmethod
    def get_log_file_log_pos(full_backup_dir):
        """
        The static method for getting master_log_file and master_log_pos from xtrabackup_binlog_info.
        Note: for now using this for PS 5.5.
        :param full_backup_dir: Full backup directory path
        :return: Tuple of (MASTER_LOG_FILE, MASTER_LOG_POS)
        """
        file_name = "{}/{}".format(full_backup_dir, 'xtrabackup_binlog_info')
        with open(file_name, 'r') as binlog_file:
            parse_me = binlog_file.readline()
            splitted = parse_me.split('\t')
            return splitted[0], splitted[1][:-1]

    @staticmethod
    def get_log_file_log_pos_slave(full_backup_dir):
        """
        The static method for getting master_log_file and master_log_pos from xtrabackup_binlog_info.
        Note: for now using this for PS 5.5.
        :param full_backup_dir: Full backup directory path
        :return: Tuple of (MASTER_LOG_FILE, MASTER_LOG_POS)
        """
        file_name = "{}/{}".format(full_backup_dir, 'xtrabackup_slave_info')
        with open(file_name, 'r') as slave_info:
            parse_me = slave_info.readline()
            splitted = parse_me.split(',')
            #MASTER_LOG_FILE = splitted[0].split('=')[1].replace("\'", "")
            #MASTER_LOG_POS = splitted[1].split('=')[1]
            return splitted[0].split('=')[1].replace("\'", ""), splitted[1].split('=')[1]

    def run_change_master(self,
                          basedir,
                          full_backup_dir,
                          mysql_slave_client_cmd,
                          mysql_master_client_cmd,
                          is_slave=None):
        """
        Method for making ordinary server as slave
        :param basedir: Basedir path(it is for checking the passed PS version)
        :param full_backup_dir: Full backup directory path
        :param mysql_slave_client_cmd: Slave client string
        :param mysql_master_client_cmd: Master client string
        :param is_slave: flag for passing if set global gtid_purged grabbed from slave or not
        :return: True if succes or raise RuntimeError exception fom run_sql_command()
        """

        logger.debug("Started to make this new server as slave...")
        sql_port = "{} -e 'select @@port'"
        if '5.5' in basedir:
            sql_change_master = '{} -e "CHANGE MASTER TO MASTER_HOST=\'{}\', ' \
                            'MASTER_USER=\'{}\', MASTER_PASSWORD=\'{}\', ' \
                            'MASTER_PORT={}, ' \
                            'MASTER_LOG_FILE=\'{}\', ' \
                            'MASTER_LOG_POS={}"'
        else:
            sql_change_master = '{} -e "CHANGE MASTER TO MASTER_HOST=\'{}\', ' \
                            'MASTER_USER=\'{}\', MASTER_PASSWORD=\'{}\', ' \
                            'MASTER_PORT={}, MASTER_AUTO_POSITION=1"'
        start_slave = "{} -e 'start slave'"
        show_slave_status = "{} -e 'show slave status\G'"
        # Getting port from master
        port = self.run_sql_command(sql_port.format(mysql_master_client_cmd))
        # Run reset master on slave fix for -> https://github.com/ShahriyarR/MySQL-AutoXtraBackup/issues/157
        reset_master = "{} -e 'reset master'"
        self.run_sql_command(reset_master.format(mysql_slave_client_cmd))

        if '5.5' not in basedir:
            if is_slave is None:
                # Run SET GLOBAL gtid_purged, get from master's xtrabackup_binlog_info
                gtid_pos = self.get_gtid_address(full_backup_dir=full_backup_dir)
                gtid_purged = '{} -e \'set global gtid_purged=\"{}\"\''.format(
                              mysql_slave_client_cmd, gtid_pos)
                self.run_sql_command(gtid_purged)
            else:
                # Run SET GLOBAL gtid_purged, get from slave's xtrabackup_slave_info
                sql_cmd = self.get_gtid_xtrabackup_slave_info(full_backup_dir=full_backup_dir)
                gtid_purged = '{} -e \"{}\"'.format(mysql_slave_client_cmd, sql_cmd)
                self.run_sql_command(gtid_purged)

        # Change master
        if '5.5' in basedir:
            if is_slave is None:
                file_pos = self.get_log_file_log_pos(full_backup_dir=full_backup_dir)
            else:
                file_pos = self.get_log_file_log_pos_slave(full_backup_dir=full_backup_dir)
            self.run_sql_command(
                sql_change_master.format(mysql_slave_client_cmd,
                                         '127.0.0.1',
                                         'repl',
                                         'Baku12345',
                                         port[7:],
                                         file_pos[0],
                                         file_pos[1]))
        else:
            self.run_sql_command(
                sql_change_master.format(mysql_slave_client_cmd, '127.0.0.1', 'repl', 'Baku12345', port[7:]))
        # Start Slave
        self.run_sql_command(start_slave.format(mysql_slave_client_cmd))
        # Check Slave output for errors
        sleep(20)
        self.check_slave_status(show_slave_status.format(mysql_slave_client_cmd))

        # Populating dsns table with slave info
        slave_port = self.run_sql_command(sql_port.format(mysql_slave_client_cmd))
        self.populate_dsns_table(sql_conn=mysql_master_client_cmd, slave_port=slave_port[7:])

        return True

    def wipe_backup_prepare_copyback(self, basedir):
        """
        Method Backup + Prepare and Copy-back actions.
        It is also going to create slave server from backup of master and start.
        :param basedir: The basedir path of MySQL
        :return: Success if no exception raised from methods
        """
        c_count = 0
        for options in ConfigGenerator(config=self.conf).options_combination_generator(self.mysql_options):
            c_count = c_count + 1
            options = " ".join(options)
            if '5.7' in basedir:
                options = options + " " + self.df_mysql_options.format(basedir, c_count)
            else:
                options = options + " " + self.df_mysql_options.format(c_count)
            logger.debug("*********************************")
            logger.debug("Starting cycle{}".format(c_count))
            logger.debug("Will start MySQL with {}".format(options))
            # Passing options to start MySQL
            if self.clone_obj.wipe_server_all(basedir_path=basedir, options=options):
                # Specifying directories and passing to WrapperForBackupTest class
                full_dir = self.backupdir + "/cycle{}".format(c_count) + "/full"
                inc_dir = self.backupdir + "/cycle{}".format(c_count) + "/inc"
                backup_obj = WrapperForBackupTest(config=self.conf,
                                                  full_dir=full_dir,
                                                  inc_dir=inc_dir,
                                                  basedir=basedir)
                # Take backups
                logger.debug("Started to run run_all_backup()")
                if backup_obj.run_all_backup():
                    prepare_obj = WrapperForPrepareTest(config=self.conf,
                                                        full_dir=full_dir,
                                                        inc_dir=inc_dir)
                    # Prepare backups
                    logger.debug("Started to run run_prepare_backup()")
                    if prepare_obj.run_prepare_backup():
                        if hasattr(self, 'make_slaves'):
                            logger.debug("make_slaves is defined so will create slaves!")
                            # Creating slave datadir
                            slave_datadir = self.create_slave_datadir(basedir=basedir, num=1)
                            # Doing some stuff for creating slave server env
                            prepare_obj.run_xtra_copyback(datadir=slave_datadir)
                            prepare_obj.giving_chown(datadir=slave_datadir)
                            slave_full_options = self.prepare_start_slave_options(basedir=basedir,
                                                                                  slave_number=1,
                                                                                  options=options)

                            prepare_obj.start_mysql_func(start_tool="{}/start_dynamic".format(basedir),
                                                         options=slave_full_options)
                            # Creating connection file for new node
                            self.create_slave_connection_file(basedir=basedir, num=1)
                            # Creating shutdown file for new node
                            self.create_slave_shutdown_file(basedir=basedir, num=1)

                            # Checking if node is up
                            logger.debug("Pausing a bit here...")
                            sleep(10)
                            chk_obj = CheckEnv(config=self.conf)
                            check_options = "--user={} --socket={}/sock{}.sock".format('root', basedir, 1)
                            chk_obj.check_mysql_uptime(options=check_options)
                            # Make this node to be slave
                            mysql_master_client_cmd = RunBenchmark(config=self.conf).get_mysql_conn(basedir=basedir)
                            # Create replication user on master server
                            self.run_sql_create_user(mysql_master_client_cmd)
                            # Drop blank users if PS version is 5.6 from master server
                            if '5.6' in basedir or '5.5' in basedir:
                                self.drop_blank_mysql_users(mysql_master_client_cmd)
                            full_backup_dir = prepare_obj.recent_full_backup_file()
                            mysql_slave_client_cmd = RunBenchmark(config=self.conf).get_mysql_conn(basedir=basedir,
                                                                                                   file_name="cl_node{}".format(
                                                                                                       1))
                            # Creating dsns table
                            self.create_dsns_table(mysql_master_client_cmd)

                            # Running change master and some other commands here
                            if self.run_change_master(basedir=basedir,
                                                      full_backup_dir="{}/{}".format(full_dir, full_backup_dir),
                                                      mysql_master_client_cmd=mysql_master_client_cmd,
                                                      mysql_slave_client_cmd=mysql_slave_client_cmd):
                                sleep(10)

                            logger.debug("Starting actions for second slave here...")
                            # Actions for second slave, it is going to be started from slave backup
                            full_dir_2 = self.backupdir + "/cycle{}".format(c_count) + "/slave_backup" + "/full"
                            inc_dir_2 = self.backupdir + "/cycle{}".format(c_count) + "/slave_backup" + "/inc"
                            # Create config for this slave node1 here
                            logger.debug("Generating special config file for second slave")
                            cnf_obj = ConfigGenerator(config=self.conf)
                            slave_conf_path = self.backupdir + "/cycle{}".format(c_count)
                            if ('5.7' in basedir) and ('2_4_ps_5_7' in self.conf):
                                slave_conf_file = 'xb_2_4_ps_5_7_slave.conf'
                            elif ('5.6' in basedir) and ('2_4_ps_5_6' in self.conf):
                                slave_conf_file = 'xb_2_4_ps_5_6_slave.conf'
                            elif ('5.6' in basedir) and ('2_3_ps_5_6' in self.conf):
                                slave_conf_file = 'xb_2_3_ps_5_6_slave.conf'
                            elif ('5.5' in basedir) and ('2_3_ps_5_5' in self.conf):
                                slave_conf_file = 'xb_2_3_ps_5_5_slave.conf'
                            elif ('5.5' in basedir) and ('2_4_ps_5_5' in self.conf):
                                slave_conf_file = 'xb_2_4_ps_5_5_slave.conf'

                            cnf_obj.generate_config_files(test_path=self.testpath,
                                                          conf_file=slave_conf_file,
                                                          basedir=basedir,
                                                          datadir="{}/node{}".format(basedir, 1),
                                                          sock_file="{}/sock{}.sock".format(basedir, 1),
                                                          backup_path=slave_conf_path)
                            # DO backup here
                            backup_obj_2 = WrapperForBackupTest(config="{}/{}".format(slave_conf_path,
                                                                                      slave_conf_file),
                                                                full_dir=full_dir_2,
                                                                inc_dir=inc_dir_2,
                                                                basedir=basedir)
                            if backup_obj_2.all_backup():
                                # DO prepare here
                                prepare_obj_2 = WrapperForPrepareTest(config="{}/{}".format(slave_conf_path,
                                                                                            slave_conf_file),
                                                                      full_dir=full_dir_2,
                                                                      inc_dir=inc_dir_2)
                                if prepare_obj_2.run_prepare_backup():
                                    # Creating slave datadir
                                    slave_datadir_2 = self.create_slave_datadir(basedir=basedir, num=2)
                                    prepare_obj_2.run_xtra_copyback(datadir=slave_datadir_2)
                                    prepare_obj_2.giving_chown(datadir=slave_datadir_2)
                                    slave_full_options = self.prepare_start_slave_options(basedir=basedir,
                                                                                          slave_number=2,
                                                                                          options=options)

                                    prepare_obj_2.start_mysql_func(start_tool="{}/start_dynamic".format(basedir),
                                                                   options=slave_full_options)
                                    # Creating connection file for new node
                                    self.create_slave_connection_file(basedir=basedir, num=2)
                                    # Creating shutdown file for new node
                                    self.create_slave_shutdown_file(basedir=basedir, num=2)
                                    logger.debug("Pausing a bit here...")
                                    sleep(10)
                                    check_options_2 = "--user={} --socket={}/sock{}.sock".format('root', basedir, 2)
                                    chk_obj.check_mysql_uptime(options=check_options_2)

                                    mysql_slave_client_cmd_2 = RunBenchmark(config=self.conf).get_mysql_conn(basedir=basedir,
                                                                                                             file_name="cl_node{}".format(2))
                                    full_backup_dir_2 = prepare_obj_2.recent_full_backup_file()
                                    if self.run_change_master(basedir=basedir,
                                                              full_backup_dir="{}/{}".format(
                                                                              full_dir_2, full_backup_dir_2),
                                                              mysql_master_client_cmd=mysql_master_client_cmd,
                                                              mysql_slave_client_cmd=mysql_slave_client_cmd_2,
                                                              is_slave=True):
                                        sleep(10)

                            # Running on master
                            self.run_pt_table_checksum(basedir=basedir)

                            # Shutdown slaves
                            self.slave_shutdown(basedir=basedir, num=1)
                            self.slave_shutdown(basedir=basedir, num=2)
                            sleep(5)

                        else:
                            prepare_obj.copy_back_action(options=options)
