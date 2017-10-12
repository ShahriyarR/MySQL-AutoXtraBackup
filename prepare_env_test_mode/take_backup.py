from master_backup_script.backuper import Backup
from prepare_env_test_mode.clone_build_start_server import CloneBuildStartServer


class WrapperForBackupTest(CloneBuildStartServer):

    def __init__(self):
        super().__init__()
        self.backup_obj = Backup(config="{}/xb_2_4.conf".format(self.testpath))


    def run_all_backup(self):
        # Method for taking backups using backuper.py::all_backup()
        for _ in range(int(self.backup_obj.incremental_count) + 1):
            self.backup_obj.all_backup()