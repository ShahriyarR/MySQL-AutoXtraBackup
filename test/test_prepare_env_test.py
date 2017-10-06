import pytest

@pytest.mark.usefixtures("return_clone_obj")
class TestBackupTestMode:
    """
    Tests for prepare_env_test_mode module
    """

    def test_clone_percona_qa(self, return_clone_obj):
        assert return_clone_obj.clone_percona_qa(test_path=return_clone_obj.testpath) == True

    def test_clone_ps_server_from_conf(self, return_clone_obj):
        assert return_clone_obj.clone_ps_server_from_conf(git_cmd=return_clone_obj.git_cmd, test_path=return_clone_obj.testpath) == True

    def test_build_server(self, return_clone_obj):
        assert return_clone_obj.build_server(return_clone_obj.testpath) == True

    def test_prepare_startup(self, return_clone_obj):
        basedir = return_clone_obj.get_basedir(return_clone_obj.testpath)
        assert return_clone_obj.prepare_startup(basedir_path=basedir, test_path=return_clone_obj.testpath) == True

    def test_start_server(self, return_clone_obj):
        basedir = return_clone_obj.get_basedir(return_clone_obj.testpath)
        assert return_clone_obj.start_server(basedir_path=basedir)