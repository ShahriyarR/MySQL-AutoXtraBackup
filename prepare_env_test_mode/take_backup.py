from master_backup_script.backuper import Backup
from prepare_env_test_mode.run_benchmark import RunBenchmark
from time import sleep
import os
import shutil
import logging
import concurrent.futures
from shlex import split
from subprocess import Popen
logger = logging.getLogger(__name__)


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

    @staticmethod
    def general_tablespace_rel(basedir):
        directory = "{}/relative_path".format(basedir)

        if os.path.exists(directory):
            try:
                logger.debug("Removing relative_path...")
                shutil.rmtree(directory)
            except Exception as err:
                logger.debug("FAILED: Removing relative_path")
                logger.error(err)

        try:
            logger.debug("Creating relative_path...")
            os.makedirs(directory)
        except Exception as err:
            logger.debug("FAILED: Creating relative_path")
            logger.error(err)

    @staticmethod
    def parallel_sleep_queries(basedir, sql, sock):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        bash_command = "{}/run_sql_queries.sh {} {} '{}'".format(dir_path, basedir, sock, sql)
        try:
            process = Popen(
                split(bash_command),
                stdin=None,
                stdout=None,
                stderr=None)
        except Exception as e:
            print(e)

    def run_all_backup(self):
        # Method for taking backups using master_backup_script.backuper.py::all_backup()
        RunBenchmark().run_sysbench_prepare(basedir=self.basedir)
        if '5.7' in self.basedir:
            # Fix for https://github.com/ShahriyarR/MySQL-AutoXtraBackup/issues/205
            # Adding compression column with predefined dictionary.
            sql_create_dictionary = "CREATE COMPRESSION_DICTIONARY numbers('08566691963-88624912351-16662227201-46648573979-64646226163-77505759394-75470094713-41097360717-15161106334-50535565977')"
            RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_create_dictionary)

            # Fix for https://github.com/ShahriyarR/MySQL-AutoXtraBackup/issues/229
            # Creating encrypted general tablespace
            sql_create_tablespace = "create tablespace ts3_enc add datafile 'ts3_enc.ibd' encryption='Y'"
            RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_create_tablespace)

            for i in range(1, 5):
                sql_encrypt = "alter table sysbench_test_db.sbtest{} encryption='Y'".format(i)
                RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_encrypt)
                # Compression related issue -> https://bugs.launchpad.net/percona-xtrabackup/+bug/1641745
                # Disabling for now
                # TODO: Enable this after #1641745 is fixed. Or disable 64K page size for MySQL;disabled.
                sql_compress = "alter table sysbench_test_db.sbtest{} compression='lz4'".format(i)
                RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_compress)
                sql_optimize = "optimize table sysbench_test_db.sbtest{}".format(i)
                RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_optimize)
                # Fix for https://github.com/ShahriyarR/MySQL-AutoXtraBackup/issues/196
                # Adding JSON + virtual + stored columns here
                sql_virtual_column = "alter table sysbench_test_db.sbtest{} add column json_test_v json generated always as (json_array(k,c,pad)) virtual".format(i)
                RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_virtual_column)
                sql_stored_column = "alter table sysbench_test_db.sbtest{} add column json_test_s json generated always as (json_array(k,c,pad)) stored".format(i)
                RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_stored_column)
                sql_create_json_column = "alter table sysbench_test_db.sbtest{} add column json_test_index varchar(255) generated always as (json_array(k,c,pad)) stored".format(i)
                RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_create_json_column)
                sql_alter_add_index = "alter table sysbench_test_db.sbtest{} add index(json_test_index)".format(i)
                RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_alter_add_index)

            general_tablespace = "create tablespace ts1 add datafile 'ts1.ibd' engine=innodb"
            RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=general_tablespace)

            outside_tablespace_full_path = '{}/out_ts1.ibd'.format(self.basedir)
            if os.path.isfile(outside_tablespace_full_path):
                os.remove(outside_tablespace_full_path)
            # Fix for https://github.com/ShahriyarR/MySQL-AutoXtraBackup/issues/219
            general_out_tablespace = "create tablespace out_ts1 add datafile '{}' engine=innodb".format(outside_tablespace_full_path)
            RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=general_out_tablespace)
            # Create general tablespace with relative path
            # TODO: enable this after fix for https://bugs.launchpad.net/percona-xtrabackup/+bug/1736380
            # self.general_tablespace_rel(self.basedir)
            # general_out_relative = "create tablespace out_rel_ts1 add datafile '../relative_path/out_rel_ts1.ibd' engine=innodb"
            # RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=general_out_relative)

            for i in range(5, 10):
                sql_compress = "alter table sysbench_test_db.sbtest{} compression='zlib'".format(i)
                RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_compress)
                sql_optimize = "optimize table sysbench_test_db.sbtest{}".format(i)
                RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_optimize)
                sql_alter_compression_dict = "alter table sysbench_test_db.sbtest{} modify c varchar(250) column_format compressed with compression_dictionary numbers".format(i)
                RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_alter_compression_dict)

            for i in range(10, 15):
                # Fix for https://github.com/ShahriyarR/MySQL-AutoXtraBackup/issues/206
                # Altering some tables to use general tablespace.
                sql_virtual_column = "alter table sysbench_test_db.sbtest{} add column json_test_v json generated always as (json_array(k,c,pad)) virtual".format(i)
                RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_virtual_column)
                sql_stored_column = "alter table sysbench_test_db.sbtest{} add column json_test_s json generated always as (json_array(k,c,pad)) stored".format(i)
                RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_stored_column)
                sql_create_json_column = "alter table sysbench_test_db.sbtest{} add column json_test_index varchar(255) generated always as (json_array(k,c,pad)) stored".format(i)
                RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_create_json_column)
                sql_alter_add_index = "alter table sysbench_test_db.sbtest{} add index(json_test_index)".format(i)
                RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_alter_add_index)
                sql_alter_tablespace = "alter table sysbench_test_db.sbtest{} tablespace=ts1".format(i)
                RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_alter_tablespace)

            for i in range(15, 20):
                sql_virtual_column = "alter table sysbench_test_db.sbtest{} add column json_test_v json generated always as (json_array(k,c,pad)) virtual".format(i)
                RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_virtual_column)
                sql_stored_column = "alter table sysbench_test_db.sbtest{} add column json_test_s json generated always as (json_array(k,c,pad)) stored".format(i)
                RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_stored_column)
                sql_create_json_column = "alter table sysbench_test_db.sbtest{} add column json_test_index varchar(255) generated always as (json_array(k,c,pad)) stored".format(i)
                RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_create_json_column)
                sql_alter_add_index = "alter table sysbench_test_db.sbtest{} add index(json_test_index)".format(i)
                RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_alter_add_index)
                sql_alter_tablespace = "alter table sysbench_test_db.sbtest{} tablespace=out_ts1".format(i)
                RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_alter_tablespace)

            for i in range(25, 30):
                # Altering encrypted tables to use encrypted general tablespace
                sql_encrypt = "alter table sysbench_test_db.sbtest{} encryption='Y'".format(i)
                RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_encrypt)

                sql_virtual_column = "alter table sysbench_test_db.sbtest{} add column json_test_v json generated always as (json_array(k,c,pad)) virtual".format(
                    i)
                RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_virtual_column)
                sql_stored_column = "alter table sysbench_test_db.sbtest{} add column json_test_s json generated always as (json_array(k,c,pad)) stored".format(
                    i)
                RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_stored_column)
                sql_create_json_column = "alter table sysbench_test_db.sbtest{} add column json_test_index varchar(255) generated always as (json_array(k,c,pad)) stored".format(
                    i)
                RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_create_json_column)
                sql_alter_add_index = "alter table sysbench_test_db.sbtest{} add index(json_test_index)".format(i)
                RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_alter_add_index)

                sql_alter_tablespace = "alter table sysbench_test_db.sbtest{} tablespace=ts3_enc".format(i)
                RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_alter_tablespace)

            # TODO: enable this after fix for https://bugs.launchpad.net/percona-xtrabackup/+bug/1736380
            # for i in range(20, 25):
            #     sql_virtual_column = "alter table sysbench_test_db.sbtest{} add column json_test_v json generated always as (json_array(k,c,pad)) virtual".format(
            #         i)
            #     RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_virtual_column)
            #     sql_stored_column = "alter table sysbench_test_db.sbtest{} add column json_test_s json generated always as (json_array(k,c,pad)) stored".format(
            #         i)
            #     RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_stored_column)
            #     sql_create_json_column = "alter table sysbench_test_db.sbtest{} add column json_test_index varchar(255) generated always as (json_array(k,c,pad)) stored".format(
            #         i)
            #     RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_create_json_column)
            #     sql_alter_add_index = "alter table sysbench_test_db.sbtest{} add index(json_test_index)".format(i)
            #     RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_alter_add_index)
            #     sql_alter_tablespace = "alter table sysbench_test_db.sbtest{} tablespace=out_rel_ts1".format(i)
            #     RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_alter_tablespace)

            # NOTE: PXB will ignore rocksdb tables, which is going to break pt-table-checksum
            # for i in range(10, 15):
            #     sql_alter = "alter table sysbench_test_db.sbtest{} engine=rocksdb".format(i)
            #     RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_alter)
        # NOTE: PXB will ignore tokudb tables, which is going to break pt-table-checksum
        # for i in range(15, 20):
        #     sql_alter = "alter table sysbench_test_db.sbtest{} engine=tokudb".format(i)
        #     RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_alter)
        if '5.5' in self.basedir:
            for i in range(1, 5):
                sql_alter = "alter table sysbench_test_db.sbtest{} modify c varchar(120) CHARACTER SET utf8 COLLATE utf8_general50_ci".format(i)
                RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_alter)

        # Altering some of the table engines from innodb to myisam
        for i in range(20, 25):
            sql_alter_engine = "alter table sysbench_test_db.sbtest{} engine=myisam".format(i)
            RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_alter_engine)

        # Fix for https://github.com/ShahriyarR/MySQL-AutoXtraBackup/issues/222
        # Creating table with data directory option
        if '5.6' in self.basedir or '5.7' in self.basedir:
            if os.path.exists('{}/{}'.format(self.basedir, 'sysbench_test_db')):
                shutil.rmtree('{}/{}'.format(self.basedir, 'sysbench_test_db'))
            sql_create_table = "create table sysbench_test_db.t1(c varchar(255)) data directory='{}'".format(self.basedir)
            RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_create_table)
            sql_insert_data = "insert into sysbench_test_db.t1 select c from sysbench_test_db.sbtest1"
            RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=sql_insert_data)

        flush_tables = "flush tables"
        RunBenchmark.run_sql_statement(basedir=self.basedir, sql_statement=flush_tables)

        sleep(10)

        for _ in range(int(self.incremental_count) + 1):
            RunBenchmark().run_sysbench_run(basedir=self.basedir)
            # Concurrently running select on myisam based tables.
            with concurrent.futures.ProcessPoolExecutor(max_workers=50) as pool:
                for _ in range(10):
                    for i in range(20, 25):
                        pool.submit(
                            self.parallel_sleep_queries(basedir=self.basedir,
                                                        sock="{}/socket.sock".format(self.basedir),
                                                        sql="select benchmark(9999999, md5(c)) from sysbench_test_db.sbtest{}".format(
                                                            i)))
            self.all_backup()

        if os.path.isfile('{}/out_ts1.ibd'.format(self.basedir)):
            os.remove('{}/out_ts1.ibd'.format(self.basedir))

        if os.path.isfile('{}/sysbench_test_db/t1.ibd'.format(self.basedir)):
            os.remove('{}/sysbench_test_db/t1.ibd'.format(self.basedir))

        # TODO: enable this after fix for https://bugs.launchpad.net/percona-xtrabackup/+bug/1736380
        # self.general_tablespace_rel(self.basedir)

        return True