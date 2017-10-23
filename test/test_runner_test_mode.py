import pytest

class TestRunnerTestMode:

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
