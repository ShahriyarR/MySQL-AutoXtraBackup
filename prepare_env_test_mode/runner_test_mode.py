from prepare_env_test_mode.clone_build_start_server import CloneBuildStartServer
from prepare_env_test_mode.config_generator import ConfigGenerator
from prepare_env_test_mode.run_benchmark import RunBenchmark
from prepare_env_test_mode.take_backup import WrapperForBackupTest
from prepare_env_test_mode.prepare_backup import WrapperForPrepareTest
import os
import logging
logger = logging.getLogger(__name__)

class RunnerTestMode:

    def __init__(self):
        self.clone_obj = CloneBuildStartServer()
        self.basedirs = self.clone_obj.get_basedir()

    def all_runner(self):
        for basedir in self.basedirs:
            if basedir and (os.path.isfile("{}/all_no_cl".format(basedir))):
                logger.debug("It seems to be the test setup already done...")
                if self.clone_obj.wipe_server_all(basedir_path=basedir):
                    if RunBenchmark().run_sysbench(basedir=basedir):
                        # Take backup
                        # TODO: pass the config file path here; for now it is hardcoded in side classed below
                        WrapperForBackupTest().run_all_backup()
                        WrapperForPrepareTest().run_prepare_backup()
                        WrapperForPrepareTest().copy_back_action()
                        pass

        else:
            logger.debug("Starting test setup from scratch...")
            if self.clone_obj.clone_percona_qa():
                if self.clone_obj.clone_ps_server_from_conf():
                    if self.clone_obj.build_server():
                        base_dir = self.clone_obj.get_basedir()
                        if self.clone_obj.prepare_startup(basedir_path=base_dir):
                            if self.clone_obj.start_server(basedir_path=base_dir):
                                url_2_4 = "http://jenkins.percona.com/view/QA/job/qa.pxb24.build/BUILD_TYPE=debug,label_exp=centos7-64/lastSuccessfulBuild/artifact/target/percona-xtrabackup-2.4.x-debug.tar.gz"
                                url_2_3 = "http://jenkins.percona.com/view/QA/job/qa.pxb23.build/BUILD_TYPE=debug,label_exp=centos7-64/lastSuccessfulBuild/artifact/target/percona-xtrabackup-2.3.x-debug.tar.gz"
                                if self.clone_obj.get_xb_packages(url_2_4[-37:], url_2_4):
                                    if self.clone_obj.get_xb_packages(url_2_3[-37:], url_2_3):
                                        archive_2_4 = "percona-xtrabackup-2.4.x-debug.tar.gz"
                                        archive_2_3 = "percona-xtrabackup-2.3.x-debug.tar.gz"
                                        if self.clone_obj.extract_xb_archive(file_name=archive_2_4):
                                            if self.clone_obj.extract_xb_archive(file_name=archive_2_3):
                                                # TODO: fix logic here
                                                conf_obj = ConfigGenerator()
                                                if conf_obj.generate_config_files():
                                                    if RunBenchmark().run_sysbench():
                                                        # Take backup
                                                        WrapperForBackupTest().run_all_backup()
                                                        WrapperForPrepareTest().run_prepare_backup()
                                                        WrapperForPrepareTest().copy_back_action()
                                                        pass