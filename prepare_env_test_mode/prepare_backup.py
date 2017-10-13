from backup_prepare.prepare import Prepare
from prepare_env_test_mode.clone_build_start_server import CloneBuildStartServer


class WrapperForPrepareTest(CloneBuildStartServer):

    def __init__(self):
        super().__init__()
        self.prepare_obj = Prepare(config="{}/xb_2_4.conf".format(self.testpath))

    def run_prepare_backup_and_copy_back(self):
        self.prepare_obj.prepare_inc_full_backups()
        self.prepare_obj.copy_back_action()