import configparser
import logging
from os.path import isfile
from typing import Dict
from typing import Union

import humanfriendly  # type: ignore

from . import path_config

logger = logging.getLogger(__name__)


class GeneralClass:
    def __init__(self, config: str = path_config.config_path_file) -> None:
        if isfile(config):
            self.con = configparser.ConfigParser()
            self.con.read(config)
        else:
            logger.critical(
                "Missing config file : {}".format(path_config.config_path_file)
            )

    @property
    def mysql_options(self) -> Dict[str, str]:
        section = "MySQL"
        return {
            "mysql": self.con.get(section, "mysql"),
            "mycnf": self.con.get(section, "mycnf"),
            "mysqladmin": self.con.get(section, "mysqladmin"),
            "mysql_user": self.con.get(section, "mysql_user"),
            "mysql_password": self.con.get(section, "mysql_password"),
            "mysql_socket": self.con.get(section, "mysql_socket", fallback=None),  # type: ignore
            "mysql_host": self.con.get(section, "mysql_host", fallback=None),  # type: ignore
            "mysql_port": self.con.get(section, "mysql_port", fallback=None),  # type: ignore
            "data_dir": self.con.get(section, "datadir"),
        }

    @property
    def logging_options(self) -> Dict[str, str]:
        section = "Logging"
        return {
            "log_level": self.con.get(section, "log"),
            "log_file_max_bytes": self.con.get(section, "log_file_max_bytes"),
            "log_file_backup_count": self.con.get(section, "log_file_backup_count"),
        }

    @property
    def compression_options(self) -> Dict[str, str]:
        section = "Compress"
        return {
            "compress": self.con.get(section, "compress", fallback=None),  # type: ignore
            "compress_chunk_size": self.con.get(section, "compress_chunk_size", fallback=None),  # type: ignore
            "compress_threads": self.con.get(section, "compress_threads", fallback=None),  # type: ignore
            "decompress": self.con.get(section, "decompress", fallback=None),  # type: ignore
            "remove_original": self.con.get(section, "remove_original", fallback=None),  # type: ignore
        }

    @property
    def xbstream_options(self) -> Dict[str, str]:
        section = "Xbstream"
        return {
            "xbstream": self.con.get(section, "xbstream", fallback=None),  # type: ignore
            "stream": self.con.get(section, "stream", fallback=None),  # type: ignore
            "xbstream_options": self.con.get(section, "xbstream_options", fallback=None),  # type: ignore
            "xbs_decrypt": self.con.get(section, "xbs_decrypt", fallback=None),  # type: ignore
        }

    @property
    def command_options(self) -> Dict[str, str]:
        section = "Commands"
        return {
            "start_mysql_command": self.con.get(section, "start_mysql_command"),
            "stop_mysql_command": self.con.get(section, "stop_mysql_command"),
            "chown_command": self.con.get(section, "chown_command"),
        }

    @property
    def encryption_options(self) -> Dict[str, str]:
        section = "Encrypt"
        return {
            "xbcrypt": self.con.get(section, "xbcrypt", fallback=None),  # type: ignore
            "encrypt": self.con.get(section, "encrypt", fallback=None),  # type: ignore
            "encrypt_key": self.con.get(section, "encrypt_key", fallback=None),  # type: ignore
            "encrypt_key_file": self.con.get(section, "encrypt_key_file", fallback=None),  # type: ignore
            "encrypt_threads": self.con.get(section, "encrypt_threads", fallback=None),  # type: ignore
            "encrypt_chunk_size": self.con.get(section, "encrypt_chunk_size", fallback=None),  # type: ignore
            "decrypt": self.con.get(section, "decrypt", fallback=None),  # type: ignore
            "remove_original": self.con.get(section, "remove_original", fallback=None),  # type: ignore
        }

    @property
    def backup_archive_options(self) -> Dict[str, Union[str, float]]:
        section = "Backup"
        # backward compatible with old config 'max_archive_size' and newer 'archive_max_size'
        archive_max_size = self.con.get(section, "max_archive_size", fallback=None)
        if archive_max_size:
            archive_max_size = humanfriendly.parse_size(archive_max_size)
        else:
            if self.con.get(section, "archive_max_size", fallback=None):
                archive_max_size = humanfriendly.parse_size(
                    self.con.get(section, "archive_max_size", fallback=None)
                )

        # backward compatible with old config 'max_archive_duration' and newer 'archive_max_duration'
        archive_max_duration = self.con.get(
            section, "max_archive_duration", fallback=None
        )
        if archive_max_duration:
            archive_max_duration = humanfriendly.parse_timespan(archive_max_duration)
        else:
            if self.con.get(section, "archive_max_size", fallback=None):
                archive_max_duration = humanfriendly.parse_timespan(
                    self.con.get(section, "archive_max_size", fallback=None)
                )

        return {
            "archive_dir": self.con.get(section, "archive_dir", fallback=None),  # type: ignore
            "prepare_archive": self.con.get(section, "prepare_archive", fallback=None),  # type: ignore
            "move_archive": self.con.get(section, "move_archive", fallback=None),  # type: ignore
            "archive_max_size": str(archive_max_size),
            "archive_max_duration": str(archive_max_duration),
        }

    @property
    def backup_options(self) -> Dict[str, Union[str, float]]:
        section = "Backup"
        return {
            "pid_dir": self.con.get(section, "pid_dir", fallback="/tmp/"),
            "tmp_dir": self.con.get(section, "tmp_dir"),
            "pid_runtime_warning": humanfriendly.parse_timespan(
                self.con.get(section, "pid_runtime_warning")
            ),
            "backup_dir": self.con.get(section, "backup_dir"),
            "full_dir": self.con.get(section, "backup_dir") + "/full",
            "inc_dir": self.con.get(section, "backup_dir") + "/inc",
            "backup_tool": self.con.get(section, "backup_tool"),
            "prepare_tool": self.con.get(section, "prepare_tool", fallback=None),  # type: ignore
            "xtra_backup": self.con.get(section, "xtra_backup", fallback=None),  # type: ignore
            "xtra_prepare_options": self.con.get(section, "xtra_prepare_options", fallback=None),  # type: ignore
            "xtra_options": self.con.get(section, "xtra_options", fallback=None),  # type: ignore
            "full_backup_interval": humanfriendly.parse_timespan(
                self.con.get(section, "full_backup_interval", fallback="86400.0")
            ),
            "partial_list": self.con.get(section, "partial_list", fallback=None),  # type: ignore
        }
