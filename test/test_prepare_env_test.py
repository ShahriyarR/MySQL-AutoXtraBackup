from prepare_env_test_mode.clone_build_start_server import CloneBuildStartServer
import pytest

@pytest.mark.usefixtures("return_clone_obj")
class TestBackupTestMode:
    """
    Tests for prepare_env_test_mode module
    """

    def test_clone_percona_qa(self, return_clone_obj):
        assert return_clone_obj.clone_percona_qa(return_clone_obj.testpath) == True
