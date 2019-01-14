import logging
import re
import subprocess
import sys
import time

from subprocess import PIPE, STDOUT

from general_conf.generalops import GeneralClass
from general_conf import path_config

logger = logging.getLogger(__name__)


class ProcessRunner(GeneralClass):

    def __init__(self, config=path_config.config_path_file):
        """
        Class to run an xtrabackup command with logging

        centralizes logic for calls to xtrabackup, available to all other classes (Prepare, Backup, etc)
        """
        self.conf = config
        GeneralClass.__init__(self, self.conf)

    @staticmethod
    def run_xtrabackup_command(xtrabackup_command):
        """
        executes a prepared xtrabackup command

        This function unifies calls to xtrabackup, and to enables real-time console & log output.

        :param xtrabackup_command: bash 'xtrabackup' command to be executed
        :type xtrabackup_command: str
        :return: True if success, False if failure
        :rtype: bool
        """
        # todo: implement this method
        # some defensive statements to make sure it's only xtrabackup commands using this function for now.
        # Should work for any subprocess we want real-time logging for
        assert 'xtrabackup' in xtrabackup_command, "invalid xtrabackup command sent to run_xtrabackup_command()"
        # todo: some logic to neatly summarize xtrabackup actions taken over the course of autoxtrabackup

        # filter out password from argument list, print command to execute
        filtered_xtrabackup_cmd = re.sub("--password='?\w+'?", "--password='*'", xtrabackup_command)
        logger.debug("SUBPROCESS STARTING: {}".format(filtered_xtrabackup_cmd))

        # start the xtrabackup process
        process = subprocess.Popen(xtrabackup_command, stdout=PIPE, stderr=STDOUT, shell=True)
        logger.debug("SUBPROCESS PID: {}".format(process.pid))

        # real time logging/stdout output
        cmd_root = filtered_xtrabackup_cmd.split(" ")[0].split("/")[-1]
        for line in iter(process.stdout.readline, b''):
            fixed_line = line.decode("utf-8")
            sys.stdout.write(fixed_line)
            logger.debug("SPC {} | {}".format(cmd_root, fixed_line.strip("\n")))

        # There can be a race condition as subprocess is exiting
        # sleep() to ensure exit code is accurate
        # 2 seconds is probably way too much (?) ...
        time.sleep(2)
        exit_code = process.poll()
        logger.debug("SUBPROCESS {} COMPLETED with exit code: {}".format(cmd_root, exit_code))

        # return True or False.
        # todo: optionally raise error instead of return false
        # todo: cnt'd or, if any subprocess fails, can we stop in a recoverable state?
        if exit_code == 0:
            return True
        else:
            return False
