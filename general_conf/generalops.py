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
            categories = con.sections()

            DB = categories[0]
            self.mysql = con[DB]['mysql']
            self.mycnf = con[DB]['mycnf']

            ######################################################

            self.mysqladmin = con[DB]['mysqladmin']
            self.mysql_user = con[DB]['mysql_user']
            self.mysql_password = con[DB]['mysql_password']
            self.mysql_socket = con[DB]['mysql_socket']
            self.mysql_port = con[DB]['mysql_port']


            ######################################################

            self.xtrabck_prepare = con[DB]['xtra_prepare']
            self.datadir = con[DB]['datadir']
            self.tmpdir = con[DB]['tmpdir']
            self.tmp = con[DB]['tmp']

            BCK = categories[1]
            self.backupdir = con[BCK]['backupdir']
            self.full_dir = self.backupdir + '/full'
            self.inc_dir = self.backupdir + '/inc'
            self.backup_tool = con[BCK]['backup_tool']
            if 'archive_dir' in con[BCK]:
                self.archive_dir = con[BCK]['archive_dir']

            RM = categories[2]
            if 'remote_conn' in con[RM]:
                self.remote_conn = con[RM]['remote_conn']
            if 'remote_dir' in con[RM]:
                self.remote_dir = con[RM]['remote_dir']

            CM = categories[3]
            self.start_mysql = con[CM]['start_mysql_command']
            self.stop_mysql = con[CM]['stop_mysql_command']
            self.mkdir_command = con[CM]['mkdir_command']
            self.chown_command = con[CM]['chown_command']
            self.systemd_start_mysql = con[CM]['systemd_start_mysql']
            self.systemd_stop_mysql = con[CM]['systemd_stop_mysql']
            self.systemd_start_mariadb = con[CM]['systemd_start_mariadb']
            self.systemd_stop_mariadb = con[CM]['systemd_stop_mariadb']

        else:
            logger.critical("Missing config file : /etc/bck.conf")