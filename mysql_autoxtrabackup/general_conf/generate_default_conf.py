# Generate the default config file dynamically.
# As part of - https://github.com/ShahriyarR/MySQL-AutoXtraBackup/issues/331

import configparser
import contextlib
from os import makedirs
from os.path import exists, join

from . import path_config


class GenerateDefaultConfig:
    def __init__(self, config: str = path_config.config_path_file) -> None:
        self.conf = config
        self.home = path_config.home
        with contextlib.suppress(FileExistsError, OSError):
            if not exists(path_config.config_path):
                makedirs(path_config.config_path)

    def generate_config_file(self) -> None:
        with open(self.conf, "w+") as cfg_file:
            config = configparser.ConfigParser(allow_no_value=True)
            section1 = "MySQL"
            config.add_section(section1)
            config.set(section1, "mysql", "/usr/bin/mysql")
            config.set(section1, "mycnf", "")
            config.set(section1, "mysqladmin", "/usr/bin/mysqladmin")
            config.set(section1, "mysql_user", "root")
            config.set(section1, "mysql_password", "12345")
            config.set(
                section1,
                "## Set either mysql_socket only, OR host + port. If both are set mysql_socket is used",
            )
            config.set(section1, "mysql_socket", "/var/lib/mysql/mysql.sock")
            config.set(section1, "#mysql_host", "127.0.0.1")
            config.set(section1, "#mysql_port", "3306")
            config.set(section1, "datadir", "/var/lib/mysql")

            section2 = "Logging"
            config.add_section(section2)
            config.set(section2, "#[DEBUG,INFO,WARNING,ERROR,CRITICAL]")
            config.set(section2, "log", "DEBUG")
            config.set(section2, "log_file_max_bytes", "1073741824")
            config.set(section2, "log_file_backup_count", "7")

            section3 = "Backup"
            config.add_section(section3)
            config.set(section3, "#Optional: set pid directory")
            config.set(section3, "pid_dir", "/tmp/MySQL-AutoXtraBackup")
            config.set(section3, "tmp_dir", join(self.home, "XB_TEST/mysql_datadirs"))
            config.set(
                section3,
                "#Optional: set warning if pid of backup us running for longer than X",
            )
            config.set(section3, "pid_runtime_warning", "2 Hours")
            config.set(section3, "backup_dir", join(self.home, "XB_TEST/backup_dir"))
            config.set(section3, "backup_tool", "/usr/bin/xtrabackup")
            config.set(section3, "xtra_options", "--no-server-version-check")
            config.set(section3, "#xtra_prepare_options", "")
            config.set(section3, "#full_backup_interval", "1 day")

            config.write(cfg_file)
