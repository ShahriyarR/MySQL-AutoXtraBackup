import pytest

@pytest.mark.usefixtures("return_clone_obj")
class TestCloneBuildStartServer:
    """
    Tests for clone_build_start_server.py module
    """

    def test_clone_percona_qa(self, return_clone_obj):
        assert return_clone_obj.clone_percona_qa() is True

    def test_clone_ps_server_from_conf(self, return_clone_obj):
        assert return_clone_obj.clone_ps_server_from_conf() is True

    def test_clone_pxb(self, return_clone_obj):
        assert return_clone_obj.clone_pxb() is True

    def test_build_pxb(self, return_clone_obj):
        assert return_clone_obj.build_pxb() is True

    def test_build_server(self, return_clone_obj):
        assert return_clone_obj.build_server() is True

    def test_rename_basedirs(self, return_clone_obj):
        assert return_clone_obj.rename_basedirs() is True

    def test_get_basedir(self, return_clone_obj):
        assert isinstance(return_clone_obj.get_basedir(), list)
        assert len(return_clone_obj.get_basedir()) > 0

    @pytest.mark.usefixtures("return_basedir")
    def test_prepare_startup(self, return_clone_obj, return_basedir):
        basedir_list = return_basedir
        for basedir in basedir_list:
            assert return_clone_obj.prepare_startup(basedir_path=basedir) is True

    @pytest.mark.usefixtures("return_basedir")
    def test_prepare_start_dynamic(self, return_clone_obj, return_basedir):
        basedir_list = return_basedir
        for basedir in basedir_list:
            assert return_clone_obj.prepare_start_dynamic(basedir_path=basedir) is True

    @pytest.mark.usefixtures("return_basedir")
    def test_start_server(self, return_clone_obj, return_basedir):
        basedirs = return_basedir
        for basedir in basedirs:
            assert return_clone_obj.start_server(basedir_path=basedir)

    @pytest.mark.usefixtures("return_basedir")
    def test_wipe_server_all(self, return_clone_obj, return_basedir):
        basedirs = return_basedir
        for basedir in basedirs:
            assert return_clone_obj.wipe_server_all(basedir_path=basedir) is True

    def test_extract_xb_archive(self, return_clone_obj):
        for branch in return_clone_obj.pxb_branches.split():
            archive_name = "percona-xtrabackup-{}.x-debug.tar.gz".format(branch)
            assert return_clone_obj.extract_xb_archive(file_name=archive_name) is True