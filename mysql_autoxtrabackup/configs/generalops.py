import configparser
import logging
from dataclasses import dataclass
from os.path import isfile
from typing import Dict, Union

import humanfriendly  # type: ignore

from mysql_autoxtrabackup.configs import path_config
from mysql_autoxtrabackup.configs.generate_default_conf import generate_default_config_file

logger = logging.getLogger(__name__)


def _create_default_config(config: str, missing: str) -> None:
    logger.critical(f"Missing config file : {missing}")
    logger.warning("Creating default config file...")
    generate_default_config_file(config=config)
    logger.info(f"Default config file is generated in {config}")


@dataclass
class GeneralClass:
    config: str = path_config.config_path_file

    def __post_init__(self):
        if not isfile(self.config):
            _create_default_config(self.config, missing=path_config.config_path_file)

        self.con = configparser.ConfigParser()
        self.con.read(self.config)

    @property
    def mysql_options(self) -> Dict[str, str]:
        section = "MySQL"
        return {
            "mysql": self.con.get(section, "mysql"),
            "mycnf": self.con.get(section, "mycnf"),
            "mysqladmin": self.con.get(section, "mysqladmin"),
            "mysql_user": self.con.get(section, "mysql_user"),
            "mysql_password": self.con.get(section, "mysql_password"),
            "mysql_socket": self.con.get(section, "mysql_socket", fallback=None),
            "mysql_host": self.con.get(section, "mysql_host", fallback=None),
            "mysql_port": self.con.get(section, "mysql_port", fallback=None),
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
            "xtra_backup": self.con.get(section, "xtra_backup", fallback=None),
            "xtra_options": self.con.get(section, "xtra_options", fallback=None),
            "xtra_prepare_options": self.con.get(
                section, "xtra_prepare_options", fallback=None
            ),
            "full_backup_interval": humanfriendly.parse_timespan(
                self.con.get(section, "full_backup_interval", fallback="86400.0")
            ),
        }
