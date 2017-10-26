import pytest

class TestRunnerTestMode:

    # No matter here which fixture to choose I need an object
    @pytest.mark.usefixtures("return_runner_test_mode_obj_5_6_xb_2_3")
    def test_get_free_tcp_port(self, return_runner_test_mode_obj_5_6_xb_2_3):
        return_runner_test_mode_obj_5_6_xb_2_3.get_free_tcp_port()

    @pytest.mark.usefixtures("return_runner_test_mode_obj_5_6_xb_2_3", "return_run_benchmark_obj")
    def test_run_pt_table_checksum(self, return_runner_test_mode_obj_5_6_xb_2_3, return_run_benchmark_obj):
        for basedir in return_runner_test_mode_obj_5_6_xb_2_3.basedirs:
            if '5.6' in basedir:
                socket = return_run_benchmark_obj.get_sock(basedir=basedir)
                conn_options = "--user={} --socket={}".format('root', socket)
        return_runner_test_mode_obj_5_6_xb_2_3.run_pt_table_checksum(conn_options=conn_options)


    @pytest.mark.usefixtures("return_runner_test_mode_obj_5_6_xb_2_3")
    def test_wipe_backup_prepare_copyback_5_6_xb_2_3(self, return_runner_test_mode_obj_5_6_xb_2_3):
        for basedir in return_runner_test_mode_obj_5_6_xb_2_3.basedirs:
            if '5.6' in basedir:
                return_runner_test_mode_obj_5_6_xb_2_3.wipe_backup_prepare_copyback(basedir=basedir)

    @pytest.mark.usefixtures("return_runner_test_mode_obj_5_6_xb_2_4")
    def test_wipe_backup_prepare_copyback_5_6_xb_2_4(self, return_runner_test_mode_obj_5_6_xb_2_4):
        for basedir in return_runner_test_mode_obj_5_6_xb_2_4.basedirs:
            if '5.6' in basedir:
                return_runner_test_mode_obj_5_6_xb_2_4.wipe_backup_prepare_copyback(basedir=basedir)

    @pytest.mark.usefixtures("return_runner_test_mode_obj_5_7_xb_2_4")
    def test_wipe_backup_prepare_copyback_5_7_xb_2_4(self, return_runner_test_mode_obj_5_7_xb_2_4):
        for basedir in return_runner_test_mode_obj_5_7_xb_2_4.basedirs:
            if '5.7' in basedir:
                return_runner_test_mode_obj_5_7_xb_2_4.wipe_backup_prepare_copyback(basedir=basedir)
