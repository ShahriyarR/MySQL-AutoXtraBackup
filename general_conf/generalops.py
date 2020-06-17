import configparser
from os.path import isfile
import humanfriendly
import logging
from general_conf import path_config
logger = logging.getLogger(__name__)


class GeneralClass:

    def __init__(self, config=path_config.config_path_file):

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

            LOG = con['Logging']
            if 'log' in LOG:
                self.log_level = LOG['log']
            if 'log_file_max_bytes' in LOG:
                self.log_file_max_bytes = LOG['log_file_max_bytes']
            if 'log_file_backup_count' in LOG:
                self.log_file_backup_count = LOG['log_file_backup_count']

            BCK = con['Backup']
            self.pid_dir = BCK['pid_dir'] if 'pid_dir' in BCK else "/tmp/"
            self.tmpdir = BCK['tmp_dir']
            if 'pid_runtime_warning' in BCK:
                self.pid_runtime_warning = humanfriendly.parse_timespan(
                    BCK['pid_runtime_warning'])
            self.backupdir = BCK['backup_dir']
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
            if 'prepare_archive' in BCK:
                self.prepare_archive = BCK['prepare_archive']
            if 'move_archive' in BCK:
                self.move_archive = BCK['move_archive']
            # backward compatible with old config 'max_archive_size' and newer 'archive_max_size'
            if 'max_archive_size' in BCK:
                self.archive_max_size = humanfriendly.parse_size(BCK['max_archive_size'])
            elif 'archive_max_size' in BCK:
                self.archive_max_size = humanfriendly.parse_size(BCK['archive_max_size'])
            # backward compatible with old config 'max_archive_duration' and newer 'archive_max_duration'
            if 'max_archive_duration' in BCK:
                self.archive_max_duration = humanfriendly.parse_timespan(BCK['max_archive_duration'])
            elif 'archive_max_duration' in BCK:
                self.archive_max_duration = humanfriendly.parse_timespan(BCK['archive_max_duration'])
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

            # Will be generated only for test environment.
            # Not generated for production things.
            if 'TestConf' in con:
                TEST = con['TestConf']
                if 'ps_branches' in TEST:
                    self.ps_branches = TEST['ps_branches']
                if 'pxb_branches' in TEST:
                    self.pxb_branches = TEST['pxb_branches']
                if 'gitcmd' in TEST:
                    self.gitcmd = TEST['gitcmd']
                if 'pxb_gitcmd' in TEST:
                    self.pxb_gitcmd = TEST['pxb_gitcmd']
                if 'testpath' in TEST:
                    self.testpath = TEST['testpath']
                if 'incremental_count' in TEST:
                    self.incremental_count = TEST['incremental_count']
                if 'xb_configs' in TEST:
                    self.xb_configs = TEST['xb_configs']
                if 'default_mysql_options' in TEST:
                    self.default_mysql_options = TEST['default_mysql_options']
                if 'mysql_options' in TEST:
                    self.mysql_options = TEST['mysql_options']
                if 'make_slaves' in TEST:
                    self.make_slaves = TEST['make_slaves']

        else:
            logger.critical("Missing config file : {}".format(path_config.config_path_file))