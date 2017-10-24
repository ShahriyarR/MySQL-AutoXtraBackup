from prepare_env_test_mode.clone_build_start_server import CloneBuildStartServer
from prepare_env_test_mode.config_generator import ConfigGenerator
from prepare_env_test_mode.run_benchmark import RunBenchmark
from prepare_env_test_mode.take_backup import WrapperForBackupTest
from prepare_env_test_mode.prepare_backup import WrapperForPrepareTest
from general_conf.generalops import GeneralClass
import os
import logging
logger = logging.getLogger(__name__)

class RunnerTestMode(GeneralClass):

    def __init__(self, config='/etc/bck.conf'):
        self.conf = config
        super().__init__(config=self.conf)

        self.clone_obj = CloneBuildStartServer(config=self.conf)
        self.basedirs = self.clone_obj.get_basedir()

    def wipe_backup_prepare_copyback(self, basedir):
        # TODO: figure out how to create cycle{num} for each cycle inside backup dir
        for options in ConfigGenerator(config=self.conf).options_combination_generator(self.mysql_options):
            logger.debug("Will start MySQL with {}".format(" ".join(options)))
            if self.clone_obj.wipe_server_all(basedir_path=basedir, options=" ".join(options)):
                WrapperForBackupTest(config=self.conf).run_all_backup()
                #WrapperForPrepareTest(config=self.conf).run_prepare_backup()
                #WrapperForPrepareTest(config=self.conf).copy_back_action()