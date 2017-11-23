from general_conf.generalops import GeneralClass
from prepare_env_test_mode.clone_build_start_server import CloneBuildStartServer
import subprocess
import logging
logger = logging.getLogger(__name__)


class RunBenchmark:
    """
    General class for running all kind of Benchmarks; For now running sysbench against started server.
    """

    def __init__(self, config="/etc/bck.conf"):
        self.conf = config
        self.testpath = GeneralClass(self.conf).testpath
        self.basedir = CloneBuildStartServer(self.conf).get_basedir()

    @staticmethod
    def get_sock(basedir):
        # Get socket connection path from PS basedir(Pythonic way)
        logger.debug("Trying to get socket file...")
        file_name = "{}/cl_noprompt_nobinary"
        with open(file_name.format(basedir)) as config:
            sock_file = config.read().split()[3][2:]

        return sock_file

    @staticmethod
    def get_mysql_conn(basedir, file_name=None):
        # Get mysql client connection
        logger.debug("Trying to get mysql client connection...")
        if file_name is None:
            get_conn = "cat {}/cl_noprompt_nobinary"
            status, output = subprocess.getstatusoutput(get_conn.format(basedir))
        else:
            get_conn = "cat {}/{}"
            status, output = subprocess.getstatusoutput(get_conn.format(basedir, file_name))
        if status == 0:
            logger.debug("Could get mysql client")
            return output
        else:
            logger.error("Failed to get mysql client connection")
            logger.error(output)
            raise RuntimeError("Failed to get mysql client connection")

    @staticmethod
    def run_sql_statement(basedir, sql_statement):
        sql = '{} -e \"{}\"'.format(RunBenchmark.get_mysql_conn(basedir), sql_statement)
        status, output = subprocess.getstatusoutput(sql)
        if status == 0:
            logger.debug("OK: Running -> {}".format(sql))
            return True
        else:
            logger.error("FAILED: running SQL -> {}".format(sql))
            logger.error(output)
            raise RuntimeError("FAILED: running SQL -> {}".format(sql))

    def create_db(self, db_name, basedir):
        # Creating DB using mysql client
        conn = self.get_mysql_conn(basedir)
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

    def run_sysbench_prepare(self, basedir):
        # Running sysbench prepare here; The parameters hard coded here, should figure out how to pass them also
        # TODO: make sysbench run with dynamic values
        # TODO: make sysbench different possible kind of runs

        # Created sysbench DB
        db_name = "sysbench_test_db"
        self.create_db(db_name=db_name, basedir=basedir)

        # Likely to fail here! Pay attention
        sock_name = self.get_sock(basedir)

        sysbench_cmd = "sysbench /usr/share/sysbench/oltp_insert.lua " \
              "--table-size={} " \
              "--tables={} " \
              "--mysql-db={} " \
              "--mysql-user=root  " \
              "--threads={} " \
              "--db-driver=mysql " \
              "--mysql-socket={} prepare"

        logger.debug("Running command -> {}".format(sysbench_cmd.format(1000,
                                                                        100,
                                                                        db_name,
                                                                        100,
                                                                        sock_name)))

        status, output = subprocess.getstatusoutput(sysbench_cmd.format(1000,
                                                                        30,
                                                                        db_name,
                                                                        100,
                                                                        sock_name))

        if status == 0:
            logger.debug("Sysbench succeeded!")
            return True
        else:
            logger.error("Failed to run sysbench")
            logger.error(output)
            raise RuntimeError("Failed to run sysbench")

    def run_sysbench_run(self, basedir):
        # Running sysbench run here
        db_name = "sysbench_test_db"

        sock_name = self.get_sock(basedir)

        sysbench_cmd = "sysbench /usr/share/sysbench/oltp_update_non_index.lua " \
                       "--table-size={} " \
                       "--tables={} " \
                       "--mysql-db={} " \
                       "--mysql-user=root  " \
                       "--threads={} " \
                       "--db-driver=mysql " \
                       "--mysql-socket={} run"

        logger.debug("Running command -> {}".format(sysbench_cmd.format(1000,
                                                                        100,
                                                                        db_name,
                                                                        100,
                                                                        sock_name)))

        status, output = subprocess.getstatusoutput(sysbench_cmd.format(1000,
                                                                        30,
                                                                        db_name,
                                                                        100,
                                                                        sock_name))

        if status == 0:
            logger.debug("Sysbench succeeded!")
            return True
        else:
            logger.error("Failed to run sysbench")
            logger.error(output)
            raise RuntimeError("Failed to run sysbench")
