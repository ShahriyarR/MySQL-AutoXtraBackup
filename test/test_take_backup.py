import pytest
from prepare_env_test_mode.take_backup import WrapperForBackupTest
from general_conf.generalops import GeneralClass

class TestTakeBackup:
    # Test class for take_backup.py

    def test_run_all_backup(self):
        gen_obj = GeneralClass()
        for conf_files in gen_obj.xb_configs:
            if ('5_7' in conf_files) and ('2_4' in conf_files):
                obj = WrapperForBackupTest(config='{}/{}'.format(gen_obj.testpath, conf_files))
                obj.run_all_backup()


