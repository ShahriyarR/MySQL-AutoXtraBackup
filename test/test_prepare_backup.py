import pytest


@pytest.mark.usefixtures("return_prepare_backup_obj")
class TestPrepareBackup:
    # class for prepare_backup.py
    def test_run_prepare_backup_and_copy_back(self, return_prepare_backup_obj):
        return_prepare_backup_obj.run_prepare_backup_and_copy_back()

