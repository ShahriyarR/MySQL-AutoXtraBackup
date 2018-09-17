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
                obj.add_tag(backup_dir=obj.backupdir, backup_name=backup_name, backup_type='Full', tag_string=obj.tag)

    def test_show_tags(self):
        gen_obj = GeneralClass()
        for conf_files in gen_obj.xb_configs.split():
            if '2_3' in conf_files and '5_6' in conf_files:
                obj = Backup(config='{}/{}'.format(gen_obj.testpath, conf_files))
                obj.show_tags(obj.backupdir)

    def test_full_backup(self):
        # Method for running full_backup()
        gen_obj = GeneralClass()
        for conf_files in gen_obj.xb_configs.split():
            if '2_3' in conf_files and '5_6' in conf_files:
                obj = Backup(config='{}/{}'.format(gen_obj.testpath, conf_files), dry_run=0, tag="My first full backup")
                obj.full_backup()

    def test_inc_backup(self):
        # Method for running inc_backup()
        gen_obj = GeneralClass()
        for conf_files in gen_obj.xb_configs.split():
            if '2_3' in conf_files and '5_6' in conf_files:
                obj = Backup(config='{}/{}'.format(gen_obj.testpath, conf_files), dry_run=0, tag="My first inc backup")
                obj.inc_backup()
