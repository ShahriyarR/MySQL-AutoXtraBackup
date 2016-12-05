#!/opt/Python-3.3.2/bin/python3

import configparser
from os.path import isfile

import logging
logger = logging.getLogger(__name__)

class GeneralClass:

    def __init__(self, config='/etc/bck.conf'):

        if isfile(config):
            con = configparser.ConfigParser()
            con.read(config)

            DB = con['MySQL']
            self.mysql = DB['mysql']
            self.mycnf = DB['mycnf']

            ######################################################

            self.mysqladmin = DB['mysqladmin']
            self.mysql_user = DB['mysql_user']
            self.mysql_password = DB['mysql_password']
            self.mysql_socket = DB['mysql_socket']
            self.mysql_port = DB['mysql_port']


            ######################################################

            self.xtrabck_prepare = DB['xtra_prepare']
            self.datadir = DB['datadir']
            self.tmpdir = DB['tmpdir']
            self.tmp = DB['tmp']

            BCK = con['Backup']
            self.backupdir = BCK['backupdir']
            self.full_dir = self.backupdir + '/full'
            self.inc_dir = self.backupdir + '/inc'
            self.backup_tool = BCK['backup_tool']
            if 'full_backup_interval' in BCK:
                self.full_backup_interval = BCK['full_backup_interval']
            else:
                self.full_backup_interval = 86400
            if 'archive_dir' in BCK:
                self.archive_dir = BCK['archive_dir']

            if 'Remote' in con:
                RM = con['Remote']
                if 'remote_conn' in RM:
                    self.remote_conn = RM['remote_conn']
                if 'remote_dir' in RM:
                    self.remote_dir = RM['remote_dir']

            CM = con['Commands']
            self.start_mysql = CM['start_mysql_command']
            self.stop_mysql = CM['stop_mysql_command']
            self.mkdir_command = CM['mkdir_command']
            self.chown_command = CM['chown_command']
            self.systemd_start_mysql = CM['systemd_start_mysql']
            self.systemd_stop_mysql = CM['systemd_stop_mysql']
            self.systemd_start_mariadb = CM['systemd_start_mariadb']
            self.systemd_stop_mariadb = CM['systemd_stop_mariadb']

        else:
            logger.critical("Missing config file : /etc/bck.conf")