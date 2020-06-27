import configparser
from os.path import isfile
import humanfriendly  # type: ignore
import logging
from general_conf import path_config
from typing import Dict
logger = logging.getLogger(__name__)


class GeneralClass:

    def __init__(self, config: str = path_config.config_path_file) -> None:
        if isfile(config):
            self.con = configparser.ConfigParser()
            self.con.read(config)
        else:
            logger.critical("Missing config file : {}".format(path_config.config_path_file))

    def mysql_options(self) -> Dict[str, str]:
        section = 'MySQL'
        return {'mysql': self.con.get(section, 'mysql'),
                'mycnf': self.con.get(section, 'mycnf'),
                'mysqladmin': self.con.get(section, 'mysqladmin'),
                'mysql_user': self.con.get(section, 'mysql_user'),
                'mysql_password': self.con.get(section, 'mysql_password'),
                'mysql_socket': self.con.get(section, 'mysql_socket'),
                'mysql_host': self.con.get(section, 'mysql_host'),
                'mysql_port': self.con.get(section, 'mysql_port'),
                'data_dir': self.con.get(section, 'data_dir')}

    def logging_options(self) -> Dict[str, str]:
        section = 'Logging'
        return {'log_level': self.con.get(section, 'log_level'),
                'log_file_max_bytes': self.con.get(section, 'log_file_max_bytes'),
                'log_file_backup_count': self.con.get(section, 'log_file_backup_count')}

    def compression_options(self) -> Dict[str, str]:
        section = 'Compress'
        return {'compress': self.con.get(section, 'compress'),
                'compress_chunk_size': self.con.get(section, 'compress_chunk_size'),
                'compress_threads': self.con.get(section, 'compress_threads'),
                'decompress': self.con.get(section, 'decompress'),
                'remove_original': self.con.get(section, 'remove_original')}

    def xbstream_options(self) -> Dict[str, str]:
        section = 'Xbstream'
        return {'xbstream': self.con.get(section, 'xbstream'),
                'stream': self.con.get(section, 'stream'),
                'xbstream_options': self.con.get(section, 'xbstream_options'),
                'xbs_decrypt': self.con.get(section, 'xbs_decrypt')}

    def command_options(self) -> Dict[str, str]:
        section = 'Commands'
        return {'start_mysql_command': self.con.get(section, 'start_mysql_command'),
                'stop_mysql_command': self.con.get(section, 'stop_mysql_command'),
                'chown_command': self.con.get(section, 'chown_command')}

    def encryption_options(self) -> Dict[str, str]:
        section = 'Encrypt'
        return {'xbcrypt': self.con.get(section, 'xbcrypt'),
                'encrypt': self.con.get(section, 'encrypt'),
                'encrypt_key': self.con.get(section, 'enrypt_key'),
                'encrypt_key_file': self.con.get(section, 'encrypt_key_file'),
                'encrypt_threads': self.con.get(section, 'encrypt_threads'),
                'encrypt_chunk_size': self.con.get(section, 'encrypt_chunk_size'),
                'decrypt': self.con.get(section, 'decrypt'),
                'remove_original': self.con.get(section, 'remove_original')}

    def backup_archive_options(self) -> Dict[str, str]:
        section = 'Backup'
        # backward compatible with old config 'max_archive_size' and newer 'archive_max_size'
        archive_max_size = self.con.get(section, 'max_archive_size')
        if archive_max_size:
            archive_max_size = humanfriendly.parse_size(archive_max_size)
        else:
            archive_max_size = humanfriendly.parse_size(self.con.get(section, 'archive_max_size'))

        # backward compatible with old config 'max_archive_duration' and newer 'archive_max_duration'
        archive_max_duration = self.con.get(section, 'max_archive_duration')
        if archive_max_duration:
            archive_max_duration = humanfriendly.parse_timespan(archive_max_duration)
        else:
            archive_max_duration = humanfriendly.parse_timespan(self.con.get(section, 'archive_max_size'))

        return {'archive_dir': self.con.get(section, 'archive_dir'),
                'prepare_archive': self.con.get(section, 'prepare_archive'),
                'move_archive': self.con.get(section, 'move_archive'),
                'archive_max_size': archive_max_size,  # type: ignore
                'archive_max_duration': archive_max_duration  # type: ignore
                }

    def backup_options(self) -> Dict[str, str]:
        section = 'Backup'
        return {'pid_dir': self.con.get(section, 'pid_dir', fallback='/tmp/'),
                'tmp_dir': self.con.get(section, 'tmp_dir'),
                'pid_runtime_warning': humanfriendly.parse_timespan(self.con.get(section, 'pid_runtime_warning')),  # type: ignore
                'backup_dir': self.con.get(section, 'backup_dir'),
                'full_dir': self.con.get(section, 'backup_dir') + '/full',
                'inc_dir': self.con.get(section, 'backup_dir') + '/inc',
                'backup_tool': self.con.get(section, 'backup_tool'),
                'prepare_tool': self.con.get(section, 'prepare_tool'),
                'xtra_backup': self.con.get(section, 'xtra_backup'),
                'xtra_prepare_options': self.con.get(section, 'xtra_prepare_options'),
                'xtra_options': self.con.get(section, 'xtra_options'),
                'full_backup_interval': humanfriendly.parse_timespan(self.con.get(section, 'full_backup_interval',
                                                                                  fallback=86400)),  # type: ignore
                'partial_list': self.con.get(section, 'partial_list')}
