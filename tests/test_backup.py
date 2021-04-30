# PyTest file for testing Backup class
import os

import pytest


@pytest.mark.usefixtures("return_bck_obj")
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
        with open("{}/backup_tags.txt".format(return_bck_obj.backupdir), "r") as file:
            assert "My first full backup" in file.read()
