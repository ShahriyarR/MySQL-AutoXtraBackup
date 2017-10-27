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
        tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp.bind(('', 0))
        addr, port = tcp.getsockname()
        tcp.close()
        return port

    def prepare_start_slave_options(self, basedir, slave_number, options):
        tmpdir="--tmpdir={}/node{}".format(basedir, slave_number)
        datadir = "--datadir={}/node{}".format(basedir, slave_number)
        socket = "--socket={}/sock{}.sock".format(basedir, slave_number)
        port = "--port={}".format(self.get_free_tcp_port())
        log_error = "--log-error={}/log/node{}".format(basedir, slave_number)
        return " ".join([tmpdir, datadir, socket, port, log_error, options])

    @staticmethod
    def run_pt_table_checksum(conn_options):
        command = "pt-table-checksum {}"
        status, output = subprocess.getstatusoutput(command.format(conn_options))
        if status == 0:
            logger.debug("pt-table-checksum succeeded on master")
            return True
        else:
            logger.error("pt-table-checksum command failed")
            logger.error(output)
            return False

    def run_change_master(self, basedir, file_name=None):
        sql_create_user = '{} -e "CREATE USER \'repl\'@\'%\' IDENTIFIED BY \'Baku12345\'"'
        sql_grant = '{} -e "GRANT REPLICATION SLAVE ON *.* TO \'repl\'@\'%\'"'
        sql_change_master = '{} -e "CHANGE MASTER TO MASTER_HOST=\'{}\', MASTER_USER=\'{}\', MASTER_PASSWORD=\'{}\', MASTER_PORT={}, MASTER_AUTO_POSITION=1"'
        mysql_slave_client_cmd = RunBenchmark(config=self.conf).get_mysql_conn(basedir=basedir, file_name=file_name)
        mysql_master_client_cmd = RunBenchmark(config=self.conf).get_mysql_conn(basedir=basedir)
        # Getting port from master
        sql_port = "{} -e 'select @@port'"
        status, port = subprocess.getstatusoutput(sql_port.format(mysql_master_client_cmd))
        # Create user
        status, output = subprocess.getstatusoutput(sql_create_user.format(mysql_master_client_cmd))
        # Grant user
        status, output = subprocess.getstatusoutput(sql_grant.format(mysql_master_client_cmd))
        # Change master
        status, output = subprocess.getstatusoutput(sql_change_master.format(mysql_slave_client_cmd, 'localhost', 'repl', 'Baku12345', port[7:]))
        if status == 0:
            logger.debug("run_change_master() succeeded")
            return True
        else:
            logger.error("Something failed in run_change_master()")
            logger.error(output)
            return False




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
                backup_obj.run_all_backup()
                prepare_obj = WrapperForPrepareTest(config=self.conf, full_dir=full_dir, inc_dir=inc_dir)
                # Prepare backups
                prepare_obj.run_prepare_backup()

                if hasattr(self, 'slave_count'):
                    for i in range(int(self.slave_count)):
                        slave_datadir = "{}/node{}".format(basedir, i)
                        if os.path.exists(slave_datadir):
                            try:
                                shutil.rmtree(slave_datadir)
                            except Exception as err:
                                logger.error("An error while removing directory {}".format(slave_datadir))
                                logger.error(err)

                        try:
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
                                            logger.error("Failed to chmod")
                                            logger.error(output)


                                    # Checking if node is up
                                    chk_obj = CheckEnv(config=self.conf)
                                    check_options = "--user={} --socket={}/sock{}.sock".format('root', basedir, i)
                                    if chk_obj.check_mysql_uptime(options=check_options):
                                        # Make this node to be slave
                                        self.run_change_master(basedir=basedir, file_name="cl_node{}".format(i))
                                        # Running on master
                                        #self.run_pt_table_checksum(conn_options=check_options)
                else:
                    prepare_obj.copy_back_action(options=options)