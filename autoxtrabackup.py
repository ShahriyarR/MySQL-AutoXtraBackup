#!/usr/local/bin/python3

import click
from master_backup_script.backuper import Backup
from backup_prepare.prepare import Prepare
from partial_recovery.partial import PartialRecovery

def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo("Developed by Shahriyar Rzayev from Azerbaijan MySQL User Community")
    click.echo("Link : https://github.com/ShahriyarR/MySQL-AutoXtraBackup")
    click.echo("Email: rzayev.sehriyar@gmail.com")
    click.echo("Based on Percona XtraBackup: https://launchpad.net/percona-xtrabackup")
    click.echo('MySQL-AutoXtrabackup Version 1.0')
    ctx.exit()


@click.command()
@click.option('--prepare', is_flag=True, help="Prepare/recover backups.")
@click.option('--backup', is_flag=True, help="Take full and incremental backups.")
@click.option('--partial', is_flag=True, help="Recover specified table (partial recovery).")
@click.option('--version', is_flag=True, callback=print_version, expose_value=False, is_eager=True, help="Version information.")


def all_procedure(prepare, backup, partial):
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



if __name__ == "__main__":
    all_procedure()