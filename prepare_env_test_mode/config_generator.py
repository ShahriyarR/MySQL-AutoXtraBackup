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
        # TODO: For now we need only generate XB 2.4 version of config with started PS server
        # TODO: For future I need to figure out how to generate configs for both version, related to PS version
        conf_2_4 = "xb_2_4.conf"
        conf_path = "{}/{}".format(self.testpath, conf_2_4)
        basedir = self.get_basedir()
        try:
            if not os.path.isfile(conf_path):
                with open(conf_path, 'w') as cfgfile:
                    config = configparser.ConfigParser()
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
                    config.write(cfgfile)

        except Exception as err:
            logger.error("Failed to generate config file...")
            logger.error(err)
            return False
        else:
            logger.debug("Config file generated successfully...")
            return True