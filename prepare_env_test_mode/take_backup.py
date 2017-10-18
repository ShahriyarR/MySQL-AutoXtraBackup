from master_backup_script.backuper import Backup


class WrapperForBackupTest(Backup):

    def __init__(self, config='/etc/bck.conf'):
        self.conf = config
        super().__init__(config=self.conf)


    def run_all_backup(self):
        # Method for taking backups using backuper.py::all_backup()
        for _ in range(int(self.incremental_count) + 1):
            self.all_backup()