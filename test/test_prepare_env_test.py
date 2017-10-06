from prepare_env_test_mode.clone_build_start_server import CloneBuildStartServer
import pytest

@pytest.mark.usefixtures("return_clone_obj")
class TestBackupTestMode:
    """
    Tests for prepare_env_test_mode module
    """

    def test_clone_percona_qa(self, return_clone_obj):
        assert return_clone_obj.clone_percona_qa(return_clone_obj.testpath) == True

    def test_clone_ps_server_from_conf(self, return_clone_obj):
        assert return_clone_obj.clone_ps_server_from_conf(return_clone_obj.git_cmd, return_clone_obj.testpath) == True

    def test_build_server(self, return_clone_obj):
        assert return_clone_obj.build_server(return_clone_obj.testpath) == True
