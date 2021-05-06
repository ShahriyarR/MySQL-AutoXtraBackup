import os
import shutil

from mysql_autoxtrabackup.utils import helpers


class TestHelpers:
    def test_get_latest_dir_name(self):
        os.makedirs("tests/DELETE_ME", mode=777, exist_ok=True)
        os.makedirs("tests/DELETE_ME/2021-05-06_11-48-31", mode=777, exist_ok=True)
        os.makedirs("tests/DELETE_ME/2021-05-06_11-47-31", mode=777, exist_ok=True)

        assert (
            helpers.get_latest_dir_name(path=f"{os.path.dirname(__file__)}/DELETE_ME")
            == "2021-05-06_11-48-31"
        )

    def test_create_backup_directory(self):
        path_ = f"{os.path.dirname(__file__)}/DELETE_ME"
        assert helpers.create_backup_directory(path_, "TEST_DIR") == f"{path_}/TEST_DIR"
        shutil.rmtree(f"{path_}/TEST_DIR")
