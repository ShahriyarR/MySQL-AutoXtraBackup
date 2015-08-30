#!/opt/Python-3.3.2/bin/python3

import configparser
from os.path import isfile

class GeneralClass:

    def __init__(self, config='/etc/bck.conf'):

        if isfile(config):
            con = configparser.ConfigParser()
            con.read(config)
            bolme = con.sections()

            DB = bolme[0]
            self.mysql = con[DB]['mysql']
            self.mycnf = con[DB]['mycnf']

            # Testing with MariaDB Galera Cluster ###############
            self.maria_cluster_cnf = con[DB]['maria_cluster_cnf']
            ######################################################

            self.mysqladmin = con[DB]['mysqladmin']
            self.myuseroption = con[DB]['useroption']
            self.xtrabck = con[DB]['xtra']


            ######################################################

            self.xtrabck_prepare = con[DB]['xtra_prepare']
            self.datadir = con[DB]['datadir']
            self.tmpdir = con[DB]['tmpdir']
            self.tmp = con[DB]['tmp']

            BCK = bolme[1]
            self.backupdir = con[BCK]['backupdir']
            self.full_dir = self.backupdir + '/full'
            self.inc_dir = self.backupdir + '/inc'
            self.backup_tool = con[BCK]['backup_tool']
            self.archive_dir = con[BCK]['archive_dir']

            RM = bolme[2]
            self.remote_conn = con[RM]['remote_conn']
            self.remote_dir = con[RM]['remote_dir']

            CM = bolme[3]
            self.start_mysql = con[CM]['start_mysql_command']
            self.stop_mysql = con[CM]['stop_mysql_command']
            self.mkdir_command = con[CM]['mkdir_command']
            self.chown_command = con[CM]['chown_command']
            self.mariadb_cluster_bootstrap = con[CM]['mariadb_cluster_bootstrap']
        else:
            print("Missing config file : /etc/bck.conf")