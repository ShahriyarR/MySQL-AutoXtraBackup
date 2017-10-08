from prepare_env_test_mode.clone_build_start_server import CloneBuildStartServer
from prepare_env_test_mode.run_benchmark import RunBenchmark
import os
import logging
logger = logging.getLogger(__name__)

class RunnerTestMode:

    def __init__(self):
        self.clone_obj = CloneBuildStartServer()
        self.basedir = self.clone_obj.get_basedir()

    def all_runner(self):
        if ('PS' in self.basedir) and (os.path.isfile("{}/all".format(self.basedir))):
            if self.clone_obj.wipe_server_all(self.basedir):
                if RunBenchmark().run_sysbench():
                    # Take backup/prepare and recover here
                    pass

        elif 'PS' not in self.basedir:
            if self.clone_obj.clone_percona_qa():
                if self.clone_obj.clone_ps_server_from_conf():
                    if self.clone_obj.build_server():
                        if self.clone_obj.prepare_startup():
                            if self.clone_obj.start_server():
                                # Take backup/prepare and recover here
                                pass
