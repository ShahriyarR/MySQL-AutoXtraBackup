# PyTest file for testing Backup class
import os

import pytest


@pytest.mark.usefixtures("return_bck_obj")
class TestBackup:

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
        assert os.path.isfile("{}/backup_tags.txt".format(return_bck_obj.builder_obj.backup_options.get('backup_dir')))
        with open("{}/backup_tags.txt".format(return_bck_obj.builder_obj.backup_options.get('backup_dir')), "r") as file:
            assert "My first full backup" in file.read()

    def test_show_tags_with_wrong_file_name(self, return_bck_obj):
        assert return_bck_obj.show_tags(return_bck_obj.builder_obj.backup_options.get('backup_dir'), "dummy.txt") \
               is None

    def test_show_tags_with_correct_file_name(self, return_bck_obj):
        assert return_bck_obj.show_tags(return_bck_obj.builder_obj.backup_options.get('backup_dir')) is True

    def test_clean_full_backup_dir_dummy_path(self, return_bck_obj):
        assert return_bck_obj.clean_full_backup_dir(full_dir='NON_EXISTING_PATH_NAME') is True

    def test_clean_full_backup_dir_with_remove_all(self, return_bck_obj):
        os.makedirs('tests/DELETE_ME')
        os.makedirs('tests/DELETE_ME/2021-05-06_11-48-31')
        assert return_bck_obj.clean_full_backup_dir(full_dir=f'{os.path.dirname(__file__)}/DELETE_ME', remove_all=True) \
               is True

    def test_clean_full_backup_dir_real_path(self, return_bck_obj):
        os.makedirs('tests/DELETE_ME', exist_ok=True)
        os.makedirs('tests/DELETE_ME/2021-05-06_11-48-31', exist_ok=True)
        assert return_bck_obj.clean_full_backup_dir(full_dir=f'{os.path.dirname(__file__)}/DELETE_ME') is True