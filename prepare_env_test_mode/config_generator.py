from prepare_env_test_mode.clone_build_start_server import CloneBuildStartServer
from prepare_env_test_mode.run_benchmark import RunBenchmark
import configparser
import os
import logging
logger = logging.getLogger(__name__)


class ConfigGenerator(CloneBuildStartServer):

    def __init__(self):
        super().__init__()
        self.benchmark_obj = RunBenchmark()

    def generate_config_files(self):
        # This method for generating separate config files for each XB versions.
        # TODO: For now we need only generate XB 2.4 version of config with started PS 5.7 server
        # TODO: For future I need to figure out how to generate configs for both version, related to PS version
        conf_2_4 = "xb_2_4.conf"
        conf_path = "{}/{}".format(self.testpath, conf_2_4)
        basedir = self.get_basedir()
        try:
            if not os.path.isfile(conf_path):
                with open(conf_path, 'w') as cfgfile:
                    config = configparser.ConfigParser(allow_no_value=True)
                    section1 = 'MySQL'
                    config.add_section("{}".format(section1))
                    config.set("{}".format(section1), "mysql", "{}/bin/mysql".format(basedir))
                    config.set("{}".format(section1), "mycnf", "")
                    config.set("{}".format(section1), "mysqladmin", "{}/bin/mysqladmin".format(basedir))
                    config.set("{}".format(section1), "mysql_user", "root")
                    config.set("{}".format(section1), "mysql_password", "")
                    config.set("{}".format(section1), "#Use either socket or port + host combination")
                    config.set("{}".format(section1), "mysql_socket", "{}".format(self.benchmark_obj.get_sock()))
                    config.set("{}".format(section1), "#mysql_host", "127.0.0.1")
                    config.set("{}".format(section1), "#mysql_port", "3306")
                    config.set("{}".format(section1), "datadir", "{}/data".format(basedir))

                    section2 = 'Backup'
                    config.add_section(section2)
                    config.set(section2, "# Optional: set pid directory")
                    config.set(section2, "pid_dir", "/tmp/MySQL-AutoXtraBackup")
                    config.set(section2, "tmp_dir", "/home/shahriyar.rzaev/XB_TEST/mysql_datadirs")
                    config.set(section2, "#Optional: set warning if pid of backup us running for longer than X")
                    config.set(section2, "pid_runtime_warning", "2 Hours")
                    config.set(section2, "backupdir", "/home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_7") # Can be changed in the future depending on PS version
                    config.set(section2, "backup_tool", "{}/target/percona-xtrabackup-2.4.x-debug/bin/xtrabackup".format(self.testpath))
                    config.set(section2, "#Optional: specify different path/version of xtrabackup here for prepare")
                    config.set(section2, "#prepare_tool", "")
                    config.set(section2, "xtra_prepare", "--apply-log-only")
                    config.set(section2, "#Optional: pass additional options for backup stage")
                    config.set(section2, "#xtra_backup", "--compact")
                    config.set(section2, "#Optional: pass additional options for prepare stage")
                    config.set(section2, "#xtra_prepare_options", "--rebuild-indexes")
                    config.set(section2, "#Optional: pass general additional options; it will go to both for backup and prepare")
                    config.set(section2, "#xtra_options", "--binlog-info=ON --galera-info")
                    config.set(section2, "#Optional: set archive and rotation")
                    config.set(section2, "#archive_dir", "/home/shahriyar.rzaev/XB_TEST/backup_archives")
                    config.set(section2, "#full_backup_interval", "1 day")
                    config.set(section2, "#max_archive_size", "100GiB")
                    config.set(section2, "#max_archive_duration", "4 Days")
                    config.set(section2, "#Optional WARNING(Enable this if you want to take partial backups). Specify database names or table names.")
                    config.set(section2, "#partial_list", "test.t1 test.t2 dbtest")

                    config.write(cfgfile)

        except Exception as err:
            logger.error("Failed to generate config file...")
            logger.error(err)
            return False
        else:
            logger.debug("Config file generated successfully...")
            return True