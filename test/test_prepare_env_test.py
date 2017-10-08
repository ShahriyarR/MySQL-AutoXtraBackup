import pytest

@pytest.mark.usefixtures("return_clone_obj")
class TestBackupTestMode:
    """
    Tests for clone_build_start_server.py module
    """

    def test_clone_percona_qa(self, return_clone_obj):
        assert return_clone_obj.clone_percona_qa() == True

    def test_clone_ps_server_from_conf(self, return_clone_obj):
        assert return_clone_obj.clone_ps_server_from_conf() == True

    def test_build_server(self, return_clone_obj):
        assert return_clone_obj.build_server() == True

    @pytest.mark.usefixtures("return_basedir")
    def test_prepare_startup(self, return_clone_obj, return_basedir):
        basedir = return_basedir
        assert return_clone_obj.prepare_startup(basedir_path=basedir) == True

    @pytest.mark.usefixtures("return_basedir")
    def test_start_server(self, return_clone_obj, return_basedir):
        basedir = return_basedir
        assert return_clone_obj.start_server(basedir_path=basedir)