import logging
import logging.handlers
import os
import re
import time
from logging.handlers import RotatingFileHandler
from sys import exit
from sys import platform as _platform
from typing import Dict

import click
import humanfriendly  # type: ignore
import pid  # type: ignore

from mysql_autoxtrabackup.api import main
from mysql_autoxtrabackup.backup_backup import BackupBuilderChecker
from mysql_autoxtrabackup.backup_backup.backup_tags import BackupTags
from mysql_autoxtrabackup.backup_backup.backuper import Backup
from mysql_autoxtrabackup.backup_prepare.prepare import Prepare
from mysql_autoxtrabackup.general_conf import path_config
from mysql_autoxtrabackup.general_conf.generalops import GeneralClass
from mysql_autoxtrabackup.general_conf.generate_default_conf import (
    GenerateDefaultConfig,
)
from mysql_autoxtrabackup.process_runner.process_runner import ProcessRunner
from mysql_autoxtrabackup.utils import version
from mysql_autoxtrabackup.utils.mysql_cli import MySQLClientHelper

logger = logging.getLogger("")
destinations_hash = {
    "linux": "/dev/log",
    "linux2": "/dev/log",
    "darwin": "/var/run/syslog",
}


def _address_matcher(plt: str) -> str:
    return destinations_hash.get(plt, ("localhost", 514))  # type: ignore


def _handle_logging() -> logging:
    global logger, destinations_hash

    handler = logging.handlers.SysLogHandler(address=_address_matcher(_platform))
    # Set syslog for the root logger
    logger.addHandler(handler)


_handle_logging()


def print_help(ctx: click.Context, param: None, value: bool) -> None:
    if not value:
        return
    click.echo(ctx.get_help())
    ctx.exit()


def _get_version_str() -> str:
    return f"""
Developed by Shahriyar Rzayev from Azerbaijan PUG(http://azepug.az)
Link : https://github.com/ShahriyarR/MySQL-AutoXtraBackup
Email: rzayev.sehriyar@gmail.com
Based on Percona XtraBackup: https://github.com/percona/percona-xtrabackup/
MySQL-AutoXtraBackup Version: {version.VERSION}
    """


def _print_version(ctx: click.Context, param: None, value: bool) -> None:
    if not value or ctx.resilient_parsing:
        return
    click.echo(_get_version_str())
    ctx.exit()


def _check_file_content(file: str) -> bool:
    """Check if all mandatory headers and keys exist in file"""
    with open(file, "r") as config_file:
        file_content = config_file.read()

    config_headers = ["MySQL", "Backup"]
    config_keys = [
        "mysql",
        "mycnf",
        "mysqladmin",
        "mysql_user",
        "mysql_password",
        "mysql_host",
        "datadir",
        "tmp_dir",
        "backup_dir",
        "backup_tool",
    ]

    for header in config_headers:
        if header not in file_content:
            raise KeyError("Mandatory header [%s] doesn't exist in %s" % (header, file))

    for key in config_keys:
        if key not in file_content:
            raise KeyError("Mandatory key '%s' doesn't exists in %s." % (key, file))

    return True


def validate_file(file: str) -> None:
    """
    Check for validity of the file given in file path. If file doesn't exist or invalid
    configuration file, throw error.
    """
    # filename extension should be .cnf
    pattern = re.compile(r".*\.cnf")

    if not os.path.isfile(file):
        raise FileNotFoundError("Specified file does not exist.")

    if not pattern.match(file):
        raise ValueError("Invalid file extension. Expecting .cnf")
    # Lastly the file should have all 2 required headers
    if not _check_file_content(file):
        raise RuntimeError("Config file content validation failed.")


@click.command()
@click.option("--dry-run", is_flag=True, help="Enable the dry run.")
@click.option("--prepare", is_flag=True, help="Prepare/recover backups.")
@click.option(
    "--run-server", is_flag=True, help="Start the FastAPI app for serving API"
)
@click.option("--backup", is_flag=True, help="Take full and incremental backups.")
@click.option(
    "--version",
    is_flag=True,
    callback=_print_version,
    expose_value=False,
    is_eager=True,
    help="Version information.",
)
@click.option(
    "--defaults-file",
    default=path_config.config_path_file,
    show_default=True,
    help="Read options from the given file",
)
@click.option(
    "--generate-config-file",
    is_flag=True,
    is_eager=True,
    help="Create a config file template in default directory",
)
@click.option("--tag", help="Pass the tag string for each backup")
@click.option("--show-tags", is_flag=True, help="Show backup tags and exit")
@click.option("-v", "--verbose", is_flag=True, help="Be verbose (print to console)")
@click.option(
    "-lf",
    "--log-file",
    default=path_config.log_file_path,
    show_default=True,
    help="Set log file",
)
@click.option(
    "-l",
    "--log",
    "--log-level",
    default="INFO",
    show_default=True,
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    help="Set log level",
)
@click.option(
    "--log-file-max-bytes",
    default=1073741824,
    show_default=True,
    nargs=1,
    type=int,
    help="Set log file max size in bytes",
)
@click.option(
    "--log-file-backup-count",
    default=7,
    show_default=True,
    nargs=1,
    type=int,
    help="Set log file backup count",
)
@click.option(
    "--help",
    is_flag=True,
    callback=print_help,  # type: ignore
    expose_value=False,
    is_eager=False,
    help="Print help message and exit.",
)
@click.pass_context
def all_procedure(
    ctx,
    prepare,
    backup,
    run_server,
    tag,
    show_tags,
    verbose,
    log_file,
    log,
    defaults_file,
    generate_config_file,
    dry_run,
    log_file_max_bytes,
    log_file_backup_count,
) -> bool:
    options = GeneralClass(defaults_file)
    logging_options = options.logging_options
    backup_options = options.backup_options
    formatter = _get_formatter()

    if verbose:
        _set_log_level_format(formatter)

    if log_file:
        try:
            file_handler = _get_log_rotate_handler(
                log_file,
                logging_options,
                max_bytes=log_file_max_bytes,
                backup_count=log_file_backup_count,
            )
            _add_log_rotate_handler(file_handler, formatter)
        except PermissionError as err:
            exit(f"{err} Please consider to run as root or sudo")

    # set log level in order: 1. user argument 2. config file 3. @click default
    _set_log_level(log, logging_options)

    validate_file(defaults_file)
    pid_file = pid.PidFile(piddir=backup_options.get("pid_dir"))

    try:
        _run_commands(
            backup,
            backup_options,
            ctx,
            defaults_file,
            dry_run,
            generate_config_file,
            pid_file,
            prepare,
            run_server,
            show_tags,
            tag,
            verbose,
        )

    except (pid.PidFileAlreadyLockedError, pid.PidFileAlreadyRunningError) as error:
        _handle_backup_pid_exception(backup_options, error, pid_file)
    except pid.PidFileUnreadableError as error:
        logger.warning(f"Pid file can not be read: {str(error)}")
    except pid.PidFileError as error:
        logger.warning(f"Generic error with pid file: {str(error)}")

    _log_command_history()
    logger.info("Autoxtrabackup completed successfully!")
    return True


def _run_commands(
    backup,
    backup_options,
    ctx,
    defaults_file,
    dry_run,
    generate_config_file,
    pid_file,
    prepare,
    run_server,
    show_tags,
    tag,
    verbose,
):
    with pid_file:  # User PidFile for locking to single instance
        dry_run_ = dry_run
        if dry_run_:
            dry_run_ = 1
            logger.warning("Dry run enabled!")

        builder_obj = BackupBuilderChecker(config=defaults_file, dry_run=dry_run_)
        tagger = BackupTags(tag, builder_obj)
        mysql_cli = MySQLClientHelper(config=defaults_file)

        if (
            prepare is False
            and backup is False
            and verbose is False
            and dry_run is False
            and show_tags is False
            and run_server is False
            and generate_config_file is False
        ):
            print_help(ctx, None, value=True)

        elif run_server:
            main.run_server()
        elif show_tags and defaults_file:

            Backup(
                config=defaults_file,
                builder_obj=builder_obj,
                tagger=tagger,
                mysql_cli=mysql_cli,
            ).tagger.show_tags(backup_dir=str(backup_options.get("backup_dir")))
        elif generate_config_file:
            GenerateDefaultConfig().generate_config_file()
            logger.info(f"Default config file is generated in {defaults_file}")
        elif prepare:
            Prepare(
                config=defaults_file, dry_run=dry_run_, tag=tag
            ).prepare_backup_and_copy_back()
        elif backup:
            Backup(
                config=defaults_file,
                builder_obj=builder_obj,
                tagger=tagger,
                mysql_cli=mysql_cli,
                dry_run=dry_run_,
                tag=tag,
            ).all_backup()


def _log_command_history():
    logger.info("Xtrabackup command history:")
    for history in ProcessRunner.xtrabackup_history_log:
        logger.info(str(history))


def _add_log_rotate_handler(file_handler, formatter):
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def _handle_backup_pid_exception(backup_options, error, pid_file):
    pid_warning = str(backup_options.get("pid_runtime_warning"))
    if float(pid_warning) and time.time() - os.stat(pid_file.filename).st_ctime > float(
        pid_warning
    ):
        pid.fh.seek(0)
        pid_str = pid.fh.read(16).split("\n", 1)[0].strip()
        pid_warning = str(humanfriendly.format_timespan(pid_warning))
        logger.warning(
            f"Pid file already exists or Pid already running! : {str(error)}",
        )
        logger.critical(
            f"Backup (pid: {pid_str}) has been running for logger than: {pid_warning}"
        )


def _set_log_level(log, logging_options):
    if log is not None:
        logger.setLevel(log)
    elif logging_options.get("log_level"):
        logger.setLevel(str(logging_options.get("log_level")))
    else:
        # this is the fallback default log-level.
        logger.setLevel("INFO")


def _get_log_rotate_handler(
    log_file: str, logging_options: Dict, max_bytes: int, backup_count: int
):
    return RotatingFileHandler(
        log_file,
        mode="a",
        maxBytes=max_bytes or int(str(logging_options.get("log_file_max_bytes"))),
        backupCount=backup_count
        or int(str(logging_options.get("log_file_backup_count"))),
    )


def _get_formatter() -> logging:
    return logging.Formatter(
        fmt="%(asctime)s %(levelname)s [%(module)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def _set_log_level_format(formatter: logging) -> None:
    ch = logging.StreamHandler()
    # control console output log level
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)


if __name__ == "__main__":
    all_procedure()
