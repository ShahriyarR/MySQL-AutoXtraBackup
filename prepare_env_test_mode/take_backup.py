from master_backup_script.backuper import Backup
from general_conf.generalops import GeneralClass

class WrapperForBackupTest(Backup):

    def __init__(self):
        self.testpath = GeneralClass().testpath
        super().__init__(config="{}/xb_2_4.conf".format(self.testpath))


    def run_all_backup(self):
        # Method for taking backups using backuper.py::all_backup()
        for _ in range(self.incremental_count + 1):
            self.all_backup()