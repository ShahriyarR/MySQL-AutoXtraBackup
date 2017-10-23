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
        for options in ConfigGenerator.options_combination_generator(self.mysql_options):
            if self.clone_obj.wipe_server_all(basedir_path=basedir, options=" ".join(options)):
                WrapperForBackupTest(config=self.conf).run_all_backup()
                #WrapperForPrepareTest(config=self.conf).run_prepare_backup()
                #WrapperForPrepareTest(config=self.conf).copy_back_action()



        # else:
        #     logger.debug("Starting test setup from scratch...")
        #     if self.clone_obj.clone_percona_qa():
        #         if self.clone_obj.clone_ps_server_from_conf():
        #             if self.clone_obj.build_server():
        #                 base_dir = self.clone_obj.get_basedir()
        #                 if self.clone_obj.prepare_startup(basedir_path=base_dir):
        #                     if self.clone_obj.start_server(basedir_path=base_dir):
        #                         url_2_4 = "http://jenkins.percona.com/view/QA/job/qa.pxb24.build/BUILD_TYPE=debug,label_exp=centos7-64/lastSuccessfulBuild/artifact/target/percona-xtrabackup-2.4.x-debug.tar.gz"
        #                         url_2_3 = "http://jenkins.percona.com/view/QA/job/qa.pxb23.build/BUILD_TYPE=debug,label_exp=centos7-64/lastSuccessfulBuild/artifact/target/percona-xtrabackup-2.3.x-debug.tar.gz"
        #                         if self.clone_obj.get_xb_packages(url_2_4[-37:], url_2_4):
        #                             if self.clone_obj.get_xb_packages(url_2_3[-37:], url_2_3):
        #                                 archive_2_4 = "percona-xtrabackup-2.4.x-debug.tar.gz"
        #                                 archive_2_3 = "percona-xtrabackup-2.3.x-debug.tar.gz"
        #                                 if self.clone_obj.extract_xb_archive(file_name=archive_2_4):
        #                                     if self.clone_obj.extract_xb_archive(file_name=archive_2_3):
        #                                         # TODO: fix logic here
        #                                         conf_obj = ConfigGenerator()
        #                                         if conf_obj.generate_config_files():
        #                                             if RunBenchmark().run_sysbench():
        #                                                 # Take backup
        #                                                 WrapperForBackupTest().run_all_backup()
        #                                                 WrapperForPrepareTest().run_prepare_backup()
        #                                                 WrapperForPrepareTest().copy_back_action()
        #                                                 pass