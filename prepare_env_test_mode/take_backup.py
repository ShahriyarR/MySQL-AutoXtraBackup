from master_backup_script.backuper import Backup
from prepare_env_test_mode.run_benchmark import RunBenchmark
from time import sleep


class WrapperForBackupTest(Backup):
    # The Backup class child to do some staff for backup in --test_mode
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
        if '5.7' in self.basedir:
            for i in range(1, 10):
                sql_encrypt = "alter table sysbench_test_db.sbtest{} encryption='Y'".format(i)
                RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_encrypt)
                # Compression related issue -> https://bugs.launchpad.net/percona-xtrabackup/+bug/1641745
                # Disabling for now
                # TODO: Enable this after #1641745 is fixed.
                # sql_compress = "alter table sysbench_test_db.sbtest{} compression='lz4'".format(i)
                # RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_compress)
                # sql_optimize = "optimize table sysbench_test_db.sbtest{}".format(i)
                # RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_optimize)
            # NOTE: PXB will ignore rocksdb tables, which is going to break pt-table-checksum
            # for i in range(10, 15):
            #     sql_alter = "alter table sysbench_test_db.sbtest{} engine=rocksdb".format(i)
            #     RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_alter)
        # NOTE: PXB will ignore tokudb tables, which is going to break pt-table-checksum
        # for i in range(15, 20):
        #     sql_alter = "alter table sysbench_test_db.sbtest{} engine=tokudb".format(i)
        #     RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_alter)

        flush_tables = "flush tables"
        RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=flush_tables)
        sleep(20)

        for _ in range(int(self.incremental_count) + 1):
            RunBenchmark().run_sysbench_run(basedir=self.basedir)
            self.all_backup()

        return True