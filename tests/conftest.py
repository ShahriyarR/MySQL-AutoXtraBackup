import pytest

from backup_backup.backuper import Backup

bck_obj = Backup()


@pytest.fixture()
def return_bck_obj():
    return bck_obj
