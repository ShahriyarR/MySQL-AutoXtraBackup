import logging
import logging.handlers
import os
import re
import time
import click
import humanfriendly  # type: ignore
import pid  # type: ignore

from mysql_autoxtrabackup.backup_prepare.prepare import Prepare
from mysql_autoxtrabackup.general_conf import path_config
from mysql_autoxtrabackup.general_conf.generalops import GeneralClass
from mysql_autoxtrabackup.backup_backup.backuper import Backup
from mysql_autoxtrabackup.process_runner.process_runner import ProcessRunner
from logging.handlers import RotatingFileHandler
from sys import exit
from sys import platform as _platform
from typing import Optional

logger = logging.getLogger('')
destinations_hash = {'linux': '/dev/log', 'linux2': '/dev/log', 'darwin': '/var/run/syslog'}


def address_matcher(plt: str) -> str:
    return destinations_hash.get(plt, ('localhost', 514)) # type: ignore


handler = logging.handlers.SysLogHandler(address=address_matcher(_platform))

# Set syslog for the root logger
logger.addHandler(handler)


def print_help(ctx: click.Context, param: None, value: bool) -> None:
    if not value:
        return
    click.echo(ctx.get_help())
    ctx.exit()


def print_version(ctx: click.Context, param: None, value: bool) -> None:
    if not value or ctx.resilient_parsing:
        return
    click.echo(
        "Developed by Shahriyar Rzayev from Azerbaijan PUG(http://azepug.az)")
    click.echo("Link : https://github.com/ShahriyarR/MySQL-AutoXtraBackup")
    click.echo("Email: rzayev.sehriyar@gmail.com")
    click.echo(
        "Based on Percona XtraBackup: https://github.com/percona/percona-xtrabackup/")
    click.echo('MySQL-AutoXtraBackup Version: 2.0')
    ctx.exit()


def check_file_content(file: str) -> Optional[bool]:
    """Check if all mandatory headers and keys exist in file"""
    with open(file, 'r') as config_file:
        file_content = config_file.read()

    config_headers = ["MySQL", "Backup", "Encrypt", "Compress", "Commands"]
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
        "xtra_prepare",
        "start_mysql_command",
        "stop_mysql_command",
        "chown_command"]

    for header in config_headers:
        if header not in file_content:
            raise KeyError(
                "Mandatory header [%s] doesn't exist in %s" %
                (header, file))

    for key in config_keys:
        if key not in file_content:
            raise KeyError(
                "Mandatory key \'%s\' doesn't exists in %s." %
                (key, file))

    return True


def validate_file(file: str) -> Optional[bool]:
    """
    Check for validity of the file given in file path. If file doesn't exist or invalid
    configuration file, throw error.
    """
    if not os.path.isfile(file):
        raise FileNotFoundError("Specified file does not exist.")

    # filename extension should be .cnf
    pattern = re.compile(r'.*\.cnf')

    if pattern.match(file):
        # Lastly the file should have all 5 required headers
        if check_file_content(file):
            return None
    else:
        raise ValueError("Invalid file extension. Expecting .cnf")
    return None


@click.command()
@click.option('--dry-run', is_flag=True, help="Enable the dry run.")
@click.option('--prepare', is_flag=True, help="Prepare/recover backups.")
@click.option('--backup',
              is_flag=True,
              help="Take full and incremental backups.")
@click.option('--version',
              is_flag=True,
              callback=print_version,  # type: ignore
              expose_value=False,
              is_eager=True,
              help="Version information.")
@click.option('--defaults-file',
              default=path_config.config_path_file,
              show_default=True,
              help="Read options from the given file") # type: ignore
@click.option('--tag',
              help="Pass the tag string for each backup")
@click.option('--show-tags',
              is_flag=True,
              help="Show backup tags and exit")
@click.option('-v', '--verbose', is_flag=True,
              help="Be verbose (print to console)")
@click.option('-lf',
              '--log-file',
              default=path_config.log_file_path,
              show_default=True,
              help="Set log file")
@click.option('-l',
              '--log',
              '--log-level',
              default='INFO',
              show_default=True,
              type=click.Choice(['DEBUG',
                                 'INFO',
                                 'WARNING',
                                 'ERROR',
                                 'CRITICAL']),
              help="Set log level")
@click.option('--log-file-max-bytes',
              default=1073741824,
              show_default=True,
              nargs=1,
              type=int,
              help="Set log file max size in bytes")
@click.option('--log-file-backup-count',
              default=7,
              show_default=True,
              nargs=1,
              type=int,
              help="Set log file backup count")
@click.option('--help',
              is_flag=True,
              callback=print_help,  # type: ignore
              expose_value=False,
              is_eager=False,
              help="Print help message and exit.")
@click.pass_context
def all_procedure(ctx, prepare, backup, tag, show_tags,
                  verbose, log_file, log, defaults_file,
                  dry_run, log_file_max_bytes,
                  log_file_backup_count):
    options = GeneralClass(defaults_file)
    logging_options = options.logging_options
    backup_options = options.backup_options

    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s [%(module)s:%(lineno)d] %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')

    if verbose:
        ch = logging.StreamHandler()
        # control console output log level
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    if log_file:
        try:
            if logging_options.get('log_file_max_bytes') and logging_options.get('log_file_backup_count'):
                file_handler = RotatingFileHandler(log_file, mode='a',
                                                   maxBytes=int(str(logging_options.get('log_file_max_bytes'))),
                                                   backupCount=int(str(logging_options.get('log_file_backup_count'))))
            else:
                file_handler = RotatingFileHandler(log_file, mode='a',
                                                   maxBytes=log_file_max_bytes, backupCount=log_file_backup_count)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except PermissionError as err:
            exit("{} Please consider to run as root or sudo".format(err))

    # set log level in order: 1. user argument 2. config file 3. @click default
    if log is not None:
        logger.setLevel(log)
    elif logging_options.get('log_level'):
        logger.setLevel(str(logging_options.get('log_level')))
    else:
        # this is the fallback default log-level.
        logger.setLevel('INFO')

    validate_file(defaults_file)
    pid_file = pid.PidFile(piddir=backup_options.get('pid_dir'))

    try:
        with pid_file:  # User PidFile for locking to single instance
            dry_run_ = dry_run
            if dry_run_:
                dry_run_ = 1
                logger.warning("Dry run enabled!")
            if (prepare is False and
                    backup is False and
                    verbose is False and
                    dry_run is False and
                    show_tags is False):
                print_help(ctx, None, value=True)

            elif show_tags and defaults_file:
                backup_ = Backup(config=defaults_file)
                backup_.show_tags(backup_dir=str(backup_options.get('backup_dir')))
            elif prepare:
                prepare_ = Prepare(config=defaults_file, dry_run=dry_run_, tag=tag)
                prepare_.prepare_backup_and_copy_back()
            elif backup:
                backup_ = Backup(config=defaults_file, dry_run=dry_run_, tag=tag)
                backup_.all_backup()

    except (pid.PidFileAlreadyLockedError, pid.PidFileAlreadyRunningError) as error:
        if float(str(backup_options.get('pid_runtime_warning'))) and time.time() - os.stat(
                pid_file.filename).st_ctime > float(str(backup_options.get('pid_runtime_warning'))):
            pid.fh.seek(0)
            pid_str = pid.fh.read(16).split("\n", 1)[0].strip()
            logger.warning("Pid file already exists or Pid already running! : ", str(error))
            logger.critical(
                "Backup (pid: " + pid_str + ") has been running for logger than: " + str(
                    humanfriendly.format_timespan(
                        backup_options.get('pid_runtime_warning'))))

    except pid.PidFileUnreadableError as error:
        logger.warning("Pid file can not be read: " + str(error))
    except pid.PidFileError as error:
        logger.warning("Generic error with pid file: " + str(error))

    logger.info("Xtrabackup command history:")
    for i in ProcessRunner.xtrabackup_history_log:
        logger.info(str(i))
    logger.info("Autoxtrabackup completed successfully!")
    return True


if __name__ == "__main__":
    all_procedure()
