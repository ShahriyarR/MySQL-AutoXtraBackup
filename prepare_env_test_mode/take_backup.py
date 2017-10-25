from master_backup_script.backuper import Backup
from prepare_env_test_mode.run_benchmark import RunBenchmark

class WrapperForBackupTest(Backup):

    def __init__(self, config='/etc/bck.conf', full_dir=None, inc_dir=None, basedir=None):
        self.conf = config
        super().__init__(config=self.conf)
        if full_dir is not None:
            self.full_dir = full_dir
        if inc_dir is not None:
            self.inc_dir = inc_dir
        if basedir is not None:
            self.basedir = basedir


    def run_all_backup(self):
        # Method for taking backups using master_backup_script.backuper.py::all_backup()
        RunBenchmark().run_sysbench_prepare(basedir=self.basedir)
        for _ in range(int(self.incremental_count) + 1):
            RunBenchmark().run_sysbench_run(basedir=self.basedir)
            self.all_backup()
