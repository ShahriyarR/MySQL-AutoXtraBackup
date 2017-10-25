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
        c_count = 0
        for options in ConfigGenerator(config=self.conf).options_combination_generator(self.mysql_options):
            c_count = c_count + 1
            options = " ".join(options)
            logger.debug("Will start MySQL with {}".format(options))
            if self.clone_obj.wipe_server_all(basedir_path=basedir, options=options):
                logger.debug("Starting cycle{}".format(c_count))
                full_dir = self.backupdir + "/cycle{}".format(c_count) + "/full"
                inc_dir = self.backupdir + "/cycle{}".format(c_count) + "/inc"
                WrapperForBackupTest(config=self.conf, full_dir=full_dir, inc_dir=inc_dir, basedir=basedir).run_all_backup()
                prepare_obj = WrapperForPrepareTest(config=self.conf, full_dir=full_dir, inc_dir=inc_dir)
                prepare_obj.run_prepare_backup()
                prepare_obj.copy_back_action(options=options)