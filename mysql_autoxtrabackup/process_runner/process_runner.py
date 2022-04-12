import datetime
import logging
import re
import shlex
import subprocess
from subprocess import PIPE, STDOUT
from typing import List, Optional

from mysql_autoxtrabackup.configs import path_config
from mysql_autoxtrabackup.configs.generalops import GeneralClass

logger = logging.getLogger(__name__)


class ProcessHandler(GeneralClass):
    """
    Class to run a command with real-time logging for process

    centralizes logic for subprocess calls, and is available to all other classes (Prepare, Backup, etc)
    """

    def __init__(self, config: str = path_config.config_path_file) -> None:
        self.conf = config
        GeneralClass.__init__(self, self.conf)
        self._xtrabackup_history_log = [
            [
                "command",
                "xtrabackup_function",
                "start time",
                "end time",
                "duration",
                "exit code",
            ]
        ]

    @property
    def xtrabackup_history_log(self) -> List[List[str]]:
        return self._xtrabackup_history_log

    def run_command(self, command: Optional[str]) -> bool:
        """
        executes a prepared command, enables real-time console & log output.

        This function should eventually be used for all subprocess calls.

        :param command: bash command to be executed
        :type command: str
        :return: True if success, False if failure
        :rtype: bool
        """
        # filter out password from argument list, print command to execute

        filtered_command = re.sub("--password='?\w+'?", "--password='*'", command)  # type: ignore
        logger.info(f"SUBPROCESS STARTING: {str(filtered_command)}")
        subprocess_args = self.command_to_args(command_str=command)
        # start the command subprocess
        cmd_start = datetime.datetime.now()
        with subprocess.Popen(subprocess_args, stdout=PIPE, stderr=STDOUT) as process:
            for line in process.stdout:  # type: ignore
                logger.debug(
                    "[{}:{}] {}".format(
                        subprocess_args[0],
                        process.pid,
                        line.decode("utf-8").strip("\n"),
                    )
                )
        logger.info(
            f"SUBPROCESS {subprocess_args[0]} COMPLETED with exit code: {process.returncode}"
        )

        cmd_end = datetime.datetime.now()
        self.summarize_process(subprocess_args, cmd_start, cmd_end, process.returncode)
        # return True or False.
        if process.returncode == 0:
            return True
        else:
            raise ChildProcessError(f"SUBPROCESS FAILED! >> {filtered_command}")

    @staticmethod
    def command_to_args(command_str: Optional[str]) -> List[str]:
        """
        convert a string bash command to an arguments list, to use with subprocess

        Most autoxtrabackup code creates a string command, e.g. "xtrabackup --prepare --target-dir..."
        If we run a string command with subprocess.Popen, we require shell=True.
        shell=True has security considerations (below), and we run autoxtrabackup with privileges (!).
        https://docs.python.org/3/library/subprocess.html#security-considerations
        So, convert to an args list and call Popen without shell=True.

        :param command_str: string command to execute as a subprocess
        :type command_str: str
        :return: list of args to pass to subprocess.Popen.
        :rtype: list
        """
        if isinstance(command_str, list):
            # already a list
            args = command_str
        elif isinstance(command_str, str):
            args = shlex.split(command_str)
        else:
            raise TypeError
        logger.debug(f"subprocess args are: {args}")
        return args

    @staticmethod
    def represent_duration(
        start_time: datetime.datetime, end_time: datetime.datetime
    ) -> str:
        # https://gist.github.com/thatalextaylor/7408395
        duration_delta = end_time - start_time
        seconds = int(duration_delta.seconds)
        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        if days > 0:
            return "%dd%dh%dm%ds" % (days, hours, minutes, seconds)
        elif hours > 0:
            return "%dh%dm%ds" % (hours, minutes, seconds)
        elif minutes > 0:
            return "%dm%ds" % (minutes, seconds)
        else:
            return "%ds" % (seconds,)

    def summarize_process(
        self,
        args: List[str],
        cmd_start: datetime.datetime,
        cmd_end: datetime.datetime,
        return_code: int,
    ) -> bool:
        cmd_root: str = args[0].split("/")[-1:][0]
        xtrabackup_function = None
        if cmd_root == "xtrabackup":
            if "--backup" in args:
                xtrabackup_function = "backup"
            elif "--prepare" in args and "--apply-log-only" not in args:
                xtrabackup_function = "prepare"
            elif "--prepare" in args:
                xtrabackup_function = "prepare/apply-log-only"

        if cmd_root != "pigz":
            # this will be just the pigz --version call
            self._xtrabackup_history_log.append(
                [
                    cmd_root,
                    str(xtrabackup_function),
                    cmd_start.strftime("%Y-%m-%d %H:%M:%S"),
                    cmd_end.strftime("%Y-%m-%d %H:%M:%S"),
                    self.represent_duration(cmd_start, cmd_end),
                    str(return_code),
                ]
            )
        return True


ProcessRunner = ProcessHandler()
