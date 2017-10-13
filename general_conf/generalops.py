import configparser
from os.path import isfile
import humanfriendly

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
            self.mysqladmin = DB['mysqladmin']
            self.mysql_user = DB['mysql_user']
            self.mysql_password = DB['mysql_password']
            if 'mysql_socket' in DB:
                self.mysql_socket = DB['mysql_socket']
            if 'mysql_host' in DB:
                self.mysql_host = DB['mysql_host']
            if 'mysql_port' in DB:
                self.mysql_port = DB['mysql_port']
            self.datadir = DB['datadir']
            # self.tmpdir = DB['tmpdir']
            # self.tmp = DB['tmp']
            
            
            BCK = con['Backup']
            if 'pid_dir' in BCK:
                self.pid_dir = BCK['pid_dir']
            else:
                self.pid_dir = "/tmp/"
            self.tmpdir = BCK['tmpdir']
            if 'pid_runtime_warning' in BCK:
                self.pid_runtime_warning = humanfriendly.parse_timespan(
                    BCK['pid_runtime_warning'])
            self.backupdir = BCK['backupdir']
            self.full_dir = self.backupdir + '/full'
            self.inc_dir = self.backupdir + '/inc'
            self.backup_tool = BCK['backup_tool']
            if 'prepare_tool' in BCK:
                self.prepare_tool = BCK['prepare_tool']
            self.xtrabck_prepare = BCK['xtra_prepare']
            if 'xtra_backup' in BCK:
                self.xtra_backup = BCK['xtra_backup']
            if 'xtra_prepare_options' in BCK:
                self.xtra_prepare_options = BCK['xtra_prepare_options']
            if 'xtra_options' in BCK:
                self.xtra_options = BCK['xtra_options'] 
            if 'full_backup_interval' in BCK:
                self.full_backup_interval = humanfriendly.parse_timespan(
                    BCK['full_backup_interval'])
            else:
                self.full_backup_interval = 86400
            if 'archive_dir' in BCK:
                self.archive_dir = BCK['archive_dir']
            if 'max_archive_size' in BCK:
                self.max_archive_size = humanfriendly.parse_size(
                    BCK['max_archive_size'])
            if 'max_archive_duration' in BCK:
                self.max_archive_duration = humanfriendly.parse_timespan(
                    BCK['max_archive_duration'])
            if 'partial_list' in BCK:
                self.partial_list = BCK['partial_list']
                
                
            if 'Remote' in con:
                RM = con['Remote']
                if 'remote_conn' in RM:
                    self.remote_conn = RM['remote_conn']
                if 'remote_dir' in RM:
                    self.remote_dir = RM['remote_dir']

            COM = con['Compress']
            if 'compress' in COM:
                self.compress = COM['compress']
            if 'compress_chunk_size' in COM:
                self.compress_chunk_size = COM['compress_chunk_size']
            if 'compress_threads' in COM:
                self.compress_threads = COM['compress_threads']
            if 'decompress' in COM:
                self.decompress = COM['decompress']
            if 'remove_original' in COM:
                self.remove_original_comp = COM['remove_original']

            ENC = con['Encrypt']
            if 'xbcrypt' in ENC:
                self.xbcrypt = ENC['xbcrypt']
            if 'encrypt' in ENC:
                self.encrypt = ENC['encrypt']
            if 'encrypt_key' in ENC:
                self.encrypt_key = ENC['encrypt_key']
            if 'encrypt_key_file' in ENC:
                self.encrypt_key_file = ENC['encrypt_key_file']
            if 'encrypt_threads' in ENC:
                self.encrypt_threads = ENC['encrypt_threads']
            if 'encrypt_chunk_size' in ENC:
                self.encrypt_chunk_size = ENC['encrypt_chunk_size']
            if 'decrypt' in ENC:
                self.decrypt = ENC['decrypt']
            if 'remove_original' in ENC:
                self.remove_original_enc = ENC['remove_original']

            XBS = con['Xbstream']
            if 'xbstream' in XBS:
                self.xbstream = XBS['xbstream']
            if 'stream' in XBS:
                self.stream = XBS['stream']
            if 'xbstream_options' in XBS:
                self.xbstream_options = XBS['xbstream_options']
            if 'xbs_decrypt' in XBS:
                self.xbs_decrypt = XBS['xbs_decrypt']


            CM = con['Commands']
            self.start_mysql = CM['start_mysql_command']
            self.stop_mysql = CM['stop_mysql_command']
            self.chown_command = CM['chown_command']

            TEST = con['TestConf']
            self.gitcmd = TEST['gitcmd']
            self.testpath = TEST['testpath']
            self.incremental_count = TEST['incremental_count']
            self.xb_configs = TEST['xb_configs']

        else:
            logger.critical("Missing config file : /etc/bck.conf")
