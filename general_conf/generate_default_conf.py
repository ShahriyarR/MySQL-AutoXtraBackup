# Generate the default config file dynamically.
# As part of - https://github.com/ShahriyarR/MySQL-AutoXtraBackup/issues/331

from general_conf import path_config
import configparser
from os.path import join, exists
from os import makedirs


class GenerateDefaultConfig:

    def __init__(self, config=path_config.config_path_file):
        self.conf = config
        self.home = path_config.home
        try:
            if not exists(path_config.config_path):
                makedirs(path_config.config_path)
        except:
            pass

    def generate_config_file(self):
        with open(self.conf, 'w+') as cfgfile:
            config = configparser.ConfigParser(allow_no_value=True)
            section1 = 'MySQL'
            config.add_section(section1)
            config.set(section1, "mysql", "/usr/bin/mysql")
            config.set(section1, "mycnf", "")
            config.set(section1, "mysqladmin", "/usr/bin/mysqladmin")
            config.set(section1, "mysql_user", "root")
            config.set(section1, "mysql_password", "")
            config.set(section1, "## Set either mysql_socket only, OR host + port. If both are set mysql_socket is used")
            config.set(section1, "mysql_socket", "/var/lib/mysql/mysql.sock")
            config.set(section1, "#mysql_host", "127.0.0.1")
            config.set(section1, "#mysql_port", "3306")
            config.set(section1, "datadir", "/var/lib/mysql")
            
            # TODO: change this in test_mode related config generator as well
            section2 = 'Logging'
            config.add_section(section2)
            config.set(section2, '#[DEBUG,INFO,WARNING,ERROR,CRITICAL]')
            config.set(section2, 'log', 'DEBUG')
            config.set(section2, 'log_file_max_bytes', '1073741824')
            config.set(section2, 'log_file_backup_count', '7')
            
            section3 = 'Backup'
            config.add_section(section3)
            config.set(section3, "#Optional: set pid directory")
            config.set(section3, "pid_dir", "/tmp/MySQL-AutoXtraBackup")
            config.set(section3, "tmp_dir", join(self.home, "XB_TEST/mysql_datadirs"))
            config.set(section3, "#Optional: set warning if pid of backup us running for longer than X")
            config.set(section3, "pid_runtime_warning", "2 Hours")
            config.set(section3, "backup_dir", join(self.home, "XB_TEST/backup_dir"))
            config.set(section3, "backup_tool", "/usr/bin/xtrabackup")
            config.set(section3, "#Optional: specify different path/version of xtrabackup here for prepare")
            config.set(section3, "#prepare_tool", "")
            config.set(section3, "xtra_prepare", "--apply-log-only")
            config.set(section3, "#Optional: pass additional options for backup stage")
            config.set(section3, "#xtra_backup", "--compact")
            config.set(section3, "#Optional: pass additional options for prepare stage")
            config.set(section3, "#xtra_prepare_options", "--rebuild-indexes")
            config.set(section3,
                       "#Optional: pass general additional options; it will go to both for backup and prepare")
            config.set(section3, "#xtra_options", "--binlog-info=ON --galera-info")
            config.set(section3, "#Optional: set archive and rotation")
            config.set(section3, "#archive_dir", join(self.home, "XB_TEST/backup_archives"))
            config.set(section3, "#prepare_archive", "1")
            config.set(section3, "#move_archive", "0")
            config.set(section3, "#full_backup_interval", "1 day")
            config.set(section3, "#archive_max_size", "100GiB")
            config.set(section3, "#archive_max_duration", "4 Days")
            config.set(section3, "#Optional: WARNING(Enable this if you want to take partial backups). "
                                 "Specify database names or table names.")
            config.set(section3, "#partial_list", "test.t1 test.t2 dbtest")

            section4 = "Compress"
            config.add_section(section4)
            config.set(section4, "#optional")
            config.set(section4, "#Enable only if you want to use compression.")
            config.set(section4, "compress", "quicklz")
            config.set(section4, "compress_chunk_size", "65536")
            config.set(section4, "compress_threads", "4")
            config.set(section4, "decompress", "TRUE")
            config.set(section4, "#Enable if you want to remove .qp files after decompression."
                                 "(Available from PXB 2.3.7 and 2.4.6)")
            config.set(section4, "remove_original", "FALSE")

            section5 = "Encrypt"
            config.add_section(section5)
            config.set(section5, "#Optional")
            config.set(section5, "#Enable only if you want to create encrypted backups")
            config.set(section5, "xbcrypt", "/usr/bin/xbcrypt")
            config.set(section5, "encrypt", "AES256")
            config.set(section5, "#Please note that --encrypt-key and --encrypt-key-file are mutually exclusive")
            config.set(section5, "encrypt_key", 'VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K')
            config.set(section5, "#encrypt_key_file", "/path/to/file/with_encrypt_key")
            config.set(section5, "encrypt_threads", "4")
            config.set(section5, "encrypt_chunk_size", "65536")
            config.set(section5, "decrypt", "AES256")
            config.set(section5, "#Enable if you want to remove .qp files after decompression."
                                 "(Available from PXB 2.3.7 and 2.4.6)")
            config.set(section5, "remove_original", "FALSE")

            section6 = "Xbstream"
            config.add_section(section6)
            config.set(section6, "#EXPERIMENTAL")
            config.set(section6, "#Enable this, if you want to stream your backups")
            config.set(section6, "xbstream", "/usr/bin/xbstream")
            config.set(section6, "stream", "xbstream")
            config.set(section6, "xbstream_options", "-x --parallel=100")
            config.set(section6, "xbs_decrypt", "1")
            config.set(section6, "# WARN, enable this, if you want to stream your backups to remote host")
            config.set(section6, "#remote_stream", "ssh xxx.xxx.xxx.xxx")

            section7 = "Remote"
            config.add_section(section7)
            config.set(section7, "#Optional remote syncing")
            config.set(section7, "#remote_conn", "root@xxx.xxx.xxx.xxx")
            config.set(section7, "#remote_dir", "{}".format(join(self.home, 'Documents')))

            section8 = "Commands"
            config.add_section(section8)
            config.set(section8, "start_mysql_command", "service mysql start")
            config.set(section8, "stop_mysql_command", "service mysql stop")
            config.set(section8, "chown_command", "chown -R mysql:mysql")

            config.write(cfgfile)