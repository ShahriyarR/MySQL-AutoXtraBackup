from general_conf.generalops import GeneralClass
from prepare_env_test_mode.clone_build_start_server import CloneBuildStartServer
import subprocess
import logging
logger = logging.getLogger(__name__)


class RunBenchmark:
    """
    General class for running all kind of Benchmarks; For now running sysbench against started server.
    """

    def __init__(self):
        self.testpath = GeneralClass().testpath
        self.basedir = CloneBuildStartServer().get_basedir()

    def get_sock(self):
        # Get socket connection path from PS basedir(Pythonic way)
        logger.debug("Trying to get socket file...")
        file_name = "{}/cl_noprompt_nobinary"
        with open(file_name.format(self.basedir)) as config:
            sock_file = config.read().split()[3][2:]

        return sock_file

    def get_mysql_conn(self):
        # Get mysql client connection
        logger.debug("Trying to get mysql client connection...")
        get_conn = "cat {}/cl_noprompt_nobinary"
        status, output = subprocess.getstatusoutput(get_conn.format(self.basedir))
        if status == 0:
            logger.debug("Could get mysql client")
            return output
        else:
            logger.error("Failed to get mysql client connection")
            logger.error(output)
            return False

    def create_db(self, db_name):
        # Creating DB using mysql client
        conn = self.get_mysql_conn()
        sql = "{} -e 'create database if not exists {} '"
        logger.debug("Trying to create DB...")
        status, output = subprocess.getstatusoutput(sql.format(conn, db_name))
        if status == 0:
            logger.debug("Given DB is created")
            return True
        else:
            logger.error("Failed to create DB")
            logger.error(output)
            return False

    def run_sysbench(self):
        # Running sysbench here; The parameters hard coded here, should figure out how to pass them also
        # TODO: make sysbench run with dynamic values
        # TODO: make sysbench different possible kind of runs

        # Created sysbench DB
        db_name = "sysbench_test_db"
        self.create_db(db_name=db_name)

        sock_name = self.get_sock()

        sysbench_cmd = "sysbench /usr/share/sysbench/oltp_insert.lua " \
              "--table-size={} " \
              "--tables={} " \
              "--mysql-db={} " \
              "--mysql-user=root  " \
              "--threads={} " \
              "--db-driver=mysql " \
              "--mysql-socket={} prepare"

        logger.debug("Started to run Sysbench...")

        status, output = subprocess.getstatusoutput(sysbench_cmd.format(1000,
                                                                        100,
                                                                        db_name,
                                                                        100,
                                                                        sock_name))

        if status == 0:
            logger.debug("Sysbench succeeded!")
            return True
        else:
            logger.error("Failed to run sysbench")
            logger.error(output)
            return False


