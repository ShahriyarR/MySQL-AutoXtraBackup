#!/opt/Python-3.3.2/bin/python3

import click
from master_backup_script.backuper import Backup
from backup_prepare.prepare import Prepare
from partial_recovery.partial import PartialRecovery
from general_conf.generalops import GeneralClass
from sys import platform as _platform
import pid

import logging
import logging.handlers

logger = logging.getLogger('')

handler = None
if _platform == "linux" or _platform == "linux2":
    # linux
    handler = logging.handlers.SysLogHandler(address='/dev/log')
elif _platform == "darwin":
    # MAC OS X
    handler = logging.handlers.SysLogHandler(address = '/var/run/syslog')
else:
    handler = logging.handlers.SysLogHandler(address=('localhost',514))

# Set syslog for the root logger
logger.addHandler(handler)

def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo("Developed by Shahriyar Rzayev from Azerbaijan MUG(http://mysql.az)")
    click.echo("Link : https://github.com/ShahriyarR/MySQL-AutoXtraBackup")
    click.echo("Email: rzayev.shahriyar@yandex.com")
    click.echo("Based on Percona XtraBackup: https://launchpad.net/percona-xtrabackup")
    click.echo('MySQL-AutoXtrabackup Version 1.3.0')
    ctx.exit()


@click.command()
@click.option('--prepare', is_flag=True, help="Prepare/recover backups.")
@click.option('--backup', is_flag=True, help="Take full and incremental backups.")
@click.option('--partial', is_flag=True, help="Recover specified table (partial recovery).")
@click.option('--version', is_flag=True, callback=print_version, expose_value=False, is_eager=True, help="Version information.")
@click.option('-v', '--verbose', is_flag=True, help="Be verbose (print to console)")
@click.option('-l', '--log', default='WARNING', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']),  help="Set log level")


def all_procedure(prepare, backup, partial, verbose, log):
    logger.setLevel(log)
    config = GeneralClass()
    if (verbose):
        logger.addHandler(logging.StreamHandler())
    try:
        with pid.PidFile(piddir=config.pid_dir): # User PidFile for locking to single instance
            if (not prepare) and (not backup) and (not partial):
                print("ERROR: you must give an option, run with --help for available options")
            elif prepare:
                a = Prepare()
                a.prepare_backup_and_copy_back()
                #print("Prepare")
            elif backup:
                b = Backup()
                b.all_backup()
                #print("Backup")
            elif partial:
                c = PartialRecovery()
                c.final_actions()
    except pid.PidFileAlreadyLockedError as error:
        logger.error("Pid file already exists: " + str(error))
    except pid.PidFileAlreadyRunningError as error:
        logger.error(error)
        print(error)
    except pid.PidFileUnreadableError as error:
        logger.critical("Pid file can not be read: " + str(error))
    except pid.PidFileError as error:
        logger.critical("Generic error with pid file: " + str(error))


if __name__ == "__main__":
    all_procedure()