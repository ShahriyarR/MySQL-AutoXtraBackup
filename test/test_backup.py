# PyTest file for testing Backup class
from master_backup_script.backuper import Backup
from general_conf.generalops import GeneralClass

class TestBackup:

    def test_add_tag(self):
        # Method for checking the add_tag() static method. All parameters are hard coded.
        gen_obj = GeneralClass()
        for conf_files in gen_obj.xb_configs.split():
            if '2_3' in conf_files and '5_6' in conf_files:
                obj = Backup(config='{}/{}'.format(gen_obj.testpath, conf_files), dry_run=0, tag="My first full backup")
                backup_name = obj.recent_full_backup_file()
                obj.add_tag(backup_dir=obj.backupdir, backup_name=backup_name, type=obj.tag)
