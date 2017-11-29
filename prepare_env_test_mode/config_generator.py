from prepare_env_test_mode.clone_build_start_server import CloneBuildStartServer
from prepare_env_test_mode.run_benchmark import RunBenchmark
import configparser
from itertools import product
import logging
logger = logging.getLogger(__name__)


class ConfigGenerator(CloneBuildStartServer):

    def __init__(self, config='/etc/bck.conf'):
        self.conf = config
        super().__init__(config=self.conf)
        # For getting socket file path using RunBenchmark()
        self.benchmark_obj = RunBenchmark()

    @staticmethod
    def generate_config_files(test_path, conf_file, basedir, datadir, sock_file, backup_path=None):
        # This method for generating separate config files for each XB versions based on PS versions
        try:
            if backup_path is None:
                conf_path = "{}/{}".format(test_path, conf_file)
            else:
                conf_path = "{}/{}".format(backup_path, conf_file)
            with open(conf_path, 'w+') as cfgfile:
                config = configparser.ConfigParser(allow_no_value=True)
                section1 = 'MySQL'
                config.add_section(section1)
                config.set(section1, "mysql", "{}/bin/mysql".format(basedir))
                config.set(section1, "mycnf", "")
                config.set(section1, "mysqladmin", "{}/bin/mysqladmin".format(basedir))
                config.set(section1, "mysql_user", "root")
                config.set(section1, "mysql_password", "")
                config.set(section1, "#Use either socket or port + host combination")
                config.set(section1, "mysql_socket", "{}".format(sock_file))
                config.set(section1, "#mysql_host", "127.0.0.1")
                config.set(section1, "#mysql_port", "3306")
                config.set(section1, "datadir", "{}/{}".format(basedir, datadir))

                section2 = 'Backup'
                config.add_section(section2)
                config.set(section2, "#Optional: set pid directory")
                config.set(section2, "pid_dir", "/tmp/MySQL-AutoXtraBackup")
                config.set(section2, "tmpdir", "/home/shahriyar.rzaev/XB_TEST/mysql_datadirs")
                config.set(section2, "#Optional: set warning if pid of backup us running for longer than X")
                config.set(section2, "pid_runtime_warning", "2 Hours")
                if ('5.7' in basedir) and ('2_4' in conf_file):
                    config.set(section2, "backupdir", "/home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_7_x_2_4")
                elif ('5.6' in basedir) and ('2_4' in conf_file):
                    config.set(section2, "backupdir", "/home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_6_x_2_4")
                elif ('5.6' in basedir) and ('2_3' in conf_file):
                    config.set(section2, "backupdir", "/home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_6_x_2_3")
                elif ('5.5' in basedir) and ('2_3' in conf_file):
                    config.set(section2, "backupdir", "/home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_5_x_2_3")
                elif ('5.5' in basedir) and ('2_4' in conf_file):
                    config.set(section2, "backupdir", "/home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_5_x_2_4")
                if '2_4' in conf_file:
                    config.set(section2, "backup_tool",
                               "{}/target/percona-xtrabackup-2.4.x-debug/bin/xtrabackup".format(test_path))
                else:
                    config.set(section2, "backup_tool",
                               "{}/target/percona-xtrabackup-2.3.x-debug/bin/xtrabackup".format(test_path))
                config.set(section2, "#Optional: specify different path/version of xtrabackup here for prepare")
                config.set(section2, "#prepare_tool", "")
                config.set(section2, "xtra_prepare", "--apply-log-only")
                config.set(section2, "#Optional: pass additional options for backup stage")
                config.set(section2, "#xtra_backup", "--compact")
                config.set(section2, "#Optional: pass additional options for prepare stage")
                config.set(section2, "#xtra_prepare_options", "--rebuild-indexes")
                config.set(section2,
                           "#Optional: pass general additional options; it will go to both for backup and prepare")
                config.set(section2, "#xtra_options", "--binlog-info=ON --galera-info")
                if '5.7' in basedir:
                    config.set(section2, "xtra_options", "--slave-info --no-version-check --core-file "
                                                         "--parallel=10 --throttle=40 --check-privileges "
                                                         "--keyring-file-data={}/mysql-keyring/keyring ".format(basedir))
                else:
                    config.set(section2, "xtra_options", "--slave-info --no-version-check --core-file "
                                                         "--parallel=10 --throttle=40 --check-privileges ")
                config.set(section2, "#Optional: set archive and rotation")
                config.set(section2, "#archive_dir", "/home/shahriyar.rzaev/XB_TEST/backup_archives")
                config.set(section2, "#full_backup_interval", "1 day")
                config.set(section2, "#max_archive_size", "100GiB")
                config.set(section2, "#max_archive_duration", "4 Days")
                config.set(section2, "#Optional: WARNING(Enable this if you want to take partial backups). "
                                     "Specify database names or table names.")
                config.set(section2, "#partial_list", "test.t1 test.t2 dbtest")

                section3 = "Compress"
                config.add_section(section3)
                config.set(section3, "#optional")
                config.set(section3, "#Enable only if you want to use compression.")
                config.set(section3, "compress", "quicklz")
                config.set(section3, "compress_chunk_size", "65536")
                config.set(section3, "compress_threads", "4")
                config.set(section3, "decompress", "TRUE")
                config.set(section3, "#Enable if you want to remove .qp files after decompression."
                                     "(Not available yet, will be released with XB 2.3.7 and 2.4.6)")
                config.set(section3, "remove_original", "FALSE")

                section4 = "Encrypt"
                config.add_section(section4)
                config.set(section4, "#Optional")
                config.set(section4, "#Enable only if you want to create encrypted backups")
                if '2_4' in conf_file:
                    config.set(section4, "xbcrypt",
                               "{}/target/percona-xtrabackup-2.4.x-debug/bin/xbcrypt".format(test_path))
                else:
                    config.set(section4, "xbcrypt",
                               "{}/target/percona-xtrabackup-2.3.x-debug/bin/xbcrypt".format(test_path))
                config.set(section4, "encrypt", "AES256")
                config.set(section4, "#Please note that --encrypt-key and --encrypt-key-file are mutually exclusive")
                config.set(section4, "encrypt_key", 'VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K')
                config.set(section4, "#encrypt_key_file", "/path/to/file/with_encrypt_key")
                config.set(section4, "encrypt_threads", "4")
                config.set(section4, "encrypt_chunk_size", "65536")
                config.set(section4, "decrypt", "AES256")
                config.set(section4, "#Enable if you want to remove .qp files after decompression."
                                     "(Not available yet, will be released with XB 2.3.7 and 2.4.6)")
                config.set(section4, "remove_original", "FALSE")

                section5 = "Xbstream"
                config.add_section(section5)
                config.set(section5, "#EXPERIMENTAL")
                config.set(section5, "#Enable this, if you want to stream your backups")
                if '2_4' in conf_file:
                    config.set(section5, "xbstream",
                               "{}/target/percona-xtrabackup-2.4.x-debug/bin/xbstream".format(test_path))
                else:
                    config.set(section5, "xbstream",
                               "{}/target/percona-xtrabackup-2.3.x-debug/bin/xbstream".format(test_path))
                config.set(section5, "stream", "xbstream")
                config.set(section5, "xbstream_options", "-x --parallel=100")
                config.set(section5, "xbs_decrypt", "1")
                config.set(section5, "# WARN, enable this, if you want to stream your backups to remote host")
                config.set(section5, "#remote_stream", "ssh xxx.xxx.xxx.xxx")

                section6 = "Remote"
                config.add_section(section6)
                config.set(section6, "#Optional remote syncing")
                config.set(section6, "#remote_conn", "root@xxx.xxx.xxx.xxx")
                config.set(section6, "#remote_dir", "/home/sh/Documents")

                section7 = "Commands"
                config.add_section(section7)
                config.set(section7, "start_mysql_command", "{}/start".format(basedir))
                config.set(section7, "stop_mysql_command", "{}/stop".format(basedir))
                config.set(section7, "chown_command", "chown -R shahriyar.rzaev:shahriyar.rzaev")

                section8 = "TestConf"
                config.add_section(section8)
                config.set(section8, "ps_branches", "5.5 5.6 5.7")
                config.set(section8, "pxb_branches", "2.3 2.4")
                config.set(section8, "gitcmd",
                                     "--recursive --depth=1 https://github.com/percona/percona-server.git")
                config.set(section8, "pxb_gitcmd", "https://github.com/percona/percona-xtrabackup.git")
                config.set(section8, "testpath", "/home/shahriyar.rzaev/XB_TEST/server_dir")
                config.set(section8, "incremental_count", "3")
                config.set(section8, "xb_configs", "xb_2_4_ps_5_6.conf xb_2_4_ps_5_7.conf xb_2_3_ps_5_6.conf xb_2_3_ps_5_5.conf xb_2_4_ps_5_5.conf")
                config.set(section8, "make_slaves", "1")
                if '5_7' in conf_file:
                    config.set(section8, "default_mysql_options",
                                         "--early-plugin-load=keyring_file.so,"
                                         "--keyring_file_data={}/mysql-keyring/keyring,"
                                         "--log-bin=mysql-bin,--log-slave-updates,--server-id={},"
                                         "--gtid-mode=ON,--enforce-gtid-consistency,--binlog-format=row")
                elif '5_6' in conf_file:
                    config.set(section8, "default_mysql_options",
                                         "--log-bin=mysql-bin,--log-slave-updates,--server-id={},"
                                         "--gtid-mode=ON,--enforce-gtid-consistency,--binlog-format=row")
                elif '5_5' in conf_file:
                    config.set(section8, "default_mysql_options",
                               "--log-bin=mysql-bin,--log-slave-updates,--server-id={},"
                               "--binlog-format=row")

                if '5_7' in conf_file:
                    config.set(section8, "mysql_options",
                                         "--innodb_buffer_pool_size=1G 2G 3G,--innodb_log_file_size=1G 2G 3G,"
                                         "--innodb_page_size=4K 8K 16K 32K")
                elif '5_6' in conf_file:
                    config.set(section8, "mysql_options",
                                         "--innodb_buffer_pool_size=1G 2G 3G,--innodb_log_file_size=1G 2G 3G,"
                                         "--innodb_page_size=4K 8K 16K")
                elif '5_5' in conf_file:
                    config.set(section8, "mysql_options",
                                         "--innodb_buffer_pool_size=1G 2G 3G,--innodb_log_file_size=1G 2G 3G,"
                                         "--innodb_page_size=4K 8K 16K")

                config.write(cfgfile)

        except Exception as err:
            logger.error("Failed to generate config file...")
            logger.error(err)
            return False
        else:
            logger.debug("Config file generated successfully...")
            return True

    def the_main_generator(self):
        # The method for calling config generator based on if statements
        conf_list = self.xb_configs.split()
        basedirs = self.get_basedir()
        print(basedirs)
        print(conf_list)
        for basedir in basedirs:
            for conf_file in conf_list:
                if ('5.7' in basedir) and ('2_4_ps_5_7' in conf_file):
                    self.generate_config_files(test_path=self.testpath,
                                               conf_file=conf_file,
                                               basedir=basedir,
                                               datadir='data',
                                               sock_file=self.benchmark_obj.get_sock(basedir=basedir))
                elif ('5.6' in basedir) and ('2_4_ps_5_6' in conf_file):
                    self.generate_config_files(test_path=self.testpath,
                                               conf_file=conf_file,
                                               basedir=basedir,
                                               datadir='data',
                                               sock_file=self.benchmark_obj.get_sock(basedir=basedir))
                elif ('5.6' in basedir) and ('2_3_ps_5_6' in conf_file):
                    self.generate_config_files(test_path=self.testpath,
                                               conf_file=conf_file,
                                               basedir=basedir,
                                               datadir='data',
                                               sock_file=self.benchmark_obj.get_sock(basedir=basedir))
                elif ('5.5' in basedir) and ('2_4_ps_5_5' in conf_file):
                    self.generate_config_files(test_path=self.testpath,
                                               conf_file=conf_file,
                                               basedir=basedir,
                                               datadir='data',
                                               sock_file=self.benchmark_obj.get_sock(basedir=basedir))
                elif ('5.5' in basedir) and ('2_3_ps_5_5' in conf_file):
                    self.generate_config_files(test_path=self.testpath,
                                               conf_file=conf_file,
                                               basedir=basedir,
                                               datadir='data',
                                               sock_file=self.benchmark_obj.get_sock(basedir=basedir))
                else:
                    continue

        return True

    @staticmethod
    def options_combination_generator(initial_str):
        '''
        Option parser method for creating option combinarotics
        :param initial_str -> mysql_options initial string from config file
        :return List of tuples with option combinations
        '''
        separated_values_list = []

        for i in initial_str.split(','):
            separated_values_list.append(i.split('='))

        all_new_list = []

        for i in separated_values_list:
            k = ["{}={}".format(i[0], j) for j in i[1].split()]
            all_new_list.append(k)

        option_combinations = []

        for i in product(*all_new_list):
            option_combinations.append(i)

        return option_combinations
