import pytest
from fastapi.testclient import TestClient

from mysql_autoxtrabackup.api.main import app
from mysql_autoxtrabackup.backup_backup.backup_builder import BackupBuilderChecker
from mysql_autoxtrabackup.backup_backup.backup_tags import BackupTags
from mysql_autoxtrabackup.backup_backup.backuper import Backup
from mysql_autoxtrabackup.general_conf.path_config import config_path_file
from mysql_autoxtrabackup.utils.mysql_cli import MySQLClientHelper

builder_obj = BackupBuilderChecker(config=config_path_file, dry_run=None)
tagger = BackupTags(None, builder_obj)
mysql_cli = MySQLClientHelper(config=config_path_file)

bck_obj = Backup(builder_obj=builder_obj, mysql_cli=mysql_cli, tagger=tagger)
client = TestClient(app)


@pytest.fixture()
def return_bck_obj():
    return bck_obj


@pytest.fixture()
def fastapi_client():
    return client
