from general_conf.generalops import GeneralClass
from prepare_env_test_mode.prepare_backup import WrapperForPrepareTest


class TestPrepareBackup:
    # class for prepare_env_test_mode.prepare_backup.py
    def test_run_prepare_backup(self):
        gen_obj = GeneralClass()
        for conf_files in gen_obj.xb_configs.split():
            obj = WrapperForPrepareTest(config='{}/{}'.format(gen_obj.testpath, conf_files))
            obj.run_prepare_backup()

    def test_run_copy_back(self):
        gen_obj = GeneralClass()
        for conf_files in gen_obj.xb_configs.split():
            obj = WrapperForPrepareTest(config='{}/{}'.format(gen_obj.testpath, conf_files))
            obj.run_copy_back()

