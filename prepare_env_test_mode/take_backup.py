from master_backup_script.backuper import Backup


class WrapperForBackupTest(Backup):

    def __init__(self, config='/etc/bck.conf', full_dir=None, inc_dir=None):
        self.conf = config
        super().__init__(config=self.conf)
        if full_dir is not None:
            self.full_dir = full_dir
        if inc_dir is not None:
            self.inc_dir = inc_dir

    def run_all_backup(self):
        # Method for taking backups using backuper.py::all_backup()
        for _ in range(int(self.incremental_count) + 1):
            self.all_backup()