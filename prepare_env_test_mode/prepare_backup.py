from backup_prepare.prepare import Prepare


class WrapperForPrepareTest(Prepare):

    def __init__(self, config='/etc/bck.conf'):
        self.conf = config
        super().__init__(config=self.conf)

    def run_prepare_backup(self):
        self.prepare_inc_full_backups()

    def run_copy_back(self):
        self.copy_back_action()