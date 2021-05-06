import pytest
from fastapi.testclient import TestClient

from mysql_autoxtrabackup.api.main import app
from mysql_autoxtrabackup.backup_backup.backuper import Backup

bck_obj = Backup()
client = TestClient(app)


@pytest.fixture()
def return_bck_obj():
    return bck_obj


@pytest.fixture()
def fastapi_client():
    return client
