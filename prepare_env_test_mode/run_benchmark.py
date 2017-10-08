from general_conf.generalops import GeneralClass
from prepare_env_test_mode.clone_build_start_server import CloneBuildStartServer
import subprocess
import shlex
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
        # Get socket connection path from PS basedir
        sock_cmd = "cat {}/cl_noprompt_nobinary | awk '\{print $4\}'"
        #status, output = subprocess.getstatusoutput(sock_cmd.format(self.basedir))
        try:
            process = subprocess.Popen(shlex.split(sock_cmd.format(self.basedir)), stdout=None, stdin=None, stderr=None)
            output, error = process.communicate()
            print(output)
            return output
        except Exception as err:
            print(err)
            return False
        # if status == 0:
        #     logger.debug("Could get socket connection")
        #     return output
        # else:
        #     logger.error("Socket info failed!")
        #     logger.error(output)
        #     return False

    def get_mysql_conn(self):
        # Get mysql client connection
        get_conn = "cat {}/cl_noprompt_nobinary"
        status, output = subprocess.getstatusoutput(get_conn.format(self.basedir))
        if status == 0:
            logger.debug("Here is the mysql client!")
            return output
        else:
            logger.error("Failed to get mysql client connection")
            logger.error(output)
            return False

    def create_db(self, db_name):
        # Creating DB using mysql client
        conn = self.get_mysql_conn()
        sql = "{} -e 'create database {}'"
        status, output = subprocess.getstatusoutput(sql.format(conn, db_name))
        if status == 0:
            logger.debug("Given DB is created!")
            return True
        else:
            logger.error("Failed to create DB")
            logger.error(output)
            return False

    def run_sysbench(self):
        # Running sysbench here; The parameters hard coded here, should figure out how to pass them also
        # TODO: make sysbench run with dynamic values

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


