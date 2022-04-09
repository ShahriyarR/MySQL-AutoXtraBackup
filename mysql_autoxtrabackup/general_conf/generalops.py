import configparser
import logging
from os.path import isfile
from typing import Dict, Union

import humanfriendly  # type: ignore

from . import path_config

logger = logging.getLogger(__name__)


class GeneralClass:
    def __init__(self, config: str = path_config.config_path_file) -> None:
        if isfile(config):
            self.con = configparser.ConfigParser()
            self.con.read(config)
        else:
            logger.critical(f"Missing config file : {path_config.config_path_file}")

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
            "xtra_backup": self.con.get(section, "xtra_backup", fallback=None),  # type: ignore
            "xtra_options": self.con.get(section, "xtra_options", fallback=None),  # type: ignore
            "full_backup_interval": humanfriendly.parse_timespan(
                self.con.get(section, "full_backup_interval", fallback="86400.0")
            ),
        }
