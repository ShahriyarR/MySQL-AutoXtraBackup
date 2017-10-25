import click
from master_backup_script.backuper import Backup
from backup_prepare.prepare import Prepare
from partial_recovery.partial import PartialRecovery
from general_conf.generalops import GeneralClass
from prepare_env_test_mode.runner_test_mode import RunnerTestMode
from sys import platform as _platform
import pid
import time
import re
import os
import humanfriendly
import logging
import logging.handlers
import sys


logger = logging.getLogger('')


destinations_hash = {'linux':'/dev/log', 'linux2': '/dev/log', 'darwin':'/var/run/syslog'}

def address_matcher(plt):
    return destinations_hash.get(plt, ('localhost', 514))

handler = logging.handlers.SysLogHandler(address=address_matcher(_platform))

# Set syslog for the root logger
logger.addHandler(handler)


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(
        "Developed by Shahriyar Rzayev from Azerbaijan MUG(http://mysql.az)")
    click.echo("Link : https://github.com/ShahriyarR/MySQL-AutoXtraBackup")
    click.echo("Email: rzayev.shahriyar@yandex.com")
    click.echo(
        "Based on Percona XtraBackup: https://github.com/percona/percona-xtrabackup/")
    click.echo('MySQL-AutoXtraBackup Version: 1.4.9')
    ctx.exit()


def check_file_content(file):
    """Check if all mandatory headers and keys exist in file"""
    with open(file, 'r') as config_file:
        file_content = config_file.read()
 
    config_headers = ["MySQL", "Backup", "Encrypt", "Compress", "Commands", "TestConf"]
    config_keys = [
        "mysql",
        "mycnf",
        "mysqladmin",
        "mysql_user",
        "mysql_password",
        "mysql_host",
        "datadir",
        "tmpdir",
        "backupdir",
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


def validate_file(file):
    """
    Check for validity of the file given in file path. If file doesn't exist or invalid
    configuration file, throw error.
    """
    if os.path.isfile(file):
        # filename extension should be .conf
        pattern = re.compile(r'.*\.conf')

        if pattern.match(file):
            # Lastly the file should have all 5 required headers
            if check_file_content(file):
                return
        else:
            raise ValueError("Invalid file extension. Expecting .conf")
    else:
        raise FileNotFoundError("Specified file does not exist.")


@click.command()
@click.option('--dry_run', is_flag=True, help="Enable the dry run.")
@click.option('--prepare', is_flag=True, help="Prepare/recover backups.")
@click.option(
    '--backup',
    is_flag=True,
    help="Take full and incremental backups.")
@click.option(
    '--partial',
    is_flag=True,
    help="Recover specified table (partial recovery).")
@click.option(
    '--version',
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True,
    help="Version information.")
@click.option('--defaults_file', default='/etc/bck.conf',
              help="Read options from the given file")
@click.option('-v', '--verbose', is_flag=True,
              help="Be verbose (print to console)")
@click.option('-l',
              '--log',
              default='WARNING',
              type=click.Choice(['DEBUG',
                                 'INFO',
                                 'WARNING',
                                 'ERROR',
                                 'CRITICAL']),
              help="Set log level")
@click.option(
    '--test_mode',
    is_flag=True,
    help="Enable test mode.Must be used with --defaults_file and only for TESTs for XtraBackup")

def all_procedure(prepare, backup, partial, verbose, log, defaults_file, dry_run, test_mode):
    logger.setLevel(log)
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    if verbose:
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    validate_file(defaults_file)
    config = GeneralClass(defaults_file)

    pid_file = pid.PidFile(piddir=config.pid_dir)

    try:
        with pid_file:  # User PidFile for locking to single instance
            if (not prepare) and (not backup) and (
                    not partial) and (not defaults_file) and (not dry_run) and (not test_mode):
                print("ERROR: you must give an option, run with --help for available options")
                logger.critical("Aborting!")
                sys.exit(-1)
            elif test_mode and defaults_file:
                # TODO: do staff here to implement all in one things for running test mode
                logger.warning("Enabled Test Mode!!!")
                logger.debug("Starting Test Mode")
                test_obj = RunnerTestMode(config=defaults_file)
                for basedir in test_obj.basedirs:
                    if ('5.7' in basedir) and ('2_4_ps_5_7' in defaults_file):
                        test_obj.wipe_backup_prepare_copyback(basedir=basedir)
                    elif ('5.6' in basedir) and ('2_4_ps_5_6' in defaults_file):
                        test_obj.wipe_backup_prepare_copyback(basedir=basedir)
                    elif ('5.6' in basedir) and ('2_3' in defaults_file):
                        test_obj.wipe_backup_prepare_copyback(basedir=basedir)
                    else:
                        logger.error("Please pass proper already generated config file!")
                        logger.error("Please check also if you have run prepare_env.bats file")
            elif prepare and not test_mode:
                if not dry_run:
                    a = Prepare(config=defaults_file)
                    a.prepare_backup_and_copy_back()
                else:
                    logger.warning("Dry run enabled!")
                    logger.warning("Do not recover/copy-back in this mode!")
                    a = Prepare(config=defaults_file, dry_run=1)
                    a.prepare_backup_and_copy_back()
                # print("Prepare")
            elif backup and not test_mode:
                if not dry_run:
                    b = Backup(config=defaults_file)
                    b.all_backup()
                else:
                    logger.warning("Dry run enabled!")
                    b = Backup(config=defaults_file, dry_run=1)
                    b.all_backup()
                # print("Backup")
            elif partial:
                if not dry_run:
                    c = PartialRecovery(config=defaults_file)
                    c.final_actions()
                else:
                    logger.critical("Dry run is not implemented for partial recovery!")
    except pid.PidFileAlreadyLockedError as error:
        if hasattr(config, 'pid_runtime_warning'):
            if time.time() - os.stat(pid_file.filename).st_ctime > config.pid_runtime_warning:
                pid.fh.seek(0)
                pid_str = pid.fh.read(16).split("\n", 1)[0].strip()
                logger.critical(
                    "Backup (pid: " + pid_str + ") has been running for logger than: " + str(
                        humanfriendly.format_timespan(
                            config.pid_runtime_warning)))
        # logger.warn("Pid file already exists: " + str(error))
    except pid.PidFileAlreadyRunningError as error:
        if hasattr(config, 'pid_runtime_warning'):
            if time.time() - os.stat(pid_file.filename).st_ctime > config.pid_runtime_warning:
                pid.fh.seek(0)
                pid_str = pid.fh.read(16).split("\n", 1)[0].strip()
                logger.critical(
                    "Backup (pid: " + pid_str + ") has been running for logger than: " + str(
                        humanfriendly.format_timespan(
                            config.pid_runtime_warning)))
        # logger.warn("Pid already running: " + str(error))
    except pid.PidFileUnreadableError as error:
        logger.warning("Pid file can not be read: " + str(error))
    except pid.PidFileError as error:
        logger.warning("Generic error with pid file: " + str(error))


if __name__ == "__main__":
    all_procedure()
