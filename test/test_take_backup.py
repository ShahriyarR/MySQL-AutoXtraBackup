import pytest

@pytest.mark.usefixtures("return_take_backup_obj")
class TestTakeBackup:
    # Test class for take_backup.py

    def test_run_all_backup(self, return_take_backup_obj):
        return_take_backup_obj.run_all_backup()