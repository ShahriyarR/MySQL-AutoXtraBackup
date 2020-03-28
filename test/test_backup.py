# PyTest file for testing Backup class
from backup_backup.backuper import Backup
from general_conf.generalops import GeneralClass
import pytest
import os


@pytest.mark.usefixtures('return_bck_obj')
class TestBackup:

    def test_create_mysql_client_command(self, return_bck_obj):
        result = '/usr/bin/mysql --defaults-file= -uroot --password=12345 --socket=/var/lib/mysql/mysql.sock -e "select 1"'
        sql = "select 1"
        assert return_bck_obj.create_mysql_client_command(sql) == result

    def test_full_backup_without_tag(self, return_bck_obj):
        return_bck_obj.clean_full_backup_dir()
        return_bck_obj.full_backup()

    def test_full_backup_with_tag(self, return_bck_obj):
        return_bck_obj.clean_full_backup_dir()
        # Giving some tag information
        return_bck_obj.tag = "My first full backup"
        return_bck_obj.full_backup()
        # Making it None back for global object
        return_bck_obj.tag = None
        # Check if the backup tag file is created and contains given string
        assert os.path.isfile("{}/backup_tags.txt".format(return_bck_obj.backupdir))
        with open("{}/backup_tags.txt".format(return_bck_obj.backupdir), 'r') as file:
            assert "My first full backup" in file.read()



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
