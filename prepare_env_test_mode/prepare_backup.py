from backup_prepare.prepare import Prepare


class WrapperForPrepareTest(Prepare):

    def __init__(self, config='/etc/bck.conf', full_dir=None, inc_dir=None):
        self.conf = config
        super().__init__(config=self.conf)
        if full_dir is not None:
            self.full_dir = full_dir
        if inc_dir is not None:
            self.inc_dir = inc_dir

    def run_prepare_backup(self):
        self.prepare_inc_full_backups()
        return True

    def run_copy_back(self):
        self.copy_back_action()
        return True